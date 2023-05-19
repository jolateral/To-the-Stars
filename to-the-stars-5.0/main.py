"""CSC111 Project Phase 2 : Final Submission

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code required to visualize the results of our computations
in an interactive video game format. To run this module, right click anywhere on this file
and select 'Run File in Python Console'. You may need to wait up to 20 seconds for the
program to begin running.

You may press any of the arrow keys to move the spaceship in the corresponding direction.
To filter by radius, press R after the ship collides with a star. To filter by mass, press
M after the ship collides with a star. Further details about the filter function can be found
in classes.py under the Galaxy class in the radius_path and mass_path function docstrings.
Have fun! :)

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2023 Janna Alyssa Lim, Jenny Nguyen
"""
import sys
import csv_reader
from classes import *

pygame.init()

pygame.display.set_caption('To The Stars!')
clock = pygame.time.Clock()
background = pygame.transform.smoothscale(pygame.image.load('graphics/Background.png'), (screen_width, screen_height))
x_position, speed = 0, 1

# Reading csv data
galaxy_stars = csv_reader.read_dataset('stars_dataset/final.csv')
galaxy, stars = galaxy_stars[0], galaxy_stars[1]
ship.current_star = stars[0]
stars.sort(key=lambda x: x.distance)

# Initialize star positions
initialize_star_positions(stars)


def collisions(player_ship: Ship, stars: list[Star]):
    for star in stars:
        if player_ship.rect.colliderect(star.rect):
            player_ship.current_star = star
            star_sound = pygame.mixer.Sound('music/star ding.mp3')
            star_sound.set_volume(0.5)
            # star_sound.play()
            # name_text = 'star name: ' + ship.current_star.name + ' radius: ' + str(
            #     ship.current_star.radius) + ' mass: ' + str(ship.current_star.mass)
            name_text = 'star name: ' + ship.current_star.name
            radius_text = 'radius: ' + str(ship.current_star.radius)
            mass_text = 'mass: ' + str(ship.current_star.mass)
            #     ship.current_star.radius)
            name_settings = pygame.font.SysFont('chalkboard', 20)
            radius_settings = pygame.font.SysFont('chalkboard', 20)
            mass_settings = pygame.font.SysFont('chalkboard', 20)
            txtattribute_name = name_settings.render(name_text, True, (255, 255, 255))
            txtattribute_radius = radius_settings.render(radius_text, True, (255, 255, 255))
            txtattribute_mass = mass_settings.render(mass_text, True, (255, 255, 255))
            screen.blit(txtattribute_name,
                        (1350 - txtattribute_name.get_width(), 550 - txtattribute_name.get_height() // 2))
            screen.blit(txtattribute_radius,
                        (1350 - txtattribute_radius.get_width(), 600 - txtattribute_radius.get_height() // 2))
            screen.blit(txtattribute_mass,
                        (1350 - txtattribute_mass.get_width(), 650 - txtattribute_mass.get_height() // 2))

            # print(player_ship.current_star)


# music
pygame.mixer.music.load('music/ninja tuna.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

while True:
    camera = camera_group.offset
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Background scrolling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x_position += speed
    elif keys[pygame.K_RIGHT]:
        x_position -= speed
    else:
        pass

    relative_x_pos = x_position % screen_width
    if relative_x_pos > 0:
        relative_x_pos_2 = relative_x_pos - screen_width
    else:
        relative_x_pos_2 = relative_x_pos + screen_width

    screen.blit(background, (relative_x_pos, 0))
    screen.blit(background, (relative_x_pos_2, 0))

    if keys[pygame.K_RIGHT]:
        camera.x += 0.1

    if keys[pygame.K_LEFT]:
        camera.x -= 0.1

    if keys[pygame.K_r]:
        galaxy.create_paths()
        stars_in_path = galaxy.radius_path(ship.current_star, set())
        stars_in_path.insert(0, ship.current_star)
        coordinates = [(star.rect.x + 50, star.rect.y + 50) for star in stars_in_path]
        pygame.draw.lines(screen, (255, 255, 255), False, [point - camera for point in coordinates], width=5)

        font = pygame.font.SysFont('chalkboard', 20)
        txtsurf = font.render('filtering by: radius', True, (255, 255, 255))
        screen.blit(txtsurf, (120 - txtsurf.get_width() // 2, 50 - txtsurf.get_height() // 2))

    if keys[pygame.K_m]:
        galaxy.create_paths()
        stars_in_path = galaxy.mass_path(ship.current_star, set())
        stars_in_path.insert(0, ship.current_star)
        coordinates = [(star.rect.x + 50, star.rect.y + 50) for star in stars_in_path]
        pygame.draw.lines(screen, (177, 156, 217), False, [point - camera for point in coordinates], width=5)

        font = pygame.font.SysFont('chalkboard', 20)
        txtsurf = font.render('filtering by: mass', True, (255, 255, 255))
        screen.blit(txtsurf, (120 - txtsurf.get_width() // 2, 50 - txtsurf.get_height() // 2))

    instructions = pygame.font.SysFont('chalkboard', 20)
    txtinstructions_radius = instructions.render('press r to filter by radius (white)', True, (255, 255, 255))
    screen.blit(txtinstructions_radius,
                (170 - txtinstructions_radius.get_width() // 2, 600 - txtinstructions_radius.get_height() // 2))

    txtinstructions_mass = instructions.render('press m to filter by mass (purple)', True, (255, 255, 255))
    screen.blit(txtinstructions_mass,
                (170 - txtinstructions_mass.get_width() // 2, 650 - txtinstructions_mass.get_height() // 2))

    camera_group.custom_draw(ship)
    camera_group.update()

    collisions(ship, stars)

    pygame.display.update()
    clock.tick(60)
