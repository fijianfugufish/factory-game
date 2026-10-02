from pygame import *

defaultStyle = {
    "color": (200, 200, 200),
    "outline": 10,
    "outlineColor": (0, 0, 0),
    "fontSize": 32,
    "font": "Comic Sans",
    "textColor": (0, 255, 0),
    "textPadx": 5,
    "textPady": 5,
    "darkeningAmount": 0.8,
    "lighteningAmount": 1.2,
}

noTexture = image.load("NoTexture.png").convert()

def lighten(color, intensity):
    return tuple(min(255, int(c * intensity)) for c in color)

class UI():
    instances = []
    
    def __init__(self, x, y, w, h, style = defaultStyle, **kwargs):
        super().__init__(**kwargs)
        
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        
        self.color = style["color"]
        self.outline = style["outline"]
        self.outlineColor = style["outlineColor"]
        
        self.hidden = False
        
        self.rect = Rect(x, y, w, h)
        
        UI.instances.append(self)
    
    def destroy(self):
        UI.instances.remove(self)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self.rect.x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self.rect.y = value
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = value
        self.rect.w = value
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
        self.rect.h = value
    
    def draw(self, window):
        if self.hidden: return
        
        draw.rect(window, self.outlineColor, Rect(self.x - self.outline, self.y  - self.outline, self.w + self.outline * 2, self.h + self.outline * 2))
        draw.rect(window, self.color, self.rect)
    
    @classmethod
    def drawAll(cls, window):
        for i in cls.instances:
            i.draw(window)

class Button(UI):
    buttonInstances = []
    
    def __init__(self, x, y, w, h, action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, style = style, **kwargs)
        
        self.action = action
        
        self.darkeningAmount = style["darkeningAmount"]
        self.lighteningAmount = style["lighteningAmount"]
        
        self._OriginalColor = style["color"]
        self._OriginalOutlineColor = style["outlineColor"]
        
        self._needsReset = False
        
        Button.buttonInstances.append(self)
    
    def onHover(self):
        self.color = lighten(self._OriginalColor, self.lighteningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.lighteningAmount)
        
    def onPress(self):
        self.color = lighten(self._OriginalColor, self.darkeningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.darkeningAmount)
    
    def resetColor(self):
        self.color = self._OriginalColor
        self.outlineColor = self._OriginalOutlineColor
    
    def onRelease(self):
        self.onHover()
        self.action()
    
    def handleButton(self, mousePos, event):
        if self.hidden: return
        
        if self.rect.collidepoint(mousePos):
            if not self._needsReset:
                self.onHover()
                
            self._needsReset = True
            
            if event == MOUSEBUTTONDOWN:
                self.onPress()
            elif event == MOUSEBUTTONUP:
                self.onRelease()
        else:
            if self._needsReset:
                self.resetColor()
                self._needsReset = False
    
    def setColor(self, value):
        self.color = value
        self._OriginalColor = value
    
    def setOutlineColor(self, value):
        self.outlineColor = value
        self._OriginalOutlineColor = value
    
    def destroy(self):
        UI.instances.remove(self)
        Button.buttonInstances.remove(self)
    
    @classmethod
    def handleAllButtons(cls, mousePos, event):
        for i in cls.buttonInstances:
            i.handleButton(mousePos, event)
    
        
class Label(UI):
    def __init__(self, x, y, w, h, text = "", style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, style = style, **kwargs)
        
        self.font = font.SysFont(style["font"], style["fontSize"])
        self.text = text
        self.textColor = style["textColor"]
        self.textPadx = style["textPadx"]
        self.textPady = style["textPady"]
    
    def draw(self, window):
        if self.hidden: return
        
        draw.rect(window, self.outlineColor, Rect(self.x - self.outline, self.y  - self.outline, self.w + self.outline * 2, self.h + self.outline * 2))
        draw.rect(window, self.color, self.rect)
        
        window.blit(self.font.render(self.text, False, self.textColor), (self.x + self.textPadx, self.y + self.textPady))
    
class TextButton(Button, Label):
    def __init__(self, x, y, w, h, text = "", action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, text = text, action = action, style = style, **kwargs)
        
        self._OriginalTextColor = style["textColor"]
    
    def onHover(self):
        self.color = lighten(self._OriginalColor, self.lighteningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.lighteningAmount)
        self.textColor = lighten(self._OriginalTextColor, self.lighteningAmount)
        
    def onPress(self):
        self.color = lighten(self._OriginalColor, self.darkeningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.darkeningAmount)
        self.textColor = lighten(self._OriginalTextColor, self.darkeningAmount)
    
    def resetColor(self):
        self.color = self._OriginalColor
        self.outlineColor = self._OriginalOutlineColor
        self.textColor = self._OriginalTextColor

class Image(UI):
    def __init__(self, x, y, w, h, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, style = style, **kwargs)
        
        self.x = x
        self.y = y
        self._w = w
        self._h = h
        self._rotation = 0
        
        self.hidden = False
        
        self._image = transform.scale(image, (w, h))
        self._OriginalImage = self.image
        
        self._surface = Surface((w, h))
        
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self._rotation = value % 360
        
        center = self.rect.center
        
        self.image = transform.rotate(self._OriginalImage, -self._rotation)
        
        self.rect = self.image.get_rect(center = center)
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = value
        self.rect.w = value
        self.image = transform.scale(image, (self.w, self.h))
        self._OriginalImage = transform.scale(image, (self.w, self.h))
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
        self.rect.h = value
        self.image = transform.scale(image, (self.w, self.h))
    
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = transform.scale(value, (self.w, self.h))
    
    def setFlipped(self, x = False, y = False):
        rotated_OriginalImage = transform.rotate(self._OriginalImage, self.rotation)
        self.image = transform.flip(rotated_OriginalImage, x, y)
    
    def draw(self, window):
        if self.hidden: return
        
        window.blit(self.image, (self.x, self.y))
    
class ImageButton(Button, Image):
    def __init__(self, x, y, w, h, image = noTexture, action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, image = image, action = action, style = style, **kwargs)
        
        self.lighteningAmount = (255 * self.lighteningAmount) - 255
        self.darkeningAmount *= 255
    
    def onHover(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.lighteningAmount, self.lighteningAmount, self.lighteningAmount), special_flags = BLEND_RGB_ADD)
        
    def onPress(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.darkeningAmount, self.darkeningAmount, self.darkeningAmount), special_flags = BLEND_RGB_MULT)
    
    def resetColor(self):
        self.image = self._OriginalImage

class Sprite(Image):
    def __init__(self, x, y, w, h, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, image = image, style = style, **kwargs)

class AnimatableSprite(Sprite):
    animationInstances = []
    
    def __init__(self, x, y, w, h, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, image = image, style = style, **kwargs)
        
        self.animations = {}
        self.currentAnimation = None
        
        self.frame = 0
        self.animationTimer = 0
        self.animationFPS = 10
        
        self._originalAnimations = {}
        
        self.animationInstances.append(self)
    
    def addAnimation(self, name, *args):
        """put frames of animation in args after name"""
        
        self.animations[name] = [transform.scale(image, (self.w, self.h)) for image in args]
        self._originalAnimations[name] = [frames.copy() for frames in self.animations[name]]
    
    def startAnimation(self, animation, fps):
        if self.currentAnimation == animation: return
        
        self.currentAnimation = animation
        self.animationFPS = fps
        self.frame = 0
        self.animationTimer = 0
        
        self.image = self.animations[animation][0]
    
    def updateAnimation(self, dt):
        if self.hidden or self.currentAnimation is None: return
        
        frames = self.animations[self.currentAnimation]
        
        self.animationTimer += dt
        
        frameTime = 1 / self.animationFPS
        
        while self.animationTimer > frameTime:
            self.animationTimer -= frameTime
            
            self.frame += 1
            self.frame %= len(self.animations[self.currentAnimation])
            
            self.image = frames[self.frame]
    
    def destroy(self):
        UI.instances.remove(self)
        AnimatableSprite.animationInstances.remove(self)
    
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self._rotation = value % 360
        
        center = self.rect.center
        
        self.image = transform.rotate(self._OriginalImage, -self._rotation)
        
        self.rect = self.image.get_rect(center = center)
        
        for animation in self.animations:
            for i, frame in enumerate(self._originalAnimations[animation]):
                frame = transform.rotate(frame, -self._rotation)
                self.animations[animation][i] = frame
    
    def setFlipped(self, x = False, y = False):
        center = self.rect.center
        
        rotated_OriginalImage = transform.rotate(self._OriginalImage, self.rotation)
        self.image = transform.flip(rotated_OriginalImage, x, y)
        
        self.rect = self.image.get_rect(center = center)
        
        for animation in self.animations:
            for i, frame in enumerate(self._originalAnimations[animation]):
                rotatedFrame = transform.rotate(frame, self.rotation)
                frame = transform.flip(rotatedFrame, x, y)
                self.animations[animation][i] = frame
    
    @classmethod
    def updateAllAnimations(cls, dt):
        for i in cls.animationInstances:
            i.updateAnimation(dt)