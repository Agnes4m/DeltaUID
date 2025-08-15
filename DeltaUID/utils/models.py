from typing import TypedDict


class UserData(TypedDict):
    qq_id: str
    group_id: int
    access_token: str
    openid: str
    if_remind_safehouse: bool  # 是否开启安全区提醒
    platform: str  # 平台名称qq/wx


class LatestRecord(TypedDict):
    """用户最新战绩记录"""

    qq_id: int  # 用户QQ号作为主键
    latest_record_id: str  # 最新战绩ID
    latest_tdm_record_id: str  # 最新TDM战绩ID


class SafehouseRecord(TypedDict):
    """用户特勤处生产记录"""

    qq_id: str  # 用户QQ号
    device_id: str  # 设备ID
    object_id: int  # 生产物品ID
    object_name: str  # 生产物品名称
    place_name: str  # 工作台名称
    left_time: int  # 剩余时间（秒）
    push_time: int  # 推送时间戳


class SignMsg(TypedDict):

    image: str
    cookie: str
    qrSig: str
    token: str
    loginSig: str


class Sign(TypedDict):
    status: bool
    message: str | SignMsg


class LoginStatus(TypedDict):
    code: int
    message: str
    data: dict
