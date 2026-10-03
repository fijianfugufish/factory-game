from pygame import *
import factory as fac
from copy import copy
from math import dist

winx = 1100
winy = 750

window = display.set_mode((winx, winy))
display.set_caption("factory game")

# must import after display initialisation due to pygames convert() requiring it
import pygameui

lastCameraPos = [0, 0]
cameraPos = [0, 0] # measured in world pos
renderDistance = 3

visibleTransports: set[int] = set()
visibleMachines: set[int] = set()
visibleProducers: set[int] = set()
visibleInventories: set[int] = set()
visibleItems: dict[int, "Item"] = {}
visibleSprites: list[pygameui.Sprite] = []
componentSprites: dict[tuple[str, int], list[pygameui.Sprite]] = {}
visibleTransportSprites: dict[tuple[int, tuple], pygameui.Sprite] = {}

_DrillFrames = [image.load(f"Images/Drill/Drill{i}.png").convert_alpha() for i in range(1, 7)]

_FurnaceFrames = [image.load(f"Images/Furnace/Furnace{i}.png").convert_alpha() for i in range(1, 7)]

_ConveyorStraightFrames = [image.load(f"Images/Conveyorbelt/ConveyorStraight/ConveyorStraight{i}.png").convert_alpha() for i in range(1, 9)]
_ConveyorTurnFrames =     [image.load(f"Images/Conveyorbelt/ConveyorTurn/ConveyorTurn{i}.png").convert_alpha() for i in range(1, 9)]

_CoalSprite = image.load(f"Images/Ore/Coal.png").convert_alpha()
_IronOreSprite = image.load(f"Images/Ore/IronOre.png").convert_alpha()

_SteelIngotSprite = image.load(f"Images/Ingot/SteelIngot.png").convert_alpha()

class Drill(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        self.addAnimation("drill", *_DrillFrames)
        self.startAnimation("drill", 8)
        self.id = id
        self.z = 1
        
        self.worldPos = worldPos

class ConveyorBelt(pygameui.AnimatableSprite):    
    def __init__(self, x, y, id, worldPos, speed, bent = False, **kwargs):
        super().__init__(x, y, w = 1 * 64, h = 1 * 64, **kwargs)
        
        if bent:
            self.addAnimation("move", *_ConveyorTurnFrames)
        else:
            self.addAnimation("move", *_ConveyorStraightFrames)
            
        self.startAnimation("move", speed * 8)
        self.id = id
        
        self.worldPos = worldPos
        self.significant = False
        
class Furnace(pygameui.AnimatableSprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        self.addAnimation("cook", *_FurnaceFrames)
        self.startAnimation("cook", 10)
        self.id = id
        self.z = 1
        
        self.worldPos = worldPos

class Box(pygameui.Sprite):
    def __init__(self, x, y, id, worldPos, **kwargs):
        super().__init__(x, y, w = 2 * 64, h = 2 * 64, **kwargs)
        
        #self.addAnimation("move", *ConveyorStraightFrames)
        self.id = id
        self.z = 1
        
        self.worldPos = worldPos

class Item(pygameui.Sprite):
    def __init__(self, x, y, item, **kwargs):
        super().__init__(x, y, w = 0.5 * 64, h = 0.5 * 64, **kwargs)
        
        match item:
            case fac.Items.Coal:
                self.image = _CoalSprite
            case fac.Items.IronOre:
                self.image = _IronOreSprite
            case fac.Items.SteelIngot:
                self.image = _SteelIngotSprite
        
        self.item = item

def lerp(start, end, t):
    return start + (end - start) * t

def worldToSreen(worldPos):
    screenx = (worldPos[0] - cameraPos[0]) * 64
    screeny = (worldPos[1] - cameraPos[1]) * 64
    return (screenx, screeny)

def isOffscreen(pos):
    tolerance = renderDistance * 64
    
    if pos[0] < -tolerance or pos[0] > winx + tolerance:
        return True
    if pos[1] < -tolerance or pos[1] > winy + tolerance:
        return True
    
    return False

def positionCamera(pos):
    global cameraPos
    cameraPos = pos

def moveCameraUp(amount):
    cameraPos[1] -= amount

def moveCameraDown(amount):
    cameraPos[1] += amount

def moveCameraLeft(amount):
    cameraPos[0] -= amount

def moveCameraRight(amount):
    cameraPos[0] += amount

def _addComponentSprite(kind, id, sprite):
    visibleSprites.append(sprite)

    key = (kind, id)

    if key not in componentSprites:
        componentSprites[key] = []

    componentSprites[key].append(sprite)


def _destroyComponentSprites(kind, id):
    key = (kind, id)

    if key not in componentSprites:
        return

    for sprite in componentSprites[key]:
        sprite.destroy()

        if sprite in visibleSprites:
            visibleSprites.remove(sprite)

    del componentSprites[key]

def _addTransportSprite(transport, worldPos, sprite):
    key = (transport.id, worldPos)

    if key in visibleTransportSprites:
        return

    visibleTransportSprites[key] = sprite
    visibleSprites.append(sprite)

def _unloadOffscreenTransportSprites():
    for key, sprite in list(visibleTransportSprites.items()):

        if isOffscreen(worldToSreen(sprite.worldPos)):
            sprite.destroy()

            if sprite in visibleSprites:
                visibleSprites.remove(sprite)

            del visibleTransportSprites[key]

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
            position = worldToSreen(turnPos)
            key = (transport.id, turnPos)
            
            if not isOffscreen(position) and key not in visibleTransportSprites:
                if transport.type == "ConveyorBelt":
                    
                    # check if first or last transport should bend
                    if bent is not None:
                        conveyor = ConveyorBelt(position[0], position[1], id, turnPos, speed = transport.speed, bent = bent)
                        conveyor.rotation = previousDirection.value if bent else turnDir.value
                    else:
                        conveyor = ConveyorBelt(position[0], position[1], id, turnPos, speed = transport.speed, bent = True)
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
                    
                    # add to visible sprite list
                    _addTransportSprite(transport, turnPos, conveyor)
                else:
                    raise ValueError("unknown transport type")
            
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
                key = (transport.id, pos)
                
                # make sure transport is a known type
                if not isOffscreen(screenPos) and key not in visibleTransportSprites:
                    if transport.type == "ConveyorBelt":
                        conveyor = ConveyorBelt(screenPos[0], screenPos[1], id, pos, speed = transport.speed)
                        conveyor.rotation = previousDirection.value
                        _addTransportSprite(transport, pos, conveyor)
                    else:
                        raise ValueError("unknown transport type")
            
            previousDirection = turnDir
            previousPos = turnPos
    
    # decode for producers
    elif id in factory.producers:
        producer = factory.producers[id]
        pos = producer.position
        
        screenPos = worldToSreen(pos)
        
        # ensure producer is a known type
        if not isOffscreen(screenPos):
            if producer.type == "Drill":
                drill = Drill(screenPos[0], screenPos[1], id, pos)
                drill.rotation = producer.rotation.value
                _addComponentSprite("producer", id, drill)
            else:
                raise ValueError("unknown producer type")
    
    # decode for machines
    elif id in factory.machines:
        machine = factory.machines[id]
        pos = machine.position
        
        screenPos = worldToSreen(pos)
        
        # ensure machine is a known type
        if not isOffscreen(screenPos):
            if machine.type == "Furnace":
                furnace = Furnace(screenPos[0], screenPos[1], id, pos)
                furnace.rotation = machine.rotation.value
                _addComponentSprite("machine", id, furnace)
            else:
                raise ValueError("unknown producer type")
    
    # decode for machines
    elif id in factory.inventories:
        inventory = factory.inventories[id]
        pos = inventory.position
        
        screenPos = worldToSreen(pos)
        
        # ensure inventory is a known type
        if not isOffscreen(screenPos):
            if inventory.type == "Box":
                box = Box(screenPos[0], screenPos[1], id, pos)
                box.rotation = inventory.rotation.value
                _addComponentSprite("inventory", id, box)
            else:
                raise ValueError("unknown producer type")
    
    #todo change 'if x.type' it is messy and not exactly necessary

def _renderVisibleItems(factory: fac.Factory):
    global nextVisibleItemid
    
    # render items on conveyorbelts, ensuring only transports whose id is unique has their items rendered
    # this avoids unnecessary multi-rendering
    for transportid in visibleTransports:
        transport = factory.transports[transportid]
        
        for i, item in enumerate(transport.items):            
            itemType = item[0]
            itemPos = item[1] - 1
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

            t = distanceIntoSegment / segmentLength if segmentLength > 0 else 0
            
            # get world pos from the lerp and offset it to center
            itemPosWorld = (lerp(startx, endx, t) + 0.25, lerp(starty, endy, t) + 0.25)
            itemPosScreen = worldToSreen(itemPosWorld)
            
            #dont render or destroy if offcreen
            if isOffscreen(itemPosScreen): 
                if itemid in visibleItems:
                    visibleItems[itemid].destroy()
                    del visibleItems[itemid]
                    
                continue
            
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

def _findAllOnscreen(factory: fac.Factory):
    for transport in factory.transports.values():
        for turn in transport.turns:
            position = turn[0]
            offscreen = isOffscreen(worldToSreen(position))
            
            # append to list of visible transports if any significant point is onscreen
            if not offscreen and transport.id not in visibleTransports:
                visibleTransports.add(transport.id)
                break # ensure copies wont fill up the list
            elif offscreen and transport.id in visibleTransports:
                visibleTransports.remove(transport.id)
    
    for producer in factory.producers.values():
        offscreen = isOffscreen(worldToSreen(producer.position))
        if not isOffscreen(worldToSreen(producer.position)) and producer.id not in visibleProducers:
            visibleProducers.add(producer.id)
        elif offscreen and producer.id in visibleProducers:
            visibleProducers.remove(producer.id)
            _destroyComponentSprites("producer", producer.id)
    
    for machine in factory.machines.values():
        offscreen = isOffscreen(worldToSreen(machine.position))
        if not isOffscreen(worldToSreen(machine.position)) and machine.id not in visibleMachines:
            visibleMachines.add(machine.id)
        elif offscreen and machine.id in visibleMachines:
            visibleMachines.remove(machine.id)
            _destroyComponentSprites("machine", machine.id)
                
    for inventory in factory.inventories.values():
        offscreen = isOffscreen(worldToSreen(inventory.position))
        if not offscreen and inventory.id not in visibleInventories:
            visibleInventories.add(inventory.id)
        elif offscreen and inventory.id in visibleInventories:
            visibleInventories.remove(inventory.id)
            _destroyComponentSprites("inventory", inventory.id)
    
def decodeAndRender(factory: fac.Factory, moved = False, forceRender = False):
    """render all factory components onscreen"""
    global cameraPos, lastCameraPos, renderDistance
    
    render = dist(cameraPos, lastCameraPos) >= renderDistance
    
    if render or forceRender:
        _findAllOnscreen(factory)
            
        for producerid in visibleProducers:
            if ("producer", producerid) not in componentSprites:
                _decodeFactoryComponent(factory, producerid)
            
        for machineid in visibleMachines:
            if ("machine", machineid) not in componentSprites:
                _decodeFactoryComponent(factory, machineid)
        
        for inventoryid in visibleInventories:
            if ("inventory", inventoryid) not in componentSprites:
                _decodeFactoryComponent(factory, inventoryid)
        
        lastCameraPos = copy(cameraPos)
    
    # check if camera moved, move everything
    if moved:
        _unloadOffscreenTransportSprites()
        
        for transport in factory.transports.values():
            _decodeFactoryComponent(factory, transport.id)
        
        for component in visibleSprites:
            component.x, component.y = worldToSreen(component.worldPos)
    
    _renderVisibleItems(factory)