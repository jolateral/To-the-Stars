"""CSC111 Project Phase 2 : Final Submission

Module Description
===============================

This Python module contains a collection of Python classes and functions accessed by
main.py to run the game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2023 Janna Alyssa Lim, Jenny Nguyen
"""
from __future__ import annotations
from typing import Optional
import random
import pygame
from pygame import K_DOWN, K_LEFT, K_RIGHT, K_UP, Rect, Surface, SurfaceType, Vector2

screen_width, screen_height = 1400, 700
screen = pygame.display.set_mode((screen_width, screen_height))


class CameraGroup(pygame.sprite.Group):
    """Responsible for moving all sprites' positions relative to the current position of the ship.

    Uses the 'box target camera' which moves the camera when the player moves beyond
    the camera borders

    Instance Attributes:
        - display_surface: the screen in which all the pygame sprites are drawn
        - offset: a vector that adjusts the position of the sprites
        - camera_borders: the borders of the screen (either onscreen or offsscreen)
        - camera_rect: similar to the camera_borders, this represents the x and y values of
            the area of the camera
    """
    # pygame attributes:
    display_surface: Optional[Surface | SurfaceType]
    offset: Vector2
    camera_borders: dict[str, int]
    camera_rect: Rect

    def __init__(self) -> None:
        """Initalizes a new camera box.

        >>> camera_group_1 = CameraGroup()
        >>> camera_group_1.camera_borders['left'] == 500
        True
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()

        # box setup
        self.camera_borders = {'left': 500, 'right': 500, 'top': 0, 'bottom': 0}
        l, t = self.camera_borders['left'], self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

    def box_target_camera(self, target: Ship) -> None:
        """Moves the camera if the player attempts to move beyond the camera borders
        """
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def custom_draw(self, player: Ship) -> None:
        """Updates the location of the sprites connected to the camera group relative
        to the position of the ship.
        """
        self.box_target_camera(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class Star(pygame.sprite.Sprite):
    """A representation of an individual star.

    This is analogous to the Node data class that we learned in lecture.

    Instance Attributes:
        - name: the name of the star
        - distance: the distance between Earth and the star
        - mass: the mass of the star in solar masses
        - radius: the radius of the star in solar radii
        - closest_stars: a dict mapping the name of the star's neighbour and its
            correspond Star object
        - image: the picture of the star that's displayed
        - rect: this represents the x and y values of the area of the star

        Representation Invariants:
        - self.name != ''
        - self.distance > 0
        - self.mass > 0
        - self.radius > 0
        - all(self in self.closest_stars[star].endpoints for star in self.closest_stars)
    """
    # data attributes:
    name: str
    distance: float
    mass: float
    radius: float
    closest_stars: Optional[dict[str, Path]]

    # pygame attributes:
    image: Surface
    rect: Optional[Rect]

    def __init__(self, group: CameraGroup, name: str, distance: float, mass: float, radius: float) -> None:
        super().__init__(group)
        image = pygame.image.load('graphics/Star.png')
        image = pygame.transform.scale(image, (100, 90))
        self.image = image.convert_alpha()
        self.rect = None
        # Note: self.rect is initalized outside of __init__

        # Actual star attributes
        self.name = name
        self.distance = distance
        self.mass = mass
        self.radius = radius
        self.closest_stars = {}


class Path:
    """A data class that represents a singular path between two Stars.

    This is analogous to the Channel data class that we learned in lecture.

    Instance Attributes:
        - endpoints: a tuple that contains the two Stars that the path is connecting

    Representation Invariants:
        - len(self.endpoints) == 2
    """
    # data attributes:
    endpoints: tuple[Star, Star]

    def __init__(self, star1: Star, star2: Star) -> None:
        """Initializes a path between the two given stars."""
        self.endpoints = star1, star2
        star1.closest_stars[star2.name] = self
        star2.closest_stars[star1.name] = self

    def get_other_endpoint(self, star: Star) -> Star:
        """Return the other star in the path with the given star."""
        if self.endpoints[0] == star:
            return self.endpoints[1]
        else:
            return self.endpoints[0]


class Ship(pygame.sprite.Sprite):
    """Representation of the user and their current position within the galaxy.

    Instance Attributes:
        - current_star: The star that the ship is currently at (i.e., the star that the ship last collided with)
        - image: the image of the ship in pygame
        - rect: this represents the x and y values of the area of the ship
        - direction: the direction that the ship is moving in
        - speed: the speed that the ship moves
    """
    # data attributes:
    current_star: Optional[Star]

    # pygame attributes:
    image: Surface
    rect: Rect
    direction: Vector2
    speed: int

    def __init__(self, pos: tuple[int, int], group: CameraGroup) -> None:
        """Initalizes a new ship.
        """
        super().__init__(group)
        image = pygame.image.load('graphics/Ship.png')
        image = pygame.transform.scale(image, (150, 90))
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.current_star = None

    def input(self) -> None:
        """A function that moves the ship in the direction corresponding to the arrow key pressed.
        """
        keys = pygame.key.get_pressed()

        if keys[K_UP]:
            self.direction.y = -1
        elif keys[K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[K_RIGHT]:
            self.direction.x = 1
        elif keys[K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self) -> None:
        """A function that changes the position of the ship based on the changes to the direction of the ship made by
        self.input().
        """
        self.input()
        self.rect.center += self.direction * self.speed


class Galaxy:
    """An abstract class for a network of stars.

    Private Instance Attributes:
        - _stars: A mapping from star name to Star in this network.

    Representation Invariants:
        - self.stars != {}
    """
    stars: dict[str, Star]

    def __init__(self, *sprites) -> None:
        """Initialize an empty Galaxy."""
        super().__init__(*sprites)
        self.stars = {}

    def add_star(self, name: str, distance: float, mass: float, radius: float) -> Star:
        """Add a new star to this galaxy and return it.

        Preconditions:
            - star_name not in self._stars
        """
        # initalize a new star with the given attributes
        new_star = Star(camera_group, name, distance, mass, radius)

        # add the star to the galaxy's collection of stars
        self.stars[new_star.name] = new_star

        return new_star

    def create_paths(self) -> None:
        """Create the paths between all the stars (i.e., with their two closest neighbour stars
        """
        # create a new list of all the stars, and order it in ascending order from their distance
        ordered_stars = [self.stars[star] for star in self.stars]
        ordered_stars.sort(key=lambda x: x.distance)

        # connect the stars, except the last ad second last stars
        for i in range(0, len(ordered_stars) - 2):
            Path(ordered_stars[i], ordered_stars[i + 1])
            Path(ordered_stars[i], ordered_stars[i + 2])

        # connec the last and second last star
        Path(ordered_stars[len(ordered_stars) - 1], ordered_stars[len(ordered_stars) - 2])

    def radius_path(self, starting_star: Star, visited: set[Star]) -> list[Star]:
        """Return a list of the stars in the galaxy, filtered by their luminosity.
        """
        visited.add(starting_star)

        # get a list of the closest stars
        closest_stars = [starting_star.closest_stars[star].get_other_endpoint(starting_star) for star in
                         starting_star.closest_stars]

        # create a mapping of the radii of the closest stars to its star if the star isn't in visited
        radii = {star.radius: star for star in closest_stars if star not in visited}

        # the base case: all the stars are in visited
        if len(radii) == 0:
            return []

        else:
            stars_so_far = []
            lowest_radius_star = radii[min(radii)]
            stars_so_far.append(lowest_radius_star)
            stars_so_far.extend(self.radius_path(lowest_radius_star, visited))

        return stars_so_far

    def mass_path(self, starting_star: Star, visited: set[Star]) -> list[Star]:
        """Return a list of the stars in the galaxy, filtered by their luminosity.
        """
        visited.add(starting_star)

        # get a list of the closest stars
        closest_stars = [starting_star.closest_stars[star].get_other_endpoint(starting_star) for star in
                         starting_star.closest_stars]

        # create a mapping of the masses of the closest stars to its star if the star isn't in visited
        masses = {star.mass: star for star in closest_stars if star not in visited}

        # the base case: all the stars are in visited
        if len(masses) == 0:
            return []

        else:
            stars_so_far = []
            lowest_mass_star = masses[min(masses)]
            stars_so_far.append(lowest_mass_star)
            stars_so_far.extend(self.mass_path(lowest_mass_star, visited))

        return stars_so_far


def initialize_star_positions(stars: list[Star]) -> None:
    """Initalizes star.rect for star in stars"""
    increasing_inverval = screen_width // 10
    new_x = 0

    for star in stars:
        new_x += increasing_inverval
        star.rect = star.image.get_rect(topleft=(new_x, random.randrange(50, 650)))
        new_x += increasing_inverval


camera_group = CameraGroup()
ship = Ship((50, 200), camera_group)


if __name__ == '__main__':
    # This runs pytest on the tests cases you've defined in this file.
    import pytest
    import doctest
    pytest.main(['classes.py', '-v'])
    doctest.testmod(verbose=True)

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (In PyCharm, select the lines below and press Ctrl/Cmd + / to toggle comments.)
    # You can use "Run file in Python Console" to run both pytest and PythonTA,
    # and then also test your methods manually in the console.
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', '__future__', 'typing', 'random'],
        'max-line-length': 120,
        'disable': ['invalid-name', 'E9992', 'E9997', 'R0913', 'E0611']
    })
