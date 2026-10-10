from pygame import *
import factory as fac
from decodeFactory import window, decodeAndRender, moveCameraUp, moveCameraDown, moveCameraLeft, moveCameraRight, screenToWorld
from encodeFactory import placeComponent, deleteAt
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
                elif e.key == K_v:
                    placeComponent(mainFactory, fac.furnace, screenToWorld(mouse.get_pos()), direction, (flipx, flipy))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_c:
                    placeComponent(mainFactory, fac.drill, screenToWorld(mouse.get_pos()), direction, (flipx, flipy))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_i:
                    placeComponent(mainFactory, fac.basicContainer, screenToWorld(mouse.get_pos()), direction, (flipx, flipy))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_z:
                    placeComponent(mainFactory, fac.drill2, screenToWorld(mouse.get_pos()), direction, (flipx, flipy))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_t:
                    placeComponent(mainFactory, fac.basicCombiner, screenToWorld(mouse.get_pos()), direction, (flipx, flipy))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                elif e.key == K_o:
                    deleteAt(mainFactory, screenToWorld(mouse.get_pos()))
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