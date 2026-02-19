from typing import Dict, Literal, TypedDict


class UserData(TypedDict):
    qq_id: str
    group_id: int
    access_token: str
    openid: str
    if_remind_safehouse: bool  # 是否开启安全区提醒
    platform: str  # 平台名称qq/wx


class UserPlayer(TypedDict):
    picurl: str
    charac_name: str


class UserGame(TypedDict):
    result: int
    error_info: int
    rankpoint: str
    tdmrankpoint: str
    soltotalfght: str
    solttotalescape: str
    solduration: str
    soltotalkill: str
    solescaperatio: str
    avgkillperminute: str
    tdmduration: str
    tdmsuccessratio: str
    tdmtotalfight: str
    totalwin: str
    tdmtotalkill: str


class UserInfo(TypedDict):
    player: UserPlayer
    game: UserGame
    coin: int
    tickets: int
    money: int


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
    avatar: str
    """头像url"""
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
    time: str | None


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


class TQCData(TypedDict):
    """特勤处数据"""

    place_name: str
    """特勤处名称"""
    status: str
    """特勤处状态
    - idle - 空闲中
    - producing - 正在生产
    """
    object_name: str
    """物品名称"""
    left_time: str
    """剩余时间"""
    finish_time: str
    """完成时间"""
    object_id: str
    """物品id"""


class ArmedForceData(TypedDict):
    ArmedForceId: int
    inum: int


class MapData(TypedDict):
    MapId: int
    inum: int


class FriendData(TypedDict):
    charac_name: str
    sol_num: str
    kill_num: str
    death_num: str
    escape_num: str
    """总撤离"""
    fail_num: str
    """撤离失败"""
    gained_str: str
    """总收入"""
    consume_str: str
    """总损失"""
    profit_str: str
    """总盈利"""


class ItemData(TypedDict):
    itemid: int
    """物品id"""
    inum: int
    """物品数量"""
    auctontype: int
    """物品类型"""
    quality: float
    """物品质量"""
    iPrice: float
    """物品价格"""


class WeeklyData(TypedDict):
    """周报数据"""

    # CarryOut_highprice_list: list[DayInfoData]
    user_name: str
    """用户名"""
    statDate_str: str
    """日期"""
    Gained_Price_Str: str
    """总收入"""
    consume_Price_Str: str
    """总损失"""
    rise_Price_Str: str
    """总盈利"""
    total_ArmedForceId_num_list: list[ArmedForceData]
    """总干员次数"""
    total_mapid_num_list: list[MapData]
    """总地图次数"""
    friend_list: list[FriendData]
    """队友列表"""
    profit: int
    """总收入"""
    rise_Price: int
    """总盈利"""
    total_sol_num: str
    """总游戏场次"""
    total_Online_Time_str: str
    """总游戏时间"""
    total_Kill_Player: str
    """总击杀"""
    total_Death_Count: str
    """总死亡"""
    total_exacuation_num: str
    """总撤离"""
    GainedPrice_overmillion_num: str
    """百万撤离次数"""
    price_list: list[str]
    """资产变化7天"""


class RecordSol(TypedDict):
    """战绩数据"""

    user_name: str
    title: Literal["百万撤离", "百万战损"]
    time: str
    map_name: str
    result: Literal["撤离成功！", "撤离失败！"]
    duration: str
    kill_count: int
    """击杀数量"""
    price: str
    loss: str
    is_gain: bool
    main_value: str
    armedforceid: str
    """干员"""


class RecordTdm(TypedDict):
    """战绩数据"""

    user_name: str
    title: Literal["战场高光！", "战场失败！"]
    time: str
    map_name: str
    result: Literal["胜利", "失败"]
    gametime: str
    armed_force: str
    """地图"""
    kill_count: int
    death_count: int
    assist_count: int
    total_score: int
    avg_score_per_minute: int
    is_good: bool
    main_label: Literal["捞薯大师", "刷分大王"]
    main_value: str
    badge_text: Literal["1000+分均得分", "1000+击杀"]


class OwnUserData(TypedDict):
    """资产数据"""

    ItemId: int
    """物品id"""
    ItemName: str
    """物品名称"""

    ItemGid: str
    """物品分组,全是0"""
    ItemQuality: str
    """物品质量"""


class OwnWeaponData(TypedDict):
    """武器数据"""

    ItemId: int
    """物品id"""
    ItemName: str
    """物品名称"""

    ItemGid: str
    """物品分组,全是0"""
    ItemQuality: str
    """物品质量"""
    ItemNum: int
    """物品数量"""
    IsCollectibles: str
    """是否是收藏品
    - 0 不是
    - 1 是
    """
    GainedTime: str
    """获得时间"""


class OwnDCData(TypedDict):
    """载具数据(未测试)"""

    PropID: str
    """物品id"""
    Rarity: str
    """0"""
    Wear: str
    """可能是id"""
    UniqueNo: str
    """0"""
    KillCnter: str
    """0"""
    CustomName: str
    AppearanceId: str
    """0"""
    AppearanceSeed: str
    """0"""
    Name: str


class OwnPriceData(TypedDict):
    """仓库物品数据"""

    iRet: str
    sMsg: str
    userData: list[OwnUserData]
    weaponData: list[OwnWeaponData]
    dCData: list[OwnDCData]


class BigRedData(TypedDict):
    """大红色物品数据"""

    time: str
    """年月日，时分秒"""
    itemId: str
    """物品id"""
    mapid: int
    """属性id"""
    num: int
    """物品数量"""
    des: str
    """物品描述"""


class BigRed(TypedDict):
    total: int
    """总数量"""
    list: list[BigRedData]


"""
    {
        "id": 10087,
        "objectID": 14060000003,
        "objectName": "高级头盔维修组合",
        "length": 2,
        "width": 2,
        "grade": 6,
        "weight": "3",
        "primaryClass": "props",
        "secondClass": "consume",
        "secondClassCN": "消耗品",
        "thirdClass": "repair",
        "thirdClassCN": "维修套件",
        "desc": "针对6级装备的局内维修工具，能快速修复头盔耐久度。每块插板消耗工具包25点耐久；启用时间4.5秒。",
        "pic": "https://playerhub.df.qq.com/playerhub/60004/object/14060000003.png",
        "prePic": "https://playerhub.df.qq.com/playerhub/60004/object/p_14060000003.png",
        "avgPrice": 347624,
        "propsDetail": {
            "repairPoints": 100,
            "repairArea": "头盔",
            "repairEfficiency": "低",
            "activeTime": "4.5",
            "replyEffect": "回复头盔耐久度"
        }
    },
"""


class PropsDetail(TypedDict):
    """物品属性详情"""

    type: str
    """物品类型"""
    propsSource: str
    """掉落位置"""


class ItemIdData(TypedDict):
    """物品数据"""

    id: int
    """物品id"""
    objectID: int
    """物品id"""
    objectName: str
    """物品名称"""
    length: int
    """物品长度"""
    width: int
    """物品宽度"""
    grade: int
    """物品等级"""
    weight: str
    """物品重量"""
    primaryClass: str
    """物品主分类"""
    secondClass: str
    """物品次分类"""
    secondClassCN: str
    """物品次分类中文"""
    # 下面两个是部分有的
    thirdClass: str
    """物品三级分类"""
    thirdClassCN: str
    """物品三级分类中文"""
    desc: str
    """物品描述"""
    pic: str
    """物品图片"""
    prePic: str
    """物品预览图片"""
    avgPrice: int
    """物品平均价格"""
    propsDetail: PropsDetail
    """物品属性详情"""


class ItemHourPriceData(TypedDict):
    """物品小时均价数据"""

    itemid: Dict[str, Dict[Literal["avg_buyprice"], float]]
    """物品小时均价数据"""
