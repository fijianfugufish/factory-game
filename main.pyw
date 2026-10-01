from pygame import *
import pygameui
import factory as fac

winx = 1100
winy = 750

font.init()

window = display.set_mode((winx, winy))
display.set_caption("factory game")

ConveyorStraightFrames = [image.load(f"Images/Conveyorbelt/ConveyorStraight/ConveyorStraight{i}.png").convert_alpha() for i in range(1, 9)]
ConveyorTurnFrames =     [image.load(f"Images/Conveyorbelt/ConveyorTurn/ConveyorTurn{i}.png").convert_alpha() for i in range(1, 9)]

class Drill(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 32, h = 32, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class ConveyorBelt(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 16, h = 16, **kwargs)
        
        self.addAnimation("move", *ConveyorStraightFrames)
        self.startAnimation("move", 12)
        self.id = id
        
        self.worldPos = worldPos
        self.significant = False

class Furnace(pygameui.Sprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 32, h = 32, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class Box(pygameui.Sprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 32, h = 32, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class Item(pygameui.Sprite):
    def __init__(self, x, y, item, **kwargs):
        super().__init__(x, y, w = 8, h = 8, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.item = id
        
def worldToSreen(worldPos):
    return worldPos[0] * 16, worldPos[1] * 16,

def decodeFactoryComponent(factory: fac.Factory, id):
    # component to decode is a transport type
    if id in factory.transports:
        transport = factory.transports[id]
        
        for turns in transport.turns:
            turnPos = turns[0]
            turnDir = turns[1] if len(turns) > 1 else fac.Directions.North
            
            if transport.type == "ConveyorBelt":
                position = worldToSreen(turnPos)
                conveyor = ConveyorBelt(position[0], position[1], id, turnPos)
                conveyor.rotation = turnDir.value

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
    drill2 = mainFactory.addProducer(fac.drill2)
    furnace = mainFactory.addMachine(fac.furnace)
    box = mainFactory.addInventory(fac.box)
    
    conveyor1 = mainFactory.addTransport(fac.conveyor)
    conveyor2 = mainFactory.addTransport(fac.conveyor)
    conveyor3 = mainFactory.addTransport(fac.conveyor)
    
    mainFactory.updateProducer(drill1, outputids = [conveyor1])
    mainFactory.updateProducer(drill2, outputids = [conveyor2])
    
    mainFactory.updateMachine(furnace, inputids = [conveyor1, conveyor2], outputid = conveyor3, recipe = fac.steelRecipe)
    
    mainFactory.updateInventory(box, inputids = [conveyor3])
    
    mainFactory.addTransportTurn(conveyor1, [(0, 0), fac.Directions.East])
    mainFactory.addTransportTurn(conveyor1, [(5, 0), fac.Directions.South])
    mainFactory.addTransportTurn(conveyor1, [(5, 2)])
    
    decodeFactoryComponent(mainFactory, conveyor1)
    
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
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()