from pygame import *
import pygameui
import decodeFactory as dec
import factory as fac
from encodeFactory import placeComponent

_ComponentTableImage = image.load("Images/UI/Buttons/ComponentTable.png").convert_alpha()
_SmallButtonImage = image.load("Images/UI/Buttons/SmallButtonPreset.png").convert_alpha()
_LongButtonImage = image.load("Images/UI/Buttons/LongButtonPreset.png").convert_alpha()
_ComponentBGImage = image.load("Images/UI/Buttons/ComponentIconBackground.png").convert_alpha()

_producers = {
    "BasicDrill": {
        "image": dec._BasicDrillFrames[0],
        "displayName": "Basic Drill",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicDrill,
    },
}

_machines = {
    "BasicFurnace": {
        "image": dec._BasicFurnaceFrames[0],
        "displayName": "Basic Furnace",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicFurnace,
    },
    "BasicExtruder": {
        "image": dec._BasicExtruderFrames[0],
        "displayName": "Basic Extruder",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicExtruder,
    },
    "BasicPress": {
        "image": dec._BasicPressFrames[0],
        "displayName": "Basic Press",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicPress,
    },
    "BasicCutter": {
        "image": dec._BasicCutterFrames[0],
        "displayName": "Basic Cutter",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicCutter,
    },
    "BasicAssembler": {
        "image": dec._BasicAssemblerFrames[0],
        "displayName": "Basic Assembler",
        "size": (3, 2), 
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicAssembler,
    },
    "AdvancedFurnace": {
        "image": dec._AdvancedFurnaceFrames[0],
        "displayName": "Uranium Furnace",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.advancedFurnace,
    },
    "AdvancedCutter": {
        "image": dec._AdvancedCutterFrames[0],
        "displayName": "Diamond Cutter",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.advancedCutter,
    },
}

_transports = {
    "BasicConveyor": {
        "image": dec._BasicConveyorStraightFrames[0],
        "bentImage": dec._BasicConveyorTurnFrames[0],
        "displayName": "Basic Conveyor",
        "size": (1, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicConveyor,
    },
    "BasicTurnConveyor": {
        "image": dec._BasicConveyorTurnFrames[0],
        "displayName": "Basic Turn Conveyor",
        "size": (1, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicConveyor,
    },
    "4WayDistributor": {
        "image": dec._FourWayDistributor,
        "displayName": "4 Way Distributor",
        "size": (1, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.fourWayDistributor,
    },
    "2WayDistributor": {
        "image": dec._TwoWayDistributor,
        "displayName": "2 Way Distributor",
        "size": (2, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.twoWayDistributor,
    },
    "BasicContainer":{
        "image": dec._BasicContainerSprite,
        "displayName": "Basic Container",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicContainer,
    },
    "AdvancedConveyor": {
        "image": dec._AdvancedConveyorStraightFrames[0],
        "bentImage": dec._AdvancedConveyorTurnFrames[0],
        "displayName": "Advanced Conveyor",
        "size": (1, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.advancedConveyor,
    },
    "AdvancedTurnConveyor": {
        "image": dec._AdvancedConveyorTurnFrames[0],
        "displayName": "Advanced Turn Conveyor",
        "size": (1, 1),
        "price": [fac.Items.IronOre, 4],
        "component": fac.advancedConveyor,
    },
}

winy = dec.winy
winx = dec.winx

def _pixelToScreen(px):
    return (px / 16) * 64

def _screenToPixel(px):
    return (px / 64) * 16

class GhostComponent(pygameui.Sprite):
    def __init__(self, x, y, w, h, image, component, **kwargs):
        super().__init__(x, y, w, h, image = image, **kwargs)
        
        self.z = 2
        
        self.normalImage = self.image.copy()
        self.redImage = self.image.copy()
        self.redImage.fill((255, 100, 100, 255), special_flags = BLEND_RGBA_MULT)
        
        self.component = component

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, value):
        self._w = value
        self.rect.w = value
        self.image = transform.scale(self.image, (self.w, self.h))
        self.redImage = transform.scale(self.redImage, (self.w, self.h))
        self._OriginalImage = transform.scale(self._OriginalImage, (self.w, self.h))
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
        self.rect.h = value
        self.image = transform.scale(self.image, (self.w, self.h))
        self.redImage = transform.scale(self.redImage, (self.w, self.h))
        self._OriginalImage = transform.scale(self._OriginalImage, (self.w, self.h))
        
class BuildMenu():
    @classmethod
    def init(cls):
        menux, menuy = 0, winy - _pixelToScreen(144)
        menuw, menuh = _pixelToScreen(83), _pixelToScreen(128)
        
        #* class variables
        cls.menupadx, cls.menupady = _pixelToScreen(8 / 5), _pixelToScreen(8 / 5)
        
        cls.buildingComponent = None
        cls.buildingComponentDict = None
        cls.buildingPosition = (0, 0)
        cls.buildingFlip = (False, False)
        cls.transportBent = False
        cls.buildingRotation = fac.Directions.North
        
        cls.initialDragPosition = (0, 0)
        cls.finalDragPosition = (0, 0)
        cls.dragxfirst = False
        
        cls.buildGhost = None
        cls.dragGhosts = []
        
        #* ui elements
        # table of components that will hold selectable icons
        cls.ComponentMenu = pygameui.Image(0, 0, 
                                            menuw, menuh,
                                            image = _ComponentTableImage)
        
        cls.ProducersButton = pygameui.TextImageButton(0, winy - _pixelToScreen(16),
                                        _pixelToScreen(83), _pixelToScreen(16), 3,
                                        image = _LongButtonImage, text = "Producers",
                                        action = cls.menuSetProducers)
        cls.MachinesButton = pygameui.TextImageButton(_pixelToScreen(83), winy - _pixelToScreen(16),
                                        _pixelToScreen(83), _pixelToScreen(16), 3,
                                        image = _LongButtonImage, text = "Machines",
                                        action = cls.menuSetMachines)
        cls.TransportsButton = pygameui.TextImageButton(_pixelToScreen(83 * 2), winy - _pixelToScreen(16),
                                        _pixelToScreen(83), _pixelToScreen(16), 3,
                                        image = _LongButtonImage, text = "Transports",
                                        action = cls.menuSetTransports)
        cls.whoknowsbutton = pygameui.TextImageButton(_pixelToScreen(83 * 3), winy - _pixelToScreen(16),
                                        _pixelToScreen(83), _pixelToScreen(16), 3,
                                        image = _LongButtonImage, text = "Polluters")
        
        cls.MenuParent = pygameui.Parent(menux, menuy, 3)
        
        
        cls.MenuParent.addChildren(cls.ComponentMenu)
        cls.MenuParent.rootChild = cls.ComponentMenu
        
        cls.UIItems = [cls.ComponentMenu, cls.ProducersButton, cls.MachinesButton, cls.TransportsButton, cls.whoknowsbutton]
        
        cls.hideMenu()
    
    @classmethod
    def showMenu(cls):
       cls.MenuParent.hidden = False

    @classmethod
    def hideMenu(cls):
       cls.MenuParent.hidden = True
    
    @classmethod
    def toggleMenu(cls):
       cls.MenuParent.hidden ^= True
    
    @classmethod
    def addMenuItem(cls, item):
        width = _pixelToScreen(18)
        height = _pixelToScreen(18)
        
        menuChildren = (len(cls.MenuParent.children) - 1) # minus 1 to account for the root child 
        xoffset = (menuChildren % 4) * (width + cls.menupadx)
        yoffset = (menuChildren // 4) * (height + cls.menupady)
        
        action = lambda: cls.buildSetComponent(item["component"], item)
        
        # draw the component icon to the bg image
        image = _ComponentBGImage.copy()
        image.blit(transform.scale(item["image"],
                                   (_screenToPixel(width - cls.menupadx),
                                    _screenToPixel(height - cls.menupady))),
                   (cls.menupadx / 4, cls.menupady / 4))
        
        menuItem = pygameui.ImageButton(xoffset + (cls.menupadx * 2), yoffset + (cls.menupady * 2),
                                        width, height, 3, image = image, action = action)
        
        cls.MenuParent.addChild(menuItem)
    
    @classmethod
    def menuSetProducers(cls):
        cls.MenuParent.destroyAllChildren()
        
        for producer in _producers.values():
            cls.addMenuItem(producer)
        
        cls.showMenu()
    
    @classmethod
    def menuSetMachines(cls):
        cls.MenuParent.destroyAllChildren()
        
        for machine in _machines.values():
            cls.addMenuItem(machine)
        
        cls.showMenu()

    @classmethod
    def menuSetTransports(cls):
        cls.MenuParent.destroyAllChildren()
        
        for transport in _transports.values():
            cls.addMenuItem(transport)
        
        cls.showMenu()
    
    @classmethod
    def buildShowGhost(cls):
        if cls.buildGhost is not None:
            cls.buildGhost.x, cls.buildGhost.y = dec.worldToSreen(cls.buildingPosition)
    
    @classmethod
    def buildUpdateGhost(cls, component: dict | None = None):
        if cls.buildGhost is not None:
            cls.buildGhost.destroy()
        
            if component is None:
                component = cls.buildGhost.component
            
        pos = dec.worldToSreen(cls.buildingPosition)
        width, height = (component["size"][0] * 64, (component["size"][1] * 64))
        
        if (cls.buildingRotation.value + 90) % 180 == 0:
            width, height = height, width
        
        ghostImage = component["image"].copy()
        ghostImage.set_alpha(128)
        
        cls.buildGhost = GhostComponent(pos[0], pos[1], width, height, ghostImage, component)
        cls.buildGhost.rotation = cls.buildingRotation.value
        cls.buildGhost.setFlipped(*cls.buildingFlip)

        cls.buildGhost.normalImage = cls.buildGhost.image.copy()

        cls.buildGhost.redImage = cls.buildGhost.normalImage.copy()
        cls.buildGhost.redImage.fill((255, 100, 100, 255), special_flags = BLEND_RGBA_MULT)

        cls.buildCheckOccipied(cls.buildingPosition)
    
    @classmethod
    def createGhost(cls, component, worldPos, orientation, flip, bent):
        pos = dec.worldToSreen(worldPos)
        width, height = (component["size"][0] * 64, (component["size"][1] * 64))
        
        if (orientation.value + 90) % 180 == 0:
            width, height = height, width
        
        ghostImage = component["image"].copy() if not bent else component["bentImage"].copy()
        ghostImage.set_alpha(128)
        
        newGhost = GhostComponent(pos[0], pos[1], width, height, ghostImage, component)
        
        cls.dragGhosts.append(newGhost)
        
        newGhost.rotation = orientation.value
        newGhost.setFlipped(*flip)

        newGhost.normalImage = newGhost.image.copy()

        newGhost.redImage = newGhost.normalImage.copy()
        newGhost.redImage.fill((255, 100, 100, 255), special_flags = BLEND_RGBA_MULT)

    @classmethod
    def destroyGhosts(cls):
        for ghost in cls.dragGhosts:
            ghost.destroy()
        
        cls.dragGhosts.clear()

    @classmethod
    def buildSetComponent(cls, component, componentdict):
        cls.buildingComponent = component
        cls.buildingComponentDict = componentdict
        
        cls.buildUpdateGhost(componentdict)
        
        cls.transportBent = "Turn" in componentdict["displayName"]
    
    @classmethod
    def buildCheckOccipied(cls, pos, returnBool = False):
        if cls.buildGhost is not None:
            width, height = cls.buildGhost.component["size"]
            
            if (cls.buildingRotation.value + 90) % 180 == 0:
                width, height = height, width

            if returnBool:
                return any((pos[0] + i, pos[1] + j) in dec.occupiedSpaces for i in range(width) for j in range(height))

            if any((pos[0] + i, pos[1] + j) in dec.occupiedSpaces for i in range(width) for j in range(height)):
                cls.buildGhost.image = cls.buildGhost.redImage
            else:
                cls.buildGhost.image = cls.buildGhost.normalImage
        
    @classmethod
    def buildSetPosition(cls, pos):
        cls.buildingPosition = dec.screenToWorld(pos)
        
        cls.buildCheckOccipied(cls.buildingPosition)
        
    @classmethod
    def buildSetRotation(cls, direction):
        cls.buildingRotation = direction
        
        if len(cls.dragGhosts) == 0:
            cls.buildUpdateGhost(cls.buildingComponentDict)
        
    @classmethod
    def buildRotateClockwise(cls):
        cls.buildingFlip = (False, False)
        cls.buildSetRotation(fac.Directions((cls.buildingRotation.value + 90) % 360))
    
    @classmethod
    def buildFlip(cls, rotation = None):
        if rotation is None:
            rotation = cls.buildingRotation
            
        if rotation is fac.Directions.North or rotation is fac.Directions.South:
            cls.buildingFlip = (cls.buildingFlip[0] ^ True, False)
            
        elif rotation is fac.Directions.East or rotation is fac.Directions.West:
            cls.buildingFlip = (False, cls.buildingFlip[1] ^ True)
        
        if len(cls.dragGhosts) == 0:
            cls.buildUpdateGhost(cls.buildingComponentDict)
    
    @classmethod
    def build(cls, factory):
        if cls.buildingComponent is not None:
            # flip flips for transports cause they weird
            if isinstance(cls.buildingComponent, fac.Transport):
                placeComponent(factory, cls.buildingComponent, cls.buildingPosition, cls.buildingRotation, (cls.buildingFlip[1], cls.buildingFlip[0]), cls.transportBent)
            else:
                placeComponent(factory, cls.buildingComponent, cls.buildingPosition, cls.buildingRotation, cls.buildingFlip, cls.transportBent)
        
    @classmethod
    def findDragPositions(cls, xfirst = True):
        dx = abs(cls.initialDragPosition[0] - cls.finalDragPosition[0])
        directionx = fac.Directions.East if cls.initialDragPosition[0] - cls.finalDragPosition[0] < 0 else fac.Directions.West
        signx = 1 if cls.initialDragPosition[0] - cls.finalDragPosition[0] < 0 else -1

        dy = abs(cls.initialDragPosition[1] - cls.finalDragPosition[1])
        directiony = fac.Directions.North if cls.initialDragPosition[1] - cls.finalDragPosition[1] > 0 else fac.Directions.South        
        signy = -1 if cls.initialDragPosition[1] - cls.finalDragPosition[1] > 0 else 1
        
        if xfirst:
            positions  = [(cls.initialDragPosition[0] + (x * signx), cls.initialDragPosition[1]) for x in range(dx)]
            positions += [(cls.initialDragPosition[0] + (dx * signx), cls.initialDragPosition[1] + (y * signy)) for y in range(dy + 1)]
        else:
            positions  = [(cls.initialDragPosition[0], cls.initialDragPosition[1] + (y * signy)) for y in range(dy)]
            positions += [(cls.initialDragPosition[0] + (x * signx), cls.initialDragPosition[1] + (dy * signy)) for x in range(dx + 1)]
        
        return positions, dx, directionx, dy, directiony
            
    @classmethod
    def startBuildDrag(cls, factory, pos):
        cls.initialDragPosition = dec.screenToWorld(pos)
        
        cls.buildGhost.destroy()
        cls.buildGhost = None
        
    @classmethod
    def updateBuildDrag(cls, factory, pos):
        cls.finalDragPosition = dec.screenToWorld(pos)
        
        cls.destroyGhosts()
    
        positions, dx, directionx, dy, directiony = cls.findDragPositions(xfirst = cls.dragxfirst)
        
        if 0 < dx < 2 and dy == 0:
            cls.dragxfirst = True
        elif 0 < dy < 2 and dx == 0:
            cls.dragxfirst = False
            
        xfirst = cls.dragxfirst
        
        flipCondition = lambda: (((directionx is fac.Directions.East and directiony is fac.Directions.North) or (directionx is fac.Directions.West and directiony is fac.Directions.South)) and i <= dx and dx != 0) if xfirst else (((directionx is fac.Directions.West and directiony is fac.Directions.North) or (directionx is fac.Directions.East and directiony is fac.Directions.South)) and i <= dy and dy != 0)
        directionCondition = lambda: i <= dx and dx != 0 if xfirst else dx != 0 and (dy == 0 or i > dy)
        bentCondition = lambda: i == dx and dx != 0 and dy != 0 if xfirst else i == dy and dx != 0 and dy != 0
        
        for i, pos in enumerate(positions):
            if flipCondition():
                cls.buildFlip(directionx if xfirst else directiony)
            
            cls.createGhost(cls.buildingComponentDict, pos,
                           directionx if directionCondition() else directiony,
                           cls.buildingFlip, bent = bentCondition())
            
            if flipCondition():
                cls.buildFlip(directionx if xfirst else directiony)
        
        if cls.buildGhost is not None:
            cls.buildGhost.destroy()
            cls.buildGhost = None
        
    @classmethod
    def endBuildDrag(cls, factory):
        cls.destroyGhosts()
        
        cls.buildUpdateGhost(cls.buildingComponentDict)
        
        positions, dx, directionx, dy, directiony = cls.findDragPositions(xfirst = cls.dragxfirst)
            
        xfirst = cls.dragxfirst
        
        flipCondition = lambda: (((directionx is fac.Directions.East and directiony is fac.Directions.North) or (directionx is fac.Directions.West and directiony is fac.Directions.South)) and i <= dx and dx != 0) if xfirst else (((directionx is fac.Directions.West and directiony is fac.Directions.North) or (directionx is fac.Directions.East and directiony is fac.Directions.South)) and i <= dy and dy != 0)
        directionCondition = lambda: i <= dx and dx != 0 if xfirst else dx != 0 and (dy == 0 or i > dy)
        bentCondition = lambda: i == dx and dx != 0 and dy != 0 if xfirst else i == dy and dx != 0 and dy != 0
        
        for i, pos in enumerate(positions):
            if flipCondition():
                cls.buildFlip(directionx if xfirst else directiony)
                
            placeComponent(factory, cls.buildingComponent, pos,
                           directionx if directionCondition() else directiony,
                           (cls.buildingFlip[1], cls.buildingFlip[0]), bent = bentCondition())
            
            if flipCondition():
                cls.buildFlip(directionx if xfirst else directiony)
        