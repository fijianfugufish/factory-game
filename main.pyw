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
    
    bgColor = (12, 45, 160)
    
    gameRunning = True
    
    mainFactory = fac.Factory()
    
    drill1 = mainFactory.addProducer(fac.drill)
    mainFactory.updateProducer(drill1, position = (1, 0), rotation = fac.Directions.West)
    
    drill2 = mainFactory.addProducer(fac.drill2)
    mainFactory.updateProducer(drill2, position = (11, 1), rotation = fac.Directions.East)
    
    furnace = mainFactory.addMachine(fac.furnace)
    mainFactory.updateMachine(furnace, position = (8, 5), rotation = fac.Directions.North)
    
    box = mainFactory.addInventory(fac.box)
    mainFactory.updateInventory(box, position = (8, 10))
    
    conveyor1 = mainFactory.addTransport(fac.conveyor)
    conveyor2 = mainFactory.addTransport(fac.conveyor)
    conveyor3 = mainFactory.addTransport(fac.conveyor)
    
    mainFactory.updateProducer(drill1, outputids = [conveyor1])
    mainFactory.updateProducer(drill2, outputids = [conveyor2])
    
    mainFactory.updateMachine(furnace, inputids = [conveyor1, conveyor2], outputid = conveyor3, recipe = fac.steelRecipe)
    
    mainFactory.updateInventory(box, inputids = [conveyor3])
    
    mainFactory.addTransportTurn(conveyor1, [(3, 1), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(5, 1), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(5, 2), fac.Directions.West])
    mainFactory.addTransportTurn(conveyor1, [(2, 2), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(2, 3), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(7, 3), fac.Directions.North])
    mainFactory.addTransportTurn(conveyor1, [(7, 2), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(8, 2), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(8, 4), fac.Directions.South])
    
    mainFactory.addTransportTurn(conveyor2, [(10, 1), fac.Directions.West])
    mainFactory.addTransportTurn(conveyor2, [(9, 1), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor2, [(9, 4), fac.Directions.South])
    
    mainFactory.addTransportTurn(conveyor3, [(8, 7), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor3, [(8, 9), fac.Directions.South])
    
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
            moveCameraUp(3 * dt)
            moved = True
        if keys[K_s]:
            moveCameraDown(3 * dt)
            moved = True
        if keys[K_a]:
            moveCameraLeft(3 * dt)
            moved = True
        if keys[K_d]:
            moveCameraRight(3 * dt)
            moved = True
        
        mainFactory.step(dt)
        
        decodeAndRender(mainFactory, moved = moved)
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()