from pygame import *
import factory as fac
from decodeFactory import window, decodeAndRender, moveCameraUp, moveCameraDown, moveCameraLeft, moveCameraRight, screenToWorld
from encodeFactory import placeComponent, deleteAt, changeRecipeAt
from buildSystem import BuildMenu
from worldGeneration import updateVisibleChunks, updateChunkPoses
import pygameui

cursor = transform.scale(image.load(f"Images/Mouse/Cursor.png").convert_alpha(), (0.25 * 64, 0.25 * 64))

def drawAll(window, dt):
    pygameui.UI.drawAll(window)
    pygameui.AnimatableSprite.updateAllAnimations(dt)

def main():
    clock = time.Clock()
    FPS = 30
    
    mouse.set_visible(False)
    
    bgColor = (80, 80, 100)
    
    gameRunning = True
    dragging = False
    
    mainFactory = fac.Factory()
    
    decodeAndRender(mainFactory, forceRender = True)
    
    BuildMenu.init()
    
    while gameRunning:
        # main game loop
        window.fill(bgColor)
                
        dt = clock.tick(FPS) / 1000
        
        events = event.get()
        
        mousex, mousey = mouse.get_pos()
        
        for e in events:
            if e.type == QUIT:
                gameRunning = False
            
            if e.type == KEYDOWN:
                if e.key == K_e:
                    changeRecipeAt(mainFactory, screenToWorld((mousex, mousey)))
                elif e.key == K_o:
                    deleteAt(mainFactory, screenToWorld((mousex, mousey)))
                elif e.key == K_r:
                    BuildMenu.buildRotateClockwise()
                elif e.key == K_f:
                    BuildMenu.buildFlip()
                elif e.key == K_p:
                    # temporary coal drill
                    placeComponent(mainFactory, fac.drill2, screenToWorld((mousex, mousey)), fac.Directions.North, (False, False))
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
            
            if not pygameui.Button.handleAllButtons((mousex, mousey), e.type):
                if e.type == MOUSEBUTTONUP:
                    if dragging:
                        BuildMenu.endBuildDrag(mainFactory)
                        dragging = False
                    else:
                        BuildMenu.build(mainFactory)
                        
                    decodeAndRender(mainFactory, dt = dt, forceRender = True)
                        
                elif e.type == MOUSEBUTTONDOWN:
                    if not dragging and isinstance(BuildMenu.buildingComponent, fac.Transport) and "Turn" not in BuildMenu.buildingComponentDict["displayName"]:
                        BuildMenu.startBuildDrag(mainFactory, (mousex, mousey))
                        dragging = True
        
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
        
        if dragging:
            BuildMenu.updateBuildDrag(mainFactory, (mousex, mousey))
        
        BuildMenu.buildSetPosition((mousex, mousey))
        
        mainFactory.step(dt)
        
        decodeAndRender(mainFactory, dt = dt, moved = moved)
        
        updateVisibleChunks()
        updateChunkPoses()
        
        BuildMenu.buildShowGhost()
        
        drawAll(window, dt)
        
        window.blit(cursor, (mousex, mousey))
        
        display.flip()

if __name__ == "__main__":
    main()