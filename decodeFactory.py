from pygame import *
import factory as fac

winx = 1100
winy = 750

window = display.set_mode((winx, winy))
display.set_caption("factory game")

# must import after display initialisation due to pygames convert() requiring it
import pygameui

visibleTransports: list[fac.Transport] = []
visibleItems: dict[int, "Item"] = {}
uniqueids: list[int] = []

_DrillFrames = [image.load(f"Images/Drill/Drill{i}.png").convert_alpha() for i in range(1, 7)]

_FurnaceFrames = [image.load(f"Images/Furnace/Furnace{i}.png").convert_alpha() for i in range(1, 7)]

_ConveyorStraightFrames = [image.load(f"Images/Conveyorbelt/ConveyorStraight/ConveyorStraight{i}.png").convert_alpha() for i in range(1, 9)]
_ConveyorTurnFrames =     [image.load(f"Images/Conveyorbelt/ConveyorTurn/ConveyorTurn{i}.png").convert_alpha() for i in range(1, 9)]

_CoalSprite = image.load(f"Images/Ore/Coal.png").convert_alpha()

class Drill(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        self.addAnimation("drill", *_DrillFrames)
        self.startAnimation("drill", 8)
        self.id = id
        
        self.worldPos = worldPos

class ConveyorBelt(pygameui.AnimatableSprite):    
    def __init__(self, x, y, id, worldPos, bent = False, **kwargs):
        super().__init__(x, y, w = 1 * 64, h = 1 * 64, **kwargs)
        
        if bent:
            self.addAnimation("move", *_ConveyorTurnFrames)
        else:
            self.addAnimation("move", *_ConveyorStraightFrames)
            
        self.startAnimation("move", 12)
        self.id = id
        
        self.worldPos = worldPos
        self.significant = False
        
        visibleTransports.append(self)
        if self.id not in uniqueids: uniqueids.append(self.id)

class Furnace(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        self.addAnimation("cook", *_FurnaceFrames)
        self.startAnimation("cook", 10)
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
        
        self.image = _CoalSprite
        
        self.item = item

def lerp(start, end, t):
    return start + (end - start) * t

def worldToSreen(worldPos):
    return (worldPos[0] * 64, worldPos[1] * 64) #todo use player location to convert properly to screen space

def _decodeFactoryComponent(factory: fac.Factory, id: int):
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
        
        previousPos = None
        previousDirection = None
        
        for i, turns in enumerate(transport.turns):
            length = 0
            
            if previousPos is None and previousDirection is None:
                previousPos = turns[0]
                previousDirection = turns[1]
                
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
                # honestly trial and error to figure this out. dont touch.
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
    
    # decode for producers
    elif id in factory.producers:
        producer = factory.producers[id]
        pos = producer.position
        
        screenPos = worldToSreen(pos)
        
        # ensure producer is a known type
        if producer.type == "Drill":
            drill = Drill(screenPos[0], screenPos[1], id, pos)
            drill.rotation = producer.rotation.value
        else:
            assert ValueError, "unknown producer type"
    
    # decode for machines
    elif id in factory.machines:
        machine = factory.machines[id]
        pos = machine.position
        
        screenPos = worldToSreen(pos)
        
        # ensure machine is a known type
        if machine.type == "Furnace":
            furnace = Furnace(screenPos[0], screenPos[1], id, pos)
            furnace.rotation = machine.rotation.value
        else:
            assert ValueError, "unknown producer type"

def _renderVisibleItems(factory: fac.Factory):
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
            # 1 transport space unit is equivalent to 0.5 world space
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
           
def decodeAndRender(factory: fac.Factory):
    #todo add decode all onscreen
    _renderVisibleItems(factory)