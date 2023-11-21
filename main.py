import json
from turtle import right
import functions as fun
import sys,pygame,os
pygame.init()

def json_key_exist(dict,key):
    for i in dict:
        if i == key:
            return True
    return False

def json_save_progress():
    # write the last try to the json to save the process
    r = open(selected_level.path,"r")
    base = json.load(r)
    boxes = {}
    boxes["startpos"] = base["startpos"]
    boxes["result"] = base["result"]
    boxes["last_try"] = selected_level.last_try
    
    w = open(selected_level.path,"w")
    json.dump(boxes,w)

class Button:
    name = any
    color = any
    pos = any
    size = any
    img = any
    img_pos = any
    hover = any
    rect = any
    
    text = any
    text_pos = any
    text_size = any
    
    
    def __init__(self,name,color,pos,hover,size):
        self.name = name
        self.color = color
        self.pos = pos
        self.size = size
        self.hover = hover
        
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])

    def add_img(self,img,img_pos):
        self.img = img        
        self.img_pos = img_pos
    
    def add_label(self,text,text_pos,size):
        self.text = text
        self.text_pos = self.pos
        self.text_pos[0] += text_pos[0]
        self.text_pos[1] += text_pos[1]
        self.text_size = size

    
    def draw(self):
        width = 1
        if self.rect.collidepoint((mx,my)):
            width = 0    
        
        pygame.draw.rect(display,self.color,self.rect,width,4)
        
        if self.img != any and self.img != None:
            display.blit(self.img,(self.img_pos[0],self.img_pos[1]))
        
        if self.text != any and self.text != None:
            font = pygame.font.SysFont("Arial",self.text_size)
            final_text = font.render(self.text,False,(255,255,255),None)
            display.blit(final_text,self.text_pos)

class Robot:
    size = any
    pos = any
    rect = any
    holding = None
    frame = 0
    counter = 0
    movedown = True
    base_values = any
    
    def __init__(self,pos,size):
        self.size = size
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size,self.size)
        self.base_values = pygame.Rect(self.rect.x,self.rect.y,self.rect.width,self.rect.height)
        
    def move_left(self):
        if self.frame % 1 == 0:
            self.rect.x -= 1
            self.counter -= 1
        
        if self.counter == -selected_level.side_move:
            if self.holding != None:
                self.holding.pos[0] -= 1
            return False   
        return True       
        
    def move_right(self):
        if self.frame % 1 == 0:
            self.rect.x += 1
            self.counter += 1
            
        if self.counter == selected_level.side_move:
            if self.holding != None:
                self.holding.pos[0] += 1
            return False    
        return True
    
    def move_down(self):  
        if self.frame % 1 ==0:
            if self.movedown:
                self.rect.height += 2
            elif not self.movedown:
                self.rect.height -= 2

            # ha nem tart semmit és lefelé megy
            if self.holding == None and self.movedown:
                #akkor végigmegyünk az összes dobozon
                for i in selected_level.boxes_array:
                    #ha valamelyikkel ütközik akkor azt fogja tartani
                    if self.rect.colliderect(i.rect):
                        self.movedown = False
                        self.holding = i
                        self.holding.pos[1] = None
                    #földdel akkor csak visszamegy
                    if self.rect.colliderect(selected_level.ground_rect):
                        self.movedown = False
            
            if self.holding != None and self.movedown:
                for i in selected_level.boxes_array:
                    if i != self.holding:
                        if i.rect.colliderect(self.holding.rect):
                            self.movedown = False
                            self.holding.rect.bottom = i.rect.y-2
                            #itt
                            self.holding.pos[1] = int(((selected_level.game_rect.bottom-selected_level.box_size-selected_level.ground_rect.height)-self.holding.rect.y)/(selected_level.box_size+2))
                            
                            self.holding = None
                            break
                        if self.holding.rect.colliderect(selected_level.ground_rect):
                            self.movedown = False
                            self.holding.pos[1] = 0
                            self.holding.rect.bottom = selected_level.ground_rect.top
                            self.holding = None
                            break
                        
        if self.rect.height ==self.base_values.height:
            self.movedown = True
            return False
        
        return True            
    
class Box:
    pos = any
    color = any
    size = any
    rect = any
    
    def __init__(self,color,pos,size):
        self.color = color
        self.pos = pos
        self.size = size
        
    def copy(self):
        box =  Box(self.color,self.pos,self.size)
        box.rect = pygame.Rect(self.rect.x,self.rect.y,self.rect.width,self.rect.height)
        
        return box

class CommandLinePart:
    rect = any
    number = any
    
    sticker = None
    command = None
    
    def __init__(self,number,rect):
        self.number = number
        self.rect = rect 

class Container:
    name = any
    path = any
    pos = any
    robot = any
    
    box_size = any
    
    boxes_array = any
    result_array= any
    save_array = any
    last_try = any
    
    game_rect = any
    ground_rect = any
    space = any
    platform_length = any
    side_move = any
    
    def __init__(self,path,name,pos,size,space):
        self.path = path
        self.pos = pos
        self.name = name
        self.size = size
        self.space = space
        self.box_size = self.size-4
        self.side_move = self.box_size+self.space[0]
        
        self.game_rect = None
        self.ground_rect = None
        self.save_array = []
        self.result_array = []
        self.boxes_array = []
        self.last_try = []
        
        self.fill_arrays()

    def fill_arrays(self):
        r = open(self.path,"r")
        boxes = json.load(r)
        
        self.platform_length = len(boxes["startpos"])

        
        self.game_rect = pygame.Rect(self.pos[0],self.pos[1],self.platform_length*(self.box_size+self.space[0])-self.space[0]+6,9*self.box_size)
        self.game_rect = pygame.Rect(self.pos[0],self.pos[1],self.platform_length*(self.box_size+self.space[0])-self.space[0]+6,9*self.box_size)

        self.ground_rect = pygame.Rect(self.game_rect.x+2,self.game_rect.bottom-1,self.game_rect.width-4,1)
        self.robot = Robot([self.game_rect.x+1,self.pos[1]],self.size)

        #FILL BOXES RESULT
        self.boxes_array = []
        self.result_array = []
        self.save_array = []
        for i in boxes["startpos"]:
            counter = 0
            for j in boxes["startpos"][i]:
                box = Box(j,[int(i),counter],self.box_size)
                box.rect = pygame.Rect(self.game_rect.x+3+(box.pos[0]*(self.box_size+self.space[0])),(self.game_rect.bottom-self.box_size)-(box.pos[1]*(self.box_size+self.space[1]))-1,self.box_size,self.box_size)
                
                self.boxes_array.append(box.copy())
                self.save_array.append(box.copy())
                counter+= 1
            counter = 0
            for j in boxes["result"][i]:
                box = Box(j,[int(i),counter],self.box_size)
                box.rect = pygame.Rect(self.game_rect.x+3+(box.pos[0]*(self.box_size+self.space[0])),(self.game_rect.bottom-self.box_size)-(box.pos[1]*(self.box_size+self.space[1]))-1,self.box_size,self.box_size)
                
                self.result_array.append(box.copy())
                counter+= 1
             
        self.last_try = boxes["last_try"]
    
    def win(self):
        
        if not animation_in_process:
            same =False
            counter = 0 
            for i in selected_level.boxes_array:
                for j in selected_level.result_array:
                    if j.pos == i.pos and j.color == i.color:
                        counter += 1     
            
            if counter == len(selected_level.result_array):
                same = True    
                return same
    
    def draw(self):
        pygame.draw.rect(display,(100,100,100),self.game_rect,1,4)
        pygame.draw.rect(display,(100,100,100),self.ground_rect,1,4)
        
        if not over:
            pygame.draw.rect(display,(100,100,100),self.robot.rect,1,4)
        else:
            pygame.draw.rect(display,(200,0,0),self.robot.rect,1,4)
            
        
        for i in self.boxes_array:
            color = any
            if i.color == "y":
                color = (255,184,50)
            if i.color == "b":
                color = (50,192,255)
            if i.color == "g":
                color = (124,228,40)
            if i.color == "r":
                color = (255,80,52)
            
            pygame.draw.rect(display,color,i.rect,0,4)    

    def copy(self):
        return Container(self.path,self.name,self.pos,self.size,self.space)
    
class Command:
    direction = any
    img = any
    rect = any
    number = any
    
    def __init__(self,direction,img):
        self.direction = direction
        self.img = img
        
class Arrow(Command):
    def action(self,ROBOT):
        
        if self.direction == "left":
            return ROBOT.move_left()
        
        if self.direction == "right":
            return ROBOT.move_right()
        
        if self.direction == "down":
            return ROBOT.move_down()
    
    def copy(self):
        copy_arrow = Arrow(self.direction,self.img)
        copy_arrow.rect = pygame.Rect(self.rect.x,self.rect.y,23,23) 
        return copy_arrow
    
class Loop(Command):
    def action(self):
        stepback_array.append([execute_indexes[0],execute_indexes[1]])
        
        execute_indexes[0] = int(self.direction)-1
        execute_indexes[1] = -1

    def copy(self):
        copy_loop = Loop(self.direction,self.img)
        copy_loop.rect = pygame.Rect(self.rect.x,self.rect.y,23,23) 
        return copy_loop

class Sticker(Command):
    def copy(self):
        copy_sticker = Sticker(self.direction,self.img)
        copy_sticker.rect = pygame.Rect(self.rect.x,self.rect.y,23,12) 
        return copy_sticker

WINDOW_SIZE = [1400,780]
SCALE = 2
screen = pygame.display.set_mode(WINDOW_SIZE,0,32)
display = pygame.Surface((WINDOW_SIZE[0]/SCALE,WINDOW_SIZE[1]/SCALE))

hold_result = False
animation_in_process = False
same  = False
base_command_x_line = 485
command_line = []
base_commands = []
stepback_array = []
buttons = []
menu_buttons = []

over = False
stop = True

execute_indexes = [0,-1]
hold = False
game_mode = False
selected = None


#region LOAD BASE_COMMANDS AND COMMAND_LINE

commands = fun.image_loader("assets/images/commands")
startbutton = fun.image_loader("assets/images/run")
classtype = any
for i in commands:
    for j in i:
        if type(j) == str:
            if j == "arrows":
                classtype = Arrow
            elif j == "stickers":
                classtype = Sticker
            elif j == "loops":
                classtype = Loop    
        else:
            base_commands.append(classtype(j[1],j[0]))
            
                            
col_counter = 0
row_counter = 0
for i in range(len(base_commands)):
    if i != 0:
        if type(base_commands[i-1]) != type(base_commands[i]):
            col_counter = 0
            row_counter +=1
    base_commands[i].rect = pygame.Rect(base_command_x_line+col_counter*30,50+row_counter*30,23,23)
    col_counter += 1

selected_level = any

#endregion

stop_rect = pygame.Rect(base_command_x_line+130,37,50,50)
startbutton = fun.image_loader("assets/images/run")

menu_button_startpositions=[18,245,472]
menu_button_endpositions=[18+221,245+221,472+221]


counter = 0
for i in os.listdir("assets/levels"):
    test = Container("assets/levels/"+i,"1",[menu_button_startpositions[counter],10],19,[10,2])

    kezdo = menu_button_startpositions[counter]
    vegso = (221/2)-test.game_rect.width/2
    
    container = Container("assets/levels/"+i,"1",[menu_button_startpositions[counter] + (221/2)-test.game_rect.width/2,10],19,[5,1])
    
    btn = Button(i.split('.')[0],(200,200,200),[container.pos[0],container.pos[1]],True,[container.game_rect.width, container.game_rect.height+container.ground_rect.height])
    btn.add_label(i.split('.')[0],[8,5],10)
    menu_buttons.append([btn,container.copy()])
    counter += 1

frame=0
while True:
    frame +=1
    display.fill((0,0,0))
    mx = pygame.mouse.get_pos()[0]/2
    my = pygame.mouse.get_pos()[1]/2
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if game_mode:
                json_save_progress()
            sys.exit()
                             
        if game_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    stop = not stop
                if stop:
                    selected_level.fill_arrays()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    #select command from base command
                    selected = None
                    
                    # region Buttons
                    for btn in buttons:
                            
                        if btn.rect.collidepoint((mx,my)) and btn.name == "show_the_result" and stop:
                            stop = True
                            hold_result = True
                            selected_level.fill_arrays()
                            break
                        #clear command line
                        if btn.rect.collidepoint((mx,my)) and btn.name == "clear":
                            #clear commands
                            for i in command_line:
                                i.command = None
                                i.sticker = None
                            #clear last try
                            selected_level.last_try = {}
                            break
                        
                        if btn.rect.collidepoint((mx,my)) and btn.name == "menu":
                            json_save_progress()
                            command_line.clear()
                            stop = True
                            game_mode = False
                            break
                            
                    #endregion
                    
                    for i in base_commands:
                        if i.rect.collidepoint((mx,my)):
                            selected = i.copy()
                
                    #remove from command line  
                    for i in command_line:
                        if i.sticker != None:
                            if i.sticker.rect.collidepoint((mx,my)):
                                selected = i.sticker.copy()
                                i.sticker = None
                                selected_level.last_try[str(i.number[0])+","+str(i.number[1])].pop("sticker")
                        if i.command != None:
                            if i.command.rect.collidepoint((mx,my)):
                                selected = i.command.copy()
                                i.command = None
                                selected_level.last_try[str(i.number[0])+","+str(i.number[1])].pop("command")
                                
                        
                        
                        if json_key_exist(selected_level.last_try,str(i.number[0])+","+str(i.number[1])):
                            if selected_level.last_try[str(i.number[0])+","+str(i.number[1])] == {}:
                                selected_level.last_try.pop(str(i.number[0])+","+str(i.number[1]))
                        json_save_progress()
                            
                    hold = True
                                             
            if event.type == pygame.MOUSEBUTTONUP:
                if game_mode:
                    if selected != None:
                        #place command to command line
                        for i in command_line:
                            if i.rect.collidepoint((mx,my)):

                                if not json_key_exist(selected_level.last_try,str(i.number[0])+","+str(i.number[1])):
                                    selected_level.last_try[str(i.number[0])+","+str(i.number[1])] = {}

                                if type(selected) != Sticker:
                                    selected.rect = pygame.Rect(i.rect.x+1,i.rect.y+1,i.rect.width,i.rect.height)
                                    i.command = selected.copy()
                                    selected_level.last_try[str(i.number[0])+","+str(i.number[1])]["command"] = selected.direction
                                else:
                                    selected.rect = pygame.Rect(i.rect.x+1,i.rect.y-10,i.rect.width,i.rect.height-10)
                                    i.sticker = selected.copy()
                                    selected_level.last_try[str(i.number[0])+","+str(i.number[1])]["sticker"] = selected.direction
                    json_save_progress()
                    hold_result = False        
                    hold = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    if selected_level != None and selected_level != any:
                        selected_level.boxes_array.clear()
                        
                    for mnu_btn in menu_buttons:
                        if mnu_btn[0].rect.collidepoint((mx,my)):
                            selected_level =Container("assets/levels/"+mnu_btn[0].name+".json","1",[10,35],38,[10,2])
                    

                    for i in range(4):
                        for j in range(8):
                            cmd_l_part = CommandLinePart([i,j],pygame.Rect(base_command_x_line+j*26,190+i*40,25,25))
                            
                            ## kattintásos betöltésre
                            for nums in selected_level.last_try:
                                if nums == str(i)+","+str(j):
                                    for commands in selected_level.last_try[nums]:
                                        for base in base_commands:
                                            if base.direction == selected_level.last_try[nums][commands]:                            
                                                if commands == "command":
                                                    cmd_l_part.command = base.copy()
                                                    cmd_l_part.command.rect = pygame.Rect(cmd_l_part.rect.x+1,cmd_l_part.rect.y+1,cmd_l_part.rect.width,cmd_l_part.rect.height)
                                                if commands == "sticker":
                                                    cmd_l_part.sticker = base.copy()
                                                    cmd_l_part.sticker.rect = pygame.Rect(cmd_l_part.rect.x+1,cmd_l_part.rect.y-10,cmd_l_part.rect.width,cmd_l_part.rect.height-13)
                            command_line.append(cmd_l_part)
                    
                    buttons.clear()
                    btn = Button("clear",(215,83,23),[base_command_x_line,140],True,[90,22])
                    btn.add_img(pygame.image.load("assets/images/trash_can.png"),[base_command_x_line+5,142])
                    btn.add_label("CLEAR",[30,3],13)
                    buttons.append(btn)
                    buttons.append(Button("show_the_result",(100,100,100),[selected_level.game_rect.x,selected_level.game_rect.bottom+10],True,[selected_level.game_rect.width,30]))
                    btn = Button("menu",(0,200,0),[10,10],True,[70,20])
                    btn.add_label("MENU",[20,3],13)
                    buttons.append(btn)
                            
                    game_mode = True
    
    if game_mode:
        #check if the result and the boxes are the same
        if not animation_in_process:
            same = selected_level.win()
        
        #show result
        if hold_result:
            selected_level.boxes_array = selected_level.result_array.copy()
        else:
            selected_level.boxes_array = selected_level.save_array.copy()
        
        if stop:
            execute_indexes = [0,-1]
            over = False
            stop = True

            selected_level.robot.counter = 0
            selected_level.robot.frame = 0
            selected_level.robot.holding = None

            animation_in_process = False
            selected_level.robot.movedown = True
            selected_level.robot.rect = pygame.Rect(selected_level.robot.base_values.x,selected_level.robot.base_values.y,selected_level.robot.base_values.width,selected_level.robot.base_values.height)
            
        #mouse movement 
        if hold and selected != None:
            selected.rect.x = mx-11
            selected.rect.y = my-11
            
            display.blit(selected.img,(selected.rect.x,selected.rect.y))
            
        #stepping forward
        if execute_indexes[1] >= 8:
            
            if len(stepback_array) > 0: 
                
                #if it would be over but the stebback array isnt empty then execute the command on last array index
                execute_indexes = [stepback_array[len(stepback_array)-1][0],stepback_array[len(stepback_array)-1][1]]
                
                #then remove it
                stepback_array.remove(stepback_array[len(stepback_array)-1])
            else:
                over = True
             
        if not stop and not over and not animation_in_process:
            execute_indexes[1]+=1
        
        #robot stopping if its out of line(wall)
        over = (selected_level.robot.rect.right > selected_level.game_rect.right or selected_level.robot.rect.left < selected_level.game_rect.left) or same

        
        for i in command_line:
            if i.number == [execute_indexes[0],execute_indexes[1]]:
                pygame.draw.rect(display,(200,200,200),pygame.Rect(i.rect.x,i.rect.y,25,25))
                
                #stickers (maybe its working properly 50%) 
                command_allowed = False
                if i.sticker == None:
                    command_allowed = True
                    
                if not command_allowed:
                    if selected_level.robot.holding == None:
                        if i.sticker.direction == "none":
                            command_allowed = True
                    else:
                        if i.sticker.direction[0] == selected_level.robot.holding.color or i.sticker.direction == "all":
                            command_allowed = True
                
                # the animation cannot stop
                if animation_in_process:
                    command_allowed = True  
                
                #command execution
                if i.command != None and not over:
                    if command_allowed:
                        if type(i.command) == Arrow:
                            animation_in_process = i.command.action(selected_level.robot)
                            if animation_in_process:
                                selected_level.robot.frame += 1
                            else:
                                selected_level.robot.frame = 0
                                selected_level.robot.counter = 0
                        else:
                            i.command.action()
                    else:
                        execute_indexes[1] += 1
    #--------------------------------------------------
    if game_mode:
        if selected_level.robot.holding != None:
            selected_level.robot.holding.rect.y = selected_level.robot.rect.bottom
            selected_level.robot.holding.rect.x = selected_level.robot.rect.x+2

        selected_level.draw()

        for i in buttons:
            i.draw()

        for i in command_line:
            if execute_indexes == i.number:
                pygame.draw.rect(display,(100,100,100),i.rect,0)    
            pygame.draw.rect(display,(255,0,0),i.rect,1,0)
            
            if i.command != None:
                display.blit(i.command.img,(i.command.rect.x,i.command.rect.y))
            if i.sticker != None:
                display.blit(i.sticker.img,(i.sticker.rect.x,i.sticker.rect.y))

        for i in base_commands:
            display.blit(i.img,(i.rect.x,i.rect.y))

        if stop:
            display.blit(startbutton[0],(stop_rect.x,stop_rect.y))
        else:
            display.blit(startbutton[1],(stop_rect.x,stop_rect.y))
    else:
        for i in menu_buttons:
            i[0].draw()
            i[1].draw()

    
    #--------------------------------------------------
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()