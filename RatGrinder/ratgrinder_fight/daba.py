import random
from typing import Dict, List

from .model import GameMap, MapCell, ItemInfo, FixedPointInfo

# 关键格点位定义，每个点有唯一id、类型、物品池、概率、以及连接到的其他点
KEY_POINTS: Dict[str, FixedPointInfo] = {
    "A": {
        "type": "出生点",
        "item_pool": [{"name": "急救包", "amount": 1}],
        "item_chance": 0.5,
        "links": ["B", "C"],
    },
    "B": {
        "type": "道路",
        "item_pool": [{"name": "能量饮料", "amount": 1}],
        "item_chance": 0.3,
        "links": ["A", "D"],
    },
    "C": {
        "type": "房子",
        "item_pool": [{"name": "金币", "amount": 50}],
        "item_chance": 0.8,
        "links": ["A", "D"],
    },
    "D": {
        "type": "补给站",
        "item_pool": [
            {"name": "手枪", "amount": 1},
            {"name": "急救包", "amount": 1},
            {"name": "金币", "amount": 100},
        ],
        "item_chance": 1.0,
        "links": ["B", "C", "E"],
    },
    "E": {
        "type": "撤离点",
        "item_pool": [],
        "item_chance": 0.0,
        "links": ["D"],
    },
    # 可继续添加更多关键格
}


async def create_keypoint_map() -> GameMap:
    """
    初始化关键格地图，每个点位有唯一id、类型、物品、连接关系
    """
    cells: Dict[str, MapCell] = {}
    for key, cfg in KEY_POINTS.items():
        cell = MapCell(id=key, type=cfg["type"], links=cfg["links"])
        item_pool = cfg.get("item_pool", [])
        item_chance = cfg.get("item_chance", 0.0)
        if item_pool and random.random() < item_chance:
            cell["items"] = [random.choice(item_pool)]
        cells[key] = cell
    return GameMap(
        name="大坝关键格模式",
        cells=cells,
        birth_points=["A"],
        extraction_point=["E"],
    )
