import pygame
import random
import sys


def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 450))
    screen.blit(floor_surface, (floor_x_pos + width, 450))


def create_pipe():
    random_pipe_position = random.choice(pipe_height)
    random_distance = random.randint(50, 200)
    bottom_pipe = pipe_surface.get_rect(midtop=(width + random_distance, random_pipe_position))
    top_pipe = pipe_surface.get_rect(midbottom=(width + random_distance, random_pipe_position - 150))

    return bottom_pipe, top_pipe


def move_pipes(pipes, score):
    for pipe in pipes:
        pipe.centerx -= 2
        if pipe.centerx == 100 or pipe.centerx == 101:
            if pipe.top < 0:
                score += 1
                point_sound.play()

    return pipes, score


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= height:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_pipe_sound.play()
            return True
    if bird_rect.top <= -100 or bird_rect.bottom >= height:
        return True

    return False


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 4, 1)
    return new_bird


def score_display():
    score_surface = game_font.render(str(score), True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(144, 50))
    screen.blit(score_surface, score_rect)


def end_score_display():
    score_surface = game_font.render('Score: ' + str(score), True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(144, 200))
    screen.blit(score_surface, score_rect)

    high_score_surface = game_font.render('Current Highcore: ' + str(high_score), True, (255, 255, 255))
    high_score_rect = high_score_surface.get_rect(center=(144, 250))
    screen.blit(high_score_surface, high_score_rect)


width = int(576 / 2)
height = int(1024 / 2)

#pygame.mixer.pre_init(channels=1, buffer=512 )
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 20)

# Game Variables
gravity = 0.1
bird_movement = 0
game_active = False
score = 0
high_score = 0

background_surface = pygame.image.load('assets/background-day.png').convert()
# background_surface = pygame.transform.scale2x(background_surface)

floor_surface = pygame.image.load('assets/base.png').convert()
# floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_downflap = pygame.image.load('assets/bluebird-downflap.png').convert()
bird_midflap = pygame.image.load('assets/bluebird-midflap.png').convert()
bird_upflap = pygame.image.load('assets/bluebird-upflap.png').convert()
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(100, int(height / 2)))
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [200, 300, 400]

game_over_surface = pygame.image.load('assets/gameover.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center=(144, 100))

game_start_surface = pygame.image.load('assets/message.png').convert_alpha()
game_start_rect = game_start_surface.get_rect(center=(144, 200))
screen.blit(background_surface, (0, 0))
screen.blit(game_start_surface, game_start_rect)

# Sounds
flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
point_sound = pygame.mixer.Sound('sound/sfx_point.wav')
dead_sound = pygame.mixer.Sound('sound/sfx_die.wav')
hit_pipe_sound = pygame.mixer.Sound('sound/sfx_hit.wav')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_movement = 0
                bird_movement -= 3
                flap_sound.play()
            if event.key == pygame.K_SPACE and game_active is False:
                score = 0
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, int(height / 2))
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        if event.type == BIRDFLAP:
            bird_index = (bird_index + 1) % 3
            bird_surface = bird_frames[bird_index]
            bird_rect = bird_surface.get_rect(center=(100, bird_rect.centery))

    if game_active:
        screen.blit(background_surface, (0, 0))
        draw_floor()
        floor_x_pos += -1
        if floor_x_pos < -width:
            floor_x_pos = 0

        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)

        # Pipes
        pipe_list, score = move_pipes(pipe_list, score)
        draw_pipes(pipe_list)
        score_display()

        # Collision
        if check_collision(pipe_list):
            game_active = False
            dead_sound.play()
            if score > high_score:
                high_score = score
            screen.blit(background_surface, (0, 0))
            screen.blit(game_over_surface, game_over_rect)
            end_score_display()

    pygame.display.update()
    clock.tick(120)
