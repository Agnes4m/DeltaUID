from typing import Literal, TypedDict


class TradeItemInfo(TypedDict):
    type_info: str
    """二级分类"""
    name: str
    """物品名称"""
    price: int
    """物品价格"""
    icon: str
    """物品图标URL"""
    desc: str
    """物品描述"""
    limit_level: int
    """物品限制购买等级"""
    quality: Literal[0, 1, 2, 3, 4, 5, 6]
    """物品品质
    0为无品质
    1为灰色品质
    2为绿色品质
    3为蓝色品质
    4为紫色品质
    5为橙色品质
    6为红色品质
    """


class TradeItem(TypedDict):
    type_: Literal["武器", "防具", "材料", "消耗品"]
    """物品类型"""
    trade_info: TradeItemInfo
    """物品交易信息"""
