from typing import Literal, Optional, TypedDict


class WeaponInfo(TypedDict):
    damage: int
    """武器伤害"""
    av_distance: int
    """武器优势射程"""
    recoil: int
    """武器后坐力"""
    method: Literal["半自动单发", "全自动单发", "全自动三发", "全自动"]
    """武器攻击方式"""


class WeaponExtra(TypedDict):
    sight: Optional[str]
    """瞄准镜"""
    side_sight: Optional[str]
    """侧瞄准镜"""
    buttstock: Optional[str]
    """枪托"""
    barrel: Optional[str]
    """枪管"""
    grip: Optional[str]
    """握把"""
    stock_cover: Optional[str]
    "'弹夹套'"
    stock: Optional[str]
    """弹夹"""


class Weapen(TypedDict):
    type_: Literal[
        "冲锋枪",
        "突击步枪",
        "精准步枪",
        "狙击步枪",
        "霰弹枪",
        "手枪",
        "轻机枪",
    ]
    """武器类型"""
    name: str
    """武器名称"""
    expe: int
    """武器等级"""
    icon: str
    """武器图标URL"""
    desc: str
    """武器描述"""
    extra: WeaponExtra
    """配件"""
