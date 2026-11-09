from pygame import *
import pygameui
from noise import pnoise2
from decodeFactory import cameraPos, lastCameraPos, worldToSreen, screenToWorld, winx, winy, getTileSize
from random import Random
from functools import lru_cache

CHUNKSIZE = 8
BASE_TILESIZE = 64
seed = 42

chunks: dict[tuple[int, int], "Chunk"] = {}

#* ground
_DirtSprites = [image.load(f"Images/Terrain/Ground/Dirt{i}.png").convert() for i in range(1, 5)]

#* ore
_CoalOreSprites = [image.load(f"Images/Terrain/Ore/CoalOre{i}.png").convert() for i in range(1, 5)]
_IronOreSprites = [image.load(f"Images/Terrain/Ore/IronOre{i}.png").convert() for i in range(1, 5)]
_UraniumOreSprites = [image.load(f"Images/Terrain/Ore/UraniumOre{i}.png").convert() for i in range(1, 5)]

def createTileImages():
    sources = {
        "Dirt": _DirtSprites,
        "Coal": _CoalOreSprites,
        "IronOre": _IronOreSprites,
        "UraniumOre": _UraniumOreSprites,
    }

    return {
        name: [
            [
                transform.flip(transform.scale(sprite, (BASE_TILESIZE, BASE_TILESIZE)), flipx, flipy)
                for flipx, flipy in ((False, False), (True, False), (False, True), (True, True))
            ]
            for sprite in sprites
        ]
        for name, sprites in sources.items()
    }

TILE_IMAGES = createTileImages()

def clearChunks():
    for chunk in chunks.values():
        chunk.destroy()

    chunks.clear()

def updateTiles():
    size = CHUNKSIZE * getTileSize()

    for chunk in chunks.values():
        original = generateChunkImage(*chunk.chunkPos, seed)

        chunk.changeImage(transform.scale(original, (size, size)))

        chunk.w = size
        chunk.h = size

        chunk.x, chunk.y = worldToSreen(chunk.worldPos)

class Chunk(pygameui.Sprite):
    def __init__(self, chunkx, chunky, seed = seed):
        self.chunkPos = (chunkx, chunky)

        self.worldPos = (chunkx * CHUNKSIZE, chunky * CHUNKSIZE)

        size = CHUNKSIZE * getTileSize()

        original = generateChunkImage(chunkx, chunky, seed)

        chunkImage = transform.scale(original, (size, size))

        screenPos = worldToSreen(self.worldPos)

        super().__init__(screenPos[0], screenPos[1], w = size, h = size, image = chunkImage)

        self.z = -2

@lru_cache(maxsize = 128)
def generateChunkImage(chunkx, chunky, seed = seed):
    size = CHUNKSIZE * BASE_TILESIZE

    chunkImage = Surface((size, size)).convert()

    for x in range(CHUNKSIZE):
        for y in range(CHUNKSIZE):
            worldx = chunkx * CHUNKSIZE + x
            worldy = chunky * CHUNKSIZE + y

            tileType = getTileType(worldx, worldy, seed)

            rng = Random(f"{worldx},{worldy}")

            variant = rng.randrange(4)
            flip = rng.randrange(4)

            tile = TILE_IMAGES[tileType][variant][flip]

            chunkImage.blit(tile, (x * BASE_TILESIZE, y * BASE_TILESIZE))

    return chunkImage

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

def updateVisibleChunks():
    tileSize = getTileSize()

    minx = int(cameraPos[0] // CHUNKSIZE) - 1
    miny = int(cameraPos[1] // CHUNKSIZE) - 1

    maxx = int((cameraPos[0] + winx / tileSize) // CHUNKSIZE) + 1
    maxy = int((cameraPos[1] + winy / tileSize) // CHUNKSIZE) + 1

    requiredChunks = set()

    for x in range(minx, maxx + 1):
        for y in range(miny, maxy + 1):
            requiredChunks.add((x, y))

    loadedChunks = set(chunks)

    for chunk in loadedChunks - requiredChunks:
        unloadChunk(*chunk)

    # generate chunks closest to the camera first
    centerx = (minx + maxx) / 2
    centery = (miny + maxy) / 2

    missingChunks = sorted(
        requiredChunks - loadedChunks,
        key = lambda pos: (pos[0] - centerx) ** 2 + (pos[1] - centery) ** 2
    )

    for chunk in missingChunks[:4]:
        generateChunk(*chunk)

def updateChunkPoses():
    if cameraPos == lastCameraPos:
        return

    for chunk in chunks.values():
        screenPos = worldToSreen(chunk.worldPos)
        chunk.x, chunk.y = screenPos