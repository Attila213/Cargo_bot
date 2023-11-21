from sqlite3 import adapt
import pygame,sys,os,random,re

# make a col*row size table and return an array full of rects
def map_generation(startpos,size,col,row):
    map = []
    x= startpos[0]
    y= startpos[1]
    
    for i in range(col):
        arr = []
        for j in range(row):
            r = pygame.Rect(x+ i*(size),y+j*(size),size,size)
            arr.append(r)
        map.append(arr)
    return map

# return an array filled with imgs in the folder
def image_loader(path):
    
    imgs = []
    path = path
    for i in os.listdir(path):
        
        if len(i.split('.')) >1:
            imgs.append(pygame.image.load(path+"/"+i))
        else:
            imgs2 =[]
            imgs2.append(i)
            
            for j in os.listdir(path+"/"+i):
                x = re.search("/*.png",j)       
                if x:
                    arr2 = [pygame.image.load(path+"/"+i+"/"+j),j.split('.')[0]]
                    imgs2.append(arr2)
                else:
                    arr = []
                    for dir in os.listdir(path+"/"+i+"/"+j):
                        arr2 = [pygame.image.load(path+"/"+i+"/"+j+"/"+dir),dir.split('.')[0]]
                        arr.append(arr2)
                    imgs2.append(arr)
            
        
            imgs.append(imgs2)
    
    return imgs

#screen pygame image load(img)
def cut_img(display,img):
    arr = []
    start_pos = []
    width = 0
    height = 0
    counter = 0

    for i in range(img.get_height()):   
        for j in range(img.get_width()):
            if img.get_at((j,i)) == (255 ,0 , 255, 255):
                start_pos = [j+1,i+1]
            if img.get_at((j,i)) == (0 ,255 , 255, 255):
                counter+=1
                
                if counter == 1:
                    width = j-start_pos[0]
                if counter == 2:
                    height = i-start_pos[1]
                    
                    handle_surf = display.copy()
                    
                    clip_rect = pygame.Rect(start_pos[0],start_pos[1],width+1,height+1)
                    handle_surf.set_clip(clip_rect)
                    image = img.subsurface(handle_surf.get_clip())
                    image = image.copy()
                    image.set_colorkey((0,0,0))
                    arr.append(image)
                    
                    start_pos = []
                    width = 0
                    height = 0
                    counter = 0
    return arr

