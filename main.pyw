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
    
    # =========================
    # COMPACT STEEL FACTORY
    # =========================

    # ---- PRODUCERS ----
    coal1 = mainFactory.addProducer(fac.drill)
    iron1 = mainFactory.addProducer(fac.drill2)
    coal2 = mainFactory.addProducer(fac.drill)
    iron2 = mainFactory.addProducer(fac.drill2)

    coal3 = mainFactory.addProducer(fac.drill)
    iron3 = mainFactory.addProducer(fac.drill2)
    coal4 = mainFactory.addProducer(fac.drill)
    iron4 = mainFactory.addProducer(fac.drill2)

    # ---- FURNACES ----
    furnace1 = mainFactory.addMachine(fac.furnace)
    furnace2 = mainFactory.addMachine(fac.furnace)
    furnace3 = mainFactory.addMachine(fac.furnace)
    furnace4 = mainFactory.addMachine(fac.furnace)

    # ---- BOXES ----
    box1 = mainFactory.addInventory(fac.box)
    box2 = mainFactory.addInventory(fac.box)
    box3 = mainFactory.addInventory(fac.box)
    box4 = mainFactory.addInventory(fac.box)


    # =========================
    # POSITIONS
    # =========================

    # top row
    mainFactory.updateProducer(coal1, position=(1,1), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron1, position=(10,1), rotation=fac.Directions.East)

    mainFactory.updateProducer(coal2, position=(13,1), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron2, position=(22,1), rotation=fac.Directions.East)

    # bottom row
    mainFactory.updateProducer(coal3, position=(1,12), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron3, position=(10,12), rotation=fac.Directions.East)

    mainFactory.updateProducer(coal4, position=(13,12), rotation=fac.Directions.West)
    mainFactory.updateProducer(iron4, position=(22,12), rotation=fac.Directions.East)

    # furnaces packed in centre
    mainFactory.updateMachine(furnace1, position=(5,6), rotation=fac.Directions.North)
    mainFactory.updateMachine(furnace2, position=(17,6), rotation=fac.Directions.North)

    mainFactory.updateMachine(furnace3, position=(5,17), rotation=fac.Directions.North)
    mainFactory.updateMachine(furnace4, position=(17,17), rotation=fac.Directions.North)

    # output boxes
    mainFactory.updateInventory(box1, position=(5,10))
    mainFactory.updateInventory(box2, position=(17,10))

    mainFactory.updateInventory(box3, position=(5,21))
    mainFactory.updateInventory(box4, position=(17,21))


    # =========================
    # TRANSPORTS
    # =========================

    coalT1 = mainFactory.addTransport(fac.conveyor)
    ironT1 = mainFactory.addTransport(fac.conveyor)
    steelT1 = mainFactory.addTransport(fac.conveyor)

    coalT2 = mainFactory.addTransport(fac.conveyor)
    ironT2 = mainFactory.addTransport(fac.conveyor)
    steelT2 = mainFactory.addTransport(fac.conveyor)

    coalT3 = mainFactory.addTransport(fac.conveyor)
    ironT3 = mainFactory.addTransport(fac.conveyor)
    steelT3 = mainFactory.addTransport(fac.conveyor)

    coalT4 = mainFactory.addTransport(fac.conveyor)
    ironT4 = mainFactory.addTransport(fac.conveyor)
    steelT4 = mainFactory.addTransport(fac.conveyor)


    # =========================
    # CONNECTIONS
    # =========================

    mainFactory.updateProducer(coal1, outputids=[coalT1])
    mainFactory.updateProducer(iron1, outputids=[ironT1])
    mainFactory.updateMachine(furnace1, inputids=[coalT1,ironT1], outputid=steelT1, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box1, inputids=[steelT1])

    mainFactory.updateProducer(coal2, outputids=[coalT2])
    mainFactory.updateProducer(iron2, outputids=[ironT2])
    mainFactory.updateMachine(furnace2, inputids=[coalT2,ironT2], outputid=steelT2, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box2, inputids=[steelT2])

    mainFactory.updateProducer(coal3, outputids=[coalT3])
    mainFactory.updateProducer(iron3, outputids=[ironT3])
    mainFactory.updateMachine(furnace3, inputids=[coalT3,ironT3], outputid=steelT3, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box3, inputids=[steelT3])

    mainFactory.updateProducer(coal4, outputids=[coalT4])
    mainFactory.updateProducer(iron4, outputids=[ironT4])
    mainFactory.updateMachine(furnace4, inputids=[coalT4,ironT4], outputid=steelT4, recipe=fac.steelRecipe)
    mainFactory.updateInventory(box4, inputids=[steelT4])


    # =========================
    # TOP LEFT CELL
    # =========================

    mainFactory.addTransportTurn(coalT1, [(3,2), fac.Directions.East])
    mainFactory.addTransportTurn(coalT1, [(5,2), fac.Directions.South])
    mainFactory.addTransportTurn(coalT1, [(5,5), fac.Directions.South])

    mainFactory.addTransportTurn(ironT1, [(9,2), fac.Directions.West])
    mainFactory.addTransportTurn(ironT1, [(6,2), fac.Directions.South])
    mainFactory.addTransportTurn(ironT1, [(6,5), fac.Directions.South])

    mainFactory.addTransportTurn(steelT1, [(5,8), fac.Directions.South])
    mainFactory.addTransportTurn(steelT1, [(5,9), fac.Directions.South])


    # =========================
    # TOP RIGHT CELL
    # =========================

    mainFactory.addTransportTurn(coalT2, [(15,2), fac.Directions.East])
    mainFactory.addTransportTurn(coalT2, [(17,2), fac.Directions.South])
    mainFactory.addTransportTurn(coalT2, [(17,5), fac.Directions.South])

    mainFactory.addTransportTurn(ironT2, [(21,2), fac.Directions.West])
    mainFactory.addTransportTurn(ironT2, [(18,2), fac.Directions.South])
    mainFactory.addTransportTurn(ironT2, [(18,5), fac.Directions.South])

    mainFactory.addTransportTurn(steelT2, [(17,8), fac.Directions.South])
    mainFactory.addTransportTurn(steelT2, [(17,9), fac.Directions.South])


    # =========================
    # BOTTOM LEFT CELL
    # =========================

    mainFactory.addTransportTurn(coalT3, [(3,13), fac.Directions.East])
    mainFactory.addTransportTurn(coalT3, [(5,13), fac.Directions.South])
    mainFactory.addTransportTurn(coalT3, [(5,16), fac.Directions.South])

    mainFactory.addTransportTurn(ironT3, [(9,13), fac.Directions.West])
    mainFactory.addTransportTurn(ironT3, [(6,13), fac.Directions.South])
    mainFactory.addTransportTurn(ironT3, [(6,16), fac.Directions.South])

    mainFactory.addTransportTurn(steelT3, [(5,19), fac.Directions.South])
    mainFactory.addTransportTurn(steelT3, [(5,20), fac.Directions.South])


    # =========================
    # BOTTOM RIGHT CELL
    # =========================

    mainFactory.addTransportTurn(coalT4, [(15,13), fac.Directions.East])
    mainFactory.addTransportTurn(coalT4, [(17,13), fac.Directions.South])
    mainFactory.addTransportTurn(coalT4, [(17,16), fac.Directions.South])

    mainFactory.addTransportTurn(ironT4, [(21,13), fac.Directions.West])
    mainFactory.addTransportTurn(ironT4, [(18,13), fac.Directions.South])
    mainFactory.addTransportTurn(ironT4, [(18,16), fac.Directions.South])

    mainFactory.addTransportTurn(steelT4, [(17,19), fac.Directions.South])
    mainFactory.addTransportTurn(steelT4, [(17,20), fac.Directions.South])
    
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
        
        decodeAndRender(mainFactory, dt = dt, moved = moved)
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()