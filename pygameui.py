from pygame import *
from typing import Literal
from random import uniform, randint
from math import sin, cos, radians
from collections import OrderedDict

font.init()

defaultStyle = {
    "color": (200, 200, 200),
    "outline": 0,
    "outlineColor": (0, 0, 0),
    "fontSize": 32,
    "font": "fonts/pixelfont.ttf",
    "textColor": (0, 0, 0),
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
    return (
        int(start[0] + (end[0] - start[0]) * t),
        int(start[1] + (end[1] - start[1]) * t),
        int(start[2] + (end[2] - start[2]) * t)
    )

def randomColorShift(color, uncertainty):
    return tuple(min(255, max(0, int(c + uniform(-uncertainty, uncertainty)))) for c in color)

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
    
    def __init__(self, x, y, w, h, z = 0, 
                 action = lambda: ..., hoverAction = lambda: ..., hoveredOffAction = lambda: ...,
                 style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, style = style, **kwargs)
        
        self.action = action
        self.hoverAction = hoverAction
        self.hoveredOffAction = hoveredOffAction
        
        self.darkeningAmount = style["darkeningAmount"]
        self.lighteningAmount = style["lighteningAmount"]
        
        self._OriginalColor = style["color"]
        self._OriginalOutlineColor = style["outlineColor"]
        
        self._needsReset = False
        
        Button.buttonInstances.append(self)
    
    def onHover(self):
        self.color = lighten(self._OriginalColor, self.lighteningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.lighteningAmount)
        self.hoverAction()
        
    def onPress(self):
        self.color = lighten(self._OriginalColor, self.darkeningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.darkeningAmount)
    
    def resetColor(self):
        self.color = self._OriginalColor
        self.outlineColor = self._OriginalOutlineColor
        self.hoveredOffAction()
    
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
    def __init__(self, x, y, w, h, z = 0, text = "",
                 action = lambda: ..., hoverAction = lambda: ..., hoveredOffAction = lambda: ...,
                 style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, text = text, action = action, hoverAction = hoverAction, hoveredOffAction = hoveredOffAction, style = style, **kwargs)
        
        self._OriginalTextColor = style["textColor"]
    
    def onHover(self):
        self.color = lighten(self._OriginalColor, self.lighteningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.lighteningAmount)
        self.textColor = lighten(self._OriginalTextColor, self.lighteningAmount)
        self.hoverAction()
        
    def onPress(self):
        self.color = lighten(self._OriginalColor, self.darkeningAmount)
        self.outlineColor = lighten(self._OriginalOutlineColor, self.darkeningAmount)
        self.textColor = lighten(self._OriginalTextColor, self.darkeningAmount)
    
    def resetColor(self):
        self.color = self._OriginalColor
        self.outlineColor = self._OriginalOutlineColor
        self.textColor = self._OriginalTextColor
        self.hoveredOffAction()

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
    def __init__(self, x, y, w, h, z = 0, image = noTexture,
                 action = lambda: ..., hoverAction = lambda: ..., hoveredOffAction = lambda: ...,
                 style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, image = image, action = action, hoverAction = hoverAction, hoveredOffAction = hoveredOffAction, style = style, **kwargs)
        
        self.lighteningAmount = (255 * self.lighteningAmount) - 255
        self.darkeningAmount *= 255
    
    def onHover(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.lighteningAmount, self.lighteningAmount, self.lighteningAmount), special_flags = BLEND_RGB_ADD)
        self.hoverAction()
        
    def onPress(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.darkeningAmount, self.darkeningAmount, self.darkeningAmount), special_flags = BLEND_RGB_MULT)
    
    def resetColor(self):
        self.image = self._OriginalImage
        self.hoveredOffAction()

class TextImageButton(Button, Label, Image):
    def __init__(self, x, y, w, h, z = 0, text = "", image = noTexture,
                 action = lambda: ..., hoverAction = lambda: ..., hoveredOffAction = lambda: ...,
                 style = defaultStyle, **kwargs):
        super().__init__(x, y, w, h, z, text = text, image = image, action = action, hoverAction = hoverAction, hoveredOffAction = hoveredOffAction, style = style, **kwargs)
        
        self._OriginalTextColor = style["textColor"]
        
        self.lighteningAmount = (255 * self.lighteningAmount) - 255
        self.darkeningAmount *= 255
    
    def onHover(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.lighteningAmount, self.lighteningAmount, self.lighteningAmount), special_flags = BLEND_RGB_ADD)
        self.textColor = lighten(self._OriginalTextColor, self.lighteningAmount)
        self.hoverAction()
        
    def onPress(self):
        self.image = self._OriginalImage.copy()
        self.image.fill((self.darkeningAmount, self.darkeningAmount, self.darkeningAmount), special_flags = BLEND_RGB_MULT)
        self.textColor = lighten(self._OriginalTextColor, self.darkeningAmount)
    
    def resetColor(self):
        self.image = self._OriginalImage
        self.textColor = self._OriginalTextColor
        self.hoveredOffAction()
        
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

class Particle():
    __slots__ = (
        "x", "y", "w", "h",
        "worldX", "worldY",
        "localX", "localY",
        "xOffset", "yOffset",
        "xDirection", "yDirection",
        "speedOffset",
        "lifetime", "totalLifetime",
        "wStart", "hStart",
        "startColor", "endColor",
        "color", "opacity",
        "image", "space"
    )

    def __init__(self, x, y, w, h, image = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.worldX = 0
        self.worldY = 0

        self.localX = 0
        self.localY = 0

        self.xOffset = 0
        self.yOffset = 0

        self.xDirection = 0
        self.yDirection = 0
        self.speedOffset = 0

        self.lifetime = 0
        self.totalLifetime = 0

        self.wStart = 0
        self.hStart = 0

        self.startColor = (0, 0, 0)
        self.endColor = (0, 0, 0)

        self.color = (0, 0, 0)
        self.opacity = 255

        self.image = image
        self.space = "Local"

class ParticleSystem():
    instances = []
    worldRelativeTo = (0, 0)
    
    surfaceCache = OrderedDict()
    maxCachedSurfaces = 1024
    
    solidCache = OrderedDict()
    maxSolidCache = 4096
        
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.hidden = False
        
        self.activeParticles: list[Particle] = []
        
        self.xOffset = 0
        self.yOffset = 0
        
        #* main settings
        
        self.maxLifetime = 3
        self.maxLifetimeUncerainty = 1
        
        self.particleSpace: Literal["World", "Local"] = "Local" 
        
        self.particleImage = None
        
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
        self.startColorUncertainty = 50
        self.endColorUncertainty = 20
        
        # can add rotation later
        
        #* emission settings
        
        self.burstEmission = 2
        self.burstUncertainty = 1
        
        self._emissionSpeed = 0.5
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
            for _ in range(self.burstEmission + randint(-self.burstUncertainty, self.burstUncertainty)):
                particle = Particle(0, 0, *self.size, image = self.particleImage)
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
                
                particle.w = self.size[0] * size
                particle.h = self.size[1] * size
                
                particle.startColor = randomColorShift(self.startColor, self.startColorUncertainty)
                particle.endColor = randomColorShift(self.endColor, self.endColorUncertainty)
                particle.opacity = self.startOpacity
                
                self.activeParticles.append(particle)
                
                particle.space = self.particleSpace

                particle.localX = particle.x
                particle.localY = particle.y

                if particle.space == "World":
                    particle.worldX = (particle.localX + self.x + self.xOffset + ParticleSystem.worldRelativeTo[0])
                    particle.worldY = (particle.localY + self.y + self.yOffset + ParticleSystem.worldRelativeTo[1])
                
            self.timer = 0
            self.currentEmissionSpeed = self.emissionSpeed + uniform(-self.emissionSpeedUncertainty, self.emissionSpeedUncertainty)
        
        # step particles
        alive = []

        for particle in self.activeParticles:
            particle.lifetime -= dt

            if particle.lifetime <= 0:
                continue
                
            t = max(0, min(1, 1 - particle.lifetime / particle.totalLifetime))

            speed = max(0, lerp(self.startSpeed, self.endSpeed, t) + particle.speedOffset)

            if particle.space == "Local":
                particle.xOffset += particle.xDirection * speed * dt
                particle.yOffset += particle.yDirection * speed * dt

                particle.x = (self.x + particle.localX + particle.xOffset + self.xOffset)
                particle.y = (self.y + particle.localY + particle.yOffset + self.yOffset)

            else:
                particle.worldX += particle.xDirection * speed * dt
                particle.worldY += particle.yDirection * speed * dt
            
            particle.w = self.size[0] * lerp(particle.wStart, self.endSize, t)
            particle.h = self.size[1] * lerp(particle.hStart, self.endSize, t)
            
            particle.color = lerpColor(particle.startColor, particle.endColor, t)
            particle.opacity = int(lerp(self.startOpacity, self.endOpacity, t))
        
            alive.append(particle)

        self.activeParticles = alive
        
        if self.destroying and not self.activeParticles:
            ParticleSystem.instances.remove(self)
    
    def destroy(self):
        self.destroying = True
    
    def draw(self, window):
        if self.hidden:
            return

        cameraX, cameraY = ParticleSystem.worldRelativeTo
        screenW, screenH = window.get_size()

        getSolid = ParticleSystem.getSolidSurface
        getImage = ParticleSystem.getSurface

        blits = []

        for particle in self.activeParticles:
            if particle.opacity <= 0:
                continue

            w = max(1, int(particle.w))
            h = max(1, int(particle.h))

            if particle.space == "World":
                x = int(particle.worldX - cameraX)
                y = int(particle.worldY - cameraY)
            else:
                x = int(particle.x)
                y = int(particle.y)

            # offscreen culling
            if (x + w <= 0 or y + h <= 0 or x >= screenW or y >= screenH):
                continue

            if particle.image is None:
                surface = getSolid(w, h, particle.color, particle.opacity)
            else:
                surface = getImage(particle, w, h)

            blits.append((surface, (x, y)))

        if blits:
            window.blits(blits, doreturn=False)

    @classmethod
    def getSurface(cls, particle, w, h):
        # reduce colors
        color = (
            particle.color[0] // 32 * 32,
            particle.color[1] // 32 * 32,
            particle.color[2] // 32 * 32
        )

        opacity = particle.opacity // 32 * 32

        key = (id(particle.image), w, h, color, opacity)

        cache = cls.surfaceCache

        surface = cache.get(key)

        if surface is not None:
            cache.move_to_end(key)
            return surface

        if particle.image is None:
            surface = Surface((w, h), SRCALPHA)
            surface.fill((*color, opacity))

        else:
            surface = transform.scale(particle.image, (w, h)).convert_alpha()

            tint = Surface((w, h), SRCALPHA)
            tint.fill((*color, 255))

            surface.blit(tint, (0, 0), special_flags = BLEND_RGBA_MULT)

            surface.set_alpha(opacity)

        cache[key] = surface

        if len(cache) > cls.maxCachedSurfaces:
            cache.popitem(last = False)

        return surface

    @classmethod
    def getSolidSurface(cls, w, h, color, opacity):
        # quantise colour and opacity
        r = color[0] & 0xE0
        g = color[1] & 0xE0
        b = color[2] & 0xE0
        a = opacity & 0xE0

        key = (w, h, r, g, b, a)

        cache = cls.solidCache
        surface = cache.get(key)

        if surface is not None:
            cache.move_to_end(key)
            return surface

        surface = Surface((w, h), SRCALPHA)
        surface.fill((r, g, b, a))

        cache[key] = surface

        if len(cache) > cls.maxSolidCache:
            cache.popitem(last=False)

        return surface

    @classmethod
    def updateAll(cls, dt):
        for system in cls.instances.copy():
            system.update(dt)
    
    @classmethod
    def drawAll(cls, window):
        for system in cls.instances.copy():
            system.draw(window)
    
    @property
    def emissionSpeed(self):
        return self._emissionSpeed
    
    @emissionSpeed.setter
    def emissionSpeed(self, value):
        self._emissionSpeed = value
        self.currentEmissionSpeed = value
                