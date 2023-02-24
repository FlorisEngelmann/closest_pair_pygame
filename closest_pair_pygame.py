from collections import deque
import sys
import math
from math import pi
import random
import pygame as pg
from pygame.sprite import Sprite

pg.init()
pg.display.set_mode((1500, 750))

def split_points(points):
  p = deque(points)
  left = [p.popleft() for i in range(len(p)//2)]
  right = [p.popleft() for i in range(len(p))]
  return left, right

def brute_force_pair(squares):
  if len(squares) <= 1:
    return []
  if len(squares) == 2:
    return squares

  pair = [squares[0], squares[1]]
  shortest_dist = distance(pair[0], pair[1])
  for i in range(len(squares)):
    for j in range(len(squares)):
      if i == j: continue
      new_dist = distance(squares[i], squares[j])
      if new_dist < shortest_dist:
        pair = [squares[i], squares[j]]
        shortest_dist = new_dist

  return pair

def closest_within_band(squares):
  if len(squares) < 2:
    return None
  pair = [squares[0], squares[1]]
  shortest_dist = distance(pair[0], pair[1])
  squares = sorted(squares, key=lambda s:s.pos.y)
  for i in range(len(squares)):
    for j in range(i+1, min(len(squares), i+7)):
      new_dist = distance(squares[i], squares[j])
      if new_dist < shortest_dist:
        pair = [squares[i], squares[j]]
        shortest_dist = new_dist

  return pair

def divide_and_conquer(squares):
  if len(squares) <= 3:
    return brute_force_pair(squares)

  left, right = split_points(squares)
  closest_left_pair = divide_and_conquer(left)
  closest_right_pair = divide_and_conquer(right)

  distance_left = distance(closest_left_pair[0], closest_left_pair[1])
  distance_right = distance(closest_right_pair[0], closest_right_pair[1])
  delta = min(distance_left, distance_right)

  middle = left[len(left)-1].pos.x
  squares_within_band = [a for a in squares if abs(a.pos.x - middle) < delta]
  closest_pair_band = closest_within_band(squares_within_band)

  if closest_pair_band:
    if distance(closest_pair_band[0], closest_pair_band[1]) < delta:
      return closest_pair_band

  if distance_left < distance_right:
    return closest_left_pair
  else:
    return closest_right_pair

def adjust_direction_randomly() -> float:
  return (random.random() - 0.5) * 0.2

def wall_collision_check(pos, direction) -> float:
  x = pos[0]
  y = pos[1]
  if x > 750: direction = pi
  if x < 0: direction = 0
  if y > 750: direction = pi/2
  if y < 0: direction = pi*1.5

  return direction

def distance(square1, square2) -> float:
  return math.sqrt(
    (abs(square1.pos.x - square2.pos.x)**2) + 
    (abs(square1.pos.y - square2.pos.y)**2)
  )

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y


class Square(Sprite):
  def __init__(self, game, x, y):
    Sprite.__init__(self, game.squares)
    self.game = game
    self.image = pg.Surface((40, 40))
    self.image.fill((0,0,0))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.pos = Point(x, y)
    self.direction = random.random()*2*pi
    self.speed = 3

  def random_walk(self):
    self.direction = wall_collision_check(self.rect.center, self.direction)
    self.direction += adjust_direction_randomly()

    move_x = math.cos(self.direction)*self.speed
    move_y = math.sin(self.direction)*-self.speed
    self.pos.x += move_x
    self.pos.y += move_y
    self.rect.centerx = self.pos.x
    self.rect.centery = self.pos.y

  def update(self):
    self.random_walk()

class Game:
  def __init__(self):
    pg.display.set_caption('Closest Pair')
    self.clock = pg.time.Clock()
    self.screen = pg.display.set_mode((1500, 750))
    self.n = 10

  def new(self):
    self.squares = pg.sprite.Group()
    for i in range(self.n):
      x = random.randint(10, 1490)
      y = random.randint(10, 740)
      Square(self, x, y)

  def run(self):
    self.playing = True
    while self.playing:
      self.clock.tick(60)
      self.events()
      self.update()
      self.draw()

  def draw(self):
    self.screen.fill((255,255,255))
    
    squares = sorted(self.squares, key=lambda s:s.pos.x)
    
    # Switch between Divide & Conquer and Brute Force
    pair = divide_and_conquer(squares)
    #pair = brute_force_pair(squares)

    if pair:
      for square in self.squares:
        if square in pair:
          square.image.fill((200,0,0))
        else:
          square.image.fill((0,0,0))

    self.squares.draw(self.screen)
    
    pg.display.flip()

  def update(self):
    self.squares.update()

  def events(self):
    for event in pg.event.get():
      if event.type == pg.QUIT:
        self.quit()

  def quit(self):
    pg.quit()
    sys.exit()


g = Game()
while True:
  g.new()
  g.run()