import pyxel
import math
from random import randint


class App:
    def __init__(self):
        pyxel.init(256,256, title="Nuit du Code",fps=60)
        
        self.camera=Camera([0,0],self)
        self.player=Player([0,0],self.camera,self)
        self.projectiles=[]
        self.enemies=[Enemy([0,0],self.camera,0.5,10,self.player,self)]
        self.fallengold = [Fallen_gold([100,100], self.camera, self)]
        pyxel.load("2.pyxres")
        self.shop = Shop(self)
               
        for _ in range(3): 
            self.shop.catalog.append(items[randint(0, 3)])
        pyxel.run(self.update,self.draw)
        
        self.nseed(2)
        
    def update(self):
        self.camera.update(self.player)
        
        if not self.player.dead:
            self.shop.update()
            if not self.shop.etat:
                self.player.update()
                for enemy in self.enemies:
                    enemy.update()
                
                for proj in self.projectiles:
                    proj.update()
                
                
                for gold in self.fallengold:
                    gold.update()
                
                if pyxel.frame_count%(20*60)==0:
                    n=5 + pyxel.frame_count//(5*60)
                    self.generate_enemies(n)
            
        if self.player.current_health <= 0:
            self.player.dead=True
            pyxel.text(128, 128, "You die! PRESS SPACE", 8)
            if pyxel.btn(pyxel.KEY_SPACE):
                self.camera=Camera([0,0],self)
                self.player=Player([0,0],self.camera,self)
                self.projectiles=[]
                self.enemies=[Enemy([0,0],self.camera,0.5,10,self.player,self)]
                self.fallengold = [Fallen_gold([100,100], self.camera, self)]

                
    
    def draw(self):
        pyxel.cls(0)
        self.draw_ground(self.player)
        self.player.draw()
        
        for enemy in self.enemies:
            enemy.draw()
            #pyxel.rect(enemy.screen_pos[0],enemy.screen_pos[1],16,16,enemy.color)
            
        for gold in self.fallengold:
            gold.draw()
            
        if self.player.dead:
            pyxel.text(128, 90, "You die!", 0)
            
        for proj in self.projectiles:
            proj.draw()
            
        pyxel.text(5, 5, f"Gold: {self.shop.gold}", 0)
        pyxel.text(5, 15, f"HP: {self.player.current_health}", 0)
        pyxel.text(5, 25, f"Score: {self.player.score}", 0)
        self.shop.draw()
        
            
        pyxel.mouse(True)
    def draw_ground(self,player):
        """
        for y in range(round(player.pos[1])-100,round(player.pos[1])+100):
            for x in range(round(player.pos[0])-100,round(player.pos[0])+100):
                xs,ys=world2screen([x,y],self.camera)
                pyxel.rect(xs,ys,1,1,4)
        """
        pyxel.rect(player.screen_pos[0]-500,player.screen_pos[1]-500,1000,1000,4)
    def generate_enemies(self,n):
        for _ in range(n):
            x=randint(round(self.player.pos[0])-400,round(self.player.pos[0])+400)
            y=randint(round(self.player.pos[1])-400,round(self.player.pos[1])+400)
            self.enemies.append(Enemy([x,y],self.camera,0.5,10,self.player,self))
        
class Camera:
    def __init__(self,pos,app):
        self.pos = pos
        self.app=app
    def update(self,player):
        self.pos= player.last_positions[0].copy()



def world2screen(pos,cam):
    return pos[0]-cam.pos[0]+128,pos[1]-cam.pos[1]+128

def screen2world(pos,cam):
    return pos[0]+cam.pos[0]-128,pos[1]+cam.pos[1]-128

def animation(frame, tile_start_x, tile_end_x,y,speed):
    if pyxel.frame_count%speed==0:
        if frame+16>=tile_end_x:
            frame=tile_start_x
        else:
            frame= (frame+16)
        
    return frame

class Player:
    def __init__(self,pos,cam,app):
        self.game=app
        self.camera=cam
        self.pos=pos
        self.size=[16,16]
        self.last_positions=[pos]
        self.screen_pos=world2screen(self.pos,self.camera)
        self.velocity=[0,0]
        self.decay=0.85
        self.input=[0,0,0,0]
        self.current_frame=0
        self.mouse_world_pos=[0,0]
        self.angle2mouse= 0
        self.current_health = 2000
        self.max_health = 2000
        self.dmg = 50
        self.speed=1
        self.mag=0
        self.atkspeed = 45
        self.score=0
        self.dead=False
    def update(self):

        self.mouse_world_pos=screen2world([pyxel.mouse_x,pyxel.mouse_y],self.camera)
        self.angle2mouse=self.get_angle_to(self.mouse_world_pos)
        
        self.screen_pos=world2screen(self.pos,self.camera)
        self.last_positions.append(self.pos.copy())
        if len(self.last_positions)>=10:
            self.last_positions.pop(0)
        
        if pyxel.btn(pyxel.KEY_LEFT):
            self.input[0]=1
        else: self.input[0]=0
        
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.input[1]=1
        else: self.input[1]=0
        
        if pyxel.btn(pyxel.KEY_UP):
            self.input[3]=1
        else: self.input[3]=0
        
        if pyxel.btn(pyxel.KEY_DOWN):
            self.input[2]=1
        else: self.input[2]=0
        
        
        if sum(self.input)>1:
            for i in range(len(self.input)):
                self.input[i]*=0.7
        self.mag=self.magnitude()
        if self.mag <0.01:
            self.mag=0
        
        self.velocity[0]=self.velocity[0]+(-self.input[0]+self.input[1])*self.speed
        self.velocity[1]=self.velocity[1]+(self.input[2]-self.input[3])*self.speed
        
        if pyxel.btn(pyxel.KEY_F):
            self.apply_force(4,self.angle2mouse)
        
        self.velocity[0]=self.velocity[0]*self.decay
        self.velocity[1]=self.velocity[1]*self.decay
        
        self.pos[0]+=self.velocity[0]
        self.pos[1]+=self.velocity[1]
    
        if pyxel.frame_count%self.atkspeed==0:
            self.game.projectiles.append(Projectile(self.pos,self.camera,1,self.angle2mouse,5,self.game))
        
    def draw(self):
        if self.mag>=2:
            self.current_frame=animation(self.current_frame, 0, 48,16,10)
        else: self.current_frame=0
        direction= -int(90<=self.angle2mouse<=180 or -180<=self.angle2mouse<=-90)
        if direction==0:
            direction=1
            
        pyxel.blt(self.screen_pos[0],self.screen_pos[1],0,self.current_frame,16,16*direction,16,colkey=2)
        
        
    def magnitude(self):
        return math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
        
    def apply_force(self,f,direction):
        direction = direction*math.pi/180
        self.velocity[0]+=math.cos(direction)*f
        self.velocity[1]-=math.sin(direction)*f
    
    def get_angle_to(self,pos):
        dx=pos[0]-self.pos[0]
        dy=pos[1]-self.pos[1]
        return math.atan2(-dy,dx)*180/math.pi
    
class Projectile:
    def __init__(self,pos, cam, speed,direction, dmg,app):
        self.pos=pos.copy()
        self.pos[0]+=8
        self.pos[1]+=8
        self.size=[4,4]
        self.game=app
        self.cam=cam
        self.speed=speed
        self.dmg=dmg
        self.velocity=[0,0]
        self.direction=direction
        self.decay=0.85
        self.start_frame=pyxel.frame_count
        self.max_frames=5*60
        
    def update(self):
        if pyxel.frame_count-self.start_frame>=self.max_frames:
            self.game.projectiles.remove(self) 
        
        self.apply_force(self.speed,self.direction)
        
        self.pos[0]+=self.velocity[0]
        self.pos[1]+=self.velocity[1]
        
        self.velocity[0]*=self.decay
        self.velocity[1]*=self.decay
        for enemy in self.game.enemies:
            if collision(self,enemy):
                enemy.pv -= self.dmg
                enemy.vertical_offset=32
    
    def draw(self):
        x,y = world2screen(self.pos,self.cam)
        pyxel.circ(x,y,2,7)
        
    
    def apply_force(self,f,direction):
        direction = direction*math.pi/180
        self.velocity[0]+=math.cos(direction)*f
        self.velocity[1]-=math.sin(direction)*f
        
class Enemy:
    def __init__(self,pos, cam, speed, pv, player,app):
        self.cam = cam
        self.pos = pos
        self.speed = speed
        self.pv = pv
        self.player = player
        self.size=[16,16]
        self.velocity=[0,0]
        self.decay=0.85
        self.screen_pos=world2screen(self.pos,self.cam)
        self.game=app
        self.color=9
        self.current_frame=64
        self.vertical_offset=16
    def follow_player(self):
        angle=self.get_angle_to(self.player.pos)
        self.apply_force(self.speed,angle)
        self.apply_force(randint(0,15)/10,randint(0,360))
            
    def update(self):
        
        self.screen_pos=world2screen(self.pos,self.cam)
        #print(self.pos,self.player.pos)
        if self.get_distance_to(self.player)>3:
            self.follow_player()
        self.pos[0]+=self.velocity[0]
        self.pos[1]+=self.velocity[1]

        self.velocity[0]*=self.decay
        self.velocity[1]*=self.decay
        
        if self.pv <= 0:
            self.die()
            self.game.player.score+=1
            
        if collision(self, self.game.player):
            self.game.player.current_health -= 3
            
    def apply_force(self,f,direction):
        direction = direction*math.pi/180
        self.velocity[0]+=math.cos(direction)*f
        self.velocity[1]-=math.sin(direction)*f
    def draw(self):
        if self.vertical_offset==16:
            self.current_frame=animation(self.current_frame, 64, 112,16,10)
            pyxel.blt(self.screen_pos[0],self.screen_pos[1],0,self.current_frame,16,16,16,colkey=2)
        else:
            pyxel.blt(self.screen_pos[0],self.screen_pos[1],0,96,32,16,16,colkey=2)
            if pyxel.frame_count%30==0:
                self.vertical_offset=16
                
    def get_angle_to(self,pos):
        dx=pos[0]-self.pos[0]
        dy=pos[1]-self.pos[1]
        return math.atan2(-dy,dx)*180/math.pi
    
    def die(self):
        self.game.enemies.remove(self)
        self.game.fallengold.append(Fallen_gold(self.pos, self.game.camera, self.game))
        
    def get_distance_to(self,obj):
        dx= obj.pos[0]-self.pos[0]
        dy= obj.pos[1]-self.pos[1]
        return math.sqrt(dx**2+dy**2)
        
    
    
    
class Shop:
    def __init__(self,app):
        self.game=app
        self.gold = 0
        self.etat = False
        self.page = 1
        self.catalog = []
        self.xShop = (256 // 2) - (240//2)
        self.yShop = (256 // 2) - (100//2)
        self.scales = [1, 1, 1]
        self.dispo = [True, True, True]
        
    def draw(self):
        if self.etat:
            pyxel.rect(self.xShop, self.yShop, 240, 90, 9) #centre de l'ecran, 180x100
            
            pyxel.blt(self.xShop + (0*(240//3)) + 24 , self.yShop + 18, 0, 0, 96, 16, 16, scale = 2.5)
            pyxel.blt(self.xShop + (1*(240//3)) + 24, self.yShop + 18, 0, 0, 96, 16, 16, scale = 2.5) #carrés des items
            pyxel.blt(self.xShop + (2*(240//3)) + 24, self.yShop + 18, 0, 0, 96, 16, 16, scale = 2.5)
            
            for i in range(3):
                if self.catalog[i] == "Indisponible":
                    pyxel.blt(self.xShop + (i*(240//3)) + 24 , self.yShop + 18, 0, 32, 96, 16, 16, scale = 2.5)
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 18 + 32, "Indisponible", 0)
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 28 + 32, "Attendez le", 0) #prix
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 38 + 32, "Prochain round", 0) #stats
                
                else:
                    pyxel.blt(self.xShop + (i*(240//3)) + 24 , self.yShop + 18, 0, self.catalog[i].u, self.catalog[i].v, 16, 16, scale = self.scales[i], colkey = 2) #images
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 18 + 32, self.catalog[i].name, 0) #noms
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 28 + 32, str(self.catalog[i].price), 0) #prix
                    pyxel.text(self.xShop + (i*(240//3)) + 16, self.yShop + 38 + 32, str(self.catalog[i].description), 0) #stats
            
            
    def update(self):
        if pyxel.btnp(pyxel.KEY_RSHIFT) and self.etat:
            self.etat = False
        elif pyxel.btnp(pyxel.KEY_RSHIFT) and not self.etat:
            self.etat = True
            
        if pyxel.frame_count%3600 == 0:
            self.reset_shop()
        
        for i in range(3):
                if (pyxel.mouse_x >= self.xShop + (i*(240//3) + 16) and pyxel.mouse_x <= self.xShop + (i*(240//3) + 48)) and (pyxel.mouse_y >= self.yShop + 18 and pyxel.mouse_y <= self.yShop + 40):
                    self.scales[i] = 2
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.dispo[i]:
                        self.buy(i)
                else:
                    self.scales[i] = 1
                    
    def reset_shop(self):
        for i in range(3):
            if self.catalog[i] == "Indisponible":
                self.catalog[i] = items[randint(0,4)]
                
    def buy(self, item):
        if self.catalog[item] == "Indisponible":
            return
        
        stat = self.catalog[item].boosts
        
        if stat[0] == "hp":
            if self.gold >= self.catalog[item].price:
                self.gold -= self.catalog[item].price
                self.game.player.current_health += stat[1]
                self.catalog[item] = "Indisponible"
                if self.game.player.current_health > self.game.player.max_health:
                    self.game.player.current_health = self.game.player.max_health
                
        if stat[0] == "atkspeed":
            if self.gold >= self.catalog[item].price:
                self.gold -= self.catalog[item].price
                self.catalog[item] = "Indisponible"
                self.game.player.atkspeed += stat[1]
                if self.game.player.atkspeed <= 0:
                    self.game.player.atkspeed = 1
                    
        if stat[0] == "max_health":
            if self.gold >= self.catalog[item].price:
                self.gold -= self.catalog[item].price
                self.game.player.max_health += stat[1]
                self.catalog[item] = "Indisponible"
                
        if stat[0] == "dmg":
            if self.gold >= self.catalog[item].price:
                self.gold -= self.catalog[item].price
                self.game.player.dmg += stat[1]
                self.catalog[item] = "Indisponible"
                
        if stat[0] == "speed":
            if self.gold >= self.catalog[item].price:
                self.gold -= self.catalog[item].price
                self.game.player.speed += stat[1]
                self.catalog[item] = "Indisponible"
        
        
class Fallen_gold:
    def __init__(self, pos, cam, app):
        self.pos = pos
        self.cam = cam
        self.size = [16, 16]
        self.game = app
        self.timer = 0
        
    def update(self):
        self.timer += 1
        if collision(self, self.game.player):
            self.game.fallengold.remove(self)
            self.game.shop.gold += 5

            
    def draw(self):
        if self.timer%60 >= 40:
            pyxel.blt(world2screen(self.pos, self.cam)[0], world2screen(self.pos, self.cam)[1], 0, 32, 48, 16, 16, colkey = 2)
        elif self.timer%60 >= 20:
            pyxel.blt(world2screen(self.pos, self.cam)[0], world2screen(self.pos, self.cam)[1], 0, 48, 48, 16, 16, colkey = 2)
        elif self.timer%60 >= 0:
            pyxel.blt(world2screen(self.pos, self.cam)[0], world2screen(self.pos, self.cam)[1], 0, 64, 48, 16, 16, colkey = 2)        
            
class Item:
    def __init__(self, name, price, boosts, description, u, v):
        self.name = name
        self.price = price
        self.boosts = boosts
        self.description = description
        self.u = u
        self.v = v
        
items = [Item("Potion", 30, ("hp", 600), "+ Vie", 0, 48), Item("Torche", 80, ("speed", 0.2), "+ Vitesse", 64, 32), Item("Epee", 60, ("dmg", 5), "+ Degats", 0, 64), Item("Armure", 60, ("maxhp", 300), "+ Defence", 0, 16), Item("Balles", 80, ("atkspeed", -5), "+Atkspeed", 80, 48)]
              
              
def collision(obj1, obj2):
    if (
        ((obj2.pos[0] >= obj1.pos[0] and obj2.pos[0] <= obj1.pos[0] + obj1.size[0]) or
        (obj2.pos[0] + obj2.size[0] >= obj1.pos[0] and obj2.pos[0] + obj2.size[0] <= obj1.pos[0] + obj1.size[0])) #verification de la collision des axes verticaux
        and
        ((obj2.pos[1] >= obj1.pos[1] and obj2.pos[1] <= obj1.pos[1] + obj1.size[1]) or
        (obj2.pos[1] + obj2.size[1] >= obj1.pos[1] and obj2.pos[1] + obj2.size[1] <= obj1.pos[1] + obj1.size[0]))
        ):
        return True
    return False           
App()


