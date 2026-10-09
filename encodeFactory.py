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

def checkTransportConnections(factory, transportid):
    transport = factory.transports[transportid]

    directionOffsets = {
        fac.Directions.North: (0, -1),
        fac.Directions.East: (1, 0),
        fac.Directions.South: (0, 1),
        fac.Directions.West: (-1, 0)
    }

    dx, dy = directionOffsets[transport.initialDirection]
    start = transport.turns[0][0]
    pos = (start[0] - dx, start[1] - dy)
    checkComponentAt(factory, transportid, pos)

    dx, dy = directionOffsets[transport.finalDirection]
    end = transport.turns[-1][0]
    pos = (end[0] + dx, end[1] + dy)
    checkComponentAt(factory, transportid, pos)

def checkComponentAt(factory, transportid, pos):
    componentid = dec.visibleComponentsAt.get(pos)

    if componentid is None:
        return

    if componentid in factory.machines:
        checkAndConnectComponent(factory, componentid, transportid)

    elif componentid in factory.inventories:
        checkAndConnectComponent(factory, componentid, transportid)

    elif componentid in factory.producers:
        checkAndConnectComponent(factory, componentid, transportid)

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
    
    directionOffsets = {
        fac.Directions.East: (1, 0),
        fac.Directions.West: (-1, 0),
        fac.Directions.North: (0, -1),
        fac.Directions.South: (0, 1)
    }

    if flip[1]:  # YOUR Y-axis mirror = left/right
        if orientation is fac.Directions.East:
            orientation = fac.Directions.West
        elif orientation is fac.Directions.West:
            orientation = fac.Directions.East

    if flip[0]:
        if orientation is fac.Directions.North:
            orientation = fac.Directions.South
        elif orientation is fac.Directions.South:
            orientation = fac.Directions.North

    if bent:
        flipped = flip[0] ^ flip[1]
        turnAmount = -90 if flipped else 90
        bendDirection = fac.Directions((orientation.value + turnAmount) % 360)
    else:
        bendDirection = orientation

    # check behind the placed conveyor
    dx, dy = directionOffsets[orientation]
    pos = (worldPos[0] - dx, worldPos[1] - dy)
    transp = dec.visibleTransportsAt.get(pos)

    if transp is not None:
        existing = factory.transports[transp]
        turns = existing.turns

        print("BEHIND")
        print("existing final:", existing.finalDirection)
        print("new incoming:", orientation)
        print("flip:", flip)
        print("bent:", bent)
        print("bend outgoing:", bendDirection)

        if turns[-1][0] == pos and transport.type == existing.type and existing.finalDirection is orientation:
            extendForward = True
            id1 = transp

            if len(turns) == 1:
                shouldAddForward = True
            else:
                incomingDirection = directionBetween(turns[-2][0], turns[-1][0])
                shouldAddForward = existing.finalDirection is not incomingDirection

    # check in front of the placed conveyor
    # for a bend, 'front' is bendDirection
    dx, dy = directionOffsets[bendDirection]
    pos = (worldPos[0] + dx, worldPos[1] + dy)
    transp = dec.visibleTransportsAt.get(pos)

    if transp is not None:
        existing = factory.transports[transp]
        turns = existing.turns
        
        print("FRONT")
        print("existing initial:", existing.initialDirection)
        print("new outgoing:", bendDirection)
        print("flip:", flip)
        print("bent:", bent)
        print("incoming:", orientation)

        if turns[0][0] == pos and transport.type == existing.type and existing.initialDirection is bendDirection:
            extendBackward = True
            id2 = transp

            if len(turns) == 1:
                shouldAddBackward = True
            else:
                outgoingDirection = directionBetween(turns[0][0], turns[1][0])
                shouldAddBackward = existing.initialDirection is not outgoingDirection

    resultTransportId = None

    if extendBackward and extendForward:
        dec.destroyTransportSprites(id1)
        dec.destroyTransportSprites(id2)

        factory.connectTransports(id1, id2, worldPos, bent, bendDirection)
        dec._decodeFactoryComponent(factory, id1)

        resultTransportId = id1

    elif extendBackward:
        transportToExtend = factory.transports[id2]

        if shouldAddBackward:
            turnDirection = bendDirection if bent else orientation
            transportToExtend.turns.insert(0, [worldPos, turnDirection])
            transportToExtend.initialDirection = orientation
            factory.updateTransport(id2, length=factory.calculateTransportLength(id2))

        else:
            factory.extendTransportTurn(id2, 1, False)

            if bent:
                pos = transportToExtend.turns[0][0]
                transportToExtend.turns[0] = [pos, bendDirection]
                transportToExtend.initialDirection = orientation

        resultTransportId = id2

    elif extendForward:
        if shouldAddForward:
            factory.addTransportTurn(id1, [worldPos, orientation])

            if bent:
                factory.changeTransportTurn(id1, [None, bendDirection], True)

        else:
            factory.extendTransportTurn(id1, 1, True)

            if bent:
                factory.changeTransportTurn(id1, [None, bendDirection], True)

        resultTransportId = id1

    else:
        resultTransportId = factory.addTransport(transport)
        factory.addTransportTurn(resultTransportId, [worldPos, orientation])

        if bent:
            factory.changeTransportTurn(resultTransportId, [None, bendDirection], True)
    
    checkTransportConnections(factory, resultTransportId)

def rotateMatrix(matrix, rotations):
    rotations %= 4

    for _ in range(rotations):
        matrix = [list(row) for row in zip(*matrix[::-1])]

    return matrix

def flipMatrixX(matrix):
    return [row[::-1] for row in matrix]

def flipMatrixY(matrix):
    return matrix[::-1]

def connectComponent(factory: fac.Factory, component: any, componentid: int, transportid: int, isInput: bool):
    if componentid in factory.machines:
        if isInput:
            if component.input is None:
                component.input = [transportid]
            elif transportid not in component.input:
                component.input.append(transportid)
        else:
            component.output = transportid

    elif componentid in factory.producers:
        if component.output is None:
            component.output = [transportid]
        elif transportid not in component.output:
            component.output.append(transportid)

    elif componentid in factory.inventories:
        if isInput:
            if component.input is None:
                component.input = [transportid]
            elif transportid not in component.input:
                component.input.append(transportid)
        else:
            if component.output is None:
                component.output = [transportid]
            elif transportid not in component.output:
                component.output.append(transportid)

def checkAndConnectComponent(factory: fac.Factory, componentid: int, transportid: int):
    component = None
    
    if componentid in factory.machines:
        component = factory.machines[componentid]
        
    elif componentid in factory.producers:
        component = factory.producers[componentid]
        
    elif componentid in factory.inventories:
        component = factory.inventories[componentid]
        
    if component is None:
        raise BaseException("component is lowk none")
        
    transport = factory.transports[transportid]
    
    componentIO = None
    
    if isinstance(component, fac.Machine):
        if component.size == (2, 2):
            componentIO = [
                [1, 1],
                [-1, 0]
            ]
            print("firnace")
            
        elif component.size == (3, 2):
            componentIO = [
                [1, 1, 1],
                [0, -1, 0]
            ]
    
    elif isinstance(component, fac.Producer):
        if component.size == (2, 2):
            componentIO = [
                [0, 0],
                [-1, 0]
            ]
            
    elif isinstance(component, fac.Inventory):
        if component.size == (2, 2):
            componentIO = [
                [1, 0],
                [0, 0]
            ]
    
    if componentIO is None:
        raise BaseException("component io is lowk none")

    componentIO = rotateMatrix(componentIO, component.rotation.value // 90)

    if component.flipped[0]:
        componentIO = flipMatrixX(componentIO)

    if component.flipped[1]:
        componentIO = flipMatrixY(componentIO)

    portDirection = fac.Directions((fac.Directions.South.value + component.rotation.value) % 360)

    if component.flipped[0]:
        if portDirection is fac.Directions.East:
            portDirection = fac.Directions.West
        elif portDirection is fac.Directions.West:
            portDirection = fac.Directions.East

    if component.flipped[1]:
        if portDirection is fac.Directions.North:
            portDirection = fac.Directions.South
        elif portDirection is fac.Directions.South:
            portDirection = fac.Directions.North

    directionOffsets = {
        fac.Directions.North: (0, -1),
        fac.Directions.East: (1, 0),
        fac.Directions.South: (0, 1),
        fac.Directions.West: (-1, 0)
    }

    dx, dy = directionOffsets[portDirection]

    for y, row in enumerate(componentIO):
        for x, port in enumerate(row):
            if port == 0:
                continue

            componentPortPos = (component.position[0] + x, component.position[1] + y)

            if port == 1:
                transportPos = (componentPortPos[0] - dx, componentPortPos[1] - dy)

                if transport.turns[-1][0] == transportPos and transport.finalDirection is portDirection:
                    connectComponent(factory, component, componentid, transportid, True)
                    
            elif port == -1:
                transportPos = (componentPortPos[0] + dx, componentPortPos[1] + dy)

                if transport.turns[0][0] == transportPos and transport.initialDirection is portDirection:
                    connectComponent(factory, component, componentid, transportid, False)
    