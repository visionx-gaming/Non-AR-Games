import pygame
import sys
import os
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_FORCE = -10
PIPE_SPEED = -3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
COLORS = {
    'background': (135, 206, 250),
    'player': (0, 255, 0),
    'pipe': (255, 0, 0),
    'text': (255, 255, 255),
    'score': (255, 255, 255),
}

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flippyblock Extreme")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Sound Generation Functions
def generate_beep_sound(frequency=523, duration=0.1, volume=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    max_amplitude = int(32767 * volume)
    samples = []

    for i in range(n_samples):
        t = i / sample_rate
        phase = t * frequency
        if (phase % 1) < 0.5:
            samples.append(max_amplitude)
        else:
            samples.append(-max_amplitude)

    sound_bytes = bytearray()
    for s in samples:
        sound_bytes.extend(s.to_bytes(2, byteorder='little', signed=True))

    return pygame.mixer.Sound(buffer=sound_bytes)

# Load sounds
jump_sound = generate_beep_sound(784, 0.1, 0.5)
collision_sound = generate_beep_sound(220, 0.3, 0.5)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, SCREEN_HEIGHT//2, 30, 30)
        self.velocity = 0
        self.gravity = GRAVITY

    def jump(self):
        self.velocity = JUMP_FORCE

    def update(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 100 - PIPE_GAP)
        self.top_pipe = pygame.Rect(SCREEN_WIDTH, 0, 50, self.gap_y)
        self.bottom_pipe = pygame.Rect(
            SCREEN_WIDTH, self.gap_y + PIPE_GAP, 50,
            SCREEN_HEIGHT - (self.gap_y + PIPE_GAP))
        self.passed = False

    def move(self):
        self.top_pipe.x += PIPE_SPEED
        self.bottom_pipe.x += PIPE_SPEED

    def off_screen(self):
        return self.top_pipe.right < 0

def main():
    # Game state initialization
    player = Player()
    pipes = []
    last_pipe_time = pygame.time.get_ticks()
    score = 0
    high_score = 0
    game_state = "menu"

    # Load high score
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if game_state == "menu":
                        # Reset game
                        game_state = "playing"
                        player.rect.y = SCREEN_HEIGHT // 2
                        player.velocity = 0
                        pipes = []
                        score = 0
                    elif game_state == "playing":
                        player.jump()
                        jump_sound.play()
                    elif game_state == "game_over":
                        game_state = "menu"
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Game state updates
        screen.fill(COLORS['background'])

        if game_state == "playing":
            # Update player
            player.update()

            # Spawn pipes
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe_time = current_time

            # Move and clean up pipes
            for pipe in pipes[:]:
                pipe.move()
                if pipe.off_screen():
                    pipes.remove(pipe)

            # Collision detection
            game_over = False
            for pipe in pipes:
                if (player.rect.colliderect(pipe.top_pipe) or
                    player.rect.colliderect(pipe.bottom_pipe)):
                    game_over = True
            if player.rect.bottom >= SCREEN_HEIGHT:
                game_over = True

            if game_over:
                collision_sound.play()
                game_state = "game_over"
                if score > high_score:
                    high_score = score
                    with open("highscore.txt", "w") as f:
                        f.write(str(high_score))

            # Score updating
            for pipe in pipes:
                if not pipe.passed and pipe.top_pipe.right < player.rect.left:
                    pipe.passed = True
                    score += 1

            # Drawing
            for pipe in pipes:
                pygame.draw.rect(screen, COLORS['pipe'], pipe.top_pipe)
                pygame.draw.rect(screen, COLORS['pipe'], pipe.bottom_pipe)
            pygame.draw.rect(screen, COLORS['player'], player.rect)

            # Score display
            score_text = font.render(f"Score: {score}", True, COLORS['score'])
            screen.blit(score_text, (10, 10))

        elif game_state == "menu":
            # Menu display
            title_text = font.render("Flippyblock Extreme", True, COLORS['text'])
            instruction = font.render("Press SPACE to Start", True, COLORS['text'])
            hs_text = font.render(f"High Score: {high_score}", True, COLORS['text'])
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 200))
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 300))
            screen.blit(hs_text, (SCREEN_WIDTH//2 - hs_text.get_width()//2, 400))

        elif game_state == "game_over":
            # Game over display
            go_text = font.render("Game Over!", True, COLORS['text'])
            score_text = font.render(f"Score: {score}", True, COLORS['text'])
            instruction = font.render("Press SPACE for Menu", True, COLORS['text'])
            screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, 200))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 300))
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 400))

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()