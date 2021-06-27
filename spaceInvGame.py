"""
Program meant to emulate space invaders
"""

import pygame as pg
import os
import random
import time
import sys


#initializing the fonts
pg.init()

screenSize = width, height = 800,600
shipX = int( 0.05*screenSize[0] )
shipY = int( 0.05*screenSize[1] )

#creating the window
WIN = pg.display.set_mode(screenSize)
pg.display.set_caption("Space Shooter Game")


def resourcePath(relativePath):
    """Get absolute path to resource,
works for dev and pyinstaller"""

    try:
        #PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except AttributeError:
        base_path = os.path.abspath( os.path.join( os.path.dirname( os.path.abspath(sys.argv[0]) ), "assets\\") ) 

    return os.path.abspath( os.path.join(base_path, relativePath) )

#load all image assets into script.
##remember to put all files in same directory
##Enemy Ships
RED_SPACE_SHIP   = pg.image.load( resourcePath("pixel_ship_red_small.png")  )
BLUE_SPACE_SHIP  = pg.image.load( resourcePath("pixel_ship_blue_small.png") )
GREEN_SPACE_SHIP = pg.image.load( resourcePath("pixel_ship_green_small.png") )


##player ship
YELLOW_SPACE_SHIP = pg.transform.scale( pg.image.load( resourcePath("pixel_ship_yellow.png") ), (shipX,shipY) )




##Lasers
RED_LASER    = pg.image.load( resourcePath("pixel_laser_red.png")  )
GREEN_LASER  = pg.image.load( resourcePath("pixel_laser_green.png"))
BLUE_LASER   = pg.image.load( resourcePath("pixel_laser_blue.png") )
YELLOW_LASER = pg.transform.scale( pg.image.load( resourcePath("pixel_laser_yellow.png")  ), (shipX,shipY) )

##Background and transforming it fit screen size
BG = pg.transform.scale( pg.image.load( resourcePath("background-black.png") ), screenSize )


class Laser:
    def __init__(self, locX, locY, img):
        self.X = locX
        self.Y = locY
        self.img = img
        self.mask = pg.mask.from_surface(self.img)

    def draw(self,win):
        win.blit( self.img, (self.X, self.Y) )

    def move(self, vel):
        self.Y += vel

    def offScreen(self, height):
        return not( self.Y <= height and self.Y >=0 )

    def collision(self, obj):
        return collide(self,obj)
    
class Ship:
    ##abstract class to create instances and values
    COOLDOWN = 30
    #constructor
    def __init__(self, locX, locY, health=100):
        self.X = locX
        self.Y = locY
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    #methods of class
    def drawBox(self, surface):
        #pg.draw.rect(surface, (255,0,0),(self.X, self.Y, 20,20))
        surface.blit(self.ship_img, (self.X, self.Y) )
        for laser in self.lasers:
            laser.draw(surface)

    def move_lasers(self, vel, obj):
        #implementing cooldown function
        self.cooldown()
        #moving laser
        for laser in self.lasers:
            laser.move(vel)
            if laser.offScreen(screenSize[1]):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
            

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.X, self.Y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x,y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pg.mask.from_surface(self.ship_img)
        self.max_health = health



    def move_lasers(self, vel, objs):
        #implementing cooldown function
        self.cooldown()
        #moving laser
        for laser in self.lasers:
            laser.move(vel)
            if laser.offScreen(screenSize[1]):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, win):
        #inheriting from the ship class
        super().drawBox(win)
        #drawing the healthbar
        self.healthbar(win)

    def healthbar(self, win):
        pg.draw.rect(win, (255,0,0), (self.X, self.Y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 15) )
        pg.draw.rect(win, (0,255,0), (self.X, self.Y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 15))


        

class Enemy(Ship):
    COLOR_MAP = {
        'red': ( RED_SPACE_SHIP, RED_LASER ),
        'green': (GREEN_SPACE_SHIP, GREEN_LASER ),
        'blue': (BLUE_SPACE_SHIP, BLUE_LASER)
        }
    def __init__(self, x,y, color, health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]

        self.mask = pg.mask.from_surface(self.ship_img)

    
    def move(self, vel):
        #moving the enemy ship down
        self.Y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.X-20, self.Y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offsetX = obj2.X - obj1.X
    offsetY = obj2.Y - obj1.Y

    return obj1.mask.overlap( obj2.mask, (offsetX, offsetY) ) != None
    
        
def mainLoop():
    #boolean value to trigger infinite loop
    run = True
    #frame per second rate
    FPS = 60
    #creating clock object to control speed
    clock = pg.time.Clock()
    #game values
    ##starting level
    level = 0
    ##starting lives
    lives = 5
    #player velocity
    playVel = 5

    #laserVelocity
    laserVel = 4
    #creating enemy stuff
    enemies = []
    waveLen = 5
    enemyVel = 1

    lost = False
    lostCount = 0


    
    #fonts
    ##fonts can be changed to others, depends on your choice
    main_font = pg.font.SysFont("Comic Sans Ms", 50)
    lost_font = pg.font.SysFont("Comic Sans Ms", 60)
    

    player = Player(300,550)
    
    

    def redrawWindow():
        WIN.blit( BG,(0,0) )
        #draw text
        livesLabel = main_font.render(f"Lives: {lives}", 1, (255,255,255) )
        levelLabel = main_font.render(f"Level: {level}", 1, (255,255,255) )

        WIN.blit( livesLabel, (10,10) )
        WIN.blit( levelLabel, ( screenSize[0] - levelLabel.get_width() - 10, 10) )


        for enemy in enemies:
            enemy.drawBox(WIN)
            
        player.drawBox(WIN)
        #drawing healthbar
        player.draw(WIN)

        if lost:
            lostLabel = lost_font.render("You Lose!!", 1, (255,0,0))
            WIN.blit( lostLabel, ( screenSize[0]/2 - lostLabel.get_width()/2, screenSize[1]/2) )

        
        
        #all drawings need to be above this line.
        pg.display.update()
    
    while run:
        clock.tick(FPS)
        redrawWindow()

        if player.health <= 0:
            #decrement the lives by 1 if the player gets to 0 health
            lives-= 1
            player.health = 100
            
        if lives <= 0 :
            lost = True
            lostCount += 1

        if lost:
            #show lost message for 3 seconds
            if lostCount > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            #incrementing level
            level += 1
            #incrementing wavelen
            waveLen += 5
            for i in range(waveLen):
                #randomly choosing the location with which the enemy appears
                enemy = Enemy( random.randrange( 50, screenSize[0]-100 ), random.randrange(-1500,-100),\
                              random.choice(['red','blue','green']) )
                #appending stuff to the enemies list
                enemies.append(enemy)

        
        for event in pg.event.get():
            #checking to see if an event has occured
            #this is for quitting during the game
            if event.type == pg.QUIT:
                #if exit button on the window is pressed then quit
                run = False
                #closing the window
                pg.quit()
                pg.display.quit()
                sys.exit()

        #returns dictionary of all keys pressed
        keys = pg.key.get_pressed()
        if ( keys[pg.K_LEFT] or keys[pg.K_a] ) and ( player.X - playVel ) > 0: #left
            player.X -= playVel
        if ( keys[pg.K_RIGHT] or keys[pg.K_d] ) and ( player.X + playVel + player.get_width() ) < screenSize[0]: #right
            player.X += playVel
        if ( keys[pg.K_UP] or keys[pg.K_w] ) and ( player.Y - playVel ) > 0: #up
            player.Y -= playVel
        if ( keys[pg.K_DOWN] or keys[pg.K_s] ) and ( player.Y + playVel + player.get_height() ) < screenSize[1]: #down
            player.Y += playVel
        if ( keys[pg.K_SPACE] or keys[pg.K_z] ):#shoot
            player.shoot()

        for enemy in enemies[:]:#making a copy of list that you are looping through so not messing up
            enemy.move(enemyVel)
            #moving the enemy lasers
            enemy.move_lasers(laserVel, player)

            if random.randrange(0,2*FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.Y + enemy.get_height() > screenSize[1]:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laserVel, enemies)


def main_menu():
    titleFont = titleFont = pg.font.SysFont("Comic Sans Ms", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0) )
        titleLab = titleFont.render("Press the mouse to begin...",1, (255,255,255) )
        WIN.blit(titleLab, (screenSize[0]/2 - titleLab.get_width()/2, screenSize[1]/2) )
        pg.display.update()
        for event in pg.event.get():
            #this is in case if you decide to quit at the main menu
            if event.type == pg.QUIT:
                run = False
                pg.quit()
                pg.display.quit()
                sys.exit()
                
            if event.type == pg.MOUSEBUTTONDOWN:
                mainLoop()
                    

                
        
main_menu()
