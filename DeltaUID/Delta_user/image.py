from copy import deepcopy
from typing import Any, Dict, cast
from functools import lru_cache

from PIL import Image, ImageDraw
from PIL.ImageDraw import ImageDraw as ID

from gsuid_core.models import Event

# from gsuid_core.utils.cache import gs_cache
from gsuid_core.utils.fonts.fonts import core_font as df_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    get_pic,
    easy_paste,
    get_event_avatar,
    draw_pic_with_ring,
)

from ..utils.image import TEXT_PATH as TEXTURE
from ..utils.models import (
    TQCData,
    InfoData,
    RecordSol,
    FriendData,
    WeeklyData,
    DayInfoData,
    RecordSolData,
    RecordTdmData,
)
from ..utils.api.util import Util

# 路径常量
avatar_path = TEXTURE / "avatar"
week_path = TEXTURE / "week"
record_path = TEXTURE / "record"

# 颜色常量
GREEN = (28, 241, 161)
WHITE = "white"
BLACK = "black"
YELLOW = "yellow"
RED = "red"

# 字体大小常量
FONT_SMALL = 25
FONT_MEDIUM = 30
FONT_LARGE = 35
FONT_XLARGE = 40
FONT_XXLARGE = 44

# 布局常量
AVATAR_SIZE = 150
HEADER_SIZE = 200
MARGIN = 20
ITEM_SPACING = 220


# 图片缓存机制
@lru_cache(maxsize=128)
def load_image_cached(path: str, mode: str = "RGBA") -> Image.Image:
    """缓存加载图片，提高性能"""
    return Image.open(path).convert(mode)


@lru_cache(maxsize=64)
def load_image_resized(path: str, size: tuple[int, int], mode: str = "RGBA") -> Image.Image:
    """缓存加载并调整大小的图片"""
    return Image.open(path).convert(mode).resize(size, Image.Resampling.LANCZOS)


# 预加载常用图片
footer = load_image_cached(str(TEXTURE / "footer.png"))

# 全局字体缓存
_font_cache: Dict[int, Any] = {}


def get_cached_font(size: int) -> Any:
    """获取缓存的字体，避免重复创建"""
    if size not in _font_cache:
        _font_cache[size] = df_font(size)
    return _font_cache[size]


# 标题相关图片缓存
@lru_cache(maxsize=8)
def get_title_bg() -> Image.Image:
    """获取标题背景图片"""
    return Image.open(TEXTURE / "header.png")


@lru_cache(maxsize=8)
def get_header_center() -> Image.Image:
    """获取头像背景图片"""
    return Image.open(TEXTURE / "头像背景.png").convert("RGBA")


async def draw_title(data: InfoData, avatar: Image.Image | None, mode: int = 0) -> Image.Image:
    """绘制用户头像标题区域 - 优化版本

    Args:
        data: 用户数据
        avatar: 用户头像图片，如果为None则从data获取头像URL
        mode: 显示模式 (0=全部, 1=全战, 2=烽火)

    Returns:
        绘制完成的标题图片
    """
    # 使用缓存的图片，避免重复加载
    title = get_title_bg().copy()
    header_center = get_header_center().copy()

    # 获取头像
    if avatar is None:
        avatar_url = data["avatar"]
        avatar = await get_pic(avatar_url)

    if avatar.mode != "RGBA":
        avatar = avatar.convert("RGBA")
    font_xlarge = get_cached_font(FONT_XLARGE)
    font_large = get_cached_font(FONT_LARGE)
    font_medium = get_cached_font(FONT_MEDIUM)

    # 添加圆环
    avatar = await draw_pic_with_ring(avatar.resize((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS), HEADER_SIZE)

    easy_paste(header_center, avatar, (150, 150), "cc")
    easy_paste(title, header_center, (150, 160), "cc")

    # 绘制文字
    title_draw = ImageDraw.Draw(title)
    texts_to_draw = []
    texts_to_draw.append((data["user_name"], (290, 85), WHITE, font_xlarge, "lt"))

    # 段位
    y_offset = 150
    if mode in [0, 2]:
        rank_sol = Util.get_rank_by_score_sol(int(data["rankpoint"]))
        texts_to_draw.append((f"烽火段位: {rank_sol}", (290, y_offset), WHITE, font_large, "lt"))
        y_offset += 45

    if mode in [0, 1]:
        rank_tdm = Util.get_rank_by_score_tdm(int(data["tdmrankpoint"]))
        texts_to_draw.append((f"全战段位:{rank_tdm}", (290, y_offset), WHITE, font_large, "lt"))
        if mode == 0:
            y_offset += 45

    # 时间
    time = data.get("time")
    if time:
        texts_to_draw.append((f"截至时间: {time}", (290, y_offset), WHITE, font_large, "lt"))

    # 排位分
    texts_to_draw.append((data["rankpoint"], (860, 250), WHITE, font_large, "mm"))
    texts_to_draw.append(("排位分", (860, 290), GREEN, font_medium, "mm"))

    for text, pos, color, font, anchor in texts_to_draw:
        title_draw.text(pos, text, color, font, anchor)

    return title


async def draw_one_msg(
    draw: ID,
    name: str,
    value: str,
    pos: tuple[int, int],
    size: int = FONT_MEDIUM,
) -> None:
    """绘制单个信息项 - 优化版本

    Args:
        draw: ImageDraw对象
        name: 项目名称
        value: 数值
        pos: 位置坐标
        size: 字体大小
    """
    # 使用缓存的字体
    value_size = size + 5
    name_y_offset = 40
    x_pos = pos[0] + 45
    y_pos = pos[1] + 30
    y_pos_name = y_pos + name_y_offset

    # 预获取字体对象
    font_value = df_font(value_size)
    font_label = df_font(size)

    # 批量绘制 - 减少函数调用开销
    draw.text((x_pos, y_pos), value, WHITE, font_value, "mm")
    draw.text((x_pos, y_pos_name), name, GREEN, font_label, "mm")


async def draw_tqc_section(img: Image.Image, tqc_data: list[TQCData], y_pos: int) -> None:
    """绘制特勤处信息区域

    Args:
        img: 目标图片
        tqc_data: 特勤处数据
        y_pos: Y轴位置
    """
    tqc_bg = Image.open(TEXTURE / "banner6.png")
    tqc_bar = Image.open(TEXTURE / "物品栏.png").convert("RGBA")

    img.paste(tqc_bg, (0, y_pos), tqc_bg)

    for i, tqc_item in enumerate(tqc_data[:4]):  # 最多显示4个
        tqc_sth = deepcopy(tqc_bar)
        tqc_sth_draw = ImageDraw.Draw(tqc_sth)

        # 绘制地点名称
        tqc_sth_draw.text(
            (150, 100),
            f"{tqc_item['place_name']}",
            GREEN,
            df_font(FONT_SMALL),
            "mm",
        )

        # 绘制状态信息
        if tqc_item.get("status") == "producing":
            tqc_sth_draw.text(
                (150, 170),
                f"{tqc_item['object_name']}",
                GREEN,
                df_font(FONT_SMALL),
                "mm",
            )
            tqc_sth_draw.text(
                (150, 220),
                f"{tqc_item['left_time']}",
                GREEN,
                df_font(FONT_SMALL),
                "mm",
            )
        else:
            tqc_sth_draw.text((150, 220), "空闲中", GREEN, df_font(FONT_SMALL), "mm")

        easy_paste(img, tqc_sth, (i * ITEM_SPACING + MARGIN, y_pos + 40), "lt")


async def draw_property_section(img: Image.Image, data: InfoData, y_pos: int) -> None:
    """绘制仓库资产信息区域

    Args:
        img: 目标图片
        data: 用户数据
        y_pos: Y轴位置
    """
    prop_bg = Image.open(TEXTURE / "banner1.png")
    prop_bar = Image.open(TEXTURE / "仓库bar.png").convert("RGBA")
    money_icon = Image.open(TEXTURE / "money1.png").convert("RGBA").resize((50, 50))
    asset_icon = Image.open(TEXTURE / "money2.png").convert("RGBA").resize((50, 50))

    img.paste(prop_bg, (0, y_pos - 120), prop_bg)

    # 现金信息
    prop_bar_1 = deepcopy(prop_bar)
    prop_draw_1 = ImageDraw.Draw(prop_bar_1)
    prop_draw_1.text((90, 30), f"现金: {data['money']}", WHITE, df_font(FONT_MEDIUM), "lt")
    easy_paste(prop_bar_1, money_icon, (30, 20), "lt")
    easy_paste(img, prop_bar_1, (60, y_pos), "lt")

    # 总资产信息
    prop_bar_2 = deepcopy(prop_bar)
    prop_draw_2 = ImageDraw.Draw(prop_bar_2)
    prop_draw_2.text(
        (90, 30),
        f"仓库总资产: {data['propcapital']}",
        WHITE,
        df_font(FONT_MEDIUM),
        "lt",
    )
    easy_paste(prop_bar_2, asset_icon, (30, 20), "lt")
    easy_paste(img, prop_bar_2, (500, y_pos), "lt")


async def draw_sol_stats_section(img: Image.Image, data: InfoData, y_pos: int) -> None:
    """绘制烽火战绩统计区域

    Args:
        img: 目标图片
        data: 用户数据
        y_pos: Y轴位置
    """
    sol_bg = Image.open(TEXTURE / "banner2.png")
    img.paste(sol_bg, (0, y_pos - 100), sol_bg)

    img_draw = ImageDraw.Draw(img)
    base_x, indent = 120, 160

    # 第一行统计
    sol_stats_row1 = [
        ("撤离率", data["solescaperatio"]),
        ("总场数", data["soltotalfght"]),
        ("撤离数", data["solttotalescape"]),
        ("总击杀", data["soltotalkill"]),
        ("赚损比", data["profitLossRatio"]),
    ]

    for i, (name, value) in enumerate(sol_stats_row1):
        await draw_one_msg(img_draw, name, value, (base_x + indent * i, y_pos))

    # 第二行统计
    sol_stats_row2 = [
        ("总带出", data["totalGainedPrice"]),
        ("游戏时长", data["totalGameTime"]),
        ("绝密KD", data["highKillDeathRatio"]),
        ("机密KD", data["medKillDeathRatio"]),
        ("普通KD", data["lowKillDeathRatio"]),
    ]

    for i, (name, value) in enumerate(sol_stats_row2):
        await draw_one_msg(img_draw, name, value, (base_x + indent * i, y_pos + 120))


async def draw_tdm_stats_section(img: Image.Image, data: InfoData, y_pos: int) -> None:
    """绘制全面战场统计区域

    Args:
        img: 目标图片
        data: 用户数据
        y_pos: Y轴位置
    """
    tdm_bg = Image.open(TEXTURE / "banner3.png")
    img.paste(tdm_bg, (0, y_pos - 100), tdm_bg)

    img_draw = ImageDraw.Draw(img)
    base_x, indent = 120, 160

    # 第一行统计
    tdm_stats_row1 = [
        ("胜率", data["tdmsuccessratio"]),
        ("总场数", data["tdmtotalfight"]),
        ("胜利数", data["totalwin"]),
        ("总击杀", data["tdmtotalkill"]),
        ("排位分", data["tdmrankpoint"]),
    ]

    for i, (name, value) in enumerate(tdm_stats_row1):
        await draw_one_msg(img_draw, name, value, (base_x + indent * i, y_pos))

    # 第二行统计
    tdm_stats_row2 = [
        ("击杀/min", data["avgkillperminute"]),
        ("游戏时长", data["tdmduration"]),
        ("分数/min", data["avgScorePerMinute"]),
        ("载具摧毁", data["totalVehicleDestroyed"]),
        ("载具击杀", data["totalVehicleKill"]),
    ]

    for i, (name, value) in enumerate(tdm_stats_row2):
        await draw_one_msg(img_draw, name, value, (base_x + indent * i, y_pos + 120))


async def draw_daily_section(img: Image.Image, day_data: DayInfoData, y_pos: int) -> None:
    """绘制日报信息区域

    Args:
        img: 目标图片
        day_data: 日报数据
        y_pos: Y轴位置
    """
    day_bg = Image.open(TEXTURE / "banner4.png")
    day_bar = Image.open(TEXTURE / "物品栏.png").convert("RGBA")
    money_icon = Image.open(TEXTURE / "money1.png").convert("RGBA").resize((120, 120))

    img.paste(day_bg, (0, y_pos), day_bg)

    # 收益信息
    day_money = deepcopy(day_bar)
    day_money_draw = ImageDraw.Draw(day_money)
    day_money_draw.text(
        (150, 100),
        f"收益: {day_data['profit_str']}",
        GREEN,
        df_font(FONT_SMALL),
        "mm",
    )
    easy_paste(day_money, money_icon, (90, 170), "lt")
    easy_paste(img, day_money, (30, y_pos + 50), "lt")

    # 热门物品
    for i, item in enumerate(day_data["top_collections"]["details"][:3]):
        day_item = deepcopy(day_bar)
        day_item_draw = ImageDraw.Draw(day_item)
        day_item_draw.text(
            (150, 100),
            f"{item['objectName']}",
            GREEN,
            df_font(FONT_SMALL),
            "mm",
        )

        item_pic = await get_pic(item["pic"], size=(120, 120))
        easy_paste(day_item, item_pic, (90, 170), "mm")
        easy_paste(img, day_item, (i * ITEM_SPACING + 240, y_pos + 50), "lt")


# @gs_cache()
async def draw_df_info_img(data: InfoData, day: DayInfoData, tqc: list[TQCData], ev: Event) -> bytes:
    """绘制用户信息完整图片

    Args:
        data: 用户数据
        day: 日报数据
        tqc: 特勤处数据
        ev: 事件对象

    Returns:
        图片字节数据
    """
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    header = await draw_title(data, await get_event_avatar(ev))

    # 特勤处区域 (300)
    await draw_tqc_section(img, tqc, 300)

    # 仓库资产区域 (800)
    await draw_property_section(img, data, 800)

    # 烽火战绩区域 (1020)
    await draw_sol_stats_section(img, data, 1020)

    # 全面战场区域 (1380)
    await draw_tdm_stats_section(img, data, 1380)

    # 日报区域 (1640)
    await draw_daily_section(img, day, 1640)

    # 添加标题和底部
    img.paste(header, (0, 0), header)
    img.paste(footer, (0, 2000), footer)

    return await convert_img(img)


async def draw_record_sol(
    avatar: Image.Image | None,
    data: list[RecordSolData],
    week_data: WeeklyData,
    msg: InfoData,
):
    if len(data) == 0:
        img = Image.open(TEXTURE / "bg.jpg").convert("RGBA").resize((1000, 2300))
    else:
        img = Image.open(TEXTURE / "bg.jpg").convert("RGBA").resize((2000, 2300))

    data_one = cast(
        InfoData,
        {
            "user_name": msg["user_name"],
            "rankpoint": msg["rankpoint"],
            "time": week_data["statDate_str"],
        },
    )
    header = await draw_title(data_one, avatar, 2)
    img.paste(header, (0, 0), header)
    img_draw = ImageDraw.Draw(img)

    money_banner = Image.open(week_path / "banner1.png")
    fight_banner = Image.open(week_path / "banner2.png")
    friend_banner = Image.open(week_path / "banner3.png")
    history_bg = Image.open(week_path / "banner4.png")
    money_bg = Image.open(week_path / "bar1.png")

    friend_bg = Image.open(week_path / "friend.png")
    hero_bg = Image.open(week_path / "hero.png").resize((315, 460))

    # 左侧
    # 收益
    easy_paste(img, money_banner, (0, 330), "lt")

    def money_draw(text, value, x, y):
        money_img = deepcopy(money_bg)
        money_draw = ImageDraw.Draw(money_img)
        money_draw.text(
            (100, 20),
            text,
            "white",
            df_font(25),
            "lt",
        )
        money_draw.text(
            (100, 50),
            value,
            "yellow",
            df_font(33),
            "lt",
        )
        easy_paste(img, money_img, (x, y), "lt")

    money_draw("总收入", f"{week_data['Gained_Price_Str']}", 60, 460)
    money_draw("总损失", f"{week_data['consume_Price_Str']}", 360, 460)
    money_draw("总盈利", f"{week_data['rise_Price_Str']}", 660, 460)

    # 战斗统计
    fight_x_indent = 180
    fight_x = 120
    fight_y = 700
    easy_paste(img, fight_banner, (0, fight_y - 110), "lt")
    await draw_one_msg(
        img_draw,
        "在线时长",
        week_data["total_Online_Time_str"],
        (fight_x, fight_y),
    )
    await draw_one_msg(
        img_draw,
        "总场数",
        week_data["total_sol_num"],
        (fight_x + fight_x_indent, fight_y),
    )
    await draw_one_msg(
        img_draw,
        "撤离数",
        week_data["total_exacuation_num"],
        (fight_x + fight_x_indent * 2, fight_y),
    )
    await draw_one_msg(
        img_draw,
        "K/D",
        f"{week_data['total_Kill_Player']}/{week_data['total_Death_Count']}",
        (fight_x + fight_x_indent * 3, fight_y),
    )
    await draw_one_msg(
        img_draw,
        "百万撤离",
        f"{week_data['GainedPrice_overmillion_num']}次",
        (fight_x + fight_x_indent * 4, fight_y),
    )

    # 战斗干员
    def draw_hero(hero: str, times: int, x: int, y: int):
        hero_img = deepcopy(hero_bg)
        hero_avatar = Image.open(avatar_path / f"{hero}.png").resize((245, 255))
        easy_paste(hero_img, hero_avatar, (35, 60), "lt")
        hero_draw = ImageDraw.Draw(hero_img)
        hero_draw.text(
            (154, 360),
            hero,
            "white",
            df_font(40),
            "mm",
        )
        hero_draw.text(
            (154, 400),
            f"{times}次",
            "yellow",
            df_font(30),
            "mm",
        )
        easy_paste(img, hero_img, (x, y), "lt")

    for i in range(min(3, len(week_data["total_ArmedForceId_num_list"]))):
        hero_name = Util.get_armed_force_name(week_data["total_ArmedForceId_num_list"][i]["ArmedForceId"])
        draw_hero(
            hero_name,
            week_data["total_ArmedForceId_num_list"][i]["inum"],
            50 + i * 305,
            804,
        )

    # 队友协作
    easy_paste(img, friend_banner, (0, 1300), "lt")

    async def draw_friend(friend: FriendData, x: int, y: int):
        friend_img = deepcopy(friend_bg)

        friend_draw = ImageDraw.Draw(friend_img)
        friend_draw.text(
            (225, 80),
            friend["charac_name"],
            "black",
            df_font(35),
            "mm",
        )
        await draw_one_msg(
            friend_draw,
            "撤离",
            f"{friend['escape_num']}",
            (50, 110),
        )
        await draw_one_msg(
            friend_draw,
            "失败",
            f"{friend['fail_num']}",
            (175, 110),
        )
        await draw_one_msg(
            friend_draw,
            "K/D",
            f"{friend['kill_num']}/{friend['death_num']}",
            (300, 110),
        )
        await draw_one_msg(
            friend_draw,
            "带出",
            f"{friend['gained_str']}",
            (50, 210),
        )
        await draw_one_msg(
            friend_draw,
            "战损",
            f"{friend['consume_str']}",
            (175, 210),
        )
        await draw_one_msg(
            friend_draw,
            "利润",
            f"{friend['profit_str']}",
            (300, 210),
        )
        easy_paste(img, friend_img, (x, y), "lt")

    for i in range(4):
        if len(week_data["friend_list"]) < i + 1:
            break
        await draw_friend(
            week_data["friend_list"][i],
            60 + i % 2 * 450,
            1404 + i // 2 * 400,
        )

    # 右侧
    # 战绩

    if len(data) == 0:
        img.paste(footer, (0, 2130), footer)
    else:
        easy_paste(img, history_bg, (1000, 90), "lt")
        record_win = Image.open(TEXTURE / "frame_win.png")
        record_fail = Image.open(TEXTURE / "frame_fail.png")

        for i in range(min(len(data), 10)):
            xy = (1000, 220 + i * 200)
            # 时间
            img_draw.text(
                (1650, 380 + i * 200),
                data[i]["time"],
                GREEN,
                df_font(25),
                "lt",
            )

            # 地图
            img_base = Image.new("RGBA", (1000, 164), (255, 255, 255, 0))
            map_path = TEXTURE / "mapsol" / f"{data[i]['map_name']}.png"
            bg_map = Image.open(map_path).convert("RGBA").resize((844, 120))
            easy_paste(img_base, bg_map, (78, 22), "lt")

            # 头像
            avatar = Image.open(avatar_path / f"{data[i]['armed_force']}.png").resize((120, 120))
            easy_paste(img_base, avatar, (140, 20), "lt")

            # 内容

            if data[i]["result"] == "撤离成功":
                bg = deepcopy(record_win)

            elif data[i]["result"] == "撤离失败":
                bg = deepcopy(record_fail)

            else:
                continue
            easy_paste(img_base, bg, (0, 0), "lt")

            # 文字
            draw_bg = ImageDraw.Draw(im=img_base)
            draw_bg.text(
                (122, 33),
                data[i]["result"][2:],
                "black",
                df_font(30),
                "mm",
            )
            draw_bg.text(
                (195, 125),
                f"击杀{data[i]['kill_count']}",
                "black",
                df_font(25),
                "mm",
            )
            draw_bg.text(
                (900, 45),
                f"{data[i]['map_name']}",
                "white",
                df_font(40),
                "rm",
            )
            draw_bg.text(
                (900, 90),
                f"利润{data[i]['profit']}/带出{data[i]['price']}",
                GREEN,
                df_font(30),
                "rm",
            )
            draw_bg.text(
                (900, 126),
                f"存活:{data[i]['duration']}",
                "white",
                df_font(25),
                "rm",
            )
            img.paste(img_base, xy, img_base)

        img.paste(footer, (500, 2170), footer)
    return await convert_img(img)


async def draw_record_tdm(avatar: Image.Image | None, data: list[RecordTdmData], msg: InfoData):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    data_one = cast(
        InfoData,
        {
            "user_name": msg["user_name"],
            "rankpoint": msg["tdmrankpoint"],
            "tdmrankpoint": msg["tdmrankpoint"],
        },
    )
    header = await draw_title(data_one, avatar, 1)
    img.paste(header, (0, 0), header)
    return await convert_img(img)


# async def draw_scb(avatar: Image.Image | None, msg: InfoData):
#     img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
#     data_one = cast(
#         InfoData,
#         {
#             "user_name": msg["user_name"],
#             "tdmrankpoint": msg["tdmrankpoint"],
#         },
#     )
#     header = await draw_title(data_one, avatar, 1)
#     img.paste(header, (0, 0), header)
#     return await convert_img(img)


async def draw_sol_record(avatar: Image.Image, data: RecordSol, win: bool = True):
    img = Image.open(record_path / "bg.png").convert("RGBA")
    line = Image.open(record_path / "line.png").convert("RGBA")
    easy_paste(img, line, (0, 0), "lt")

    header_center = Image.open(TEXTURE / "头像背景.png").convert("RGBA")

    avatar = await draw_pic_with_ring(avatar.convert("RGBA").resize((150, 150)), 200)
    easy_paste(header_center, avatar, (150, 150), "cc")
    easy_paste(img, header_center, (30, 30), "lt")
    # 干员图标
    armed_img = await Util.armed_to_img(data["armedforceid"])
    armed_img = armed_img.resize((432, 692), Image.Resampling.LANCZOS)
    armed_img = armed_img.rotate(-9.2, expand=True)
    easy_paste(img, armed_img, (956, 81), "lt")
    # 文字部分
    img_draw = ImageDraw.Draw(img)
    img_draw.text((330, 60), data["user_name"], "white", font=df_font(40))
    result_c = GREEN if data["result"] == "撤离成功" else "red"
    img_draw.text((330, 110), data["result"], result_c, font=df_font(44))

    title_c = GREEN if data["title"] == "百万撤离！" else "red"
    img_draw.text((117.6, 321.7), data["title"], title_c, font=df_font(84))

    img_draw.text((145, 450), f"{data['map_name'][-2:]}行动", "grey", font=df_font(24))
    img_draw.text((145, 490), data["map_name"].split("-")[0], "white", font=df_font(44))
    img_draw.text((385, 450), "时长", "grey", font=df_font(24))
    img_draw.text((385, 490), data["duration"], "white", font=df_font(44))
    img_draw.text((630, 450), "击杀", "grey", font=df_font(24))
    img_draw.text((630, 490), f"{data['kill_count']}", "white", font=df_font(44))

    img_draw.text((130, 575), "本局收获", "grey", font=df_font(24))
    img_draw.text((130, 615), f"{data['price']}", "white", font=df_font(44))
    img_draw.text((385, 575), "战损", "grey", font=df_font(24))
    img_draw.text((385, 615), f"{data['loss']}", "white", font=df_font(44))

    easy_paste(img, footer.resize((800, 104)), (0, 780), "lt")
    return await convert_img(img)
