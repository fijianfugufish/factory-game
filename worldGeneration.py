from pygame import *
import pygameui
from noise import pnoise2
from decodeFactory import cameraPos, lastCameraPos, worldToSreen, screenToWorld, winx, winy, getTileSize
from random import Random
from functools import lru_cache

CHUNKSIZE = 8
seed = 42

chunks: dict[tuple[int, int], "Chunk"] = {}

_lastVisibleChunk = None

#* ground
_DirtSprites = [image.load(f"Images/Terrain/Ground/Dirt{i}.png").convert() for i in range(1, 5)]

#* ore
_CoalOreSprites = [image.load(f"Images/Terrain/Ore/CoalOre{i}.png").convert() for i in range(1, 5)]
_IronOreSprites = [image.load(f"Images/Terrain/Ore/IronOre{i}.png").convert() for i in range(1, 5)]
_UraniumOreSprites = [image.load(f"Images/Terrain/Ore/UraniumOre{i}.png").convert() for i in range(1, 5)]

TILE_IMAGES = {}

def createTileImages():
    sources = {
        "Dirt": _DirtSprites,
        "Coal": _CoalOreSprites,
        "IronOre": _IronOreSprites,
        "UraniumOre": _UraniumOreSprites,
    }

    size = getTileSize()

    return {
        name: [
            [
                transform.flip(transform.scale(sprite, (size, size)), flipX, flipY)
                for flipX, flipY in ((False, False), (True, False), (False, True), (True, True))
            ]
            for sprite in sprites
        ]
        for name, sprites in sources.items()
    }

TILE_IMAGES = createTileImages()

def clearChunks():
    global _lastVisibleChunk

    for chunk in chunks.values():
        chunk.destroy()

    chunks.clear()
    _lastVisibleChunk = None

def updateTiles():
    global TILE_IMAGES
    global CHUNKSIZE
    
    TILE_IMAGES = createTileImages()
    
    clearChunks()

class Chunk(pygameui.Sprite):
    def __init__(self, chunkx, chunky, seed=seed):
        self.chunkPos = (chunkx, chunky)

        self.worldPos = (chunkx * CHUNKSIZE, chunky * CHUNKSIZE)

        size = CHUNKSIZE * getTileSize()

        chunkImage = Surface((size, size)).convert()

        for x in range(CHUNKSIZE):
            for y in range(CHUNKSIZE):
                worldx = self.worldPos[0] + x
                worldy = self.worldPos[1] + y

                tileType = getTileType(worldx, worldy, seed)
                
                rng = Random(f"{worldx},{worldy}")

                variant = rng.randrange(4)
                flip = rng.randrange(4)

                tile = TILE_IMAGES[tileType][variant][flip]

                chunkImage.blit(tile, (x * getTileSize(), y * getTileSize()))

        screenPos = worldToSreen(self.worldPos)

        super().__init__(screenPos[0], screenPos[1], w = size, h = size, image = chunkImage)

        self.z = -2

@lru_cache(maxsize = 100000)
def getTileType(x, y, seed = seed):  
    # note for me so im not intimidated by perlin noise numbers
    # x / y divisor controls size of patch, the higher the bigger
    # octaves control 'complexity' of the patch
    # the xNoise > y controls how common it is, higher being rarer
    # persistence sounds like smoothness, the lower the smoother
    # nobody knows what lacunarity does maybe the higher the rougher
    
    ironNoise = pnoise2(x / 8, y / 8, octaves = 3, persistence = 0.5, lacunarity = 2, base = seed + 100)

    if ironNoise > 0.25:
        return "IronOre"

    coalNoise = pnoise2(x / 18, y / 18, octaves = 6, persistence = 0.5, lacunarity = 2, base = seed + 200)

    if coalNoise > 0.175:
        return "Coal"
    
    uraniumNoise = pnoise2(x / 18, y / 18, octaves = 6, persistence = 0.5, lacunarity = 2, base = seed + 300)

    if uraniumNoise > 0.175:
        return "UraniumOre"

    return "Dirt"

def generateChunk(chunkx, chunky, seed = seed):
    if (chunkx, chunky) in chunks:
        return

    chunks[(chunkx, chunky)] = Chunk(chunkx, chunky, seed)
    
def unloadChunk(chunkx, chunky):
    chunk = chunks.pop((chunkx, chunky), None)

    if chunk is not None:
        chunk.destroy()

def updateVisibleChunks(radius = 4):
    global _lastVisibleChunk
    
    worldx, worldy = screenToWorld((winx // 2, winy // 2))

    chunkx = worldx // CHUNKSIZE
    chunky = worldy // CHUNKSIZE
    
    currentChunk = (chunkx, chunky)

    if currentChunk == _lastVisibleChunk:
        return

    _lastVisibleChunk = currentChunk

    requiredChunks = set()

    for x in range(chunkx - radius, chunkx + radius + 1):
        for y in range(chunky - radius, chunky + radius + 1):
            requiredChunks.add((x, y))

    loadedChunks = set(chunks)

    for chunk in loadedChunks - requiredChunks:
        unloadChunk(*chunk)

    for chunk in requiredChunks - loadedChunks:
        generateChunk(*chunk)

def updateChunkPoses():
    if cameraPos == lastCameraPos:
        return
    
    for chunk in chunks.values():
        screenPos = worldToSreen(chunk.worldPos)
        chunk.x, chunk.y = screenPos