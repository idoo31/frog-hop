from ursina import *
import random

class Frog(Entity):
    def __init__(self, idle_tex, jump_tex, **kwargs):
        super().__init__(
            model='quad',
            texture=idle_tex,
            scale=(1.5, 1.5),
            collider='box',
            **kwargs
        )
        self.idle_tex = idle_tex
        self.jump_tex = jump_tex
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 8
        self.jump_power = 18
        self.gravity = -40
        self.is_jumping = False
        self.on_platform = None
        
        # Adjust collider to be slightly smaller than the visual
        self.collider = BoxCollider(self, center=Vec3(0, -0.2, 0), size=Vec3(0.6, 0.4, 0))

    def update(self):
        # Horizontal movement
        self.vel_x = (held_keys['right arrow'] - held_keys['left arrow']) * self.speed
        self.x += self.vel_x * time.dt
        
        # Screen bounds (approximate based on aspect ratio)
        if self.x < -4.5: self.x = -4.5
        if self.x > 4.5: self.x = 4.5

        # Apply gravity
        self.vel_y += self.gravity * time.dt
        self.y += self.vel_y * time.dt
        
        # Jumping
        if held_keys['space'] and not self.is_jumping and self.on_platform:
            self.vel_y = self.jump_power
            self.is_jumping = True
            self.on_platform = None
            self.texture = self.jump_tex

        # Platform Collision (only when falling)
        if self.vel_y < 0:
            self.texture = self.idle_tex
            hit_info = self.intersects()
            if hit_info.hit:
                hit_entity = hit_info.entity
                if isinstance(hit_entity, Platform) and self.y > hit_entity.y:
                    # Snap to top of platform
                    self.y = hit_entity.y + 0.8 # offset based on scale
                    self.vel_y = 0
                    self.is_jumping = False
                    self.on_platform = hit_entity

        else:
            self.on_platform = None

        # Move with platform
        if self.on_platform:
            self.x += self.on_platform.speed * self.on_platform.direction * time.dt
            if self.x < -4.5: self.x = -4.5
            if self.x > 4.5: self.x = 4.5

class Platform(Entity):
    def __init__(self, tex, speed, direction, **kwargs):
        super().__init__(
            model='quad',
            texture=tex,
            scale=(3, 1),
            collider='box',
            **kwargs
        )
        self.speed = speed
        self.direction = direction

    def update(self):
        self.x += self.speed * self.direction * time.dt
        # Wrap around
        if self.direction == 1 and self.x > 6:
            self.x = -6
        elif self.direction == -1 and self.x < -6:
            self.x = 6

class Collectible(Entity):
    def __init__(self, tex, type_name, **kwargs):
        super().__init__(
            model='quad',
            texture=tex,
            scale=(1, 1),
            collider='box',
            **kwargs
        )
        self.type_name = type_name
