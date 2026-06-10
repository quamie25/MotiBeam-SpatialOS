"""
presence_node.py — MotiBeam bidirectional CircleBeam link
Manages the persistent TCP connection between Pi 4 and Pi 5.

Architecture: each node is both server (accepts incoming) and client (connects
outward). Either side can reconnect after a link drop without a reboot.

Resilience features:
  - SO_REUSEADDR + SO_KEEPALIVE on all sockets
  - Application heartbeat every 25 s (PRESENCE_HEARTBEAT) keeps TCP alive
  - Watchdog: if no message received in 90 s, tears down and reconnects
  - Client reconnects with exponential backoff (2 → 4 → 8 → 16 → 32 s)
  - broadcast() queues messages if disconnected; delivers on reconnect
  - All socket errors are caught; link never poisons the main thread

API (consumed by spatial_os.py):
  PresenceNode(my_port, peer_host, peer_port, node_name)
  .start(event_queue)   — begin background threads
  .broadcast(dict)      — enqueue outbound JSON message
  .node_name            — string attribute
"""

import json
import queue
import socket
import threading
import time

# -------------------------------------------------------------------
# Tuning constants
# -------------------------------------------------------------------
_HEARTBEAT_INTERVAL  = 25    # seconds between outbound heartbeats
_WATCHDOG_TIMEOUT    = 90    # seconds of silence before reconnect
_RECONNECT_DELAYS    = [2, 4, 8, 16, 32]   # backoff ladder; last value repeats
_SEND_QUEUE_MAXSIZE  = 64    # bound the outbound queue
_RECV_BUF            = 4096  # TCP recv buffer size
_CONNECT_TIMEOUT     = 10    # seconds to wait for outbound connect()
_ACCEPT_TIMEOUT      = 2     # seconds between accept() polling loops


class PresenceNode:
    def __init__(self, my_port, peer_host, peer_port, node_name):
        self.my_port    = my_port
        self.peer_host  = peer_host
        self.peer_port  = peer_port
        self.node_name  = node_name

        self._event_queue  = None          # set by start()
        self._send_queue   = queue.Queue(maxsize=_SEND_QUEUE_MAXSIZE)
        self._stop         = threading.Event()

        # Shared peer socket — written by _client_loop, read by _sender_loop.
        self._peer_conn    = None
        self._conn_lock    = threading.Lock()

        # Watchdog timestamp — updated whenever any message is received.
        self._last_rx      = time.monotonic()

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def start(self, event_queue):
        self._event_queue = event_queue
        for name, target in [
            ("PresServer",    self._server_loop),
            ("PresClient",    self._client_loop),
            ("PresSender",    self._sender_loop),
            ("PresHeartbeat", self._heartbeat_loop),
            ("PresWatchdog",  self._watchdog_loop),
        ]:
            t = threading.Thread(target=target, daemon=True, name=name)
            t.start()
        print(f"[Presence] {self.node_name} started — "
              f"listening on :{self.my_port}, "
              f"peer {self.peer_host}:{self.peer_port}")

    def broadcast(self, msg):
        """Enqueue an outbound message. Never raises; drops silently if queue full."""
        try:
            self._send_queue.put_nowait(msg)
        except queue.Full:
            print(f"[Presence] send queue full — dropped {msg.get('type','?')}")

    def stop(self):
        self._stop.set()

    # -------------------------------------------------------------------
    # Server loop — accepts incoming connections from the peer
    # -------------------------------------------------------------------

    def _server_loop(self):
        while not self._stop.is_set():
            srv = None
            try:
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv.settimeout(_ACCEPT_TIMEOUT)
                srv.bind(("0.0.0.0", self.my_port))
                srv.listen(1)
                print(f"[Presence:server] listening on :{self.my_port}")
                while not self._stop.is_set():
                    try:
                        conn, addr = srv.accept()
                        print(f"[Presence:server] accepted connection from {addr[0]}")
                        self._set_keepalive(conn)
                        # Hand off to a receiver thread; keep accepting in this loop
                        t = threading.Thread(
                            target=self._recv_loop,
                            args=(conn,),
                            daemon=True,
                            name="PresRecv",
                        )
                        t.start()
                    except socket.timeout:
                        continue
            except Exception as e:
                print(f"[Presence:server] error: {e} — retrying in 5s")
                time.sleep(5)
            finally:
                _close(srv)

    # -------------------------------------------------------------------
    # Client loop — connects outward to peer, reconnects on drop
    # -------------------------------------------------------------------

    def _client_loop(self):
        delay_idx = 0
        while not self._stop.is_set():
            conn = None
            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._set_keepalive(conn)
                conn.settimeout(_CONNECT_TIMEOUT)
                print(f"[Presence:client] connecting to "
                      f"{self.peer_host}:{self.peer_port}...")
                conn.connect((self.peer_host, self.peer_port))
                conn.settimeout(None)  # blocking mode after connect
                print(f"[Presence:client] connected to {self.peer_host}")
                delay_idx = 0           # reset backoff on success
                with self._conn_lock:
                    _close(self._peer_conn)
                    self._peer_conn = conn
                    conn = None         # ownership transferred
                # Block until the connection is closed or stop requested
                self._wait_for_disconnect()
                with self._conn_lock:
                    _close(self._peer_conn)
                    self._peer_conn = None
                print(f"[Presence:client] connection closed — will reconnect")
            except Exception as e:
                _close(conn)
                with self._conn_lock:
                    self._peer_conn = None
                delay = _RECONNECT_DELAYS[min(delay_idx, len(_RECONNECT_DELAYS) - 1)]
                print(f"[Presence:client] connect failed ({e}) — "
                      f"retry in {delay}s")
                delay_idx += 1
                for _ in range(delay * 10):
                    if self._stop.is_set():
                        return
                    time.sleep(0.1)

    def _wait_for_disconnect(self):
        """Spin until the outbound connection object is cleared or stop fires."""
        while not self._stop.is_set():
            with self._conn_lock:
                if self._peer_conn is None:
                    return
            time.sleep(0.5)

    # -------------------------------------------------------------------
    # Receiver loop — reads from one accepted or connected socket
    # -------------------------------------------------------------------

    def _recv_loop(self, conn):
        buf = b""
        try:
            while not self._stop.is_set():
                try:
                    chunk = conn.recv(_RECV_BUF)
                except socket.timeout:
                    continue
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line.decode("utf-8"))
                    except Exception:
                        print(f"[Presence:recv] bad JSON: {line[:80]}")
                        continue
                    self._last_rx = time.monotonic()
                    msg_type = msg.get("type", "")
                    if msg_type == "PRESENCE_HEARTBEAT":
                        # Silently absorb — we already updated _last_rx above
                        pass
                    else:
                        print(f"[Presence:recv] {msg_type} from {msg.get('from','?')}")
                        if self._event_queue is not None:
                            try:
                                self._event_queue.put_nowait(msg)
                            except queue.Full:
                                print("[Presence:recv] event queue full — dropped")
        except Exception as e:
            print(f"[Presence:recv] error: {e}")
        finally:
            _close(conn)

    # -------------------------------------------------------------------
    # Sender loop — drains the outbound send queue over the peer socket
    # -------------------------------------------------------------------

    def _sender_loop(self):
        while not self._stop.is_set():
            try:
                msg = self._send_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            sent = False
            for attempt in range(3):
                with self._conn_lock:
                    conn = self._peer_conn
                if conn is None:
                    time.sleep(0.5)
                    continue
                try:
                    data = (json.dumps(msg) + "\n").encode("utf-8")
                    conn.sendall(data)
                    sent = True
                    break
                except Exception as e:
                    print(f"[Presence:send] error (attempt {attempt+1}): {e}")
                    with self._conn_lock:
                        if self._peer_conn is conn:
                            _close(self._peer_conn)
                            self._peer_conn = None
                    time.sleep(0.5)
            if not sent:
                print(f"[Presence:send] dropped {msg.get('type','?')} "
                      f"after 3 attempts — no connection")

    # -------------------------------------------------------------------
    # Heartbeat loop — sends PRESENCE_HEARTBEAT every 25 s
    # -------------------------------------------------------------------

    def _heartbeat_loop(self):
        time.sleep(_HEARTBEAT_INTERVAL)   # stagger startup
        while not self._stop.is_set():
            with self._conn_lock:
                connected = self._peer_conn is not None
            if connected:
                self.broadcast({"type": "PRESENCE_HEARTBEAT",
                                "from": self.node_name})
            for _ in range(_HEARTBEAT_INTERVAL * 10):
                if self._stop.is_set():
                    return
                time.sleep(0.1)

    # -------------------------------------------------------------------
    # Watchdog loop — triggers reconnect if no traffic for 90 s
    # -------------------------------------------------------------------

    def _watchdog_loop(self):
        time.sleep(_WATCHDOG_TIMEOUT)     # let connection establish first
        while not self._stop.is_set():
            silence = time.monotonic() - self._last_rx
            if silence > _WATCHDOG_TIMEOUT:
                with self._conn_lock:
                    connected = self._peer_conn is not None
                if connected:
                    print(f"[Presence:watchdog] {silence:.0f}s silence — "
                          f"dropping stale connection to force reconnect")
                    with self._conn_lock:
                        _close(self._peer_conn)
                        self._peer_conn = None
                    self._last_rx = time.monotonic()  # reset so we don't thrash
            time.sleep(10)

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _set_keepalive(sock):
        """Enable OS-level TCP keepalive probes."""
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Linux-specific: idle 30s, probe every 10s, 6 probes before drop
            if hasattr(socket, "TCP_KEEPIDLE"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE,  30)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT,    6)
        except Exception:
            pass  # keepalive is best-effort; not fatal if unsupported


def _close(sock):
    """Close a socket without raising."""
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass
