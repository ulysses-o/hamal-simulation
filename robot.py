import pygame 
from settings import * 
from time import sleep 
from obstacle_sensor import ObstacleSensor
from datetime import datetime 

class Robot(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.Surface((size/2,size/2))
        self.image.fill("#66d9e8")
        self.rect = self.image.get_rect(topleft=(pos[0]+(size-size/2)/2,pos[1]+(size-size/2)/2))
        self.speed = 5
        self.mission = None
        self.mission_flag = True 
        self.id = 0
        
        self.moving_around_the_obstacle_mode = False 
        self.center_mode = False 
        self.center_object = None 
        self.load = None 

        self.direction = pygame.math.Vector2()
        self.before_centered_mode_direction = None 
        self.flag = False 
        self.obstacles_sensor = self.create_obstacles_sensor()
        
        self.moving_around_process = {
            "obj_deceted_sensors":[],
            "directions_robot_going":[],
            "step":0
        }

        self.data = {}

    def line_control(self,line):
        flag = 0 

        for sprite in line.sprites():
            if sprite.rect.colliderect(self.rect):
                flag += 1 
        
        return flag 

    def qr_code_reader(self,qr_code):
        
        for sprite in qr_code.sprites():
            if sprite.rect.colliderect(self.rect):
                return sprite 
        
        return False 
        
    def go_target(self,target):
        target = [target[0] + (size-size/2)/2, target[1] + (size-size/2)/2]
        if self.rect.x > target[0] and self.direction.x != 1:
            self.direction.y = 0
            self.direction.x = -1 
        elif self.rect.x < target[0] and self.direction.x != -1:
            self.direction.y = 0
            self.direction.x = 1
        elif self.rect.y > target[1] and self.direction.y != 1:
            self.direction.y = -1
            self.direction.x = 0 
        elif self.rect.y < target[1] and self.direction.y != -1:
            self.direction.y = 1
            self.direction.x = 0

    def on(self,qr_code,line,load):

        total = self.line_control(line) 

        if self.moving_around_the_obstacle_mode:
            if self.moving_around_process["obj_deceted_sensors"] and self.moving_around_process["step"] % 2 == 0:
                self.moving_around_process["step"] += 1
            elif self.moving_around_process["step"] % 2 == 1 and not self.moving_around_process["obj_deceted_sensors"]:
                self.moving_around_process["step"] += 1
            if self.moving_around_process["step"] == 6:
                self.moving_around_process = {
                    "obj_deceted_sensors":[],
                    "directions_robot_going":[],
                    "step":0
                }
                self.moving_around_the_obstacle_mode = False 
            elif self.moving_around_process["step"] == 5 and len(self.moving_around_process["obj_deceted_sensors"]) > 1:
                self.direction.x = 0
                if self.moving_around_process["directions_robot_going"][0] == 0:
                    self.direction.y = -1 
                elif self.moving_around_process["directions_robot_going"][0] == 2:
                    self.direction.y = 1
                else:
                    self.direction.x,self.direction.y = 0,0
                
            elif self.moving_around_process["step"] == 4 and not self.moving_around_process["obj_deceted_sensors"]:
                self.direction.x = -1 
                self.direction.y = 0 
            elif self.moving_around_process["step"] == 2 and self.moving_around_process["directions_robot_going"] and not self.moving_around_process["obj_deceted_sensors"]:
                self.direction.x = 0
                if self.moving_around_process["directions_robot_going"][0] == 0:
                    self.direction.y = -1 
                elif self.moving_around_process["directions_robot_going"][0] == 2:
                    self.direction.y = 1
                else:
                    self.direction.x,self.direction.y = 0,0
            elif self.moving_around_process["step"] == 1 and self.moving_around_process["obj_deceted_sensors"] and not self.moving_around_process["directions_robot_going"]:
                direction = self.moving_around_process["obj_deceted_sensors"][0].name
                if direction in [0,2]:
                    self.direction.x = 1 
                    self.direction.y = 0
                else:
                    self.direction.x,self.direction.y = 0,0
                self.moving_around_process["directions_robot_going"].append(direction)

        elif total != 0:

            qrCode = self.qr_code_reader(qr_code)
            self.flag = True

            if qrCode:
                
                center_x = qrCode.rect.x - ((size/2)-10)/2
                center_y = qrCode.rect.y - ((size/2)-10)/2

                if self.direction.y != 0 and center_y != self.rect.y:
                    self.flag = False 
                if self.direction.x != 0 and center_x != self.rect.x:
                    self.flag = False 

                self.data[self.id]["data"].append([qrCode.name,[qrCode.rect.x,qrCode.rect.y]])

            if self.flag and qrCode and qrCode.name == self.mission[0]:
                self.mission.pop(0)
                self.data[self.id]["end_time"] = datetime.now()

            if qrCode and self.flag:
                if qrCode.name in obj_meaning:
                    if obj_meaning[qrCode.name] == "load":
                        for sprite in load.sprites():
                            if sprite.name == qrCode.name:
                                self.load = sprite
                        sleep(5)
                    elif obj_meaning[qrCode.name] == "unload":
                        self.load = None 
                        sleep(5)

            if len(self.mission) != 0 and total > 1 and self.flag and not self.moving_around_the_obstacle_mode:
                target = (obj_cordinate[self.mission[0]][0] + 5,obj_cordinate[self.mission[0]][1] + 5)
                self.go_target(target)
            
    def create_obstacles_sensor(self):
        obstacles_sensor = pygame.sprite.Group()
        obstacles_sensor.add(ObstacleSensor((self.rect.x-5,self.rect.y-5),0))
        obstacles_sensor.add(ObstacleSensor((self.rect.x+size/2-5,self.rect.y-5),1))
        obstacles_sensor.add(ObstacleSensor((self.rect.x+size/2-5,self.rect.y+size/2-5),2))
        obstacles_sensor.add(ObstacleSensor((self.rect.x-5,self.rect.y+size/2-5),3))
        return obstacles_sensor
    
    def appy_speed(self):

        self.rect.x += self.direction.x * self.speed 
        self.rect.y += self.direction.y * self.speed 

    def update_tools(self,obstacles):
        self.moving_around_process["obj_deceted_sensors"].clear()
        for sprite in self.obstacles_sensor.sprites():
            sprite.rect.x += self.direction.x * self.speed
            sprite.rect.y += self.direction.y * self.speed 
            for s in sprite.laser.sprites():
                s.rect.x += self.direction.x * self.speed
                s.rect.y += self.direction.y * self.speed 
                for obs in obstacles.sprites():
                    if obs.rect.colliderect(s.rect):
                        if self.moving_around_process["step"] == 0:
                            self.moving_around_the_obstacle_mode = True
                        if obs not in self.moving_around_process["obj_deceted_sensors"]:
                            self.moving_around_process["obj_deceted_sensors"].append(s)
                            
    def update(self,qr_code,line,load,obstacles):
        if self.load:
           self.load.rect.x = self.rect.x + 10 
           self.load.rect.y = self.rect.y + 10  

        self.obstacles_sensor.draw(pygame.display.get_surface())
        self.obstacles_sensor.update()
        self.update_tools(obstacles)

        if self.mission or self.center_mode or self.flag:
            if self.mission_flag:
                self.id += 1
                self.data[str(self.id)] = {
                    "start_time":datetime.now(),
                    "end_time":None,
                    "data":[]
                }
                self.mission_flag = False

            self.on(qr_code,line,load)
            self.appy_speed()
        else:
            self.direction.x = 0
            self.direction.y = 0