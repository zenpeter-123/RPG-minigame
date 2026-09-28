"""
Sphinx UI - Popup window for the Sphinx encounter
"""

import pygame
from typing import List, Dict
from questions import QuestionManager
from sphinx_hmm import SphinxHMM
from utils import resource_path


class SphinxPopup:
    """
    Sphinx popup window with questions
    """
    
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font_large = pygame.font.Font(resource_path('arial.ttf'), 48)
        self.font_medium = pygame.font.Font(resource_path('arial.ttf'), 32)
        self.font_small = pygame.font.Font(resource_path('arial.ttf'), 24)
        
        # Load Sphinx image
        try:
            self.sphinx_image = pygame.image.load(resource_path("img/sphinx.png")).convert_alpha()
            self.sphinx_image = pygame.transform.scale(self.sphinx_image, (200, 250))
        except:
            # If there is no image, create a placeholder
            self.sphinx_image = self._create_placeholder_image()
        
        # Question manager
        self.question_manager = QuestionManager()
        
        # States
        self.is_open = False
        self.current_question_index = 0
        self.questions: List[Dict] = []
        self.results: List[bool] = []
        self.selected_option = -1
        self.show_result = False
        self.result_timer = 0
        self.waiting_for_input = False
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Buttons
        self.buttons = []
        self.close_button = None
        
        # Colors
        self.colors = {
            "bg": (20, 15, 30, 240),  # Dark purple, transparent
            "panel": (40, 35, 60),
            "border": (200, 180, 100),
            "text": (255, 255, 255),
            "title": (255, 215, 0),
            "button": (60, 55, 80),
            "button_hover": (80, 75, 100),
            "button_correct": (0, 200, 0),
            "button_wrong": (200, 0, 0),
            "button_selected": (100, 100, 150)
        }
    
    def _create_placeholder_image(self) -> pygame.Surface:
        """Create a placeholder Sphinx image"""
        surf = pygame.Surface((200, 250), pygame.SRCALPHA)
        
        # Body (sphinx body)
        pygame.draw.ellipse(surf, (180, 150, 100), (50, 120, 100, 80))
        
        # Head (sphinx head)
        pygame.draw.circle(surf, (220, 190, 160), (100, 80), 50)
        
        # Eyes
        pygame.draw.circle(surf, (255, 255, 255), (85, 70), 12)
        pygame.draw.circle(surf, (255, 255, 255), (115, 70), 12)
        pygame.draw.circle(surf, (0, 0, 0), (85, 70), 6)
        pygame.draw.circle(surf, (0, 0, 0), (115, 70), 6)
        
        # Mouth
        pygame.draw.arc(surf, (150, 100, 80), (70, 90, 60, 30), 0, 3.14, 2)
        
        # Wings
        pygame.draw.polygon(surf, (200, 180, 150), [
            (30, 120), (0, 80), (20, 60), (50, 100)
        ])
        pygame.draw.polygon(surf, (200, 180, 150), [
            (170, 120), (200, 80), (180, 60), (150, 100)
        ])
        
        # "SPHINX" text
        font = pygame.font.Font(None, 20)
        text = font.render("SPHINX", True, (255, 215, 0))
        text_rect = text.get_rect(center=(100, 235))
        surf.blit(text, text_rect)
        
        return surf
    
    def open(self):
        """Open the Sphinx popup"""
        self.is_open = True
        self.current_question_index = 0
        self.results = []
        self.selected_option = -1
        self.show_result = False
        self.waiting_for_input = False
        
        # Questions generated based on the player's abilities
        if hasattr(self.game, 'sphinx_hmm'):
            questions = self.game.sphinx_hmm.get_sphinx_challenge()
            self.questions = questions
        else:
            # If no HMM is available, generate random questions
            self.questions = self.question_manager.get_sphinx_questions([1, 1, 1], 3)
        
        # If there aren't enough questions, fill them up
        while len(self.questions) < 3:
            q = self.question_manager.get_random_question()
            if q:
                self.questions.append(q)
        
        self.results = [False] * len(self.questions)
    
    def close(self):
        """Close the Sphinx popup"""
        self.is_open = False
        self.current_question_index = 0
        self.questions = []
        self.results = []
        self.selected_option = -1
        self.show_result = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the popup
        
        Returns:
            bool: True if the event was handled
        """
        if not self.is_open:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # ESC closes the popup
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not self.waiting_for_input:
                self.close()
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                
                # Close button
                if self.close_button and self.close_button.collidepoint(mouse_pos):
                    self.close()
                    return True
                
                # Answer buttons
                if self.current_question_index < len(self.questions):
                    for i, button in enumerate(self.buttons):
                        if button["rect"].collidepoint(mouse_pos):
                            if not self.show_result and not self.waiting_for_input:
                                self._select_answer(i)
                                return True
                
                # Continue button (after showing result)
                if self.show_result and self.continue_button_rect.collidepoint(mouse_pos):
                    self._next_question()
                    return True
        
        return False
    
    def _select_answer(self, index: int):
        """Select an answer"""
        self.selected_option = index
        self.show_result = True
        self.result_timer = pygame.time.get_ticks()
        
        # Check if correct
        question = self.questions[self.current_question_index]
        self.results[self.current_question_index] = self.question_manager.check_answer(
            question, index
        )
        
        # Record answer in HMM
        if hasattr(self.game, 'sphinx_hmm'):
            type_names = ["math", "history", "literature"]
            q_type = type_names[self.current_question_index % 3]
            self.game.sphinx_hmm.add_answer(
                q_type, 
                self.results[self.current_question_index]
            )
    
    def _next_question(self):
        """Move to the next question or finish"""
        self.current_question_index += 1
        self.selected_option = -1
        self.show_result = False
        self.waiting_for_input = False
        
        if self.current_question_index >= len(self.questions):
            self._finish_challenge()
    
    def _finish_challenge(self):
        """Finish the Sphinx challenge"""
        correct_count = sum(self.results)
        total = len(self.questions)
        
        if correct_count == total:
            # All correct - reward
            self.game.add_message(
                "The Sphinx is impressed! You gain +150 XP!",
                (255, 215, 0)
            )
            if hasattr(self.game, 'player'):
                self.game.player.gain_xp(150)
                # Extra reward for perfect
                if correct_count == 3:
                    self.game.player.gold += 200
                    self.game.add_message(
                        "Perfect! +200 gold!",
                        (255, 215, 0)
                    )
        elif correct_count >= total // 2:
            # Partial - small reward
            self.game.add_message(
                f"The Sphinx acknowledges your efforts. +{correct_count * 40} XP",
                (200, 200, 200)
            )
            if hasattr(self.game, 'player'):
                self.game.player.gain_xp(correct_count * 40)
        else:
            # Failed - punishment
            self.game.add_message(
                "The Sphinx is displeased! You take damage!",
                (255, 100, 100)
            )
            if hasattr(self.game, 'player'):
                damage = self.game.player.max_hp // 2
                self.game.player.hp -= damage
                if self.game.player.hp <= 0:
                    self.game.player.hp = 0
                    self.game.player.alive = False
                    self.game.game_over()
        
        self.close()
    
    def draw(self, surface: pygame.Surface):
        """Draw the Sphinx popup"""
        if not self.is_open:
            return
        
        win_width, win_height = surface.get_size()
        
        # --- Overlay ---
        overlay = pygame.Surface((win_width, win_height), pygame.SRCALPHA)
        overlay.fill(self.colors["bg"])
        surface.blit(overlay, (0, 0))
        
        # --- Main panel ---
        panel_width = 800
        panel_height = 550
        panel_x = (win_width - panel_width) // 2
        panel_y = (win_height - panel_height) // 2
        
        # Panel background
        pygame.draw.rect(surface, self.colors["panel"], 
                        (panel_x, panel_y, panel_width, panel_height),
                        border_radius=15)
        pygame.draw.rect(surface, self.colors["border"], 
                        (panel_x, panel_y, panel_width, panel_height), 
                        3, border_radius=15)
        
        # --- Close button (X) ---
        close_x = panel_x + panel_width - 40
        close_y = panel_y + 10
        self.close_button = pygame.Rect(close_x, close_y, 30, 30)
        pygame.draw.rect(surface, (200, 50, 50), self.close_button, border_radius=5)
        close_text = self.font_small.render("✕", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=self.close_button.center)
        surface.blit(close_text, close_text_rect)
        
        # --- Title ---
        title = self.font_large.render("THE SPHINX", True, self.colors["title"])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 40))
        surface.blit(title, title_rect)
        
        # --- Sphinx image (left side) ---
        image_x = panel_x + 30
        image_y = panel_y + 80
        surface.blit(self.sphinx_image, (image_x, image_y))
        
        # --- Question area (right side) ---
        text_x = panel_x + 250
        text_width = panel_width - 280
        
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            
            # Question number
            q_num_text = self.font_small.render(
                f"Question {self.current_question_index + 1}/{len(self.questions)}",
                True, (200, 200, 200)
            )
            surface.blit(q_num_text, (text_x, panel_y + 80))
            
            # Question text (with word wrap)
            question_text = question["question"]
            wrapped_lines = self._wrap_text(question_text, self.font_medium, text_width - 20)
            
            y_offset = panel_y + 120
            for line in wrapped_lines:
                q_text = self.font_medium.render(line, True, self.colors["text"])
                surface.blit(q_text, (text_x + 10, y_offset))
                y_offset += 35
            
            # Options
            self.buttons = []
            option_y = y_offset + 20
            
            for i, option in enumerate(question["options"]):
                option_rect = pygame.Rect(
                    text_x + 10,
                    option_y + i * 45,
                    text_width - 20,
                    40
                )
                
                # Button color based on state
                if self.show_result:
                    if i == question["correct_index"]:
                        color = self.colors["button_correct"]
                    elif i == self.selected_option and not self.results[self.current_question_index]:
                        color = self.colors["button_wrong"]
                    else:
                        color = self.colors["button"]
                elif self.selected_option == i:
                    color = self.colors["button_selected"]
                else:
                    # Hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    if option_rect.collidepoint(mouse_pos):
                        color = self.colors["button_hover"]
                    else:
                        color = self.colors["button"]
                
                pygame.draw.rect(surface, color, option_rect, border_radius=8)
                pygame.draw.rect(surface, (200, 200, 200), option_rect, 1, border_radius=8)
                
                # Option text
                option_text = f"{chr(65 + i)}. {option}"  # A, B, C, D
                opt_surf = self.font_small.render(option_text, True, self.colors["text"])
                opt_rect = opt_surf.get_rect(center=option_rect.center)
                surface.blit(opt_surf, opt_rect)
                
                # Store button
                self.buttons.append({
                    "rect": option_rect,
                    "index": i
                })
            
            # Result feedback
            if self.show_result:
                result_y = option_y + len(question["options"]) * 45 + 20
                if self.results[self.current_question_index]:
                    result_text = self.font_medium.render(
                        "CORRECT!",
                        True, (0, 255, 0)
                    )
                else:
                    result_text = self.font_medium.render(
                        "WRONG! The correct answer was:",
                        True, (255, 100, 100)
                    )
                    # Show correct answer
                    correct_ans = question["options"][question["correct_index"]]
                    correct_text = self.font_small.render(
                        f"  {chr(65 + question['correct_index'])}. {correct_ans}",
                        True, (200, 200, 200)
                    )
                    surface.blit(correct_text, 
                                (text_x + 30, result_y + 35))
                
                surface.blit(result_text, (text_x + 10, result_y))
                
                # Continue button
                cont_y = result_y + 70
                self.continue_button_rect = pygame.Rect(
                    panel_x + panel_width - 150,
                    panel_y + panel_height - 60,
                    120, 40
                )
                
                # Hover effect
                mouse_pos = pygame.mouse.get_pos()
                if self.continue_button_rect.collidepoint(mouse_pos):
                    color = (80, 75, 100)
                else:
                    color = (60, 55, 80)
                
                pygame.draw.rect(surface, color, self.continue_button_rect, border_radius=8)
                pygame.draw.rect(surface, (200, 200, 200), self.continue_button_rect, 1, border_radius=8)
                
                cont_text = self.font_medium.render(
                    "Continue",
                    True, (255, 255, 255)
                )
                cont_rect = cont_text.get_rect(center=self.continue_button_rect.center)
                surface.blit(cont_text, cont_rect)
            
            # Progress bar
            prog_y = panel_y + panel_height - 30
            prog_width = panel_width - 40
            prog_x = panel_x + 20
            progress = (self.current_question_index + (1 if self.show_result else 0)) / len(self.questions)
            
            pygame.draw.rect(surface, (60, 60, 80), (prog_x, prog_y, prog_width, 6), border_radius=3)
            pygame.draw.rect(surface, (255, 215, 0), 
                            (prog_x, prog_y, prog_width * progress, 6), 
                            border_radius=3)
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = " ".join(current_line)
            if font.size(line_text)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def update(self):
        """Update the Sphinx popup"""
        if not self.is_open:
            return
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4