import pygame

class Frog:
    def __init__(self, x, y, idle_img, jump_img):
        self.idle_img = idle_img
        self.jump_img = jump_img
        self.image = self.idle_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -13
        self.gravity = 0.5
        self.is_jumping = False
        self.on_platform = None

    def update(self, keys, width, height, platforms):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        else:
            self.vel_x = 0

        self.rect.x += self.vel_x

        # Keep frog within screen bounds horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width

        # Jumping
        if keys[pygame.K_SPACE] and not self.is_jumping and self.on_platform:
            self.vel_y = self.jump_power
            self.is_jumping = True
            self.on_platform = None
            self.image = self.jump_img

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # If we start falling down, we might land on a platform
        if self.vel_y >= 0:
            self.image = self.idle_img # fall or idle
            # Check collision with platforms only when falling
            for plat in platforms:
                if self.rect.colliderect(plat.rect) and self.rect.bottom <= plat.rect.centery + self.vel_y:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.is_jumping = False
                    self.on_platform = plat
                    break
        else:
            self.on_platform = None

        # Move with platform if standing on it
        if self.on_platform:
            self.rect.x += self.on_platform.speed * self.on_platform.direction
            # Still keep in bounds
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > width:
                self.rect.right = width

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Platform:
    def __init__(self, x, y, image, speed, direction, width):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = speed
        self.direction = direction # 1 for right, -1 for left
        self.screen_width = width

    def update(self):
        self.rect.x += self.speed * self.direction
        # Wrap around
        if self.direction == 1 and self.rect.left > self.screen_width:
            self.rect.right = 0
        elif self.direction == -1 and self.rect.right < 0:
            self.rect.left = self.screen_width

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Collectible:
    def __init__(self, x, y, image, type_name):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.type_name = type_name # 'fly' or 'heart'

    def update(self, scroll_y):
        self.rect.y += scroll_y

    def draw(self, surface):
        surface.blit(self.image, self.rect)
