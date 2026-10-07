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
    
    # case transport should be extended at the end
    match orientation:
        case fac.Directions.West:
            # west case
            pos = (worldPos[0] + 1, worldPos[1])

            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[-1][1] is not turns[-2][1]):
                    shouldAddForward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.East:
            # east case
            pos = (worldPos[0] - 1, worldPos[1])
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[-1][1] is not turns[-2][1]):
                    shouldAddForward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.North:
            # north case
            pos = (worldPos[0], worldPos[1] + 1)
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[-1][1] is not turns[-2][1]):
                    shouldAddForward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.South:
            # south case
            pos = (worldPos[0], worldPos[1] - 1)
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[-1][1] is not turns[-2][1]):
                    shouldAddForward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

    # case transport should be extended at the start
    match orientation:
        case fac.Directions.West:
            # west case
            pos = (worldPos[0] - 1, worldPos[1])
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[0][1] is not turns[1][1]):
                    shouldAddBackward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.East:
            # east case
            pos = (worldPos[0] + 1, worldPos[1])
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[0][1] is not turns[1][1]):
                    shouldAddBackward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.North:
            # north case
            pos = (worldPos[0], worldPos[1] - 1)
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[0][1] is not turns[1][1]):
                    shouldAddBackward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp

        case fac.Directions.South:
            # south case
            pos = (worldPos[0], worldPos[1] + 1)
            transp = dec.visibleTransportsAt.get(pos)

            if transp is not None:
                turns = factory.transports[transp].turns

                if len(turns) == 1 or (len(turns) > 1 and turns[0][1] is not turns[1][1]):
                    shouldAddBackward = True

                if turns[-1][0] == pos and transport.type == factory.transports[transp].type and factory.transports[transp].finalDirection is orientation:
                    extendForward = True
                    id1 = transp
    
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
            return
        
        factory.extendTransportTurn(id2, 1, False)
        
        if bent:
            orientation = fac.Directions((orientation.value + (90 * bentSign)) % 360)
            factory.changeTransportTurn(id2, [None, orientation], False)
        return
    
    elif extendForward:
        if shouldAddForward:
            factory.addTransportTurn(id1, [worldPos, orientation])
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
    
def encodeMachine(factory):...
    

def encodeProducer(factory):...
    

def encodeInventory(factory):...
    