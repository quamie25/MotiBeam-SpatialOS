#!/usr/bin/env python3
"""
MotiBeam Spatial OS Pro - Production System
Professional spatial computing platform for OEM licensing

All 9 Realms - Fullscreen Pygame Experience
"""

import pygame
import sys
import time
import math
import os

# Ensure imports work
sys.path.insert(0, '/home/motibeam/motibeam-spatial-os')

from core.ui.framework import Theme, UIComponents, Animations


class SpatialOSPro:
    """MotiBeam Spatial OS - Production System"""
    
    def __init__(self):
        pygame.init()
        
        # Initialize fullscreen display for projector
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("MotiBeam Spatial OS Pro")
        pygame.mouse.set_visible(False)
        
        print(f"\n{'='*70}")
        print(f"  MotiBeam Spatial OS Pro - Production System")
        print(f"  Display: {self.width}×{self.height} FULLSCREEN")
        print(f"{'='*70}\n")
        
        self.clock = pygame.time.Clock()
        self.theme = Theme()
        self.ui = UIComponents()
        
        # Realm configuration
        self.realms = {
            'home': {
                'num': '1', 'name': 'Home & Smart Living',
                'icon': '🏡', 'color': self.theme.REALM_COLORS['home'],
                'module': 'realms.home_realm_pro', 'class': 'HomeRealmPro'
            },
            'clinical': {
                'num': '2', 'name': 'Clinical & Health',
                'icon': '⚕️', 'color': self.theme.REALM_COLORS['clinical'],
                'module': 'realms.clinical_realm_pro', 'class': 'ClinicalRealmPro'
            },
            'education': {
                'num': '3', 'name': 'Education & Learning',
                'icon': '📚', 'color': self.theme.REALM_COLORS['education'],
                'module': 'realms.education_realm_pro', 'class': 'EducationRealmPro'
            },
            'transport': {
                'num': '4', 'name': 'Transport & Automotive',
                'icon': '🚗', 'color': self.theme.REALM_COLORS['transport'],
                'module': 'realms.transport_realm_pro', 'class': 'TransportRealmPro'
            },
            'emergency': {
                'num': '5', 'name': 'Emergency Response',
                'icon': '🚨', 'color': self.theme.REALM_COLORS['emergency'],
                'module': 'realms.emergency_realm_pro', 'class': 'EmergencyRealmPro'
            },
            'security': {
                'num': '6', 'name': 'Security & Surveillance',
                'icon': '🛡️', 'color': self.theme.REALM_COLORS['security'],
                'module': 'realms.security_realm_pro', 'class': 'SecurityRealmPro'
            },
            'enterprise': {
                'num': '7', 'name': 'Enterprise & Workspace',
                'icon': '🏢', 'color': self.theme.REALM_COLORS['enterprise'],
                'module': 'realms.enterprise_realm_pro', 'class': 'EnterpriseRealmPro'
            },
            'aviation': {
                'num': '8', 'name': 'Aviation & ATC',
                'icon': '✈️', 'color': self.theme.REALM_COLORS['aviation'],
                'module': 'realms.aviation_realm_pro', 'class': 'AviationRealmPro'
            },
            'maritime': {
                'num': '9', 'name': 'Maritime & Naval',
                'icon': '⚓', 'color': self.theme.REALM_COLORS['maritime'],
                'module': 'realms.maritime_realm_pro', 'class': 'MaritimeRealmPro'
            }
        }
        
        self.realm_order = ['home', 'clinical', 'education', 'transport', 
                           'emergency', 'security', 'enterprise', 'aviation', 'maritime']
        
        self.running = True
        self.selected_index = 0
    
    def draw_banner(self, elapsed: float) -> None:
        """Draw animated banner"""
        # Pulsing glow effect
        pulse = self.ui.pulse_value(elapsed, 0.5, 0.8, 1.0)
        glow_color = tuple(int(c * pulse) for c in self.theme.PRIMARY)
        
        # Title
        font_huge = pygame.font.Font(None, int(self.height * 0.12))
        title = font_huge.render("MOTIBEAM", True, glow_color)
        title_rect = title.get_rect(center=(self.width // 2, int(self.height * 0.12)))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        font_medium = pygame.font.Font(None, int(self.height * 0.04))
        subtitle = font_medium.render("SPATIAL OS PRO", True, self.theme.TEXT_SECONDARY)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, int(self.height * 0.20)))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Tagline
        font_small = pygame.font.Font(None, int(self.height * 0.025))
        tagline = font_small.render("Enterprise Spatial Computing Platform", True, self.theme.TEXT_DIM)
        tagline_rect = tagline.get_rect(center=(self.width // 2, int(self.height * 0.25)))
        self.screen.blit(tagline, tagline_rect)
    
    def draw_realm_menu(self, elapsed: float) -> None:
        """Draw professional realm selection menu"""
        # Section headers
        font_header = pygame.font.Font(None, int(self.height * 0.032))
        font_item = pygame.font.Font(None, int(self.height * 0.028))
        
        y_pos = int(self.height * 0.30)
        
        # Consumer Realms
        consumer_header = font_header.render("CONSUMER REALMS", True, self.theme.INFO)
        self.screen.blit(consumer_header, (int(self.width * 0.1), y_pos))
        y_pos += int(self.height * 0.045)
        
        for i, realm_id in enumerate(self.realm_order[:4]):
            self.draw_realm_item(realm_id, i, y_pos, elapsed, font_item)
            y_pos += int(self.height * 0.052)
        
        # Operations Realms
        y_pos += int(self.height * 0.025)
        ops_header = font_header.render("OPERATIONS REALMS", True, self.theme.WARNING)
        self.screen.blit(ops_header, (int(self.width * 0.1), y_pos))
        y_pos += int(self.height * 0.045)
        
        for i, realm_id in enumerate(self.realm_order[4:], start=4):
            self.draw_realm_item(realm_id, i, y_pos, elapsed, font_item)
            y_pos += int(self.height * 0.052)
    
    def draw_realm_item(self, realm_id: str, index: int, y_pos: int, 
                       elapsed: float, font: pygame.font.Font) -> None:
        """Draw individual realm menu item"""
        realm = self.realms[realm_id]
        is_selected = (index == self.selected_index)
        
        # Selection highlight
        if is_selected:
            pulse = self.ui.pulse_value(elapsed, 2.0, 0.3, 0.6)
            highlight_rect = pygame.Rect(
                int(self.width * 0.08), y_pos - 6,
                int(self.width * 0.84), int(self.height * 0.048)
            )
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_surface.fill((*realm['color'], int(255 * pulse)))
            self.screen.blit(highlight_surface, highlight_rect)
            pygame.draw.rect(self.screen, realm['color'], highlight_rect, 3, border_radius=10)
        
        # Realm text
        text = f"[{realm['num']}] {realm['icon']}  {realm['name']}"
        color = self.theme.TEXT_PRIMARY if is_selected else self.theme.TEXT_SECONDARY
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, (int(self.width * 0.12), y_pos))
    
    def show_menu(self) -> str:
        """Show main menu and return selected realm"""
        start_time = time.time()
        
        while self.running:
            elapsed = time.time() - start_time
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return None
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % 9
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % 9
                    elif event.key == pygame.K_RETURN:
                        return self.realm_order[self.selected_index]
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                                      pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        index = int(chr(event.key)) - 1
                        return self.realm_order[index]
            
            # Render
            self.screen.fill(self.theme.BACKGROUND)
            self.draw_banner(elapsed)
            self.draw_realm_menu(elapsed)
            
            # Footer
            self.ui.draw_footer(self.screen, 
                               "↑↓ Navigate | 1-9 Quick Select | ENTER Launch | ESC/Q Exit",
                               self.theme.PRIMARY)
            
            pygame.display.flip()
        
        return None
    
    def launch_realm(self, realm_id: str) -> None:
        """Launch a spatial realm"""
        realm_config = self.realms[realm_id]
        
        print(f"\n{'='*70}")
        print(f"  Launching: {realm_config['name']}")
        print(f"{'='*70}")
        
        try:
            # Dynamic import
            module = __import__(realm_config['module'], fromlist=[realm_config['class']])
            RealmClass = getattr(module, realm_config['class'])
            
            # Create and run realm
            realm = RealmClass(realm_id, realm_config['name'], realm_config['color'])
            realm.initialize(self.screen)
            realm.run(duration=60)
            
        except ImportError as e:
            print(f"  ⚠️  Realm not yet implemented: {e}")
            self.show_placeholder(realm_config)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_placeholder(self, realm_config: dict) -> None:
        """Show placeholder for unimplemented realm"""
        start_time = time.time()
        running = True
        
        while running:
            elapsed = time.time() - start_time
            
            if elapsed > 5:  # Auto-exit after 5 seconds
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                    running = False
            
            self.screen.fill(self.theme.BACKGROUND)
            
            # Title
            font_large = pygame.font.Font(None, int(self.height * 0.08))
            title = font_large.render(realm_config['name'], True, realm_config['color'])
            title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(title, title_rect)
            
            # Message
            font_medium = pygame.font.Font(None, int(self.height * 0.04))
            msg = font_medium.render("Coming Soon - Under Development", True, self.theme.TEXT_SECONDARY)
            msg_rect = msg.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(msg, msg_rect)
            
            self.ui.draw_footer(self.screen, "ESC/Q: Return to Menu", realm_config['color'])
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def run(self) -> None:
        """Main application loop"""
        while self.running:
            realm_id = self.show_menu()
            
            if realm_id is None:
                break
            
            self.launch_realm(realm_id)
        
        pygame.quit()
        print("\n" + "="*70)
        print("  MotiBeam Spatial OS Pro - Shutdown Complete")
        print("="*70 + "\n")


if __name__ == "__main__":
    app = SpatialOSPro()
    app.run()
