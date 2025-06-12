from os import name
from typing import Dict, List, Union, Optional, TypedDict


class ItemInfo(TypedDict, total=False):
    """物品信息"""

    name: str
    amount: int


class ContainerInfo(TypedDict, total=False):
    """储物柜"""

    name: str
    type: str
    items: List[ItemInfo]


class EnemyInfo(TypedDict, total=False):
    """敌人信息"""

    name: str
    type: str
    hp: int
    level: int


class LootInfo(TypedDict, total=False):
    """战利品信息"""

    name: str
    items: List[ItemInfo]
    quality: Optional[str]


class MapCell(TypedDict, total=False):
    x: int
    y: int
    items: List[ItemInfo]
    container: Optional[ContainerInfo]
    enemy: Optional[EnemyInfo]
    loot: Optional[LootInfo]


class GameMap(TypedDict):
    name: str
    """地图名称"""
    width: int
    height: int
    cells: Dict[str, MapCell]
    birth_points: List[str]
    """出生点"""
    extraction_point: List[str]
    """撤离点"""


class FixedPointInfo(TypedDict, total=False):
    type: str
    item_pool: List[ItemInfo]
    item_chance: float
    links: List[str]
