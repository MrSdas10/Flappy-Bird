import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Game settings
GRAVITY = 0.5
FLAP_STRENGTH = -8  # Decrease the bird's jump height slightly
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 3

# Load images
BIRD_IMAGE = pygame.transform.scale(pygame.image.load('bird.png'), (40, 30))
PIPE_IMAGE = pygame.image.load('pipe.png')
BACKGROUND_IMAGE = pygame.image.load('background.png')
BASE_HEIGHT = 100
BASE_IMAGE = pygame.transform.scale(pygame.image.load('base.png'), (SCREEN_WIDTH, BASE_HEIGHT))

def draw_base(screen, base_x):
    screen.blit(BASE_IMAGE, (base_x, SCREEN_HEIGHT - BASE_HEIGHT))
    screen.blit(BASE_IMAGE, (base_x + SCREEN_WIDTH, SCREEN_HEIGHT - BASE_HEIGHT))

class Bird:
    def __init__(self):
        self.image = BIRD_IMAGE
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, 40, 30)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - BASE_HEIGHT - 30:
            self.y = SCREEN_HEIGHT - BASE_HEIGHT - 30
            self.velocity = 0

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.velocity * 3)
        screen.blit(rotated_image, (self.x, self.y))

# Refine collision detection logic using pixel-perfect collision
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - BASE_HEIGHT - 50)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP - BASE_HEIGHT)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        top_pipe_image = pygame.transform.scale(PIPE_IMAGE, (PIPE_WIDTH, self.height))
        bottom_pipe_image = pygame.transform.scale(PIPE_IMAGE, (PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP - BASE_HEIGHT))
        screen.blit(top_pipe_image, (self.x, 0))
        screen.blit(bottom_pipe_image, (self.x, self.height + PIPE_GAP))

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def passed(self, bird):
        return self.x + PIPE_WIDTH < bird.x and not hasattr(self, 'scored')

    def check_collision(self, bird):
        # Use pixel-perfect collision detection
        bird_mask = pygame.mask.from_surface(bird.image)
        top_pipe_mask = pygame.mask.from_surface(pygame.transform.scale(PIPE_IMAGE, (PIPE_WIDTH, self.height)))
        bottom_pipe_mask = pygame.mask.from_surface(pygame.transform.scale(PIPE_IMAGE, (PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP - BASE_HEIGHT)))

        # Calculate offsets
        top_offset = (self.x - bird.x, 0 - bird.y)
        bottom_offset = (self.x - bird.x, self.height + PIPE_GAP - bird.y)

        # Check for overlap
        top_collision = bird_mask.overlap(top_pipe_mask, top_offset)
        bottom_collision = bird_mask.overlap(bottom_pipe_mask, bottom_offset)

        return top_collision or bottom_collision

class Button:
    def __init__(self, text, x, y, width, height, font, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.hover_color = hover_color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

# Add score counting and highest score tracking
class GameStats:
    def __init__(self):
        self.score = 0
        self.highest_score = 0

    def reset_score(self):
        self.score = 0

    def update_highest_score(self):
        if self.score > self.highest_score:
            self.highest_score = self.score

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(3)]
    base_x = 0
    font = pygame.font.Font(None, 40)
    score_font = pygame.font.Font(None, 60)
    exit_button = Button("Exit", SCREEN_WIDTH - 120, 20, 100, 40, font, BLACK, GREEN)

    # Initialize game stats
    stats = GameStats()

    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP:
                    bird.flap()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                bird.flap()

        if exit_button.is_clicked():
            pygame.quit()
            return

        if not game_over:
            bird.update()
            for pipe in pipes:
                pipe.update()

                if pipe.check_collision(bird):
                    game_over = True
                    stats.update_highest_score()
                    break

                if pipe.passed(bird):
                    setattr(pipe, 'scored', True)
                    stats.score += 1

            if pipes and pipes[0].is_off_screen():
                pipes.pop(0)
                pipes.append(Pipe(pipes[-1].x + 300))

            base_x -= PIPE_SPEED
            if base_x <= -SCREEN_WIDTH:
                base_x = 0

        screen.blit(BACKGROUND_IMAGE, (0, 0))
        for pipe in pipes:
            pipe.draw(screen)
        draw_base(screen, base_x)
        bird.draw(screen)
        exit_button.draw(screen)

        # Display current score and highest score
        score_surface = score_font.render(f"Score: {stats.score}", True, WHITE)
        highest_score_surface = score_font.render(f"Highest Score: {stats.highest_score}", True, WHITE)
        screen.blit(score_surface, (20, 20))
        screen.blit(highest_score_surface, (20, 60))

        if game_over:
            game_over_text = score_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))

            start_again_button = Button("Start Again", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, font, BLACK, GREEN)
            start_again_button.draw(screen)

            if start_again_button.is_clicked():
                # Reset game state
                bird = Bird()
                pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(3)]
                base_x = 0
                stats.reset_score()
                game_over = False

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__": 
    main()
