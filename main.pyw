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

CoalSprite = image.load(f"Images/Ore/Coal.png").convert_alpha()

visibleTransports: list[fac.Transport] = []
visibleItems: dict[int, "Item"] = {}
uniqueids: list[int] = []

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
        
        visibleTransports.append(self)
        if self.id not in uniqueids: uniqueids.append(self.id)

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
        
        self.image = CoalSprite
        
        self.item = item

def lerp(start, end, t):
    return start + (end - start) * t

def worldToSreen(worldPos):
    return (worldPos[0] * 64, worldPos[1] * 64) #todo use player location to convert properly to screen space

def decodeFactoryComponent(factory: fac.Factory, id):
    # component to decode is a transport type        
    if id in factory.transports:
        # bent transports bend right, they must be flipped if they turn left
        leftTurns = {
            (fac.Directions.North, fac.Directions.West),
            (fac.Directions.West,  fac.Directions.South),
            (fac.Directions.South, fac.Directions.East),
            (fac.Directions.East,  fac.Directions.North),
        }
        
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
                
                #todo dont render if offcreen
                
                # check if first or last transport should bend
                if bent is not None:
                    conveyor = ConveyorBelt(position[0], position[1], id, turnPos, bent = bent)
                    conveyor.rotation = previousDirection.value if bent else turnDir.value
                else:
                    conveyor = ConveyorBelt(position[0], position[1], id, turnPos, bent = True)
                    conveyor.rotation = previousDirection.value
                
                # flip if needed
                if (previousDirection, turnDir) in leftTurns:
                    if previousDirection is fac.Directions.East:
                        if turnDir is fac.Directions.North:
                            conveyor.setFlipped(x = True)
                        else:
                            conveyor.setFlipped(y = True)
                    else:
                        conveyor.setFlipped(x = True)
            else:
                assert ValueError("unknown transport type")
            
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
                
                #todo dont render if offcreen
                
                # make sure transport is a known type
                if transport.type == "ConveyorBelt":
                    conveyor = ConveyorBelt(screenPos[0], screenPos[1], id, pos)
                    conveyor.rotation = previousDirection.value
                else:
                    assert ValueError, "unknown transport type"
            
            previousDirection = turnDir
            previousPos = turnPos

def renderVisibleItems(factory: fac.Factory):
    global nextVisibleItemid
    
    # render items on conveyorbelts, ensuring only transports whose id is unique has their items rendered
    # this avoids unnecessary multi-rendering
    for transport in [transp for transp in visibleTransports if transp.id in uniqueids]:
        # change reference of transport from the sprite to the actual transport in the factory
        transport = factory.transports[transport.id]
        for i, item in enumerate(transport.items):            
            itemType = item[0]
            itemPos = item[1]
            itemid = transport.itemids[i]
            
            # itemPos is recorded in 'transport space', distance along the trasport
            # lerp between key points to translate it to world space
            
            # find which two key points to lerp from
            startPoint, endPoint, segmentStartDistance = factory.calculateKeyPointsItemIsBetween(transport.id, itemPos)
            
            # find values for lerp
            startx, starty = startPoint
            endx, endy = endPoint
            dx = endx - startx
            dy = endy - starty

            segmentLength = abs(dx) + abs(dy)

            distanceIntoSegment = (itemPos / 2) - segmentStartDistance

            t = distanceIntoSegment / segmentLength
            
            # get world pos from the lerp and offset it to center
            itemPosWorld = (lerp(startx, endx, t) + 0.25, lerp(starty, endy, t) + 0.25)
            itemPosScreen = worldToSreen(itemPosWorld)
            
            #todo dont render if offcreen
            
            # instantiate visible items if it doesnt already exist visually
            if itemid not in visibleItems:
                visibleItems[itemid] = Item(itemPosScreen[0], itemPosScreen[1], itemType)
            else:
                visibleItems[itemid].x = itemPosScreen[0]
                visibleItems[itemid].y = itemPosScreen[1]
    
        # clean up visible items
        while transport.lastDestroyedid in visibleItems:
            visibleItems[transport.lastDestroyedid].destroy()
            del visibleItems[transport.lastDestroyedid]
            
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
        
        renderVisibleItems(mainFactory)
        
        drawAll(window, dt)
        
        display.flip()

if __name__ == "__main__":
    main()