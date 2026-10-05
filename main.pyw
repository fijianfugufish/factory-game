from pygame import *
import factory as fac
from decodeFactory import window, decodeAndRender, moveCameraUp, moveCameraDown, moveCameraLeft, moveCameraRight
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
    box1 = mainFactory.addInventory(fac.basicContainer)
    mainFactory.updateProducer(coal1, position=(1,1), rotation=fac.Directions.East)
    mainFactory.updateProducer(iron1, position=(10,1), rotation=fac.Directions.East, flipped = (True, False))
    mainFactory.updateMachine(furnace1, position=(5,6), rotation=fac.Directions.North)
    mainFactory.updateInventory(box1, position=(5,10))
    coalT1 = mainFactory.addTransport(fac.conveyor)
    ironT1 = mainFactory.addTransport(fac.conveyor)
    steelT1 = mainFactory.addTransport(fac.conveyor)
    mainFactory.updateProducer(coal1, outputids=[coalT1])
    mainFactory.updateProducer(iron1, outputids=[ironT1])
    mainFactory.updateMachine(furnace1, inputids=[coalT1,ironT1], outputid=steelT1, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box1, inputids=[steelT1])
    mainFactory.addTransportTurn(coalT1, [(3,2), fac.Directions.East])
    mainFactory.addTransportTurn(coalT1, [(5,2), fac.Directions.South])
    mainFactory.addTransportTurn(coalT1, [(5,5), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(9,2), fac.Directions.West])
    mainFactory.addTransportTurn(ironT1, [(6,2), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(6,5), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(5,8), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(5,9), fac.Directions.South])
    
    decodeAndRender(mainFactory, forceRender = True)
    
    while gameRunning:
        # main game loop
        window.fill(bgColor)
        
        dt = clock.tick(FPS) / 1000
        
        events = event.get()
        
        for e in events:
            if e.type == QUIT:
                gameRunning = False
            
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