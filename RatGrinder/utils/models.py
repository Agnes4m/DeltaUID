from typing import List, TypedDict


class SsPlayer(TypedDict):
    name: str
    money: int
    level: int
    exp: float
    bag: List[str]
    """
    背包物品
        1. 武器(枪)
        2. 防具
        3. 子弹
        4. 药品
        5. 维修品
        6. 激素
        7. 任务道具
        8. 刀
        9. 皮肤外观
        10. 其他一般等价物
    """
