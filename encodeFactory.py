from pygame import *
import factory as fac
import decodeFactory as dec

def placeComponent(factory: fac.Factory, component, worldPos: tuple[int, int], orientation: fac.Directions, flip: tuple[bool, bool], bent = False):
    """validates and encodes components based on how they were placed"""
    
    # check component type
    match component:
        case fac.Transport():
            _validateAndEncodeTransport(factory, component, worldPos, orientation, flip, bent)

        case fac.Producer():
            _validateAndEncodeComponent(factory, component, worldPos, orientation, flip)

        case fac.Machine():
            _validateAndEncodeComponent(factory, component, worldPos, orientation, flip)

        case fac.Inventory():
            _validateAndEncodeComponent(factory, component, worldPos, orientation, flip)
        
        case fac.Router():
            _validateAndEncodeComponent(factory, component, worldPos, orientation, flip)

        case _:
            raise ValueError(f"unknown component type {component!r}")

def deleteAt(factory, worldPos):
    if worldPos in dec.visibleTransportsAt:
        _deleteTransportAt(factory, worldPos)
        return

    if worldPos in dec.visibleComponentsAt:
        _deleteComponent(factory, worldPos)

def _deleteTransportAt(factory, worldPos):
    transportid = dec.visibleTransportsAt.get(worldPos)

    if transportid is None:
        return

    dec.destroyTransportSprites(transportid)

    id1, id2, destroyedItemids = factory.splitTransport(transportid, worldPos)

    # destroy items that were standing on deleted conveyor
    for itemid in destroyedItemids:
        sprite = dec.visibleItems.pop(itemid, None)

        if sprite is not None:
            sprite.destroy()

    # redraw and connect both remaining halves
    for transportid in (id1, id2):
        if transportid is None:
            continue

        dec._decodeFactoryComponent(factory, transportid)
        _checkTransportConnections(factory, transportid)

def _deleteComponent(factory: fac.Factory, worldPos):
    componentid = dec.visibleComponentsAt.get(worldPos)

    if componentid is None:
        return

    if componentid in factory.producers:
        factory.destroyProducer(componentid)

    elif componentid in factory.machines:
        factory.destroyMachine(componentid)

    elif componentid in factory.inventories:
        factory.destroyInventory(componentid)
    
    elif componentid in factory.routers:
        factory.destroyRouter(componentid)

    dec._destroyComponentSprites(componentid)

    # clear occupied tiles for this component
    for pos, id in list(dec.visibleComponentsAt.items()):
        if id == componentid:
            dec.visibleComponentsAt.pop(pos, None)
            dec.occupiedSpaces.discard(pos)

def _directionBetween(pos1, pos2):
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

def _checkTransportConnections(factory, transportid):
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
    _checkComponentAt(factory, transportid, pos)

    dx, dy = directionOffsets[transport.finalDirection]
    end = transport.turns[-1][0]
    pos = (end[0] + dx, end[1] + dy)
    _checkComponentAt(factory, transportid, pos)

def _checkComponentAt(factory, transportid, pos):
    componentid = dec.visibleComponentsAt.get(pos)

    if componentid is None:
        return

    if componentid in factory.machines:
        _checkAndConnectComponent(factory, componentid, transportid)

    elif componentid in factory.inventories:
        _checkAndConnectComponent(factory, componentid, transportid)

    elif componentid in factory.producers:
        _checkAndConnectComponent(factory, componentid, transportid)
    
    elif componentid in factory.routers:
        _checkAndConnectComponent(factory, componentid, transportid)

def _validateAndEncodeTransport(factory: fac.Factory, transport, 
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

    if flip[1]:
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

        if turns[-1][0] == pos and transport.type == existing.type and existing.finalDirection is orientation:
            extendForward = True
            id1 = transp

            if len(turns) == 1:
                shouldAddForward = True
            else:
                incomingDirection = _directionBetween(turns[-2][0], turns[-1][0])
                shouldAddForward = existing.finalDirection is not incomingDirection

    # check in front of the placed conveyor
    # for a bend, 'front' is bendDirection
    dx, dy = directionOffsets[bendDirection]
    pos = (worldPos[0] + dx, worldPos[1] + dy)
    transp = dec.visibleTransportsAt.get(pos)

    if transp is not None:
        existing = factory.transports[transp]
        turns = existing.turns
        
        if turns[0][0] == pos and transport.type == existing.type and existing.initialDirection is bendDirection:
            extendBackward = True
            id2 = transp

            if len(turns) == 1:
                shouldAddBackward = True
            else:
                outgoingDirection = _directionBetween(turns[0][0], turns[1][0])
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
    
    _checkTransportConnections(factory, resultTransportId)

def _rotateMatrix(matrix, rotations):
    rotations %= 4

    for _ in range(rotations):
        matrix = [list(row) for row in zip(*matrix[::-1])]

    return matrix

def _flipMatrixX(matrix):
    return [row[::-1] for row in matrix]

def _flipMatrixY(matrix):
    return matrix[::-1]

def _connectComponent(factory: fac.Factory, component: any, componentid: int, transportid: int, isInput: bool):
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
    
    elif componentid in factory.routers:
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

def _transformPort(x, y, side, size, rotation, flipped):
    width, height = size

    # rotate clockwise
    for _ in range(rotation.value // 90):
        x, y = height - 1 - y, x
        width, height = height, width
        side = fac.Directions((side.value + 90) % 360)

    # flip X
    if flipped[0]:
        x = width - 1 - x

        if side is fac.Directions.East:
            side = fac.Directions.West
        elif side is fac.Directions.West:
            side = fac.Directions.East

    # flip Y
    if flipped[1]:
        y = height - 1 - y

        if side is fac.Directions.North:
            side = fac.Directions.South
        elif side is fac.Directions.South:
            side = fac.Directions.North

    return x, y, side

def _checkAndConnectComponent(factory: fac.Factory, componentid: int, transportid: int):
    component = None

    if componentid in factory.machines:
        component = factory.machines[componentid]

    elif componentid in factory.producers:
        component = factory.producers[componentid]

    elif componentid in factory.inventories:
        component = factory.inventories[componentid]

    elif componentid in factory.routers:
        component = factory.routers[componentid]

    if component is None:
        raise BaseException("component is lowk none")

    transport = factory.transports[transportid]

    # ports:
    #  1: input
    # -1: output
    #  2: input or output
    # each port is (x, y, side, type)

    componentPorts = None

    if isinstance(component, fac.Machine):
        if component.size == (2, 2):
            componentPorts = [
                (0, 0, fac.Directions.North, 1),
                (1, 0, fac.Directions.North, 1),
                (0, 1, fac.Directions.South, -1),
            ]

        elif component.size == (3, 2):
            componentPorts = [
                (0, 0, fac.Directions.North, 1),
                (1, 0, fac.Directions.North, 1),
                (2, 0, fac.Directions.North, 1),
                (1, 1, fac.Directions.South, -1),
            ]

    elif isinstance(component, fac.Producer):
        if component.size == (2, 2):
            componentPorts = [
                (0, 1, fac.Directions.South, -1),
            ]

    elif isinstance(component, fac.Inventory):
        if component.size == (2, 2):
            componentPorts = [
                (0, 0, fac.Directions.North, 2),
                (0, 1, fac.Directions.South, 2),
            ]

    elif isinstance(component, fac.Router):
        if component.size == (1, 1):
            if component.type == "Combiner":
                componentPorts = [
                    (0, 0, fac.Directions.West, 1),
                    (0, 0, fac.Directions.North, 1),
                    (0, 0, fac.Directions.East, -1),
                ]

    if componentPorts is None:
        raise BaseException("component ports is lowk none")

    directionOffsets = {
        fac.Directions.North: (0, -1),
        fac.Directions.East: (1, 0),
        fac.Directions.South: (0, 1),
        fac.Directions.West: (-1, 0)
    }

    for x, y, side, portType in componentPorts:
        x, y, side = _transformPort(
            x,
            y,
            side,
            component.size,
            component.rotation,
            component.flipped
        )

        componentPortPos = (
            component.position[0] + x,
            component.position[1] + y
        )

        dx, dy = directionOffsets[side]

        transportPos = (
            componentPortPos[0] + dx,
            componentPortPos[1] + dy
        )

        incomingDirection = fac.Directions((side.value + 180) % 360)
        outgoingDirection = side

        # INPUT
        if portType == 1:
            if transport.turns[-1][0] == transportPos and transport.finalDirection is incomingDirection:
                _connectComponent(factory, component, componentid, transportid, True)

        # OUTPUT
        elif portType == -1:
            if transport.turns[0][0] == transportPos and transport.initialDirection is outgoingDirection:
                _connectComponent(factory, component, componentid, transportid, False)

        # BOTH
        elif portType == 2:
            if transport.turns[-1][0] == transportPos and transport.finalDirection is incomingDirection:
                _connectComponent(factory, component, componentid, transportid, True)

            elif transport.turns[0][0] == transportPos and transport.initialDirection is outgoingDirection:
                _connectComponent(factory, component, componentid, transportid, False)
                    
def _validateAndEncodeComponent(factory: fac.Factory, component, worldPos: tuple[int, int], orientation: fac.Directions, flip: tuple[bool, bool]):
    width, height = component.size

    # rotating 90/270 swaps the footprint dimensions
    if orientation in (fac.Directions.East, fac.Directions.West):
        width, height = height, width

    # check whole footprint for collisions
    for y in range(height):
        for x in range(width):
            pos = (worldPos[0] + x, worldPos[1] + y)

            if pos in dec.occupiedSpaces:
                print("occupied")
                return

    # actually create the component
    if isinstance(component, fac.Producer):
        componentid = factory.addProducer(component)
        factory.updateProducer(componentid, position = worldPos, rotation = orientation, flipped = flip)

    elif isinstance(component, fac.Machine):
        componentid = factory.addMachine(component)
        factory.updateMachine(componentid, position = worldPos, rotation = orientation, flipped = flip, recipe = component.recipes[0])

    elif isinstance(component, fac.Inventory):
        componentid = factory.addInventory(component)
        factory.updateInventory(componentid, position = worldPos, rotation = orientation, flipped = flip)
    
    elif isinstance(component, fac.Router):
        componentid = factory.addRouter(component)
        factory.updateRouter(componentid, position = worldPos, rotation = orientation, flipped = flip)

    else:
        raise ValueError(f"unknown component {component!r}")

    # connect it to any conveyors that were already there
    for transportid in factory.transports:
        _checkAndConnectComponent(factory, componentid, transportid)

    return componentid