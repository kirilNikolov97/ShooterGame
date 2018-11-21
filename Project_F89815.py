import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), "img")
snd_dir = path.join(path.dirname(__file__), "snd")

WIDTH = 800
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


# Initialize the game
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHMUP!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font("arial")
def draw_text(surf, text, size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surf.blit(text_surface, text_rect)

def newMob():
	m = Mob()
	mobs.add(m)
	all_sprites.add(m)

def draw_shield_bar(surface, x, y, pct):
	if pct < 0:
		pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 10
	fill = (pct / 100) * BAR_LENGTH
	outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
	pygame.draw.rect(surface, GREEN, fill_rect)
	pygame.draw.rect(surface, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
	for i in range(lives):
		img_rect = img.get_rect()
		img_rect.x = x + 30 * i
		img_rect.y = y
		surf.blit(img, img_rect)

def show_go_screen():
	screen.blit(background, background_rect)
	draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
	draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
	draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False


class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.transform.scale(player_img, (50, 34))
		self.image.set_colorkey(BLACK)

		self.rect = self.image.get_rect()

		self.radius = 20

		self.rect.centerx = WIDTH / 2
		self.rect.bottom = HEIGHT - 10

		self.speedx = 0
		self.shield = 100
		self.lives = 3
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		self.power = 1
		self.power_time =pygame.time.get_ticks()

	def update(self):
		# timeout for powerups
		if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
			self.power -= 1
			self.power_time = pygame.time.get_ticks()

		# unhide if hidden
		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH / 2
			self.rect.bottom = HEIGHT - 10

		self.speedx = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_LEFT]:
			self.speedx = -5
		if keystate[pygame.K_RIGHT]:
			self.speedx = 5
		
		self.rect.x += self.speedx

		if self.rect.right >= WIDTH:
			self.rect.right = WIDTH
		if self.rect.left <= 0:
			self.rect.left = 0

	def powerup(self):
		self.power += 1
		self.power_time = pygame.time.get_ticks()

	def shoot(self):
		if self.power == 1:
			bullet = Bullet(self.rect.centerx, self.rect.top)
			all_sprites.add(bullet)
			bullets.add(bullet)
			shoot_sound.play()
		if self.power >= 2:
			bullet1 = Bullet(self.rect.left, self.rect.centery)
			bullet2 = Bullet(self.rect.right, self.rect.centery)
			all_sprites.add(bullet1)
			all_sprites.add(bullet2)
			bullets.add(bullet1)
			bullets.add(bullet2)
			shoot_sound.play()

	def hide(self):
		# hide the player temporarily
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.image = random.choice(metero_images)
		self.image.set_colorkey(BLACK)

		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width / 2.2)
		
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-100, -40)

		self.speedy = random.randrange(1, 8)
		self.speedx = random.randrange(-3, 3)

		self.scoreOfMob = int(self.rect.width * .85 / 2)

	def update(self):
		self.rect.x += self.speedx
		self.rect.y += self.speedy

		if self.rect.top > HEIGHT + 10 or self.rect.left < - 30 or self.rect.right > WIDTH + 30:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-100, -40)
			self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.transform.scale(bullet_img, (6, 40))
		self.image.set_colorkey(BLACK)

		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -10

	def update(self):
		self.rect.y += self.speedy

		# kill if it moves off the screen
		if self.rect.bottom < 0:
			self.kill()

class Pow(pygame.sprite.Sprite):
	def __init__(self, center):
		pygame.sprite.Sprite.__init__(self)

		self.type = random.choice(['shield', 'gun'])

		self.image = powerup_images[self.type]
		self.image.set_colorkey(BLACK)

		self.rect = self.image.get_rect()
		self.rect.center = center
		self.speedy = 4

	def update(self):
		self.rect.y += self.speedy

		# kill if it moves off the screen
		if self.rect.top > HEIGHT:
			self.kill()


class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosion_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 75

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

# Load all game graphics
background = pygame.image.load(path.join(img_dir, "back.png")).convert()
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_dir, "ship.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "bullet.png")).convert()

metero_images = []
meteor_list = ["meteor0.png", "meteor1.png", "meteor2.png"]
for img in meteor_list:
	metero_images.append(pygame.image.load(path.join(img_dir, img)).convert())

explosion_anim = {}
explosion_anim["lg"] = []
explosion_anim["sm"] = []
explosion_anim["player"] = []
for i in range(9):
	filename = 'regularExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	img_lg = pygame.transform.scale(img, (75, 75))
	explosion_anim["lg"].append(img_lg)
	img_sm = pygame.transform.scale(img, (32, 32))
	explosion_anim["sm"].append(img_sm)

	filename = 'sonicExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	explosion_anim["player"].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "Shoot.wav"))
pow_sound = pygame.mixer.Sound(path.join(snd_dir, "pow4.wav"))
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, "rumble1.ogg"))
expl_sounds = pygame.mixer.Sound(path.join(snd_dir, "Explosion.wav"))
pygame.mixer.music.load(path.join(snd_dir, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.5)




pygame.mixer.music.play(loops = -1)

# Game loop
game_over = True
running = True
while running:
	if game_over:
		show_go_screen()
		game_over = False

		# Declare sprites
		all_sprites = pygame.sprite.Group()
		mobs = pygame.sprite.Group()
		bullets = pygame.sprite.Group()
		powerups = pygame.sprite.Group()

		player = Player()
		all_sprites.add(player)

		# Make 8 Mobs
		for i in range(1, 8):
			newMob()
		score = 0


	# Keep the loop the right speed (FPS)
	clock.tick(FPS)

	# Process input (events)
	for event in pygame.event.get():
		# Check if the window is closed
		if event.type == pygame.QUIT:
			running = False
		# Check if "Space" is pushed
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				player.shoot()

	# Update
	all_sprites.update()

	# check to see if bullet hit a mob
	hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
	for hit in hits:
		score += 50 - hit.scoreOfMob
		expl_sounds.play()
		expl = Explosion(hit.rect.center, "lg")
		all_sprites.add(expl)
		if random.random() > 0.9:
			pow = Pow(hit.rect.center)
			all_sprites.add(pow)
			powerups.add(pow)
		newMob()

	# check to see if mob hit the player
	hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
	for hit in hits:
		player.shield -= hit.scoreOfMob * 2
		expl = Explosion(hit.rect.center, "sm")
		all_sprites.add(expl)
		newMob()
		if player.shield <= 0:
			player_die_sound.play()
			death_explosion = Explosion(player.rect.center, "player")
			all_sprites.add(death_explosion)
			player.hide()
			player.lives -= 1
			player.shield = 100

	# check to see if player hit a powerup
	hits = pygame.sprite.spritecollide(player, powerups, True)
	for hit in hits:
		if hit.type == 'shield':
			player.shield += 20
			pow_sound.play()
			if player.shield >= 100:
				player.shield = 100
		if hit.type == 'gun':
			player.powerup()
			pow_sound.play()
		
	# If the player died and the explosion has finished playing
	if player.lives == 0 and not death_explosion.alive():
		game_over = True

	# Draw / render
	screen.fill(BLACK)
	screen.blit(background, background_rect)
	all_sprites.draw(screen)

	draw_text(screen, str(score), 18, WIDTH / 2, 10)
	
	draw_shield_bar(screen, 5, 5, player.shield)
	draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

	# Flip the display
	pygame.display.flip()

pygame.quit()