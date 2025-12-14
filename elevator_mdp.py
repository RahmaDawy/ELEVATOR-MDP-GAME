import pygame
import numpy as np
import itertools
import random
import time

# --- PART 1: THE MDP BRAIN (Value Iteration) ---
class ElevatorMDP:
    def __init__(self):
        # Parameters according to Project 2 requirements
        self.floors = [1, 2, 3] #
        self.actions = ['UP', 'DOWN', 'STAY', 'PICK'] #
        self.gamma = 0.9 # Discount factor
        self.arrival_prob = 0.1 # New request probability per floor
        
        # State Space: (e_floor, request_mask)
        self.states = list(itertools.product(self.floors, list(itertools.product([0, 1], repeat=3))))
        self.V = {s: 0.0 for s in self.states}
        self.policy = {s: 'STAY' for s in self.states}

    def solve(self):
        """Value Iteration: Finds the Optimal Policy by solving the Bellman Equation."""
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
                        r -= 0.5 # Energy cost
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

# --- PART 2: THE GAME INTERFACE (Visual Testing) ---
class ElevatorGame:
    def __init__(self, mdp):
        pygame.init()
        self.mdp = mdp
        self.width, self.height = 450, 680
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MDP Elevator Optimization System")
        self.font = pygame.font.SysFont("Verdana", 18)
        self.bold_font = pygame.font.SysFont("Verdana", 20, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 22, bold=True)
        self.clock = pygame.time.Clock()
        
        self.reset_game()
        self.running = True

    def reset_game(self):
        self.curr_floor = 1
        self.requests = [0, 0, 1] 
        self.total_reward = 0.0
        self.last_step_reward = 0.0
        self.current_action = "INITIALIZING"

    def draw(self, action, step_reward):
        self.screen.fill((30, 33, 40)) 
        
        # --- Draw HUD Area ---
        hud_rect = pygame.Rect(0, 0, self.width, 140)
        pygame.draw.rect(self.screen, (20, 22, 28), hud_rect)
        
        # Status Text (Moving tags)
        status_text = f"Action: {action}"
        if action == "UP": status_text = "Action: Moving UP"
        elif action == "DOWN": status_text = "Action: Moving DOWN"
        elif action == "PICK": status_text = "Action: PICKING Passenger"
        
        txt = self.font.render(status_text, True, (46, 204, 113))
        self.screen.blit(txt, (20, 15))

        # Reward Display (Immediate +5/-1 and Cumulative)
        rew_color = (255, 255, 255) if step_reward == 0 else (46, 204, 113) if step_reward > 0 else (231, 76, 60)
        step_txt = self.bold_font.render(f"Step Reward: {step_reward:+.1f}", True, rew_color)
        self.screen.blit(step_txt, (20, 45))

        cum_txt = self.font.render(f"Cumulative Reward: {self.total_reward:.1f}", True, (241, 196, 15))
        self.screen.blit(cum_txt, (20, 75))

        # Reset Button
        self.reset_btn_rect = pygame.Rect(280, 35, 140, 55)
        pygame.draw.rect(self.screen, (231, 76, 60), self.reset_btn_rect, border_radius=8)
        btn_txt = self.btn_font.render("RESET", True, (255, 255, 255))
        self.screen.blit(btn_txt, (315, 45))

        # --- Draw Building ---
        for i in range(1, 4):
            y_pos = self.height - (i * 180)
            pygame.draw.line(self.screen, (120, 120, 120), (80, y_pos), (380, y_pos), 3)
            f_label = self.font.render(f"Floor {i}", True, (255, 255, 255))
            self.screen.blit(f_label, (10, y_pos - 35))

        # Draw Passengers
        for i, req in enumerate(self.requests):
            if req == 1:
                y_pos = self.height - ((i+1) * 180) + 75
                pygame.draw.circle(self.screen, (231, 76, 60), (350, y_pos), 18)

        # Draw Elevator
        elev_y = self.height - (self.curr_floor * 180) + 35
        pygame.draw.rect(self.screen, (52, 152, 219), (160, elev_y, 90, 125), border_radius=5)
        
        pygame.display.flip()

    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.reset_btn_rect.collidepoint(event.pos):
                        self.reset_game()

            # 1. Decision Logic
            state = (self.curr_floor, tuple(self.requests))
            action = self.mdp.policy[state]
            
            # 2. Transition & Reward Logic
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
            
            step_reward -= sum(self.requests) # Wait time penalty
            self.total_reward += step_reward

            # 3. Stochastic Requests
            for i in range(3):
                if random.random() < 0.1: self.requests[i] = 1

            # 4. Render
            self.draw(action, step_reward)
            time.sleep(1.2) 
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    brain = ElevatorMDP()
    brain.solve()
    game = ElevatorGame(brain)
    game.play()
