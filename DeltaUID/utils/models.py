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


class InfoData(TypedDict):
    user_name: str
    """用户名"""

    money: str
    """现金"""
    propcapital: str
    """仓库总资产"""
    rankpoint: str
    soltotalfght: str
    """总战斗场次"""
    solttotalescape: str
    """总撤离场次"""

    soltotalkill: str
    """总击杀"""

    solescaperatio: str
    """撤离率"""
    profitLossRatio: str
    """赚损比"""
    highKillDeathRatio: str
    """绝密KD"""
    medKillDeathRatio: str
    """机密KD"""
    lowKillDeathRatio: str
    """常规KD"""
    totalGainedPrice: str
    """总盈利"""
    totalGameTime: str
    """总游戏时间"""

    # 全面战场
    tdmrankpoint: str
    """全面战场积分"""

    avgkillperminute: str
    """平均每分击杀数"""

    tdmtotalfight: str
    """总战斗场次"""

    totalwin: str
    """总胜利场次"""

    tdmtotalkill: str
    """总击杀"""

    tdmduration: str
    """总游戏时间"""
    tdmsuccessratio: str
    """全面战场胜率"""

    avgScorePerMinute: str
    """平均每分得分"""

    totalVehicleDestroyed: str
    """总载具摧毁数"""
    totalVehicleKill: str
    """总载具击杀数"""


class DayMoneyData(TypedDict):
    """日物品"""

    objectID: str
    objectName: str
    pic: str
    avgPrice: str


class DayListData(TypedDict):
    list_str: str
    details: list[DayMoneyData]


class DayInfoData(TypedDict):
    """日数据"""

    daily_report_date: str
    """日期"""
    profit: int
    """利润"""
    profit_str: str
    """利润字符串"""

    top_collections: DayListData


class RecordSolData(TypedDict):
    """战绩数据"""

    user_name: str
    time: str
    map_name: str
    armed_force: str
    result: str
    duration: str
    kill_count: int
    price: str
    profit: str
    title: str


class RecordTdmData(TypedDict):
    """战绩数据"""

    title: str
    time: str
    user_name: str
    map_name: str
    armed_force: str
    result: str
    gametime: str
    kill_count: int
    death_count: int
    assist_count: int
    rescue_count: str
    total_score: int
    avg_score_per_minute: int
