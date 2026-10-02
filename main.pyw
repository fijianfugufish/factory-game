from pygame import *
import factory as fac
from decodeFactory import window, decodeAndRender, _decodeFactoryComponent
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
    furnace = mainFactory.addMachine(fac.furnace)
    
    conveyor1 = mainFactory.addTransport(fac.conveyor)
    
    mainFactory.updateProducer(drill1, outputids = [conveyor1])
    
    mainFactory.updateMachine(furnace, inputids = [conveyor1], outputid = None, recipe = fac.steelRecipe)
    
    mainFactory.addTransportTurn(conveyor1, [(1, 0), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(3, 0), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(3, 2), fac.Directions.West])
    mainFactory.addTransportTurn(conveyor1, [(1, 2), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(1, 3), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(5, 3), fac.Directions.North])
    mainFactory.addTransportTurn(conveyor1, [(5, 2), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(8, 2), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(8, 4), fac.Directions.West])
    mainFactory.addTransportTurn(conveyor1, [(6, 4), fac.Directions.North])
    
    _decodeFactoryComponent(mainFactory, conveyor1)
    
    while gameRunning:
        # main game loop
        window.fill(bgColor)
        
        dt = clock.tick(FPS) / 1000
        
        events = event.get()
        
        for e in events:
            if e.type == QUIT:
                gameRunning = False
            
            pygameui.Button.handleAllButtons(mouse.get_pos(), e.type)
        
        mainFactory.step(dt)
        
        decodeAndRender(mainFactory)
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()