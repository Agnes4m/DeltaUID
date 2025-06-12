from typing import Dict, List, Tuple, Union, Optional


class MapCell:
    def __init__(
        self,
        x: int,
        y: int,
        cell_type: str = "空地",
        items: Optional[List[Union[str, Dict[str, Union[str, int]]]]] = None,
        container: Optional[str] = None,
    ):
        self.x = x
        self.y = y
        self.cell_type = cell_type  # "道路"、"房子"、"空地"等
        self.items = items if items is not None else []  # 物品列表
        self.container = container  # 例如"箱子"、"保险柜"等

    def to_dict(self) -> Dict:
        return {
            "x": self.x,
            "y": self.y,
            "cell_type": self.cell_type,
            "container": self.container,
            "items": self.items,
        }


class DabaMap:
    def __init__(self, width: int = 200, height: int = 100):
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], MapCell] = {}
        for x in range(width):
            for y in range(height):
                self.grid[(x, y)] = MapCell(x, y)

    def set_cell(
        self,
        x: int,
        y: int,
        cell_type: str,
        items: Optional[List[Union[str, Dict[str, Union[str, int]]]]] = None,
        container: Optional[str] = None,
    ):
        if (0 <= x < self.width) and (0 <= y < self.height):
            cell = self.grid[(x, y)]
            cell.cell_type = cell_type
            cell.items = items if items is not None else []
            cell.container = container

    def get_cell(self, x: int, y: int) -> Optional[MapCell]:
        return self.grid.get((x, y))

    def to_dict(self) -> List[Dict]:
        return [cell.to_dict() for cell in self.grid.values()]


# 示例：初始化地图并设置部分格子
if __name__ == "__main__":
    daba_map = DabaMap()
    # 设置一条横向道路
    for x in range(10, 50):
        daba_map.set_cell(x, 20, "道路")
    # 设置一个房子区域
    for x in range(60, 70):
        for y in range(30, 40):
            daba_map.set_cell(x, y, "房子")
    # 在某个格子放置一个保险柜，里面有多个物品
    daba_map.set_cell(
        15,
        20,
        "房子",
        items=["急救包", {"name": "金币", "amount": 100}, "手枪"],
        container="保险柜",
    )
    # 打印部分格子信息
    for pos in [(15, 20), (65, 35), (0, 0)]:
        cell = daba_map.get_cell(*pos)
        print(cell.to_dict())
