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
    
    # line 1
    coal1 = mainFactory.addProducer(fac.drill)
    iron1 = mainFactory.addProducer(fac.drill2)
    furnace1 = mainFactory.addMachine(fac.furnace)
    box1 = mainFactory.addInventory(fac.box)

    mainFactory.updateProducer(coal1, position=(1, 1), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron1, position=(18, 1), rotation=fac.Directions.East)
    mainFactory.updateMachine(furnace1, position=(9, 10), rotation=fac.Directions.North)
    mainFactory.updateInventory(box1, position=(9, 18))

    coalT1 = mainFactory.addTransport(fac.conveyor)
    ironT1 = mainFactory.addTransport(fac.conveyor)
    steelT1 = mainFactory.addTransport(fac.conveyor)

    mainFactory.updateProducer(coal1, outputids=[coalT1])
    mainFactory.updateProducer(iron1, outputids=[ironT1])
    mainFactory.updateMachine(furnace1, inputids=[coalT1, ironT1], outputid=steelT1, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box1, inputids=[steelT1])

    mainFactory.addTransportTurn(coalT1, [(3, 2), fac.Directions.East])
    mainFactory.addTransportTurn(coalT1, [(7, 2), fac.Directions.South])
    mainFactory.addTransportTurn(coalT1, [(7, 5), fac.Directions.West])
    mainFactory.addTransportTurn(coalT1, [(4, 5), fac.Directions.South])
    mainFactory.addTransportTurn(coalT1, [(4, 8), fac.Directions.East])
    mainFactory.addTransportTurn(coalT1, [(9, 8), fac.Directions.South])
    mainFactory.addTransportTurn(coalT1, [(9, 9), fac.Directions.South])

    mainFactory.addTransportTurn(ironT1, [(17, 2), fac.Directions.West])
    mainFactory.addTransportTurn(ironT1, [(14, 2), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(14, 6), fac.Directions.East])
    mainFactory.addTransportTurn(ironT1, [(16, 6), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(16, 8), fac.Directions.West])
    mainFactory.addTransportTurn(ironT1, [(10, 8), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(10, 9), fac.Directions.South])

    mainFactory.addTransportTurn(steelT1, [(9, 12), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(9, 14), fac.Directions.East])
    mainFactory.addTransportTurn(steelT1, [(13, 14), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(13, 16), fac.Directions.West])
    mainFactory.addTransportTurn(steelT1, [(10, 16), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(10, 17), fac.Directions.South])


    # line 2
    coal2 = mainFactory.addProducer(fac.drill)
    iron2 = mainFactory.addProducer(fac.drill2)
    furnace2 = mainFactory.addMachine(fac.furnace)
    box2 = mainFactory.addInventory(fac.box)

    mainFactory.updateProducer(coal2, position=(30, 3), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron2, position=(52, 4), rotation=fac.Directions.East)
    mainFactory.updateMachine(furnace2, position=(40, 14), rotation=fac.Directions.North)
    mainFactory.updateInventory(box2, position=(40, 24))

    coalT2 = mainFactory.addTransport(fac.conveyor)
    ironT2 = mainFactory.addTransport(fac.conveyor)
    steelT2 = mainFactory.addTransport(fac.conveyor)

    mainFactory.updateProducer(coal2, outputids=[coalT2])
    mainFactory.updateProducer(iron2, outputids=[ironT2])
    mainFactory.updateMachine(furnace2, inputids=[coalT2, ironT2], outputid=steelT2, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box2, inputids=[steelT2])

    mainFactory.addTransportTurn(coalT2, [(32, 4), fac.Directions.East])
    mainFactory.addTransportTurn(coalT2, [(37, 4), fac.Directions.South])
    mainFactory.addTransportTurn(coalT2, [(37, 7), fac.Directions.West])
    mainFactory.addTransportTurn(coalT2, [(34, 7), fac.Directions.South])
    mainFactory.addTransportTurn(coalT2, [(34, 11), fac.Directions.East])
    mainFactory.addTransportTurn(coalT2, [(40, 11), fac.Directions.South])
    mainFactory.addTransportTurn(coalT2, [(40, 13), fac.Directions.South])

    mainFactory.addTransportTurn(ironT2, [(51, 5), fac.Directions.West])
    mainFactory.addTransportTurn(ironT2, [(47, 5), fac.Directions.South])
    mainFactory.addTransportTurn(ironT2, [(47, 8), fac.Directions.East])
    mainFactory.addTransportTurn(ironT2, [(50, 8), fac.Directions.South])
    mainFactory.addTransportTurn(ironT2, [(50, 11), fac.Directions.West])
    mainFactory.addTransportTurn(ironT2, [(41, 11), fac.Directions.South])
    mainFactory.addTransportTurn(ironT2, [(41, 13), fac.Directions.South])

    mainFactory.addTransportTurn(steelT2, [(40, 16), fac.Directions.South])
    mainFactory.addTransportTurn(steelT2, [(40, 18), fac.Directions.West])
    mainFactory.addTransportTurn(steelT2, [(36, 18), fac.Directions.South])
    mainFactory.addTransportTurn(steelT2, [(36, 21), fac.Directions.East])
    mainFactory.addTransportTurn(steelT2, [(40, 21), fac.Directions.South])
    mainFactory.addTransportTurn(steelT2, [(40, 23), fac.Directions.South])


    # line 3 - deliberately long
    coal3 = mainFactory.addProducer(fac.drill)
    iron3 = mainFactory.addProducer(fac.drill2)
    furnace3 = mainFactory.addMachine(fac.furnace)
    box3 = mainFactory.addInventory(fac.box)

    mainFactory.updateProducer(coal3, position=(-18, 28), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron3, position=(14, 29), rotation=fac.Directions.East)
    mainFactory.updateMachine(furnace3, position=(-1, 43), rotation=fac.Directions.North)
    mainFactory.updateInventory(box3, position=(-1, 54))

    coalT3 = mainFactory.addTransport(fac.conveyor)
    ironT3 = mainFactory.addTransport(fac.conveyor)
    steelT3 = mainFactory.addTransport(fac.conveyor)

    mainFactory.updateProducer(coal3, outputids=[coalT3])
    mainFactory.updateProducer(iron3, outputids=[ironT3])
    mainFactory.updateMachine(furnace3, inputids=[coalT3, ironT3], outputid=steelT3, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box3, inputids=[steelT3])

    mainFactory.addTransportTurn(coalT3, [(-16, 29), fac.Directions.East])
    mainFactory.addTransportTurn(coalT3, [(-10, 29), fac.Directions.South])
    mainFactory.addTransportTurn(coalT3, [(-10, 33), fac.Directions.East])
    mainFactory.addTransportTurn(coalT3, [(-5, 33), fac.Directions.South])
    mainFactory.addTransportTurn(coalT3, [(-5, 37), fac.Directions.West])
    mainFactory.addTransportTurn(coalT3, [(-11, 37), fac.Directions.South])
    mainFactory.addTransportTurn(coalT3, [(-11, 40), fac.Directions.East])
    mainFactory.addTransportTurn(coalT3, [(-1, 40), fac.Directions.South])
    mainFactory.addTransportTurn(coalT3, [(-1, 42), fac.Directions.South])

    mainFactory.addTransportTurn(ironT3, [(13, 30), fac.Directions.West])
    mainFactory.addTransportTurn(ironT3, [(9, 30), fac.Directions.South])
    mainFactory.addTransportTurn(ironT3, [(9, 34), fac.Directions.East])
    mainFactory.addTransportTurn(ironT3, [(12, 34), fac.Directions.South])
    mainFactory.addTransportTurn(ironT3, [(12, 38), fac.Directions.West])
    mainFactory.addTransportTurn(ironT3, [(5, 38), fac.Directions.South])
    mainFactory.addTransportTurn(ironT3, [(5, 40), fac.Directions.West])
    mainFactory.addTransportTurn(ironT3, [(0, 40), fac.Directions.South])
    mainFactory.addTransportTurn(ironT3, [(0, 42), fac.Directions.South])

    mainFactory.addTransportTurn(steelT3, [(-1, 45), fac.Directions.South])
    mainFactory.addTransportTurn(steelT3, [(-1, 47), fac.Directions.East])
    mainFactory.addTransportTurn(steelT3, [(5, 47), fac.Directions.South])
    mainFactory.addTransportTurn(steelT3, [(5, 50), fac.Directions.West])
    mainFactory.addTransportTurn(steelT3, [(0, 50), fac.Directions.South])
    mainFactory.addTransportTurn(steelT3, [(0, 53), fac.Directions.South])
    
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