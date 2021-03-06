import json
import pygame
import math

from tile import Tile
from mario import Mario
from enemy import Enemy
from interactive_tile import InteractiveTile


class TileMap:
    def __init__(self, file, screen):
        self.screen = screen

        with open(file) as f:
            self.__info = json.load(f)

        self.tile = pygame.Rect(0, 0, self.__info['tile_width'],
                                self.__info['tile_height'])

        self.camera = pygame.Rect(0, 0, self.screen.get_rect().width,
                                  self.screen.get_rect().height)

        map = self.__info['map']

        width = self.tile.width
        height = self.tile.height

        self.visible_tiles_x = int(self.tile.width / width)
        self.visible_tiles_y = int(self.tile.height / height)

        self.tiles = []
        self.interacting_tiles = []
        self.enemies = []

        self.total_tiles_x = len(map[0])
        self.total_tiles_y = len(map)

        self.total_width = self.total_tiles_x * width
        self.total_height = self.total_tiles_y * height

        self.__visible_tiles = []

        self.mario = None

        mario = self.__info['mario']
        images = self.__info['images']

        interacting_tiles = self.__info['interacting_tiles']

        self.flag = self.flag = Tile(screen, 0, 0, 'f', width, height,
                                     ['assets/images/map_assets' +
                                      '/dynamic/pole/flag.png'])

        top_of_pole = self.__info['finish']

        colliding_tiles_types = self.__info['colliding_tiles']

        colliding_tiles = []

        self.eatables_tiles = self.__info['eatables']['tiles']
        eatables_images = self.__info['eatables']['images']

        for row, data_row in enumerate(map):
            row_contents = []

            for col, data_col in enumerate(data_row):
                    if images[data_col]:
                        row_contents.append(Tile(screen, row, col,
                                                 data_col,
                                                 width,
                                                 height,
                                                 images[data_col]))
                        if data_col in interacting_tiles:
                            tile = row_contents[-1]
                            self.interacting_tiles.append(InteractiveTile(
                                                            tile))
                            tile.interactive_id = \
                                len(self.interacting_tiles) - 1

                            if data_col in self.eatables_tiles:
                                interacting_tile = Tile(screen, row, col,
                                                        data_col, width,
                                                        height,
                                                        eatables_images[
                                                            data_col])

                                self.interacting_tiles[-1].interactive_tile \
                                    = interacting_tile

                        elif data_col is top_of_pole:
                            head = row_contents[-1]
                            self.flag.rect.top = head.rect.bottom
                            self.flag.rect.right = head.rect.centerx

                        if data_col in colliding_tiles_types:
                            colliding_tiles.append(row_contents[-1])
                    else:
                        row_contents.append(Tile(screen, row, col, data_col,
                                                 width, height))

            self.tiles.append(row_contents)

        for enemy in self.__info['enemies']:
            new_enemy = Enemy(screen, enemy['x'], enemy['y'],
                              enemy['type'], colliding_tiles_types,
                              width, height, enemy['images'])

            new_enemy.set_max_position(self.total_width, self.total_height)

            self.enemies.append(new_enemy)

        for enemy in self.enemies:
            enemy.set_visible_tiles(colliding_tiles)

        mario = self.__info['mario']
        self.mario = Mario(screen, mario['x'], mario['y'], self.camera,
                           colliding_tiles_types, self.interacting_tiles,
                           width, height, self.enemies, mario['images'])

        self.last_camera_x = -1
        self.last_camera_y = -1

        self.update()

    def update(self):
        last_x = self.camera.x

        self.camera.centerx = self.mario.tile.rect.centerx

        if self.camera.left < 0:
            self.camera.left = 0
        elif self.camera.right > self.total_width:
            self.camera.right = self.total_width

        # camare freedom
        if last_x > self.camera.left:
            self.camera.left = last_x

        min_x = max(int(self.camera.left / self.tile.width) - 1, 0)
        max_x = min(math.ceil(self.camera.right / self.tile.width),
                    self.total_tiles_x)
        min_y = 0
        max_y = self.total_tiles_y

        if self.last_camera_x != self.camera.x or \
                self.last_camera_y != self.camera.y:
            self.__visible_tiles = []

            for i in range(min_y, max_y):
                for j in range(min_x, max_x):
                    if self.tiles[i][j].image:
                        self.__visible_tiles.append(self.tiles[i][j])

            self.mario.set_visible_tiles(self.__visible_tiles)

        self.last_camera_x = self.camera.x
        self.last_camera_y = self.camera.y

        self.mario.update()

        for enemy in self.enemies:
            if enemy.active is False and \
                    self.camera.colliderect(enemy.tile.rect):
                if enemy.enemy_type not in self.eatables_tiles:
                    enemy.active = True

            enemy.update()

        for tile in self.interacting_tiles:
            tile.update()

    def render(self):
        x = self.camera.left
        y = self.camera.top

        self.screen.fill((92, 150, 252))
        for tile in self.__visible_tiles:
            if tile:
                if tile.interactive_id is not -1:
                    interactive_tile = self.interacting_tiles[
                        tile.interactive_id]
                    if interactive_tile.interactive_tile_action:
                        interactive_tile.interactive_tile.render(x, y)

                    tile.render(x, y)
                else:
                    tile.render(x, y)

        for enemy in self.enemies:
            enemy.render(x, y)

        self.flag.render(x, y)

        self.mario.render(x, y)
