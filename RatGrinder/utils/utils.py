from typing import List, Optional

from .models import SsPlayer


async def create_ssplayer(
    name: str = '鼠鼠',
    money: int = 0,
    level: int = 1,
    exp: float = 0.0,
    bag: Optional[List[str]] = None,
) -> SsPlayer:
    """
    创建一个带默认值的SsPlayer对象
    """
    return SsPlayer(
        name=name,
        money=money,
        level=level,
        exp=exp,
        bag=bag if bag is not None else [],
    )
