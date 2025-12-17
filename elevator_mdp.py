import pygame
import numpy as np
import itertools
import random
import time

# --- PART 1: THE MDP BRAIN  ---
class ElevatorMDP:
    def __init__(self):
        self.floors = [1, 2, 3] 
        self.actions = ['UP', 'DOWN', 'STAY', 'PICK'] 
        self.gamma = 0.9 
        self.arrival_prob = 0.1 # New request probability per floor
        
        # State Space: (e_floor, request_mask)
        self.states = list(itertools.product(self.floors, list(itertools.product([0, 1], repeat=3))))
        self.V = {s: 0.0 for s in self.states}
        self.policy = {s: 'STAY' for s in self.states}

    def solve(self):
        # Value Iteration Algorithm
        theta = 0.001
        while True:
            delta = 0
            for state in self.states:
                floor, requests = state
                old_v = self.V[state]
                q_values = {}
                
                for action in self.actions:
                    # Transition Model (T)
                    next_f, next_reqs, r = floor, list(requests), 0
                    
                    if action == 'UP' and next_f < 3: 
                        next_f += 1
                        r -= 0.5 # Energy cost
                    elif action == 'DOWN' and next_f > 1: 
                        next_f -= 1
                        r -= 0.5 
                    elif action == 'PICK':
                        if next_reqs[floor-1] == 1:
                            next_reqs[floor-1] = 0 # Clear request
                            r += 5 # Successful pick reward
                        else:
                            r -= 0.5 # Penalty for invalid action
                    
                    # Reward (R): -1 per timestep for each pending request
                    r -= sum(requests) 
                    
                    # Bellman Update: r + gamma * V(s')
                    v_next = self.V[(next_f, tuple(next_reqs))]
                    q_values[action] = r + self.gamma * v_next
                
                best_action = max(q_values, key=q_values.get)
                self.V[state] = q_values[best_action]
                self.policy[state] = best_action
                delta = max(delta, abs(old_v - self.V[state]))
            if delta < theta: break

class ElevatorGame:
    def __init__(self, mdp):
        pygame.init()
        self.mdp = mdp
        self.width, self.height = 600, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Smart Elevator MDP | Optimization Control")
        
        # Modern Fonts
        self.font_small = pygame.font.SysFont("Segoe UI", 16)
        self.font_main = pygame.font.SysFont("Segoe UI", 20)
        self.font_bold = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 36, bold=True)
        
        self.clock = pygame.time.Clock()
        self.reset_game()
        self.running = True

      
        self.COLORS = {
            'bg': (30, 30, 40),          # Dark Slate
            'floor': (50, 50, 60),       # Lighter Slate
            'elevator': (52, 152, 219),  # Bright Blue
            'doors': (41, 128, 185),     # Darker Blue
            'passenger': (231, 76, 60),  # Red
            'text': (236, 240, 241),     # White/Grey
            'hud_bg': (20, 20, 25),      # Almost Black
            'success': (46, 204, 113),   # Green
            'alert': (230, 126, 34)      # Orange
        }

    def reset_game(self):
        self.curr_floor = 1
        self.requests = [0, 0, 1] 
        self.total_reward = 0.0
        self.last_step_reward = 0.0
        self.current_action = "WAITING"

    def draw_passenger(self, x, y):
        """Draws a simple stick figure/person icon."""
        # Head
        pygame.draw.circle(self.screen, self.COLORS['passenger'], (x, y), 8)
        # Body
        pygame.draw.rect(self.screen, self.COLORS['passenger'], (x - 6, y + 8, 12, 18), border_radius=4)

    def draw_elevator(self, x, y):
        """Draws a detailed elevator cabin."""
        # Main Cabin
        rect = pygame.Rect(x, y, 100, 120)
        pygame.draw.rect(self.screen, self.COLORS['elevator'], rect, border_radius=6)
        # Inner Doors (Visual detail)
        pygame.draw.rect(self.screen, self.COLORS['doors'], (x + 10, y + 10, 38, 100))
        pygame.draw.rect(self.screen, self.COLORS['doors'], (x + 52, y + 10, 38, 100))
        # Top Light
        color = self.COLORS['success'] if self.current_action == "PICK" else (200, 200, 200)
        pygame.draw.circle(self.screen, color, (x + 50, y - 5), 6)

    def draw(self, action, step_reward):
        self.screen.fill(self.COLORS['bg']) 
        self.current_action = action

        # --- 1. Draw The Building (Floors) ---
        floor_height = 160
        base_y = 650
        
        for i in range(1, 4):
            y_pos = base_y - ((i-1) * floor_height)
            
            # Floor Line
            pygame.draw.line(self.screen, self.COLORS['floor'], (50, y_pos), (550, y_pos), 4)
            
            # Floor Label
            label = self.font_large.render(f"{i}", True, (60, 65, 75))
            self.screen.blit(label, (20, y_pos - 45))

            # Draw Pending Requests (Passengers waiting)
            if self.requests[i-1] == 1:
                self.draw_passenger(450, y_pos - 30)
                req_text = self.font_small.render("WAITING", True, self.COLORS['passenger'])
                self.screen.blit(req_text, (430, y_pos - 55))

        # --- 2. Draw The Elevator ---
        # Calculate pixel position based on floor (1,2,3)
        elev_y = base_y - ((self.curr_floor-1) * floor_height) - 120
        self.draw_elevator(250, elev_y)

        # --- 3. Heads-Up Display ---
        # Top Panel Background
        pygame.draw.rect(self.screen, self.COLORS['hud_bg'], (0, 0, self.width, 100))
        pygame.draw.line(self.screen, (50, 50, 50), (0, 100), (self.width, 100), 2)

        # Status Text
        action_color = self.COLORS['success'] if "PICK" in str(action) else self.COLORS['elevator']
        status_txt = self.font_bold.render(f"ACTION: {action}", True, action_color)
        self.screen.blit(status_txt, (30, 20))

        # Stats
        rew_color = self.COLORS['success'] if step_reward > 0 else self.COLORS['alert']
        step_txt = self.font_main.render(f"Step Reward: {step_reward:+.1f}", True, rew_color)
        cum_txt = self.font_main.render(f"Total Score: {self.total_reward:.1f}", True, self.COLORS['text'])
        
        self.screen.blit(step_txt, (30, 55))
        self.screen.blit(cum_txt, (200, 55))

        # Reset Button
        self.reset_btn_rect = pygame.Rect(460, 25, 110, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (231, 76, 60) if self.reset_btn_rect.collidepoint(mouse_pos) else (192, 57, 43)
        
        pygame.draw.rect(self.screen, btn_color, self.reset_btn_rect, border_radius=8)
        btn_txt = self.font_bold.render("RESET", True, self.COLORS['text'])
        text_rect = btn_txt.get_rect(center=self.reset_btn_rect.center)
        self.screen.blit(btn_txt, text_rect)

        pygame.display.flip()

    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.reset_btn_rect.collidepoint(event.pos):
                        self.reset_game()

            # Logic steps 
            state = (self.curr_floor, tuple(self.requests))
            action = self.mdp.policy[state]
            
            step_reward = 0
            if action == 'UP' and self.curr_floor < 3: 
                self.curr_floor += 1
                step_reward -= 0.5
            elif action == 'DOWN' and self.curr_floor > 1: 
                self.curr_floor -= 1
                step_reward -= 0.5
            elif action == 'PICK':
                if self.requests[self.curr_floor-1] == 1:
                    self.requests[self.curr_floor-1] = 0
                    step_reward += 5
                else:
                    step_reward -= 0.5
            
            step_reward -= sum(self.requests) 
            self.total_reward += step_reward

            for i in range(3):
                if random.random() < 0.1: self.requests[i] = 1

            self.draw(action, step_reward)
            time.sleep(1.2) 
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    brain = ElevatorMDP()
    brain.solve()
    game = ElevatorGame(brain)
    game.play()
