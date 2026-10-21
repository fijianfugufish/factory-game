from pygame import *
import pygameui
from noise import pnoise2
from decodeFactory import cameraPos, lastCameraPos, worldToSreen, screenToWorld, winx, winy

CHUNKSIZE = 3
TILESIZE = 64
seed = 42

chunks: dict[tuple[int, int], "Chunk"] = {}

_lastVisibleChunk = None

#* ground
_DirtSprite = image.load("Images/Terrain/Ground/Dirt.png").convert()

#* ore
_CoalOreSprite = image.load("Images/Terrain/Ore/CoalOre.png").convert()
_IronOreSprite = image.load("Images/Terrain/Ore/IronOre.png").convert()

TILE_IMAGES = {
    "Dirt": transform.scale(_DirtSprite, (TILESIZE, TILESIZE)),
    "CoalOre": transform.scale(_CoalOreSprite, (TILESIZE, TILESIZE)),
    "IronOre": transform.scale(_IronOreSprite, (TILESIZE, TILESIZE))
}

class Chunk(pygameui.Sprite):
    def __init__(self, chunkx, chunky, seed=seed):
        self.chunkPos = (chunkx, chunky)

        self.worldPos = (chunkx * CHUNKSIZE, chunky * CHUNKSIZE)

        size = CHUNKSIZE * TILESIZE

        chunkImage = Surface((size, size)).convert()

        for x in range(CHUNKSIZE):
            for y in range(CHUNKSIZE):
                worldx = self.worldPos[0] + x
                worldy = self.worldPos[1] + y

                tileType = getTileType(worldx, worldy, seed)

                chunkImage.blit(TILE_IMAGES[tileType], (x * TILESIZE, y * TILESIZE))

        screenPos = worldToSreen(self.worldPos)

        super().__init__(screenPos[0], screenPos[1], w = size, h = size, image = chunkImage)

        self.z = -1

def getTileType(x, y, seed = seed):  
    # note for me so im not intimidated by perlin noise numbers
    # x / y divisor controls size of patch, the higher the bigger
    # octaves control 'complexity' of the patch
    # the xNoise > y controls how common it is, higher being rarer
    # who even knows what the others do
    
    ironNoise = pnoise2(x / 8, y / 8, octaves = 3, persistence = 0.5, lacunarity = 2, base = seed + 100)

    if ironNoise > 0.25:
        return "IronOre"

    coalNoise = pnoise2(x / 18, y / 18, octaves = 3, persistence = 0.5, lacunarity = 2, base = seed + 200)

    if coalNoise > 0.225:
        return "CoalOre"

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