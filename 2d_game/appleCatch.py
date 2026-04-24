import pyglet
from pyglet import window, shapes, image
from DIPPID import SensorUDP
import time
import random
import os

WINDOW_HEIGHT= 800
WINDOW_WIDTH = 600

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

PORT = 5700
sensor = SensorUDP(PORT)
start_time = time.time()
start_time_updates = time.time()

batch = pyglet.graphics.Batch()
apples = []
bombs = []

fall_speed = 3
spawn_time = 2
score = 0
lives = 3
gameState = 0

APPLE_LIMIT = 12
BOMB_LIMIT = 3
MAX_SPEED = 50
LOWEST_TILT = -5
HIGHEST_TILT = 5
RANGE = 10
BASKET_MOVEMENT_WIDTH = WINDOW_WIDTH - 64
ITEM_HEIGHT = 32
BASKET_WIDTH = 64
UPDATE_TIME = 20

background_image = pyglet.resource.image('background.png')
background = pyglet.sprite.Sprite(background_image, x=0, y=0)
apple_image = pyglet.resource.image('apple.png')
basket_image = pyglet.resource.image('basket.png')
basket = pyglet.sprite.Sprite(basket_image, x=268, y=50, batch=batch)
bomb_image = pyglet.resource.image('bomb.png')
label = pyglet.text.Label(f"Score: {score}   Lives: {lives}",
                          font_name='Times New Roman',
                          font_size=30,
                          x=20, y=WINDOW_HEIGHT-50)
intro = pyglet.text.Label("The goal of this game is to catch as many apples as you can. But beware the bombs!\nUse your phone in landscape mode and tilt it left or right to move the basket accordingly.",
                          font_name='Times New Roman',
                          font_size=26,
                          x=20, y=WINDOW_HEIGHT-150, multiline=True,  width=WINDOW_WIDTH-40)
instruction = pyglet.text.Label("Press Button1 to start the game.",
                          font_name='Times New Roman',
                          font_size=30,
                          x=20, y=50, multiline=True,  width=WINDOW_WIDTH-40)
loss = pyglet.text.Label(f"You lost!\nScore: {score}\nPress Button 1 to restart game.",
                          font_name='Times New Roman',
                          font_size=26,
                          x=20, y=WINDOW_HEIGHT-150, multiline=True,  width=WINDOW_WIDTH-40)

#generates a random number within expected range and returns it
def randomizeNumInRange(low, high):
    number = random.randrange(low, high)
    return number

#adds one apple before game starts
def initGame():
    global real_start_time, start_time, start_time_updates, fall_speed, spawn_time, score, lives
    pos_x = randomizeNumInRange(0, WINDOW_WIDTH)
    apples.append(pyglet.sprite.Sprite(apple_image, x=pos_x, y=750, batch=batch))
    start_time = time.time()
    start_time_updates = time.time()
    fall_speed = 3
    spawn_time = 2
    score = 0
    lives = 3

#updates fall_speed and spawn_time after a certain amount of time (UPDATE_TIME)
def updateGameStats():
    global start_time_updates, fall_speed, spawn_time, UPDATE_TIME
    if (UPDATE_TIME <= time.time() - start_time_updates):
        fall_speed += 0.5
        spawn_time -= 0.2
        start_time_updates = time.time()
    

#moves the basket dependent on the gravity that was sent
def move_basket(data):
    basket_pos = data['y'] + HIGHEST_TILT
    if basket_pos < 0:
        basket_pos = 0
    if basket_pos > RANGE:
        basket_pos = RANGE
    pos_percent = basket_pos/RANGE
    basket.x = BASKET_MOVEMENT_WIDTH*pos_percent

#checks if it is time to spawn a new item, itemId gets randomized to decide wether to spawn an apple or a bomb
def spawnNewItem():
    global apples, bombs, start_time
    pos_x = randomizeNumInRange(0, WINDOW_WIDTH-32)
    if (spawn_time <= time.time() - start_time):
        itemID = randomizeNumInRange(0, 5)
        if (itemID <= 3):
            if (len(apples) < APPLE_LIMIT):
                apples.append(pyglet.sprite.Sprite(apple_image, x=pos_x, y=750, batch=batch))
            elif (len(bombs) < BOMB_LIMIT):
                bombs.append(pyglet.sprite.Sprite(bomb_image, x=pos_x, y=750, batch=batch))
        if (itemID == 4):
            if (len(bombs) < BOMB_LIMIT):
                bombs.append(pyglet.sprite.Sprite(bomb_image, x=pos_x, y=750, batch=batch))
            elif (len(apples) < APPLE_LIMIT):
                apples.append(pyglet.sprite.Sprite(apple_image, x=pos_x, y=750, batch=batch))
        start_time = time.time()
def checkOutOfBounds(list, item):
    if (item.y <= 0):
        list.remove(item)
def checkInBasket(list, item, type):
    global basket, fall_speed, score, lives, label, gameState
    if (type == "apple"):
        width = 27
    if (type == "bomb"):
        width = 32
    else:
        pass
    #checks if item was  not already below basket when it collides with it
    if (item.y - ITEM_HEIGHT >= basket.y):
        #checks if item is within basket parameters
        if (item.y - ITEM_HEIGHT - fall_speed < basket.y and item.x > basket.x and item.x + width < basket.x + BASKET_WIDTH):
            list.remove(item)
            if (type == "apple"):
                score += 10
                label.text = f"Score: {score}   Lives: {lives}"
            if (type == "bomb"):
                score -= 5
                lives -= 1
                if (lives == 0):
                    gameState = 2
                label.text = f"Score: {score}   Lives: {lives}"

#checks if items on screen either move out of screen or land in basket
def checkCollision():
    global apples, bombs
    for item in apples:
        checkOutOfBounds(apples, item)
        checkInBasket(apples, item, "apple")
    for item in bombs:
        checkOutOfBounds(bombs, item)
        checkInBasket(bombs, item, "bomb")
def moveItem():
    global apples, bombs
    for item in apples:
        item.y -= fall_speed
    for item in bombs:
        item.y -= fall_speed


def updateItems():
    spawnNewItem()
    checkCollision()
    moveItem()

def startGame(data):
    global gameState
    if(gameState == 0):
        gameState = 1
    if (gameState == 2):
        initGame()
        gameState = 1

sensor.register_callback('gravity', move_basket)
sensor.register_callback('button_1', startGame)
initGame()

@win.event 
def on_key_press(symbol, modifiers):
    if (symbol == window.key.Q):
        os._exit(0)

@win.event
def on_draw():
    win.clear()
    background.draw()
    if (gameState == 0):
        intro.draw()
        instruction.draw()
    if (gameState == 1):
        label.draw()
        updateGameStats()
        updateItems()
        batch.draw()
    if (gameState == 2):
        loss.draw()

pyglet.app.run()
