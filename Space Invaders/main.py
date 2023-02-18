import pygame
import os
import time
import random
pygame.font.init()

# Window Dimensions
WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders!")

# ENEMY SHIPS
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player Ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not self.y <= height and self.y >= 0

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20  # How long to wait between shots.

    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.hp -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.player_img.get_width()

    def get_height(self):
        return self.player_img.get_height()


class Player(Ship):
    def __init__(self, x, y, hp=100, kcount=0):
        super().__init__(x, y, hp)
        self.player_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.player_img)
        self.max_health = hp
        self.kcount = kcount

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.kcount += 1
                        #self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.hp_bar(window)

    def hp_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.player_img.get_height() + 10,
                                               self.player_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.player_img.get_height() + 10,
                                               self.player_img.get_width() * (self.hp/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)

                }

    def __init__(self, x, y, color, hp=100):
        super().__init__(x, y, hp)
        self.player_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.player_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    lvl = 0
    lives = 5
    lost = False
    l_count = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemy = []
    wave_length = 5
    enemyVel = 1

    player_vel = 5
    laser_vel = 4

    player = Player(200, 630)

    clock = pygame.time.Clock()

    def redraw_window():
        # Draw Background
        WIN.blit(BG, (0, 0))
        # Draw Text
        life_label = main_font.render(f"Level: {lvl}", False, (255, 255, 255))
        level_label = main_font.render(f"Lives: {lives}", False, (255, 255, 255))
        kills_label = main_font.render(f"Kill Count: {player.kcount}", False, (255, 0, 0))
        WIN.blit(life_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(kills_label, (WIDTH - life_label.get_width() - 200, 650))

        for e in enemy:
            e.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!!", False, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.hp <= 0:
            lost = True
            l_count += 1

        if lost:
            if l_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemy) == 0:
            lvl += 1
            wave_length += 5
            for i in range(wave_length):
                enemies = Enemy(random.randrange(100, WIDTH-100), random.randrange(-1500, -100),
                                random.choice(["red", "blue", "green"]))
                enemy.append(enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # Move Left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # Move Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # Move Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # Move Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:  # FIRE LASER
            player.shoot()

        for i in enemy[:]:
            i.move(vel=enemyVel)
            i.move_lasers(laser_vel, player)

            if random.randrange(0, 6*60) == 1:  # How often enemies shoot
                i.shoot()

            if collide(i, player):  # Handles player collision with enemies
                player.hp -= 10
                enemy.remove(i)
                player.kcount += 1
            elif i.y + i.get_height() > HEIGHT:
                lives -= 1
                enemy.remove(i)

        player.move_lasers(-laser_vel, enemy)

        redraw_window()


def menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title = title_font.render("Press Mouse Button to Begin...", False, (255, 255, 255))
        WIN.blit(title, (WIDTH/2 - title.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == "__main__":
    menu()
