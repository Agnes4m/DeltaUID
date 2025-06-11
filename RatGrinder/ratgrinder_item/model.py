from shutil import move
from typing import Literal, TypedDict

from casbin import effect
from numpy import quantile


class Pill(TypedDict):
    name: str
    type_: Literal["医疗"]
    recover: int
    """回血总量"""
    recover_time: int
    """持续回血时间,0为单次使用"""
    recover_bleed: int
    """修复流血数量"""
    recover_fractrue: int
    """修复骨折数量"""
    recover_wound: int
    """修复创伤(通用修复)数量"""
    use_time: int
    """使用花费时间"""


class Hormone(TypedDict):
    name: str
    type_: Literal["激素"]
    physical_up: float
    """体力提升百分比"""
    block_pain: bool
    """阻挡疼痛"""
    effect_time: int
    """效果持续时间"""
    use_time: int
    """使用花费时间"""


class WeaponBase(TypedDict):
    """武器基础信息"""

    name: str
    type_: Literal["武器"]
    type_info: Literal["手枪", "步枪", "霰弹枪", "狙击枪", "机枪", "近战武器"]
    """武器类型"""
    damage: int
    """伤害"""
    attack_speed: float
    """攻击速度"""
    move_speed: float
    """移动速度"""
    recoil: float
    """后坐力"""
    move_recoil: float
    """移动时后坐力"""


class Armor(TypedDict):
    """防具基础信息"""

    name: str
    type_: Literal["防具"]
    type_info: Literal["头甲", "体甲"]
    quality: Literal[1, 2, 3, 4, 5, 6]
    """防具品质"""
    durability: int
    """耐久"""
    defense: int
    """防御"""
    hearing: float
    """听觉变化"""
    vision: float
    """视觉变化"""
    move_speed: float
    """移动速度变化"""
