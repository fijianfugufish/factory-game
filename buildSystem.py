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
    "BasicAssembler": {
        "image": dec._BasicAssemblerFrames[0],
        "displayName": "Basic Assembler",
        "size": (3, 2), 
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicAssembler,
    },
    "BasicContainer":{
        "image": dec._BasicContainerSprite,
        "displayName": "Basic Container",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.basicContainer,
    },
    "AdvancedFurnace": {
        "image": dec._AdvancedFurnaceFrames[0],
        "displayName": "Uranium Furnace",
        "size": (2, 2),
        "price": [fac.Items.IronOre, 4],
        "component": fac.advancedFurnace,
    },
}

_transports = {
    "BasicConveyor": {
        "image": dec._BasicConveyorStraightFrames[0],
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
        cls.buildingPosition = (0, 0)
        cls.buildingFlip = (False, False)
        cls.buildingRotation = fac.Directions.North
        
        cls.buildGhost = GhostComponent(0, 0, _pixelToScreen(16), _pixelToScreen(16), dec._BasicConveyorStraightFrames[0], _transports["BasicConveyor"])
        
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
        cls.buildGhost.x, cls.buildGhost.y = dec.worldToSreen(cls.buildingPosition)
    
    @classmethod
    def buildUpdateGhost(cls, component: dict | None = None):
        cls.buildGhost.destroy()
        
        if component is None:
            component = cls.buildGhost.component
            
        pos = dec.worldToSreen(cls.buildingPosition)
        width, height = dec.worldToSreen(component["size"])
        
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
    def buildSetComponent(cls, component, componentstr):
        cls.buildingComponent = component
        
        cls.buildUpdateGhost(componentstr)
    
    @classmethod
    def buildCheckOccipied(cls, pos):
        width, height = cls.buildGhost.component["size"]

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
        
        cls.buildUpdateGhost()
        
    @classmethod
    def buildRotateClockwise(cls):
        cls.buildingFlip = (False, False)
        cls.buildSetRotation(fac.Directions((cls.buildingRotation.value + 90) % 360))
    
    @classmethod
    def buildFlip(cls):
        if cls.buildingRotation is fac.Directions.North or cls.buildingRotation is fac.Directions.South:
            cls.buildingFlip = (cls.buildingFlip[0] ^ True, False)
            
        elif cls.buildingRotation is fac.Directions.East or cls.buildingRotation is fac.Directions.West:
            cls.buildingFlip = (False, cls.buildingFlip[1] ^ True)
        
        cls.buildUpdateGhost()
    
    @classmethod
    def build(cls, factory):
        if cls.buildingComponent is not None:
            placeComponent(factory, cls.buildingComponent, cls.buildingPosition, cls.buildingRotation, cls.buildingFlip)
            