from pygame import *
import factory as fac
import decodeFactory as dec

def placeComponent(factory: fac.Factory, component, worldPos: tuple[int, int], orientation: fac.Directions, flip: tuple[bool, bool], bent = False):
    """validates and encodes components based on how they were placed"""
    
    # check component type
    match component:
        case fac.Transport():
            print("placing transport")
            validateAndEncodeTransport(factory, component, worldPos, orientation, flip, bent)
        
        case fac.Producer():
            ...
        case fac.Machine():
            ... 
        case fac.Inventory():
            ...
        case _:
            raise ValueError(f"unknown component type {component!r}")

def directionBetween(pos1, pos2):
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]

    if dx > 0:
        return fac.Directions.East
    elif dx < 0:
        return fac.Directions.West
    elif dy > 0:
        return fac.Directions.South
    elif dy < 0:
        return fac.Directions.North

def validateAndEncodeTransport(factory: fac.Factory, transport, 
                               worldPos: tuple[int, int], orientation: fac.Directions,
                               flip: tuple[bool, bool], bent: bool):
    extendForward = False
    extendBackward = False
    id1 = None
    id2 = None
    
    shouldAddForward = False
    shouldAddBackward = False
    
    # check for collisions
    if worldPos in dec.occupiedSpaces: 
        print("occupied")
        return
    
    # change orientation to account for flip
    if flip[0]:
        if orientation is fac.Directions.North:
            orientation = fac.Directions.South
        elif orientation is fac.Directions.South:
            orientation = fac.Directions.North
    if flip[1]:
        if orientation is fac.Directions.West:
            orientation = fac.Directions.East
        elif orientation is fac.Directions.East:
            orientation = fac.Directions.West
    
    directionOffsets = {
        fac.Directions.East: (1, 0),
        fac.Directions.West: (-1, 0),
        fac.Directions.North: (0, -1),
        fac.Directions.South: (0, 1)
    }

    dx, dy = directionOffsets[orientation]

    # check for extending at the end
    pos = (worldPos[0] - dx, worldPos[1] - dy)
    transp = dec.visibleTransportsAt.get(pos)

    if transp is not None:
        existing = factory.transports[transp]
        turns = existing.turns

        if turns[-1][0] == pos and transport.type == existing.type and existing.finalDirection is orientation:
            extendForward = True
            id1 = transp

            if len(turns) == 1:
                shouldAddForward = True
            else:
                incomingDirection = directionBetween(turns[-2][0], turns[-1][0])
                shouldAddForward = existing.finalDirection is not incomingDirection

    # check for extending at the start
    pos = (worldPos[0] + dx, worldPos[1] + dy)
    transp = dec.visibleTransportsAt.get(pos)

    if transp is not None:
        existing = factory.transports[transp]
        turns = existing.turns

        if turns[0][0] == pos and transport.type == existing.type and existing.initialDirection is orientation:
            extendBackward = True
            id2 = transp

            if len(turns) == 1:
                shouldAddBackward = True
            else:
                outgoingDirection = directionBetween(turns[0][0], turns[1][0])
                shouldAddBackward = existing.initialDirection is not outgoingDirection
    
    bentSign = 1 if flip[0] else -1
                  
    if extendBackward and extendForward:
        factory.connectTransports(id1, id2)
        return
    
    elif extendBackward:
        if shouldAddBackward:
            transportToExtend = factory.transports[id2]
            transportToExtend.turns.insert(0, [worldPos, orientation])
            transportToExtend.initialDirection = orientation
            factory.updateTransport(id2, length=factory.calculateTransportLength(id2))
            
            if bent:
                orientation = fac.Directions((orientation.value - (90 * bentSign)) % 360)
                factory.transports[id2].initialDirection = orientation
            
            return
        
        factory.extendTransportTurn(id2, 1, False)
        
        if bent:
            orientation = fac.Directions((orientation.value - (90 * bentSign)) % 360)
            factory.changeTransportTurn(id2, [None, orientation], False)
            
        return
    
    elif extendForward:
        if shouldAddForward:
            factory.addTransportTurn(id1, [worldPos, orientation])
            
            if bent:
                orientation = fac.Directions((orientation.value + (90 * bentSign)) % 360)
                factory.changeTransportTurn(id1, [None, orientation], True)
                
            return
        
        factory.extendTransportTurn(id1, 1, True)
        
        if bent:
            orientation = fac.Directions((orientation.value + (90 * bentSign)) % 360)
            factory.changeTransportTurn(id1, [None, orientation], True)
            print("im so bent yo")
            
        return
    
    # if no connections, create a new transport
    newTransport = factory.addTransport(transport)
    factory.addTransportTurn(newTransport, [worldPos, orientation])

    if bent:
        newDirection = fac.Directions((orientation.value + (90 * bentSign)) % 360)
        factory.changeTransportTurn(newTransport, [None, newDirection], True)
    
def encodeMachine(factory):...
    

def encodeProducer(factory):...
    

def encodeInventory(factory):...
    