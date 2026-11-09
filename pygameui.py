from pygame import *
from typing import Literal
from random import uniform
from math import sin, cos, radians

font.init()

defaultStyle = {
    "color": (200, 200, 200),
    "outline": 0,
    "outlineColor": (0, 0, 0),
    "fontSize": 32,
    "font": "fonts/pixelfont.ttf",
    "textColor": (0, 255, 0),
    "textPadx": 32,
    "textPady": 16,
    "darkeningAmount": 0.8,
    "lighteningAmount": 1.2,
}

noTexture = image.load("NoTexture.png").convert()

def lighten(color, intensity):
    return tuple(min(255, int(c * intensity)) for c in color)

def lerp(start, end, t):
    return start + (end - start) * t

def lerpColor(start, end, t):
    t = max(0, min(1, t))
    return tuple(int(lerp(s, e, t)) for s, e in zip(start, end))

class UI():
    instances = []
    
    def __init__(self, x, y, w, h, z = 0, style = defaultStyle, **kwargs):
        super().__init__(**kwargs)
        
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.z = z or 2
        
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
        
        if self.outline > 0:
            draw.rect(window, self.outlineColor, Rect(self.x - self.outline, self.y  - self.outline, self.w + self.outline * 2, self.h + self.outline * 2))
        
        draw.rect(window, self.color, self.rect)
    
    @classmethod
    def drawAll(cls, window):
        cls.instances.sort(key = lambda item: item.z)
        for i in cls.instances:
            i.draw(window)

class Button(UI):
    buttonInstances = []
    
    def __init__(self, x, y, w, h, z = 0, action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, style = style, **kwargs)
        
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
    
    def handleButton(self, mousePos, event) -> bool:
        """returns true if the button was interacted with"""
        
        if self.hidden: return False
        
        if self.rect.collidepoint(mousePos):
            if not self._needsReset:
                self.onHover()
                
            self._needsReset = True
            
            if event == MOUSEBUTTONDOWN:
                self.onPress()
            elif event == MOUSEBUTTONUP:
                self.onRelease()
                
            return True
        
        else:
            if self._needsReset:
                self.resetColor()
                self._needsReset = False
            
            return False
    
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
    def handleAllButtons(cls, mousePos, event) -> bool:
        """returns true if a button was interacted with"""
        
        returnValues = []
        
        for i in cls.buttonInstances:
            returnValues.append(i.handleButton(mousePos, event))
        
        return any(returnValues) 
        
class Label(UI):
    def __init__(self, x, y, w, h, z = 0, text = "", style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, style = style, **kwargs)
        
        self.font = font.Font(style["font"], style["fontSize"])
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
    def __init__(self, x, y, w, h, z = 0, text = "", action = lambda: ..., style = defaultStyle, **kwargs):
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
    def __init__(self, x, y, w, h, z = 0, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, style = style, **kwargs)
        
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
        self.image = transform.scale(self.image, (self.w, self.h))
        self._OriginalImage = transform.scale(self._OriginalImage, (self.w, self.h))
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
        self.rect.h = value
        self.image = transform.scale(self.image, (self.w, self.h))
        self._OriginalImage = transform.scale(self._OriginalImage, (self.w, self.h))
    
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = transform.scale(value, (self.w, self.h))
    
    def changeImage(self, value):
        self._image = transform.scale(value, (self.w, self.h))
        self._OriginalImage = self._image
    
    def setFlipped(self, x = False, y = False):
        rotated_OriginalImage = transform.rotate(self._OriginalImage, -self.rotation)
        self.image = transform.flip(rotated_OriginalImage, x, y)
    
    def draw(self, window):
        if self.hidden: return
        
        window.blit(self.image, (self.x, self.y))
    
class ImageButton(Button, Image):
    def __init__(self, x, y, w, h, z = 0, image = noTexture, action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, image = image, action = action, style = style, **kwargs)
        
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

class TextImageButton(Button, Label, Image):
    def __init__(self, x, y, w, h, z = 0, text = "", image = noTexture, action = lambda: ..., style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, text = text, image = image, action = action, style = style, **kwargs)
        
        self._OriginalTextColor = style["textColor"]
        
        self.lighteningAmount = (255 * self.lighteningAmount) - 255
        self.darkeningAmount *= 255
    
    def onHover(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.lighteningAmount, self.lighteningAmount, self.lighteningAmount), special_flags = BLEND_RGB_ADD)
        self.textColor = lighten(self._OriginalTextColor, self.lighteningAmount)
        
    def onPress(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.darkeningAmount, self.darkeningAmount, self.darkeningAmount), special_flags = BLEND_RGB_MULT)
        self.textColor = lighten(self._OriginalTextColor, self.darkeningAmount)
    
    def resetColor(self):
        self.image = self._OriginalImage
        self.textColor = self._OriginalTextColor
        
    def draw(self, window):
        if self.hidden: return
        
        window.blit(self.image, (self.x, self.y))
        window.blit(self.font.render(self.text, False, self.textColor), (self.x + self.textPadx, self.y + self.textPady))

class Parent():
    """class in which all children ui elements depend on the parent in some way"""
    
    def __init__(self, x, y, z = 0, **kwargs):
        super().__init__(**kwargs)
        
        self._x = x
        self._y = y
        self._z = z
        
        self._hidden = False
        
        # children will treat the parents hidden as their own, and x y and z as origin
        
        self.children: dict[UI, list[float | bool]] = {}
        self.rootChild = None
        # index by element, holds original x y z and hidden properties
    
    def addChild(self, child):
        values = [child.x, child.y, child.z, child.hidden]
        self.children[child] = values
        
        child.x = values[0] + self.x
        child.y = values[1] + self.y
        child.z = values[2] + self.z
        child.hidden = values[3] or self.hidden
    
    def addChildren(self, *children):
        for child in children:
            self.addChild(child)
    
    def removeChild(self, child):
        del self.children[child]
    
    def destroyChild(self, child):
        self.removeChild(child)
        
        child.destroy()
        
    def destroyAllChildren(self):
        toRemove = []
        
        for child in self.children:
            if child is self.rootChild: continue
            
            toRemove.append(child)
            
            child.destroy()
        
        for child in toRemove:
            self.removeChild(child)
    
    def destroy(self):
        self.destroyAllChildren()
        
        if self.rootChild is not None:
            self.rootChild.destroy()
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value

        for child, values in self.children.items():
            child.x = values[0] + self.x + getattr(child, "xOffset", 0)
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value

        for child, values in self.children.items():
            child.y = values[1] + self.y + getattr(child, "yOffset", 0)

    @property
    def z(self):
        return self._z
    
    @z.setter
    def z(self, value):
        self._z = value
    
        for child, values in self.children.items():
            child.z = values[2] + self.z
    
    @property
    def hidden(self):
        return self._hidden
    
    @hidden.setter
    def hidden(self, value):
        self._hidden = value
        
        for child, values in self.children.items():
            child.hidden = values[3] or self.hidden
        
class Sprite(Image):
    def __init__(self, x, y, w, h, z = 0, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, image = image, style = style, **kwargs)

class AnimatableSprite(Sprite):
    animationInstances = []
    
    def __init__(self, x, y, w, h, z = 0, autoAnimate = True, image = noTexture, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, image = image, style = style, **kwargs)
        
        self.animations = {}
        self.currentAnimation = None
        
        self.frame = 0
        self.animationTimer = 0
        self.animationFPS = 10
        
        self.z = z
        
        self._originalAnimations = {}
        
        self.autoAnimate = autoAnimate
        
        if autoAnimate: self.animationInstances.append(self)
    
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
        if self.autoAnimate: AnimatableSprite.animationInstances.remove(self)
    
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
        
        rotated_OriginalImage = transform.rotate(self._OriginalImage, -self.rotation)
        self.image = transform.flip(rotated_OriginalImage, x, y)
        
        self.rect = self.image.get_rect(center = center)
        
        for animation in self.animations:
            for i, frame in enumerate(self._originalAnimations[animation]):
                rotatedFrame = transform.rotate(frame, -self.rotation)
                frame = transform.flip(rotatedFrame, x, y)
                self.animations[animation][i] = frame
    
    @classmethod
    def updateAllAnimations(cls, dt):
        for i in cls.animationInstances:
            i.updateAnimation(dt)

class Particle(UI):
    def __init__(self, x, y, w, h, z = 0, style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, style = style, **kwargs)
        
        self.lifetime = 0
        self.totalLifetime = 0
        self.opacity = 0
        
        self.wStart = 0
        self.hStart = 0
        
        self.xDirection = 0
        self.yDirection = 0
        
        self.xOffset = 0
        self.yOffset = 0
        
        self.worldX = 0
        self.worldY = 0
        
        self.speedOffset = 0
        
        self.space = "Local"
    
    def draw(self, window):
        if self.hidden:
            return

        surface = Surface(self.rect.size, SRCALPHA)
        surface.fill((*self.color, self.opacity))

        if self.space == "World":
            cameraX, cameraY = ParticleSystem.worldRelativeTo

            x = self.worldX - cameraX
            y = self.worldY - cameraY

        else:
            x = self.x
            y = self.y
        
        window.blit(surface, (x, y))

class ParticleSystem():
    instances = []
    worldRelativeTo = (0, 0)
        
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._hidden = False
        
        self.particles = Parent(self.x, self.y) 
        self.activeParticles: list[Particle] = []
        
        #* main settings
        
        self.maxLifetime = 3
        self.maxLifetimeUncerainty = 1
        
        self.particleSpace: Literal["World", "Local"] = "Local" #todo figure out how to make world work with camera movement
        
        #* over time settings
        
        self.startSize = 1
        self.endSize = 0
        self.sizeUncertainty = 0.7
        
        self.startOpacity = 255
        self.endOpacity = 0
        
        self.startSpeed = 5
        self.endSpeed = 20
        self.speedUncertainty = 10
        
        self.startColor = (50, 255, 100)
        self.endColor = (0, 0, 0)
        self.colorUncertainty = 0.2 #todo implement
        
        # can add rotation later
        
        #* emission settings
        
        self.burstEmission = 2
        self.burstUncertainty = 1
        
        self.emissionSpeed = 0.5
        self.emissionSpeedUncertainty = 0.2
        self.currentEmissionSpeed = self.emissionSpeed
        
        self.emissionType: Literal["Radial", "Area"] = "Area"
        
        self.emissionArea = (24, 24)
        self.emissionAngle = 135
        self.emissionArcWidth = 360
        
        self.size = (5, 5)

        self.timer = 0
        
        self.destroying = False
        
        ParticleSystem.instances.append(self)
    
    def update(self, dt):
        if self.hidden: return
        
        self.timer += dt 
        
        # create particles
        if not self.destroying and self.timer >= self.currentEmissionSpeed:
            for _ in range(self.burstEmission):
                particle = Particle(0, 0, *self.size)
                particle.color = self.startColor
                
                # add particle specific properties
                lifetime = self.maxLifetime + uniform(-self.maxLifetimeUncerainty, self.maxLifetimeUncerainty)
                particle.lifetime = lifetime
                particle.totalLifetime = lifetime
                
                angle = radians(self.emissionAngle + uniform(-self.emissionArcWidth / 2, self.emissionArcWidth / 2))
                
                particle.xDirection = sin(angle)
                particle.yDirection = cos(angle)
                    
                if self.emissionType == "Area":
                    particle.x = uniform(0, self.emissionArea[0])
                    particle.y = uniform(0, self.emissionArea[1])
                
                particle.speedOffset = uniform(-self.speedUncertainty, self.speedUncertainty)
                
                size = max(0, self.startSize + uniform(-self.sizeUncertainty, self.sizeUncertainty))
                
                particle.wStart = size
                particle.hStart = size
                
                particle.w *= size
                particle.h *= size
                
                particle.color = self.startColor
                particle.opacity = self.startOpacity
                
                self.activeParticles.append(particle)
                
                particle.space = self.particleSpace

                if particle.space == "Local":
                    self.particles.addChild(particle)

                else:
                    particle.worldX = particle.x + self.x + ParticleSystem.worldRelativeTo[0]
                    particle.worldY = particle.y + self.y + ParticleSystem.worldRelativeTo[1]
            
            self.timer = 0
            self.currentEmissionSpeed = self.emissionSpeed + uniform(-self.emissionSpeedUncertainty, self.emissionSpeedUncertainty)
        
        # step particles
        toRemove = []
        
        for particle in self.activeParticles:
            if particle.lifetime <= 0:
                particle.destroy()
                toRemove.append(particle)
                continue
                
            particle.lifetime -= dt
            
            t = max(0, min(1, 1 - particle.lifetime / particle.totalLifetime))

            speed = max(0, lerp(self.startSpeed, self.endSpeed, t) + particle.speedOffset)

            if particle.space == "Local":
                particle.xOffset += particle.xDirection * speed * dt
                particle.yOffset += particle.yDirection * speed * dt

                particle.x = self.x + self.particles.children[particle][0] + particle.xOffset
                particle.y = self.y + self.particles.children[particle][1] + particle.yOffset

            else:
                particle.worldX += particle.xDirection * speed * dt
                particle.worldY += particle.yDirection * speed * dt
            
            particle.w = self.size[0] * lerp(particle.wStart, self.endSize, t)
            particle.h = self.size[1] * lerp(particle.hStart, self.endSize, t)
            
            particle.color = lerpColor(self.startColor, self.endColor, t)
            particle.opacity = int(lerp(self.startOpacity, self.endOpacity, t))
        
        for particle in toRemove:
            if particle in self.particles.children:
                self.particles.removeChild(particle)

            self.activeParticles.remove(particle)

        if self.destroying and not self.activeParticles:
            ParticleSystem.instances.remove(self)
    
    def destroy(self):
        self.destroying = True

    @classmethod
    def updateAll(cls, dt):
        for i in cls.instances:
            i.update(dt)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self.particles.x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self.particles.y = value

    @property
    def z(self):
        return self._z
    
    @z.setter
    def z(self, value):
        self._z = value
        self.particles.z = value
    
    @property
    def hidden(self):
        return self._hidden
    
    @hidden.setter
    def hidden(self, value):
        self._hidden = value
        self.particles.hidden = value
                