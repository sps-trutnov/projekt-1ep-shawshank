import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    DATA_ROOT = '.'
else:
    DATA_ROOT = '..'

import pygame
from animations import getImage
pygame.init()

inventoryImages = pygame.image.load(DATA_ROOT + "/data/hud/inventory/inventory.png")

class inventoryHasKey(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = getImage(32, 0, 32, 32, inventoryImages)
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.completed = False

    def update(self, Janitor):
        if self.completed: self.completed = False
        else: self.completed = True
        
        if self.completed:
            if Janitor:
                self.image = getImage(32, 0, 32, 32, inventoryImages)
            else:
                self.image = getImage(0, 0, 32, 32, inventoryImages)
        else:
            if Janitor:
                self.image = getImage(32, 0, 32, 32, inventoryImages)
            else:
                self.image = getImage(32, 0, 32, 32, inventoryImages)

class inventoryHasBoots(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = getImage(128, 0, 32, 32, inventoryImages)
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.completed = False
        self.unlocked = False

    def update(self, state):
        
        if state == "odemknout":
            if self.unlocked:
                self.unlocked = False
            else:
                self.unlocked = True
                
            if self.unlocked:
                if self.completed:
                    self.image = getImage(64, 0, 32, 32, inventoryImages)
                else:
                    self.image = getImage(96, 0, 32, 32, inventoryImages)
                    
            else:
                self.image = getImage(128, 0, 32, 32, inventoryImages)
        
        if state == "sebrat":
            if self.completed:
                self.completed = False
            else:
                self.completed = True
            
            if self.completed:
                self.image = getImage(64, 0, 32, 32, inventoryImages)
            else:
                self.image = getImage(96, 0, 32, 32, inventoryImages)
