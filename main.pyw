from pygame import *
import factory as fac
from decodeFactory import window, decodeAndRender, moveCameraUp, moveCameraDown, moveCameraLeft, moveCameraRight, screenToWorld
from encodeFactory import placeComponent
import pygameui

def drawAll(window, dt):
    pygameui.UI.drawAll(window)
    pygameui.AnimatableSprite.updateAllAnimations(dt)

def main():
    clock = time.Clock()
    FPS = 30
    
    bgColor = (80, 80, 100)
    
    gameRunning = True
    
    mainFactory = fac.Factory()
    
    coal1 = mainFactory.addProducer(fac.drill)
    iron1 = mainFactory.addProducer(fac.drill2)
    furnace1 = mainFactory.addMachine(fac.furnace)
    mainFactory.updateProducer(coal1, position=(1,1), rotation=fac.Directions.East)
    mainFactory.updateProducer(iron1, position=(10,1), rotation=fac.Directions.East, flipped = (True, False))
    mainFactory.updateMachine(furnace1, position=(5,6), rotation=fac.Directions.North)
    mainFactory.updateMachine(furnace1, inputids=None, outputid=None, recipe=fac.steelRecipe)

    #mainFactory.extendTransportTurn(steelT1, 1, True)
    
    decodeAndRender(mainFactory, forceRender = True)
    
    direction = fac.Directions.North
    flipx = False
    flipy = False
    bent = False
    
    while gameRunning:
        # main game loop
        window.fill(bgColor)
        
        dt = clock.tick(FPS) / 1000
        
        events = event.get()
        
        for e in events:
            if e.type == QUIT:
                gameRunning = False
            
            if e.type == KEYDOWN:
                if e.key == K_b:
                    placeComponent(mainFactory, fac.conveyor, screenToWorld(mouse.get_pos()), direction, (flipx, flipy), bent = bent)
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_r:
                    direction = fac.Directions((direction.value + 90) % 360)
                elif e.key == K_x:
                    flipx = not flipx
                elif e.key == K_y:
                    flipy = not flipy
                elif e.key == K_p:
                    bent = not bent
            
            pygameui.Button.handleAllButtons(mouse.get_pos(), e.type)
        
        keys = key.get_pressed()
        
        moved = False
        
        if keys[K_w]:
            moveCameraUp(5 * dt)
            moved = True
        if keys[K_s]:
            moveCameraDown(5 * dt)
            moved = True
        if keys[K_a]:
            moveCameraLeft(5 * dt)
            moved = True
        if keys[K_d]:
            moveCameraRight(5 * dt)
            moved = True
        
        mainFactory.step(dt)
        
        decodeAndRender(mainFactory, dt = dt, moved = moved)
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()