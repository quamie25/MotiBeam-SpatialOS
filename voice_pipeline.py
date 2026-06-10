"""
voice_pipeline.py — MotiBeam wake-word listener for Pi 4
Runs Vosk speech recognition in a background thread, maps transcripts to
command tokens, and enqueues them for spatial_os.py to consume.

API (consumed by spatial_os.py):
  VoicePipeline(queue)  — constructor
  .start()              — begin listening thread
  get_pending_tone()    — return and clear the next UI tone ('wake'/'confirm'/'back'/None)
"""

import threading
import queue as _queue
import os
import json

# ---------------------------------------------------------------------------
# Tone queue — spatial_os main thread pulls these each frame to play audio
# ---------------------------------------------------------------------------
_tone_queue = _queue.Queue()

def get_pending_tone():
    """Return the next pending tone name, or None if none queued."""
    try:
        return _tone_queue.get_nowait()
    except _queue.Empty:
        return None


# ---------------------------------------------------------------------------
# Fuzzy phrase matching
# ---------------------------------------------------------------------------

# Each entry: (canonical_command, [accepted_phrases])
# Phrases are lowercase; matching is done on normalised transcript words.
_PHRASE_TABLE = [
    ("CALL_DAD", [
        "call dad",
        "cause dad",
        "call that",
        "cause that",
        "call dead",
        "call add",
        "called dad",
        "calling dad",
        "call the dad",
    ]),
    ("NUDGE_DAD", [
        "nudge dad",
        "nuts dad",
        "nudge that",
        "notch dad",
        "nudge dead",
        "nudge the dad",
        "nods dad",
        "not dad",
    ]),
    ("WAKE", [
        "hey beam",
        "hey moti",
        "moti beam",
        "hey motibeam",
        "activate",
        "wake up",
    ]),
    ("CIRCLE", [
        "circle beam",
        "circle",
        "open circle",
        "show circle",
    ]),
    ("HOME", [
        "go home",
        "home screen",
        "main screen",
        "home",
    ]),
    ("EDUCATION", [
        "education",
        "school",
        "learning",
        "study",
    ]),
    ("HEALTH", [
        "health",
        "wellness",
        "health wellness",
    ]),
    ("PRODUCTIVITY", [
        "productivity",
        "focus",
        "work",
    ]),
    ("MARKETPLACE", [
        "marketplace",
        "market",
        "shop",
        "store",
    ]),
    ("BACK", [
        "go back",
        "back",
        "previous",
    ]),
    ("EXIT", [
        "quit",
        "exit",
        "close",
    ]),
]


def _normalise(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return " ".join(text.split())


def _char_similarity(a, b):
    """Character-level Jaccard similarity on trigrams."""
    def trigrams(s):
        return set(s[i:i+3] for i in range(len(s) - 2)) if len(s) >= 3 else set(s)
    ta, tb = trigrams(a), trigrams(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# Tuning constants — conservative to minimise false positives.
# Raise _WORD_OVERLAP_THRESHOLD toward 1.0 to tighten; lower to widen.
_WORD_OVERLAP_THRESHOLD = 0.7   # fraction of phrase words that must appear in transcript
_CHAR_SIM_THRESHOLD     = 0.45  # trigram Jaccard fallback floor
_MIN_WORD_MATCH         = 1     # absolute minimum phrase-word hits before scoring


def match_command(raw_transcript):
    """
    Map a raw Vosk transcript to a command token, or return None.

    Matching priority:
      1. Exact match after normalisation.
      2. Word-overlap: >= _WORD_OVERLAP_THRESHOLD of phrase words found in transcript.
      3. Character-similarity fallback on full strings (catches phonetic misreads).

    Returns (command_token, matched_phrase, score) or None.
    """
    norm       = _normalise(raw_transcript)
    norm_words = set(norm.split())

    best_cmd    = None
    best_phrase = None
    best_score  = 0.0

    for cmd, phrases in _PHRASE_TABLE:
        for phrase in phrases:
            phrase_words = phrase.split()

            # 1 — exact match
            if norm == phrase:
                print(f"[Voice:MATCH] exact '{norm}' → {cmd}")
                return cmd, phrase, 1.0

            # 2 — word overlap
            overlap_count = sum(1 for w in phrase_words if w in norm_words)
            if overlap_count >= _MIN_WORD_MATCH:
                overlap_score = overlap_count / len(phrase_words)
                if overlap_score >= _WORD_OVERLAP_THRESHOLD and overlap_score > best_score:
                    best_score  = overlap_score
                    best_cmd    = cmd
                    best_phrase = phrase

            # 3 — trigram character similarity fallback
            csim = _char_similarity(norm, phrase)
            if csim >= _CHAR_SIM_THRESHOLD and csim > best_score:
                best_score  = csim
                best_cmd    = cmd
                best_phrase = phrase

    if best_cmd:
        print(f"[Voice:MATCH] fuzzy '{norm}' ~ '{best_phrase}' "
              f"(score={best_score:.2f}) → {best_cmd}")
        return best_cmd, best_phrase, best_score

    print(f"[Voice:NO_MATCH] '{norm}' — below threshold, ignoring")
    return None


# ---------------------------------------------------------------------------
# VoicePipeline — Vosk-based continuous listener
# ---------------------------------------------------------------------------

_VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "/home/motibeam/vosk-model")
_SAMPLE_RATE     = 16000
_CHUNK_FRAMES    = 4000   # 0.25 s at 16 kHz


class VoicePipeline:
    def __init__(self, cmd_queue):
        self._cmd_queue = cmd_queue
        self._thread    = None
        self._stop      = threading.Event()

    def start(self):
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="VoicePipeline"
        )
        self._thread.start()
        print("[Voice] Pipeline started (Vosk, fuzzy matcher active)")

    def stop(self):
        self._stop.set()

    def _listen_loop(self):
        try:
            import vosk
        except ImportError:
            print("[Voice] vosk not installed — pipeline disabled")
            return

        try:
            model = vosk.Model(_VOSK_MODEL_PATH)
        except Exception as e:
            print(f"[Voice] Could not load model from '{_VOSK_MODEL_PATH}': {e}")
            return

        try:
            import sounddevice as sd
        except ImportError:
            print("[Voice] sounddevice not installed — pipeline disabled")
            return

        rec = vosk.KaldiRecognizer(model, _SAMPLE_RATE)
        print(f"[Voice] Listening (model={_VOSK_MODEL_PATH}, "
              f"rate={_SAMPLE_RATE}, chunk={_CHUNK_FRAMES})")

        try:
            with sd.RawInputStream(
                samplerate=_SAMPLE_RATE,
                blocksize=_CHUNK_FRAMES,
                dtype="int16",
                channels=1,
            ) as stream:
                while not self._stop.is_set():
                    data, _ = stream.read(_CHUNK_FRAMES)
                    if rec.AcceptWaveform(bytes(data)):
                        result = json.loads(rec.Result())
                        text   = result.get("text", "").strip()
                        if text:
                            print(f"[Voice:HEARD] {text}")
                            _tone_queue.put("wake")
                            match = match_command(text)
                            if match:
                                cmd, _, _ = match
                                _tone_queue.put("confirm")
                                self._cmd_queue.put(cmd)
        except Exception as e:
            print(f"[Voice] Stream error: {e}")
