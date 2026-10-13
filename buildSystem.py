from pygame import *
import pygameui
import decodeFactory as dec
from factory import Items

_ComponentTableImage = image.load("Images/UI/Buttons/ComponentTable.png").convert_alpha()
_SmallButtonImage = image.load("Images/UI/Buttons/SmallButtonPreset.png").convert_alpha()
_LongButtonImage = image.load("Images/UI/Buttons/LongButtonPreset.png").convert_alpha()
_ComponentBGImage = image.load("Images/UI/Buttons/ComponentIconBackground.png").convert_alpha()

_producers = {
    "BasicDrill": {
        "image": dec._BasicDrillFrames[0],
        "displayName": "Basic Drill",
        "price": [Items.IronOre, 4],
    },
}

_machines = {
    "BasicFurnace": {
        "image": dec._BasicFurnaceFrames[0],
        "displayName": "Basic Furnace",
        "price": [Items.IronOre, 4],
    },
    "BasicExtruder": {
        "image": dec._BasicExtruderFrames[0],
        "displayName": "Basic Extruder",
        "price": [Items.IronOre, 4],
    },
    "BasicPress": {
        "image": dec._BasicPressFrames[0],
        "displayName": "Basic Press",
        "price": [Items.IronOre, 4],
    },
    "BasicAssembler": {
        "image": dec._BasicAssemblerFrames[0],
        "displayName": "Basic Assembler",
        "price": [Items.IronOre, 4],
    },
    "BasicContainer":{
        "image": dec._BasicContainerSprite,
        "displayName": "Basic Container",
        "price": [Items.IronOre, 4],
    },
}

_transports = {
    "BasicConveyor": {
        "image": dec._BasicConveyorStraightFrames[0],
        "displayName": "Basic Conveyor",
        "price": [Items.IronOre, 4],
    },
    "BasicTurnConveyor": {
        "image": dec._BasicConveyorTurnFrames[0],
        "displayName": "Basic Turn Conveyor",
        "price": [Items.IronOre, 4],
    },
    "4WayDistributor": {
        "image": dec._FourWayDistributor,
        "displayName": "4 Way Distributor",
        "price": [Items.IronOre, 4],
    },
    "2WayDistributor": {
        "image": dec._TwoWayDistributor,
        "displayName": "2 Way Distributor",
        "price": [Items.IronOre, 4],
    },
}

winy = dec.winy
winx = dec.winx

def _pixelToScreen(px):
    return (px / 16) * 64

def _screenToPixel(px):
    return (px / 64) * 16

class BuildMenu():
    @classmethod
    def init(cls):
        menux, menuy = 0, winy - _pixelToScreen(128 + 16)
        menuw, menuh = _pixelToScreen(80), _pixelToScreen(128)
        
        cls.menupadx, cls.menupady = _pixelToScreen(8 / 5), _pixelToScreen(8 / 5)
        
        # table of components that will hold selectable icons
        cls.ComponentMenu = pygameui.Image(0, 0, 
                                            menuw, menuh,
                                            image = _ComponentTableImage)
        
        cls.ProducersButton = pygameui.TextImageButton(0, winy - _pixelToScreen(16),
                                        _pixelToScreen(80), _pixelToScreen(16),
                                        image = _LongButtonImage, text = "Producers",
                                        action = cls.menuSetProducers)
        cls.MachinesButton = pygameui.TextImageButton(_pixelToScreen(80), winy - _pixelToScreen(16),
                                        _pixelToScreen(80), _pixelToScreen(16),
                                        image = _LongButtonImage, text = "Machines",
                                        action = cls.menuSetMachines)
        cls.TransportsButton = pygameui.TextImageButton(_pixelToScreen(80 * 2), winy - _pixelToScreen(16),
                                        _pixelToScreen(80), _pixelToScreen(16),
                                        image = _LongButtonImage, text = "Transports",
                                        action = cls.menuSetTransports)
        cls.whoknowsbutton = pygameui.TextImageButton(_pixelToScreen(80 * 3), winy - _pixelToScreen(16),
                                        _pixelToScreen(80), _pixelToScreen(16),
                                        image = _LongButtonImage, text = "Polluters")
        
        cls.MenuParent = pygameui.Parent(menux, menuy, 2)
        
        
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
        
        image = _ComponentBGImage.copy()
        image.blit(transform.scale(item["image"],
                                   (_screenToPixel(width - cls.menupadx),
                                    _screenToPixel(height - cls.menupady))),
                   (cls.menupadx / 4, cls.menupady / 4))
        
        menuItem = pygameui.ImageButton(xoffset + (cls.menupadx * 2), yoffset + (cls.menupady * 2),
                                        width, height, 3, image = image)
        
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
        