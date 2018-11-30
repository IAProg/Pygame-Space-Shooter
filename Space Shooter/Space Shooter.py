import pygame, sys
from pygame.locals import *
from random import randint

class Star:
	#loading star textures into list
	star1 = pygame.image.load("Sprites\\Star1.png")
	star2 = pygame.image.load("Sprites\\Star2.png")
	star3 = pygame.image.load("Sprites\\Star3.png")
	star4 = pygame.image.load("Sprites\\Star4.png")
	skins = [star1,star2,star3,star4]

	#Star init function giving random start data
	def __init__(self,surface):
		self.surface = surface
		self.size = randint(1,4)
		self.pos = [randint(0,600),randint(-10,610)]
	
	#reset function to reuse star object
	def new(self):
		self.pos[0] = randint(0,600)
		self.pos[1] = -10
		self.size = randint(1,4)

	#update function, moves and displays star
	def tick(self):
		self.pos[1] += 0.1 * self.size
		if self.pos[1]>610:
			self.new()
		self.surface.blit(Star.skins[self.size-1],(self.pos))

class Mine:
	#loading mine texture
	mineImage = pygame.image.load("Sprites\\mine.png")
	speed = 2
	reward = 10
	#mine init with random X start location
	def __init__(self,game):
		self.game = game
		self.cull = False
		self.pos = [randint(0,600),-10]
		self.rect = pygame.Rect(self.pos[0],self.pos[1],50,50)

	def tick(self,array,pos):
		self.pos[1] += Mine.speed

		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

		if self.pos[1] > 600 or self.cull: del array[pos]
		self.game.surface.blit(Mine.mineImage,(self.pos))

class Bullet:
	bulletImage = pygame.image.load("Sprites\\bullet.png")
	speed = 15
	def __init__(self,game):
		self.game = game
		self.cull = False
		self.pos = [game.player.pos[0],game.player.pos[1]]
		self.rect = pygame.Rect(self.pos[0],self.pos[1],20,52)

	def tick(self,array,i):
		self.pos[1] -= Bullet.speed

		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

		if self.pos[1] < 0 or self.cull: del array[i]

		self.game.surface.blit(Bullet.bulletImage,(self.pos))

class Player:
	friction = 0.85
	speed = 2
	shipImage = pygame.image.load("Sprites\\ship.png")
	def __init__(self,game):
		self.game = game
		self.pos = [400,300]
		self.rect = pygame.Rect(self.pos[0],self.pos[1],50,50)
		self.vel = [0,0]

	def move(self,axis,direction):
		self.vel[axis] += Player.speed*direction

	def fire(self):
		self.game.bullets.append(Bullet(self,self))

	def tick(self):
		self.vel[0] *= Player.friction
		self.vel[1] *= Player.friction

		self.pos[0] += self.vel[1]
		self.pos[1] += self.vel[0]

		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

		self.game.surface.blit(Player.shipImage,(self.pos))

class ScoreBoard:
	#Loading images 0-9
	digits = []
	for i in range(0,10): digits.append(pygame.image.load("Sprites\\digit"+str(i)+".png"))

	#Loading background image
	background = pygame.image.load("Sprites\\scoreBackground.png")
	#init scoreboard
	def __init__(self,game):
		self.game = game

	#update and display scoreboard
	def tick(self):
		#converting the game score into a useable list
		scoreArray = [int(value) for value in str(self.game.score)]
		if len(scoreArray) < 4:
			for i in range(4-len(scoreArray)):
				scoreArray.insert(0,0)

		#pushing to display
		self.game.surface.blit(ScoreBoard.background,(600,0))

		for i in range(self.game.playerHealth):
			rect = pygame.Rect(620+(i*8),138,7,60)

			r = 255+((i*12)*-1)
			g = 0+(12*i)

			pygame.draw.rect(self.game.surface,(r,g,100),rect)

		for i in range(len(scoreArray)):
			self.game.surface.blit(ScoreBoard.digits[scoreArray[i]],((624+(40*i)),40))

class Game:
	clock = pygame.time.Clock()
	def __init__(self):
		pygame.init()
		pygame.display.set_caption('Space Shooter!')

		self.score = 0		
		self.bulletTimer = 1
		self.dt = 0

		self.playerHealth = 20

		self.surface = pygame.display.set_mode((800,600))
		self.player = Player(self)

		self.scoreBoard = ScoreBoard(self)

		self.stars = []
		for i in range(50):
			self.stars.append(Star(self.surface))

		self.mines = []

		self.bullets = []

		self.mainloop()

	def spawnEnemy(self):
		choice = randint(0,1)
		if choice == 1:
			self.mines.append(Mine(self))

	def eventHandle(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

		pressed = pygame.key.get_pressed()
		self.bulletTimer -= self.dt
		if pressed[pygame.K_SPACE] and self.bulletTimer <= 0:
			self.bulletTimer = .1
			self.bullets.append(Bullet(self))
		if pressed[pygame.K_a]:
			self.player.move(1,-1)
		if pressed[pygame.K_d]:
			self.player.move(1,1)
		if pressed[pygame.K_w]:
			self.player.move(0,-1)
		if pressed[pygame.K_s]:
			self.player.move(0,1)

	def collisionDetect(self):
		for bullet in self.bullets:
			for mine in self.mines:
				if bullet.rect.colliderect(mine.rect):
					mine.cull=True
					bullet.cull=True
					self.score+=Mine.reward
					print("bullet hit mine \nScore:",self.score)

		for mine in self.mines:
			if self.player.rect.colliderect(mine.rect):
				mine.cull=True
				self.playerHealth -= 1
				print("player hit mine")

	def update(self):

		self.surface.fill([20,20,60])

		for i in range (len(self.stars)):
			self.stars[i].tick()

		try:
			for i in range (len(self.mines)):
				self.mines[i].tick(self.mines,i)
		except:
			pass

		try:
			for i in range (len(self.bullets)):
				self.bullets[i].tick(self.bullets,i)
		except:
			pass

		if randint(0,50) == 1:
			self.spawnEnemy()

		self.scoreBoard.tick()

		self.player.tick()

		pygame.display.flip()

	def mainloop(self):
		while True:
			Game.clock.tick(60)
			self.dt = Game.clock.tick(60) / 1000
			self.collisionDetect()
			self.eventHandle()
			self.update()

if __name__ == "__main__":
	game = Game()
