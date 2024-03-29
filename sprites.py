import math
import random

import pygame
import os
import config
from queue import PriorityQueue
from itertools import permutations


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


# Aki - Greedy Local Best First Search

class Aki(Agent):
    def __int__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        queue = PriorityQueue()
        visited = [0]
        path = []
        i = 0
        while len(visited) != len(coin_distance[i]):
            j = 0
            for k in range(len(coin_distance[i])):
                if coin_distance[i][j] != 0 and k not in visited:
                    # k is the index of the node and we add it to the tuple
                    queue.put((coin_distance[i][j], k))
                j += 1
            # i is the next node were visiting
            i = queue.get()[1]
            # Add it to the final return path
            path.append(i)
            # Add it to the visited nodes so we dont backtrack
            visited.append(i)
            # Empty the queue
            for l in range(queue.qsize()):
                queue.get()
        return [0] + path + [0]


# Jocke - brute force
class Jocke(Agent):
    def __int__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        paths = []
        minPathCost = 9999
        minPath = []
        permSet = [i for i in range(1, len(coin_distance))]
        permArr = permutations(permSet)
        # Add zeros to the start and end of the path and then calcuate the path
        for permutation in permArr:
            paths.append([0] + list(permutation) + [0])
        for path in paths:
            currSum = 0
            for i in range(len(path) - 1):
                currSum += coin_distance[path[i]][path[i + 1]]
            if currSum < minPathCost:
                minPathCost = currSum
                minPath = path
        return minPath


# Uki - Branch and Bound
class Uki(Agent):
    def __int__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        queue = PriorityQueue()
        i = 0
        j = 0
        partialPath = []
        for k in range(len(coin_distance[i])):
            partialPath = [0]
            if coin_distance[i][j] != 0:
                partialPath.append(k)
                partialPath.reverse()
                queue.put((coin_distance[i][j], partialPath))
            j += 1
        current = queue.get()
        possiblePaths = []
        while len(current[1]) != len(coin_distance):
            j = 0
            i = current[1][0]
            for k in range(len(coin_distance[i])):
                currentArr = current[1].copy()
                if coin_distance[i][j] != 0 and k not in current[1]:
                    currentArr.insert(0, k)
                    if len(currentArr) == len(coin_distance):
                        possiblePaths.append([current[0] + coin_distance[i][j], currentArr])
                    queue.put((current[0] + coin_distance[i][j], currentArr))
                j += 1
            current = queue.get()
        for i in range(len(possiblePaths)):
            possiblePaths[i][0] += coin_distance[possiblePaths[i][1][0]][0]
        return [0] + min(possiblePaths)[1]


class Micko(Agent):
    def __int__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def MST(self, coin_dist, currentPathLen):
        visited = [0]
        cost = 0
        while len(visited) != len(coin_dist) - currentPathLen + 1:
            minCost = 9999
            nextj = 0
            nexti = 0
            flag = 0
            for currentVertex in visited:
                for index in range(len(coin_dist)):
                    if index not in visited:
                        if coin_dist[currentVertex][index] < minCost:
                            minCost = coin_dist[currentVertex][index]
                            nexti = index
                            nextj = currentVertex
                            flag = 1
            if not flag:
                continue
            visited.append(nexti)
            cost += coin_dist[nexti][nextj]
        return cost

    def get_agent_path(self, coin_distance):
        queue = PriorityQueue()
        i = 0
        j = 0
        partialPath = []
        for k in range(len(coin_distance[i])):
            partialPath = [0]
            if coin_distance[i][j] != 0:
                partialPath.append(k)
                partialPath.reverse()
                queue.put((self.MST(coin_distance, len(partialPath)) + coin_distance[i][j], partialPath))
            j += 1
        current = queue.get()
        possiblePaths = []
        while len(current[1]) != len(coin_distance):
            j = 0
            i = current[1][0]
            for k in range(len(coin_distance[i])):
                currentArr = current[1].copy()
                if coin_distance[i][j] != 0 and k not in current[1]:
                    currentArr.insert(0, k)
                    if len(currentArr) == len(coin_distance):
                        possiblePaths.append([self.MST(coin_distance, len(currentArr)) + current[0] + coin_distance[i][j], currentArr])
                    queue.put((self.MST(coin_distance, len(currentArr)) + current[0] + coin_distance[i][j], currentArr))
                j += 1
            current = queue.get()
        for i in range(len(possiblePaths)):
            possiblePaths[i][0] += coin_distance[possiblePaths[i][1][0]][0]
        return [0] + min(possiblePaths)[1]
