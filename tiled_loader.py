"""
tiled_loader.py

Tiled (mapeditor.org) altal exportalt .json terkep betoltese pygame-hez.
A .tsx tileset fajlokat (marble.tsx, arena_colors.tsx) futaskor XML-kent
olvassa be, igy nem kell kezzel megadni oszlopszamot / kep meretet -
azt automatikusan kiszedi a .tsx-bol.

Hasznalat (Game.__init__-ben vagy new()-ban):

    from tiled_loader import TiledMap

    self.map = TiledMap('map.json')          # relativ ut a jelenlegi konyvtarhoz
    self.walkable_grid = self.map.build_walkable_grid()   # ez lesz az uj "tilemap"
"""

import json
import os
import xml.etree.ElementTree as ET
import pygame
from utils import resource_path


class TiledTileset:
    """Egy .tsx fajlt reprezental (pl. marble.tsx vagy arena_colors.tsx)."""

    def __init__(self, tsx_path, firstgid):
        self.firstgid = firstgid

        tree = ET.parse(resource_path(tsx_path))
        root = tree.getroot()

        self.tilewidth = int(root.get('tilewidth'))
        self.tileheight = int(root.get('tileheight'))
        self.columns = int(root.get('columns'))
        self.tilecount = int(root.get('tilecount'))

        image_el = root.find('image')
        image_source = image_el.get('source')

        tsx_dir = os.path.dirname(tsx_path)
        self.image_path = os.path.normpath(os.path.join(tsx_dir, image_source))
        self.surface = pygame.image.load(resource_path(self.image_path)).convert_alpha()

        self.lastgid = self.firstgid + self.tilecount - 1

    def contains(self, gid):
        return self.firstgid <= gid <= self.lastgid

    def get_surface(self, gid):
        """Kivagja a gid-hez tartozo darabot a tileset kepbol."""
        local_id = gid - self.firstgid
        col = local_id % self.columns
        row = local_id // self.columns
        x = col * self.tilewidth
        y = row * self.tileheight

        tile = pygame.Surface((self.tilewidth, self.tileheight), pygame.SRCALPHA)
        tile.blit(self.surface, (0, 0), (x, y, self.tilewidth, self.tileheight))
        return tile


class TiledMap:
    """Betolt egy Tiled .json terkepet (egyetlen tile layer-rel)."""

    def __init__(self, json_path):
        json_full_path = resource_path(json_path)
        base_dir = os.path.dirname(os.path.abspath(json_full_path))

        with open(resource_path(json_path), 'r') as f:
            data = json.load(f)

        self.width = data['width']
        self.height = data['height']
        self.tilewidth = data['tilewidth']
        self.tileheight = data['tileheight']

        # Csak az elso tile layer-t hasznaljuk (Tile Layer 1)
        layer = data['layers'][0]
        flat = layer['data']
        self.gid_grid = [
            flat[i * self.width:(i + 1) * self.width]
            for i in range(self.height)
        ]

        # Tilesetek betoltese - nagyobb firstgid elore, hogy a contains()
        # keresesnel a helyes tileset-et talaljuk elsonek
        self.tilesets = []
        for ts in data['tilesets']:
            tsx_path = os.path.normpath(os.path.join(base_dir, ts['source']))
            self.tilesets.append(TiledTileset(tsx_path, ts['firstgid']))
        self.tilesets.sort(key=lambda t: -t.firstgid)

        self._surface_cache = {}

    def gid_at(self, x, y):
        return self.gid_grid[y][x]

    def is_void(self, x, y):
        """True, ha a mezo teljesen ures (gid == 0) - ez a kor alaku arena
        'levagott sarkai'."""
        return self.gid_at(x, y) == 0

    def get_surface(self, gid):
        """Visszaadja a gid-hez tartozo kivagott pygame.Surface-t (cache-elve)."""
        if gid == 0:
            return None
        if gid not in self._surface_cache:
            surf = None
            for ts in self.tilesets:
                if ts.contains(gid):
                    surf = ts.get_surface(gid)
                    break
            self._surface_cache[gid] = surf
        return self._surface_cache[gid]

    def build_walkable_grid(self, blocking_gids=frozenset()):
        """
        Visszaad egy stringekbol allo listat, ugyanolyan formaban mint a
        regi kezzel irt `tilemap`, hogy a sprites.py-ban levo bfs_path /
        is_walkable / collide_blocks logika VALTOZATLANUL mukodjon:

            'B' -> nem jarhato (ures mezo VAGY explicit blokkolo gid)
            'G' -> jarhato talaj

        blocking_gids: opcionalis set/frozenset azokrol a gid-ekrol, amik
        talajkent latszanak, de nem jarhatoak (pl. ha kesobb kiderul, hogy
        pl. a szoborok vagy oszlop-tetok is a tile layer-ben vannak).
        Alapertelmezesben ures - minden nem-0 mezo jarhato.
        """
        grid = []
        for y in range(self.height):
            row_chars = []
            for x in range(self.width):
                gid = self.gid_grid[y][x]
                if gid == 0 or gid in blocking_gids:
                    row_chars.append("B")
                else:
                    row_chars.append("G")
            grid.append("".join(row_chars))
        return grid

    def find_center_walkable(self, blocking_gids=frozenset()):
        """Visszaadja a terkep kozepehez legkozelebbi jarhato (x, y) tile-t.
        Hasznos a jatekos spawn pontjahoz, mivel a Tiled export nem
        tartalmaz 'P' jelolot."""
        cx, cy = self.width // 2, self.height // 2
        grid = self.build_walkable_grid(blocking_gids)

        if grid[cy][cx] == "G":
            return cx, cy

        # spiralisan kifele keresunk a kozeptol
        for radius in range(1, max(self.width, self.height)):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        if grid[y][x] == "G":
                            return x, y
        raise ValueError("Nem talalhato jarhato mezo a terkepen!")
