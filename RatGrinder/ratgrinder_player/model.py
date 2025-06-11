from typing import List, TypedDict


class PlayInfo(TypedDict):
    qq_uid: str
    uid: List[str]
    name: str
    """角色名称"""
    money: int
    """鼠鼠币"""
    level: int
    """等级"""
