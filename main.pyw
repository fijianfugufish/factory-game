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
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class ConveyorBelt(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, bent = False, **kwargs):
        super().__init__(x, y, w = 1 * 64, h = 1 * 64, **kwargs)
        
        if bent:
            self.addAnimation("move", *ConveyorTurnFrames)
        else:
            self.addAnimation("move", *ConveyorStraightFrames)
            
        self.startAnimation("move", 12)
        self.id = id
        
        self.worldPos = worldPos
        self.significant = False

class Furnace(pygameui.Sprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class Box(pygameui.Sprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        
        self.worldPos = worldPos

class Item(pygameui.Sprite):
    def __init__(self, x, y, item, **kwargs):
        super().__init__(x, y, w = 0.5 * 64, h = 0.5 * 64, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.item = item
        
def worldToSreen(worldPos):
    return worldPos[0] * 64, worldPos[1] * 64,

def decodeFactoryComponent(factory: fac.Factory, id):
    # component to decode is a transport type
    if id in factory.transports:
        transport = factory.transports[id]
        
        previousPos = (0, 0)
        previousDirection = fac.Directions.North
        
        for i, turns in enumerate(transport.turns):
            length = 0
            turnPos = turns[0]
            turnDir = turns[1] if len(turns) > 1 else previousDirection
            
            bent = None
            
            # check next direction to see if it lines up, only for the first and last transport
            numTurns = len(transport.turns)
            if (i == numTurns - 1 or i == 0) and numTurns > 1:
                # check next position if first transport, else check previous
                if i == 0:
                    nextPos = transport.turns[i + 1][0] 

                    dx = nextPos[0] - turnPos[0]
                    dy = nextPos[1] - turnPos[1]

                    if dx > 0:
                        nextDirection = fac.Directions.East
                    elif dx < 0:
                        nextDirection = fac.Directions.West
                    elif dy > 0:
                        nextDirection = fac.Directions.South
                    elif dy < 0:
                        nextDirection = fac.Directions.North
                    
                    bent = transport.initialDirection is not nextDirection
                else:
                    bent = transport.finalDirection is not previousDirection
                
            # make sure transport is a known type and place significant transports
            if transport.type == "ConveyorBelt":
                position = worldToSreen(turnPos)
                
                # check if first transport should bend
                if bent is not None:
                    conveyor = ConveyorBelt(position[0], position[1], id, turnPos, bent = bent)
                    conveyor.rotation = previousDirection.value if bent else turnDir.value
                else:
                    conveyor = ConveyorBelt(position[0], position[1], id, turnPos, bent = True)
                    conveyor.rotation = previousDirection.value
            else:
                assert ValueError, "unknown transport type"
            
            # find length and direction between significant points
            deltaX = turnPos[0] - previousPos[0]
            deltaY = turnPos[1] - previousPos[1]

            dx = abs(deltaX)
            dy = abs(deltaY)

            xDirection = 1 if deltaX > 0 else -1
            yDirection = 1 if deltaY > 0 else -1
            
            length += dx + dy
            
            # place conveyors between significant transports
            for j in range(length - 1):
                if dx > 0:
                    pos = (previousPos[0] + (j + 1) * xDirection, previousPos[1])
                elif dy > 0:
                    pos = (previousPos[0], previousPos[1] + (j + 1) * yDirection)

                screenPos = worldToSreen(pos)
                
                # make sure transport is a known type
                if transport.type == "ConveyorBelt":
                    conveyor = ConveyorBelt(screenPos[0], screenPos[1], id, pos)
                    conveyor.rotation = previousDirection.value
                else:
                    assert ValueError, "unknown transport type"
            
            previousDirection = turnDir
            previousPos = turnPos

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
    mainFactory.addTransportTurn(conveyor1, [(5, 2), fac.Directions.South])
    
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