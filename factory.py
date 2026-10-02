from enum import Enum
from dataclasses import dataclass, field
from copy import deepcopy

MISSING = object()

class Directions(Enum):
    North = 0
    East = 90
    South = 180
    West = 270

class Items(Enum):
    Wood = 1
    IronOre = 2
    Coal = 3
    Steel = 4
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
    result = [Items.Steel, 1],
    time = 2,
)

@dataclass
class Machine():
    type: str
    recipes: list[Recipe]
    maxItems: int
    size: tuple[int, int]                       # how many tiles the machine takes up, x by y from position
    position: tuple[int, int] = (0, 0)
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
    # input: int | None   <- perhaps unnecessary?
    # output: int | None  <- 

@dataclass
class Inventory():
    type: str
    maxItems: int
    position: tuple[int, int] = (0, 0)
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
    position: tuple[int, int] = (0, 0)
    inventory: dict[Items, int] = field(default_factory = dict)
    output: list[int] | None = None
    progress: float = 0
    id: int = 0
    
    def totalItems(self) -> int:
        return sum(self.inventory.values())

conveyor = Transport(
    type = "ConveyorBelt",
    speed = 3,
    length = 10,
    # input = None,
    # output = None,
)

furnace = Machine(
    type = "Furnace",
    recipes = [steelRecipe],
    progress = 0,
    maxItems = 5,
    size = [1, 1]
)

drill = Producer(
    type = "Drill",
    material = Items.Coal,
    speed = 1,
    efficiency = 1,
    maxItems = 5,
)

drill2 = Producer(
    type = "Drill",
    material = Items.IronOre,
    speed = 2,
    efficiency = 1,
    maxItems = 5,
)

box = Inventory(
    type = "Box",
    maxItems = 10,
)

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
                       outputids: list[int] = MISSING,
                       position: tuple[int, int] = MISSING):
        producer = self.producers[producerid]
        
        if outputids is not MISSING: producer.output = outputids
        if position  is not MISSING: producer.position = position
    
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
                      inputids: list[int] = MISSING, outputid: int = MISSING, recipe: Recipe = MISSING,
                      position: tuple[int, int] = MISSING):
        machine = self.machines[machineid]
        
        if inputids is not MISSING: machine.input = inputids
        if outputid is not MISSING: machine.output = outputid
        if position is not MISSING: machine.position = position
        if recipe   is not MISSING: 
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
                        #inputids: list[int] = MISSING, outputid: int = MISSING,
                        length: int = MISSING):
        transport = self.transports[transportid]
        
        # if inputids is not MISSING: transport.input = inputids
        # if outputid is not MISSING: transport.output = outputid
        if length   is not MISSING: transport.length = length
    
    def calculateTransportLength(self, transportid: int) -> int:
        transport = self.transports[transportid]
        
        cumulativeLength = 0
        
        for i, turn in enumerate(transport.turns):
            prevTurnPos = transport.turns[i - 1][0] if i > 0 else transport.turns[i][0]
            turnPos = turn[0]
            
            dx = abs(turnPos[0] - prevTurnPos[0])
            dy = abs(turnPos[1] - prevTurnPos[1])
            
            cumulativeLength += dx + dy
            
        length = cumulativeLength 
        
        return length if length > 2 else 2

    def calculateKeyPointsItemIsBetween(self, transportid: int, itemPos: float) -> tuple[tuple[int, int], tuple[int, int], int]:
        """returns the key points in world pos an item on a given transport would be between"""
        
        transport = self.transports[transportid]
        
        cumulativeLength = 0
        
        for i, turn in enumerate(transport.turns):
            prevTurnPos = transport.turns[i - 1][0] if i > 0 else transport.turns[i][0]
            turnPos = turn[0]
            
            dx = abs(turnPos[0] - prevTurnPos[0])
            dy = abs(turnPos[1] - prevTurnPos[1])
            
            cumulativeLength += dx + dy
            
            if cumulativeLength > itemPos / 2: break
            
        return (prevTurnPos, turnPos, cumulativeLength - dx - dy)
    
    def addTransportTurn(self, transportid: int, turn: list[tuple[int, int] | Directions]): 
        transport = self.transports[transportid]
        
        if not transport.turns:
            transport.initialDirection = turn[1]
        
        transport.finalDirection = turn[1]
        
        transport.turns.append(turn)
        
        length = self.calculateTransportLength(transportid)
        
        self.updateTransport(transportid, length = length)
        
    def destroyTransport(self, transportid: int):
        del self.transports[transportid]
    
    def addInventory(self, inventoryTemplate: Inventory) -> int:
        inventory = deepcopy(inventoryTemplate)
        
        inventory.id = self.nextid
        self.inventories[inventory.id] = inventory
        
        self.nextid += 1
        
        return inventory.id
    
    def updateInventory(self, inventoryid: int, *,
                        inputids: list[int] = MISSING, outputids: list[int] = MISSING,
                        position: tuple[int, int] = MISSING):
        inventory = self.inventories[inventoryid]
        
        if inputids  is not MISSING: inventory.input = inputids
        if outputids is not MISSING: inventory.output = outputids
        if position  is not MISSING: inventory.position = position
    
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
                
                totalItems = producer.totalItems()
                
                if totalItems > producer.maxItems:
                    itemsToRemove = totalItems - producer.maxItems
                    producer.inventory[producer.material] -= itemsToRemove
            
            print(f"{producer.material.name} made")
            
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
                
                # remove ingredients from machine's inventory
                for ingredient, amount in ingredients:
                    machine.input_inventory[ingredient] -= amount
                
                # add result to output inventory
                machine.output_inventory[result[0]] = machine.output_inventory.get(result[0], 0) + result[1]
                
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
                        
                        print(f"{itemToTransfer.name} put on conveyor")
        
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
                        
                        print(f"{itemToTransport.name} took into furnace")
                        
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
                        
    def step(self, dt: float):
        """main factory update function"""
        
        self._stepProducers(dt)
        self._stepMachines(dt)
        self._stepTransports(dt)
        self._stepConnections()
        
        # todo fix known edgecases
        # conveyor cannot loop into itself