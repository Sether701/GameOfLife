# inspired by Gravitar: https://www.youtube.com/channel/UCvu-g3WAsFGWJKwF4QAvBZg

from collections import Counter

import asyncio
import pygame as pg
import random as rnd
import time

PAUSE = 'Pause'
CONTINUE = 'Continue'
CLEAR = 'Clear'
RESET_POSITION = 'Reset Position'

def draw_grid(screen, width, height, cell_width, cell_height):
    pg.draw.rect(screen, (0,0,0), (1,1,width,height)) # fill background of grid with black
    for x in range(int(width/cell_width)):  # iterate through all coordinates of the grid
        for y in range(int(height/cell_height)):
            rect = pg.Rect(x*cell_width-1, y*cell_height-1, # create a rectangle as a frame for the cell
                               cell_width+1, cell_height+1)
            pg.draw.rect(screen, (50, 50, 50), rect, 1) # draw rectangle


def get_neighbors(cell): # searches for the cell's neighbors
    for dx, dy in [(-1,-1), ( 0,-1), ( 1,-1),
                   (-1, 0),          ( 1, 0),
                   (-1, 1), ( 0, 1), ( 1, 1)]:
        yield cell[0] + dx, cell[1] + dy

def next_generation(world):
    # count neighbors of "each" cell
    neighbors = Counter([pos for cell in world for pos in get_neighbors(cell)])

    # check if a cell will die or be born and return all of them
    return {pos for pos,amnt in neighbors.items() if amnt == 3 or (amnt == 2 and pos in world)}

'''def calculate_cell_size(world, width, height):
    # calculate cell size based on the size of the current world
    xValues, yValues = zip(*world)
    minX, maxX, minY, maxY = min(xValues), max(xValues), min(yValues), max(yValues)
    columns, rows = maxX-minX + 1, maxY-minY + 1
    #return  width / columns - 1, height / rows - 1, -minX, -minY
    return 5,5,0,0'''

def button(screen, text, mouse_position, x, y, width, height, color_normal, color_hover):

    # create text 
    text_object = pg.font.SysFont('Corbel',30).render(text, True, (0,0,0))

    # check if mouse cursor is inside the button's area
    if mouse_position[0] > x and mouse_position[0] < x + width and mouse_position[1] > y and mouse_position[1] < y + height:
        # raw hovered button
        pg.draw.rect(screen, color_hover, (x,y,width,height))
    else:
        # draw normal button
        pg.draw.rect(screen, color_normal, (x,y,width,height))

    # calculate position for the text to be on
    text_rect = text_object.get_rect(center=(int(x+width/2), int(y+height/2)))

    # put text on right spot
    screen.blit(text_object, text_rect)

    return (x, x+width, y, y+height, text)



def build_command_field(screen, command_field_x, command_field_y, command_field_width, command_field_height, paused, counter, framerate):

    # fill background of command field with white
    pg.draw.rect(screen, (255,255,255), (command_field_x,command_field_y,command_field_width,command_field_height))

    # draw counter
    counter_text = pg.font.SysFont('Corbel',20).render('Generations: ' + str(counter), True, (100,100,100))
    screen.blit(counter_text,(command_field_x,command_field_y))

    # draw framerate
    framerate_text = pg.font.SysFont('Corbel',20).render('Framerate: ' + str(framerate), True, (100, 100, 100))
    screen.blit(framerate_text, (command_field_x,command_field_y + 30))

    # get mouse position
    mouse_position = pg.mouse.get_pos()

    # create pause button
    text = ''
    if(paused): text = CONTINUE
    else: text = PAUSE

    button_list = []

    # create pause/continue button
    button_list.append(button(screen, text, pg.mouse.get_pos(), command_field_x + 150, command_field_y + 170,120,60,(200,0,0),(150,0,0)))

    # create clear button
    button_list.append(button(screen, CLEAR, mouse_position, command_field_x + 150, command_field_y + 260, 120, 60, (150, 0, 150), (100, 0, 100)))

    # create reset position button
    button_list.append(button(screen, RESET_POSITION, mouse_position, command_field_x + 120, command_field_y + 350, 150, 60, (0, 150, 150), (0, 100, 100)))

    return button_list


# generate a random start world
world = [(rnd.randrange(200), rnd.randrange(200)) for i in range(6000)]

# counter for counting the generation
generation_counter = 1

# framerate
framerate = 20

pg.init()

# setting up some constants
grid_x = grid_y = 1
grid_width = grid_height = 1000
command_field_width = 300
command_field_height = grid_height
command_field_x = grid_width+1
command_field_y = 1

# create pygame screen
screen = pg.display.set_mode([grid_width+command_field_width, grid_height])


cell_width = cell_height = cell_width_min = cell_height_min = 5
cell_width_max = cell_height_max = 50

offset_x = offset_y = 0

clock = pg.time.Clock()

# initialize loop variable
paused = False

# initialize navigating variable -> shows if the mouse is navigating or not
navigating = False

# when getting the mouse's movement, the first one has to be ignored (otherwise it resets the offset)
ignoreMovement = True

while True:
    
    clock.tick(framerate)

    # check if the simulation is not paused
    if not paused: 
        old_world = world
        world = next_generation(world)

        generation_counter += 1

        # check if there are any new living cells
        if all(cell in world for cell in old_world) and len(world) == len(old_world):
            # if there a no new cells, the simulation is static => stop calculation
            # PROBLEM: cant recognize oscillators
            paused = True

        # check if there are no living cells anymore
        if not world:
            paused = True

    #cell_width, cell_height, offsetX, offsetY = calculate_cell_size(world, grid_width, grid_height)

    # (re)draw grid
    draw_grid(screen, grid_width, grid_height, cell_width, cell_height)

    # draw living cells
    for x,y in world:
        pg.draw.rect(screen, (200,200,0), ((x+offset_x)*cell_height, (y+offset_y)*cell_height , cell_width-1, cell_width-1))
    
    # (re)build command field
    button_list = build_command_field(screen, command_field_x,command_field_y,command_field_width,command_field_height, paused, generation_counter, framerate)

    pg.display.flip()

    # check events
    for event in pg.event.get():
        if event.type == pg.QUIT: # quit game if window is closed
            quit()
        elif event.type == pg.MOUSEBUTTONDOWN: # check for mousebutton events

            if event.button == 4: # check for scrolling down // zooming out

                if(cell_width < cell_width_max and cell_height < cell_height_max): # check if cells are not too big
                    # adjust cell size
                    cell_width+= 1
                    cell_height+= 1
            elif event.button == 5: # check for scrolling up // zooming in
                
                if(cell_width > cell_width_min and cell_height > cell_height_min): # check if cells are not too small
                    # adjust cell size
                    cell_width-= 1
                    cell_height-= 1
                    
            elif event.button == 3: # check for right-click
                
                # check for mouse position
                pos = pg.mouse.get_pos()

                # check if mouse is in grid area
                if(pos[0] < grid_width and pos[0] > grid_x and pos[1] < grid_height and pos[1] > grid_y):
                    # pg.mouse.set_cursor(*pg.cursors.diamond)
                    pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
                    ignoreMovement = True
                    navigating = True

            elif event.button == 1: # check for left-click 
               
                # check for mouse position
                pos = pg.mouse.get_pos()

                # check if mouse is in grid area
                if(pos[0] < grid_width and pos[0] > grid_x and pos[1] < grid_height and pos[1] > grid_y):
                   
                    # check if the generation counter is at 1 -> user should only give birth to new cells and kill living cells if the generation is at 1
                    if generation_counter == 1:
                        
                        # calculate possible cell position based on mouse position
                        #x = (pos[0] - pos[0] % cell_width) / cell_width
                        #y = (pos[1] - pos[1] % cell_height) / cell_height
                        x = int(pos[0] / cell_width) - offset_x
                        y = int(pos[1] / cell_height) - offset_y

                        # check if there is a cell at this position
                        if (x,y) in world:
                            world.remove((x,y))
                        else:
                            world.append((x,y))

                # check if mouse is in command field area
                elif (pos[0] > command_field_x):
                    for but in button_list:
                        # check if mouse is in the area of a button
                        if (pos[0] >= but[0] and pos[0] <= but[1] and pos[1] >= but[2] and pos[1] <= but[3]):
                            # execute button
                            button_text = but[4]
                            
                            if button_text == PAUSE:
                                paused = not paused
                            elif button_text == CONTINUE:
                                paused = not paused
                            elif button_text == CLEAR:
                                # pause simulation
                                paused = True
                                # clear all living cells
                                world = []
                                # reset generation counter
                                generation_counter = 1
                            elif button_text == RESET_POSITION:
                                # reset navigation
                                offset_x = offset_y = 0

                            # stop searching for buttons
                            break
        
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 3: # check for left-click (release)
                pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW)
                navigating = False

        elif event.type == pg.MOUSEMOTION:
            # check if user wants to navigate
            if(navigating):
                # ignore movement, if it is not allowed yet
                movement = pg.mouse.get_rel()
                if not ignoreMovement:
                    offset_x = offset_x + movement[0]
                    offset_y = offset_y + movement[1]
                    
                else:
                    # as the movement has been ignored, the program should no longer ignore it
               
                    ignoreMovement = not ignoreMovement

  