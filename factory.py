from enum import Enum
from dataclasses import dataclass, field
from copy import deepcopy

_MISSING = object()

class Directions(Enum):
    North = 0
    East = 90
    South = 180
    West = 270

class Items(Enum):
    Wood = 1
    IronOre = 2
    Coal = 3
    SteelIngot = 4
    # etc...

@dataclass
class Recipe():
    ingredients: dict[Items, int]
    result: list[Items | int]
    time: float

steelRecipe = Recipe(
    ingredients = {
        Items.IronOre: 3,
        Items.Coal: 1
        },
    result = [Items.SteelIngot, 1],
    time = 2,
)

@dataclass
class Machine():
    type: str
    recipes: list[Recipe]
    maxItems: int
    size: tuple[int, int]                       # how many tiles the machine takes up, x by y from position
    position: tuple[int, int] = (0, 0)
    rotation: Directions = Directions.North
    flipped: tuple[bool, bool] = (False, False)  # (flipped x, flipped y)
    input_inventory: dict[Items, int] = field(default_factory = dict)
    output_inventory: dict[Items, int] = field(default_factory = dict)
    input: list[int] | None = None
    output: int | None = None
    currentRecipe: Recipe = None
    progress: float = 0
    id: int = 0
    
    def totalItems(self) -> int:
        return sum(self.input_inventory.values()) + sum(self.output_inventory.values())

@dataclass
class Transport():
    type: str
    speed: float
    length: int
    turns: list[list[tuple[int, int] | Directions]] = field(default_factory = list)  # first and last 'turn' define origin and destination
    initialDirection: Directions = Directions.North
    finalDirection: Directions = Directions.South
    items: list[list[Items | float]] = field(default_factory = list)
    itemids: list[int] = field(default_factory = list)
    lastDestroyedid: int = 0
    id: int = 0
    # input: int | None   <- may be needed if conveyors can connect into other conveyors
    # output: int | None  <- 

@dataclass
class Inventory():
    type: str
    maxItems: int
    size: tuple[int, int]
    position: tuple[int, int] = (0, 0)
    rotation: Directions = Directions.North
    flipped: tuple[bool, bool] = (False, False)  # (flipped x, flipped y)
    inventory: dict[Items, int] = field(default_factory = dict)
    input: list[int] | None = None
    output: list[int] | None = None
    id: int = 0
    
    def totalItems(self) -> int:
        return sum(self.inventory.values())

@dataclass
class Producer():
    type: str
    material: Items
    speed: int
    efficiency: int
    maxItems: int
    size: tuple[int, int]
    position: tuple[int, int] = (0, 0)
    rotation: Directions = Directions.North
    flipped: tuple[bool, bool] = (False, False)  # (flipped x, flipped y)
    inventory: dict[Items, int] = field(default_factory = dict)
    output: list[int] | None = None
    progress: float = 0
    id: int = 0
    
    def totalItems(self) -> int:
        return sum(self.inventory.values())

#todo add routers

conveyor = Transport(
    type = "StandardConveyorBelt",
    speed = 2,
    length = 10,
    # input = None,
    # output = None,
)

furnace = Machine(
    type = "Furnace",
    recipes = [steelRecipe],
    progress = 0,
    maxItems = 5,
    size = (2, 2)
)

drill = Producer(
    type = "Drill",
    material = Items.Coal,
    speed = 1,
    efficiency = 1,
    maxItems = 5,
    size = (2, 2)
)

drill2 = Producer(
    type = "Drill",
    material = Items.IronOre,
    speed = 4,
    efficiency = 5,
    maxItems = 5,
    size = (2, 2)
)

basicContainer = Inventory(
    type = "BasicContainer",
    maxItems = 10,
    size = (2, 2)
)

#!    size is currently unused.
#todo make it matter when instantiating sprites

class Factory():
    def __init__(self):
        self.producers: dict[int, Producer] = {}
        self.machines: dict[int, Machine] = {}
        self.transports: dict[int, Transport] = {}
        self.inventories: dict[int, Inventory] = {}
        
        self.nextid = 1
    
    def addProducer(self, producerTemplate: Producer) -> int:
        producer = deepcopy(producerTemplate)
        
        producer.id = self.nextid
        self.producers[producer.id] = producer
        
        self.nextid += 1
        
        return producer.id
    
    def updateProducer(self, producerid: int, *,
                       outputids: list[int] = _MISSING,
                       position: tuple[int, int] = _MISSING,
                       rotation: Directions = _MISSING,
                       flipped: tuple[bool, bool] = _MISSING):
        producer = self.producers[producerid]
        
        if outputids is not _MISSING: producer.output = outputids
        if position  is not _MISSING: producer.position = position
        if rotation  is not _MISSING: producer.rotation = rotation
        if flipped   is not _MISSING: producer.flipped = flipped
    
    def destroyProducer(self, producerid: int):
        del self.producers[producerid]
    
    def addMachine(self, machineTemplate: Machine) -> int:
        machine = deepcopy(machineTemplate)
        
        machine.id = self.nextid
        self.machines[machine.id] = machine
        
        self.nextid += 1
        
        return machine.id
    
    def clearMachineInv(self, machineid):
        self.machines[machineid].input_inventory.clear()
    
    def updateMachine(self, machineid: int, *, 
                      inputids: list[int] = _MISSING, outputid: int = _MISSING, recipe: Recipe = _MISSING,
                      position: tuple[int, int] = _MISSING,
                      rotation: Directions = _MISSING,
                      flipped: tuple[bool, bool] = _MISSING):
        machine = self.machines[machineid]
        
        if inputids is not _MISSING: machine.input = inputids
        if outputid is not _MISSING: machine.output = outputid
        if position is not _MISSING: machine.position = position
        if rotation is not _MISSING: machine.rotation = rotation
        if flipped  is not _MISSING: machine.flipped = flipped
        if recipe   is not _MISSING: 
            machine.currentRecipe = recipe
            self.clearMachineInv(machineid)
            machine.progress = 0
    
    def destroyMachine(self, machineid: int):
        del self.machines[machineid]
    
    def addTransport(self, transportTemplate: Transport) -> int:
        
        transport = deepcopy(transportTemplate)
        
        transport.id = self.nextid
        self.transports[transport.id] = transport
        
        self.nextid += 1
        
        return transport.id
    
    def updateTransport(self, transportid: int, *,
                        #inputids: list[int] = _MISSING, outputid: int = _MISSING,
                        length: int = _MISSING):
        transport = self.transports[transportid]
        
        # if inputids is not _MISSING: transport.input = inputids
        # if outputid is not _MISSING: transport.output = outputid
        if length   is not _MISSING: transport.length = length
    
    def calculateTransportLength(self, transportid: int) -> int:
        transport = self.transports[transportid]
        
        cumulativeLength = 0
        
        for i, turn in enumerate(transport.turns):
            prevTurnPos = transport.turns[i - 1][0] if i > 0 else transport.turns[i][0]
            turnPos = turn[0]
            
            dx = abs(turnPos[0] - prevTurnPos[0])
            dy = abs(turnPos[1] - prevTurnPos[1])
            
            cumulativeLength += dx + dy
            
        length = cumulativeLength + 1
        
        return length if length > 1 else 1

    def calculateKeyPointsItemIsBetween(self, transportid: int, itemPos: float) -> tuple[tuple[int, int], tuple[int, int], int]:
        """returns the key points in world pos an item on a given transport would be between"""
        
        transport = self.transports[transportid]
        
        cumulativeLength = 0
        
        if len(transport.turns) == 1:
            x, y = transport.turns[0][0]
            centre = (x, y)
            distance = itemPos / 2

            if distance < 0:
                direction = transport.initialDirection

                if direction is Directions.East:
                    tip = (x - 0.5, y)
                elif direction is Directions.West:
                    tip = (x + 0.5, y)
                elif direction is Directions.North:
                    tip = (x, y + 0.5)
                else:
                    tip = (x, y - 0.5)

                return tip, centre, -0.5

            else:
                direction = transport.finalDirection

                if direction is Directions.East:
                    tip = (x + 0.5, y)
                elif direction is Directions.West:
                    tip = (x - 0.5, y)
                elif direction is Directions.North:
                    tip = (x, y - 0.5)
                else:
                    tip = (x, y + 0.5)

                return centre, tip, 0
        
        distance = itemPos / 2

        if distance < 0:
            startPos = transport.turns[0][0]
            nextPos = transport.turns[1][0]

            outgoingDirection = Factory.directionBetween(startPos, nextPos)
            incomingDirection = transport.initialDirection

            if incomingDirection is not outgoingDirection:
                x, y = startPos

                if incomingDirection is Directions.East:
                    prevPoint = (x - 1, y)
                elif incomingDirection is Directions.West:
                    prevPoint = (x + 1, y)
                elif incomingDirection is Directions.North:
                    prevPoint = (x, y + 1)
                else:
                    prevPoint = (x, y - 1)

                return prevPoint, startPos, -1
        
        for i in range(1, len(transport.turns)):
            prevTurnPos = transport.turns[i - 1][0] if i > 0 else transport.turns[i]
            turnPos = transport.turns[i][0]
            
            dx = abs(turnPos[0] - prevTurnPos[0])
            dy = abs(turnPos[1] - prevTurnPos[1])
            
            cumulativeLength += dx + dy
            
            if cumulativeLength > itemPos / 2: break
        
        # handle unmatching directional end
        if i == len(transport.turns) - 1 and itemPos / 2 >= cumulativeLength:
            incomingDirection = transport.turns[i - 1][1]
            outgoingDirection = transport.finalDirection

            if incomingDirection is not outgoingDirection:
                x, y = turnPos

                if outgoingDirection is Directions.East:
                    endPoint = (x + 1, y)
                elif outgoingDirection is Directions.West:
                    endPoint = (x - 1, y)
                elif outgoingDirection is Directions.North:
                    endPoint = (x, y - 1)
                elif outgoingDirection is Directions.South:
                    endPoint = (x, y + 1)

                return (turnPos, endPoint, cumulativeLength)

        return (prevTurnPos, turnPos, cumulativeLength - dx - dy)
    
    def addTransportTurn(self, transportid: int, turn: list[tuple[int, int] | Directions]): 
        if transportid is None: return
        
        transport = self.transports[transportid]
        
        if not transport.turns:
            transport.initialDirection = turn[1]
        
        transport.finalDirection = turn[-1] # maybe this is supposed to be -1 but if it aint broke dont fix it
        
        transport.turns.append(turn)
        
        length = self.calculateTransportLength(transportid)
        
        self.updateTransport(transportid, length = length)

    def changeTransportTurn(self, transportid: int, turn: list[tuple[int, int] | Directions], isEnd: bool): 
        if transportid is None: return
        
        transport = self.transports[transportid]
        
        turnToExtend = -1 if isEnd else 0
        
        pos = turn[0] if turn[0] is not None else transport.turns[turnToExtend][0]
        direction = turn[1]
        
        transport.turns[turnToExtend] = (pos, direction)
        
        if isEnd:
            transport.finalDirection = direction
        else:
            transport.initialDirection = direction
        
    def extendTransportTurn(self, transportid: int, amount: int, isEnd: bool):
        if transportid is None: return
        
        transport = self.transports[transportid]
        
        turnToExtend = transport.turns[-1] if isEnd else transport.turns[0]
        turnDirection = transport.finalDirection if isEnd else transport.initialDirection
        
        # sign switch as extending the start would mean to extend backwards
        sign = 1 if isEnd else -1
        
        # check direction to extend properly
        if turnDirection is Directions.East:
            turnToExtend[0] = (turnToExtend[0][0] + (amount * sign), turnToExtend[0][1]) # tuples are immutable so this is ugly but i dont care
        elif turnDirection is Directions.West:
            turnToExtend[0] = (turnToExtend[0][0] - (amount * sign), turnToExtend[0][1])
        elif turnDirection is Directions.North:
            turnToExtend[0] = (turnToExtend[0][0], turnToExtend[0][1] - (amount * sign))
        elif turnDirection is Directions.South:
            turnToExtend[0] = (turnToExtend[0][0], turnToExtend[0][1] + (amount * sign))
        
        length = self.calculateTransportLength(transportid)
                
        self.updateTransport(transportid, length = length)
    
    def connectTransports(self, id1: int, id2: int, joinPos: tuple[int, int], bent: bool = False, bendDirection: Directions = Directions.North):
        """combines the end of transport 1 with the start of transport 2"""

        transport1 = self.transports[id1]
        transport2 = self.transports[id2]
        
        # record offset for items and add them to transport 1
        itemOffset = (transport1.length - 1) * 2

        for item in transport2.items:
            item[1] += itemOffset

        transport1.items.extend(transport2.items)
        transport1.itemids.extend(transport2.itemids)

        # remove straight end of transport 1
        if len(transport1.turns) > 1:
            pos1 = transport1.turns[-2][0]
            pos2 = transport1.turns[-1][0]

            incomingDirection = Factory.directionBetween(pos1, pos2)

            if transport1.finalDirection is incomingDirection:
                del transport1.turns[-1]

        # remove straight start of transport 2
        if len(transport2.turns) > 1:
            pos1 = transport2.turns[0][0]
            pos2 = transport2.turns[1][0]

            outgoingDirection = Factory.directionBetween(pos1, pos2)

            if transport2.initialDirection is outgoingDirection:
                del transport2.turns[0]
                
        if bent:
            transport1.turns.append([joinPos, bendDirection])

        transport1.turns.extend(transport2.turns)

        transport1.finalDirection = transport2.finalDirection
        transport1.length = self.calculateTransportLength(id1)

        self.destroyTransport(id2)
                
    def _transportTiles(self, transport):
        if not transport.turns:
            return []

        tiles = [transport.turns[0][0]]

        for i in range(1, len(transport.turns)):
            x, y = transport.turns[i - 1][0]
            endX, endY = transport.turns[i][0]

            dx = 0 if endX == x else (1 if endX > x else -1)
            dy = 0 if endY == y else (1 if endY > y else -1)

            while (x, y) != (endX, endY):
                x += dx
                y += dy
                tiles.append((x, y))

        return tiles


    def _setTransportFromTiles(self, transport, tiles, initialDirection, finalDirection):
        transport.initialDirection = initialDirection
        transport.finalDirection = finalDirection
        transport.turns = []

        if len(tiles) == 1:
            transport.turns = [[tiles[0], finalDirection]]
            transport.length = 1
            return

        directions = [
            Factory.directionBetween(tiles[i], tiles[i + 1])
            for i in range(len(tiles) - 1)
        ]

        transport.turns.append([tiles[0], directions[0]])

        for i in range(1, len(tiles) - 1):
            if directions[i] is not directions[i - 1]:
                transport.turns.append([tiles[i], directions[i]])

        transport.turns.append([tiles[-1], finalDirection])
        transport.length = len(tiles)


    def disconnectTransport(self, transportid):
        for producer in self.producers.values():
            if producer.output:
                producer.output = [id for id in producer.output if id != transportid]

                if not producer.output:
                    producer.output = None

        for machine in self.machines.values():
            if machine.input:
                machine.input = [id for id in machine.input if id != transportid]

                if not machine.input:
                    machine.input = None

            if machine.output == transportid:
                machine.output = None

        for inventory in self.inventories.values():
            if inventory.input:
                inventory.input = [id for id in inventory.input if id != transportid]

                if not inventory.input:
                    inventory.input = None

            if inventory.output:
                inventory.output = [id for id in inventory.output if id != transportid]

                if not inventory.output:
                    inventory.output = None

    def splitTransport(self, transportid, deletePos):
        transport = self.transports[transportid]
        tiles = self._transportTiles(transport)

        if deletePos not in tiles:
            return transportid, None, []

        deleteIndex = tiles.index(deletePos)

        beforeTiles = tiles[:deleteIndex]
        afterTiles = tiles[deleteIndex + 1:]

        oldInitialDirection = transport.initialDirection
        oldFinalDirection = transport.finalDirection

        # direction pointing into the deleted tile
        if deleteIndex > 0:
            beforeFinalDirection = Factory.directionBetween(
                tiles[deleteIndex - 1],
                tiles[deleteIndex]
            )
        else:
            beforeFinalDirection = oldInitialDirection

        # direction pointing out of the deleted tile
        if deleteIndex < len(tiles) - 1:
            afterInitialDirection = Factory.directionBetween(
                tiles[deleteIndex],
                tiles[deleteIndex + 1]
            )
        else:
            afterInitialDirection = oldFinalDirection

        # each conveyor tile is 2 item pos units
        deletedStart = deleteIndex * 2
        deletedEnd = deletedStart + 2

        beforeItems = []
        beforeItemids = []

        afterItems = []
        afterItemids = []

        destroyedItemids = []

        for item, itemid in zip(transport.items, transport.itemids):
            itemPos = item[1]

            # before deleted tile
            if itemPos < deletedStart:
                beforeItems.append(item)
                beforeItemids.append(itemid)

            # after deleted tile
            elif itemPos >= deletedEnd:
                item[1] -= deletedEnd

                afterItems.append(item)
                afterItemids.append(itemid)

            # delete items one deleted tiles
            else:
                destroyedItemids.append(itemid)

        # save a copy before changing the original
        oldTransport = deepcopy(transport)

        # remove old component connections
        self.disconnectTransport(transportid)

        beforeId = None
        afterId = None

        if beforeTiles:
            beforeId = transportid

            transport.items = beforeItems
            transport.itemids = beforeItemids

            self._setTransportFromTiles(
                transport,
                beforeTiles,
                oldInitialDirection,
                beforeFinalDirection
            )

        if afterTiles:
            if beforeTiles:
                newTransport = deepcopy(oldTransport)

                afterId = self.nextid
                self.nextid += 1

                newTransport.id = afterId
                self.transports[afterId] = newTransport

            else:
                # deleted first tile so reuse original id
                afterId = transportid
                newTransport = transport

            newTransport.items = afterItems
            newTransport.itemids = afterItemids

            self._setTransportFromTiles(
                newTransport,
                afterTiles,
                afterInitialDirection,
                oldFinalDirection
            )

        # if only single length conveyor is split
        if not beforeTiles and not afterTiles:
            self.destroyTransport(transportid)

        return beforeId, afterId, destroyedItemids
        
    def destroyTransport(self, transportid: int):
        del self.transports[transportid]
    
    def addInventory(self, inventoryTemplate: Inventory) -> int:
        inventory = deepcopy(inventoryTemplate)
        
        inventory.id = self.nextid
        self.inventories[inventory.id] = inventory
        
        self.nextid += 1
        
        return inventory.id
    
    def updateInventory(self, inventoryid: int, *,
                        inputids: list[int] = _MISSING, outputids: list[int] = _MISSING,
                        position: tuple[int, int] = _MISSING,
                        rotation: Directions = _MISSING,
                        flipped: tuple[bool, bool] = _MISSING):
        inventory = self.inventories[inventoryid]
        
        if inputids  is not _MISSING: inventory.input = inputids
        if outputids is not _MISSING: inventory.output = outputids
        if position  is not _MISSING: inventory.position = position
        if rotation  is not _MISSING: inventory.rotation = rotation
        if flipped   is not _MISSING: inventory.flipped = flipped
    
    def destroyInventory(self, inventoryid: int):
        del self.inventories[inventoryid]
    
    def _stepProducers(self, dt):
        for id, producer in self.producers.items():
            if producer.material is None: continue
            
            producer.progress += dt
            
            if producer.progress < producer.speed:
                continue
            
            # produce items
            if producer.totalItems() < producer.maxItems:
                producer.inventory[producer.material] = producer.inventory.get(producer.material, 0) + producer.efficiency
                
                #print(f"{producer.material.name} made")
                
                totalItems = producer.totalItems()
                
                if totalItems > producer.maxItems:
                    itemsToRemove = totalItems - producer.maxItems
                    producer.inventory[producer.material] -= itemsToRemove
            
            producer.progress = 0
    
    def _stepMachines(self, dt):
        for id, machine in self.machines.items():
            if not machine.input_inventory or machine.currentRecipe is None: continue
            
            recipeMet = all(
                machine.input_inventory.get(ingredient, 0) >= amount 
                for ingredient, amount in machine.currentRecipe.ingredients.items()
                )
            
            if recipeMet:
                machine.progress += dt
                
                if machine.progress < machine.currentRecipe.time:
                    continue
                
                # make stuff
                ingredients = machine.currentRecipe.ingredients.items()
                result = machine.currentRecipe.result
                
                #print(f"{result[0].name} made")
                
                # remove ingredients from machine's inventory
                for ingredient, amount in ingredients:
                    machine.input_inventory[ingredient] -= amount
                
                # add result to output inventory
                machine.output_inventory[result[0]] = machine.output_inventory.get(result[0], 0) + result[1]
                
                #print(f"{result[0].name} put on conveyor")
                
                machine.progress = 0
            
    def _stepTransports(self, dt):
        for id, transport in self.transports.items():
            # farthest length a moving item may go
            farthest = transport.length * 2
            
            for item in transport.items:
                # move items
                item[1] += transport.speed * dt
                
                if item[1] > farthest:
                    item[1] = farthest
                    
                farthest = item[1] - 1
            
    def _stepConnections(self):
        """resolve in/outputs"""
        
        # resolve producer outputs
        for id, producer in self.producers.items():
            if producer.output and producer.inventory:
                for output in producer.output:
                    if output in self.transports:
                        # check for space on the transport
                        transport = self.transports[output]
                        if transport.items:
                            if transport.items[-1][1] < 1: continue
                        
                        # remove item from producer
                        itemToTransfer = next(iter(producer.inventory), None)
                        producer.inventory[itemToTransfer] -= 1
                        
                        if producer.inventory[itemToTransfer] <= 0:
                            del producer.inventory[itemToTransfer]
                        
                        # transfer to transport at position 0
                        transport.items.append([itemToTransfer, 0])
                        # id item
                        transport.itemids.append(self.nextid)
                        self.nextid += 1
                        
                        #print(f"{itemToTransfer.name} put on conveyor")
        
        # resolve machine i/o
        for id, machine in self.machines.items():
            if machine.output and machine.output_inventory:
                if machine.output in self.transports:
                    # check for space on the transport
                    transport = self.transports[machine.output]
                    if transport.items:
                        if transport.items[-1][1] < 1: continue
                    
                    # remove item from producer
                    itemToTransfer = next(iter(machine.output_inventory), None)
                    machine.output_inventory[itemToTransfer] -= 1
                    
                    if machine.output_inventory[itemToTransfer] <= 0:
                        del machine.output_inventory[itemToTransfer]
                    
                    # transfer to transport at position 0
                    transport.items.append([itemToTransfer, 0])
                    # id item
                    transport.itemids.append(self.nextid)
                    self.nextid += 1
            
            if machine.input and machine.currentRecipe:
                for input in machine.input:
                    if input in self.transports:
                        # check for item at end of transport
                        transport = self.transports[input]
                        if transport.items:
                            if transport.items[0][1] / 2 < transport.length: continue
                        else: continue
                        
                        # check for space in the machine
                        if machine.totalItems() >= machine.maxItems: continue
                        
                        # check the current recipe to only allow certain materials and a certain amount
                        allowItems = machine.currentRecipe.ingredients
                        itemToTransport = transport.items[0][0]
                        
                        if itemToTransport not in allowItems: continue
                        if machine.input_inventory.get(itemToTransport, 0) + 1 > allowItems[itemToTransport]: continue
                        
                        transport.lastDestroyedid = transport.itemids[0] # flag to the renderer to destroy the visual rep
                        
                        #print(f"{itemToTransport.name} took into furnace")
                        
                        # remove last item from transport
                        del transport.items[0] 
                        del transport.itemids[0] 
                        
                        # add item into the machine
                        machine.input_inventory[itemToTransport] = machine.input_inventory.get(itemToTransport, 0) + 1
        
        # resolve inventory i/o
        for id, inventory in self.inventories.items():
            if inventory.output and inventory.inventory:
                for output in inventory.output:
                    if output in self.transports:
                        # check for space on the transport
                        transport = self.transports[output]
                        if transport.items:
                            if transport.items[-1][1] < 1: continue
                        
                        # remove item from inventory
                        itemToTransfer = next(iter(inventory.inventory), None)
                        inventory.inventory[itemToTransfer] -= 1
                        
                        if inventory.inventory[itemToTransfer] <= 0:
                            del inventory.inventory[itemToTransfer]
                        
                        # transfer to transport at position 0
                        transport.items.append([itemToTransfer, 0])
                        # id item
                        transport.itemids.append(self.nextid)
                        self.nextid += 1
            
            if inventory.input:
                for input in inventory.input:
                    if input in self.transports:
                        # check for item at end of transport
                        transport = self.transports[input]
                        if transport.items:
                            if transport.items[0][1] / 2 < transport.length: continue
                        else: continue
                        
                        # check for space in the inventory
                        if inventory.totalItems() >= inventory.maxItems: continue
                        
                        itemToTransport = transport.items[0][0]
                        
                        transport.lastDestroyedid = transport.itemids[0] # flag to the renderer to destroy the visual rep
                        
                        # remove last item from transport
                        del transport.items[0] 
                        del transport.itemids[0] 
                
                        # add item into the machine
                        inventory.inventory[itemToTransport] = inventory.inventory.get(itemToTransport, 0) + 1
                        
                        #print(f"{itemToTransport.name} stored")
                        
    def step(self, dt: float):
        """main factory update function"""
        
        self._stepProducers(dt)
        self._stepMachines(dt)
        self._stepTransports(dt)
        self._stepConnections()
        
        # todo fix known edgecases
        # conveyor cannot loop into itself
        # large step in dt could overrun producer / furnace timers and stop it from being produced for one time
    
    @staticmethod
    def directionBetween(pos1, pos2):
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]

        if dx > 0:
            return Directions.East
        elif dx < 0:
            return Directions.West
        elif dy > 0:
            return Directions.South
        elif dy < 0:
            return Directions.North