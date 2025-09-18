from copy import deepcopy
from typing import cast

from PIL import Image, ImageDraw
from PIL.ImageDraw import ImageDraw as ID
from PIL.ImageFile import ImageFile

from gsuid_core.models import Event

# from gsuid_core.utils.cache import gs_cache
from gsuid_core.utils.fonts.fonts import core_font as df_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    draw_pic_with_ring,
    easy_paste,
    get_event_avatar,
    get_pic,
)

from ..utils.api.util import Util
from ..utils.image import TEXT_PATH as TEXTURE
from ..utils.models import (
    DayInfoData,
    FriendData,
    InfoData,
    RecordSolData,
    RecordTdmData,
    TQCData,
    WeeklyData,
)

avatar_path = TEXTURE / "avatar"
week_path = TEXTURE / "week"
green = (28, 241, 161)


async def draw_title(
    data: InfoData, avatar: Image.Image | None, mode: int = 0
):
    title = Image.open(TEXTURE / "header.png")

    header_center = Image.open(TEXTURE / "头像背景.png").convert("RGBA")
    if avatar is None:
        avatar_url = data["avatar"]
        avatar = await get_pic(avatar_url)

    avatar = await draw_pic_with_ring(
        avatar.convert("RGBA").resize((150, 150)), 200
    )

    easy_paste(header_center, avatar, (150, 150), "cc")
    easy_paste(title, header_center, (150, 160), "cc")

    title_draw = ImageDraw.Draw(title)
    title_draw.text(
        (290, 85),
        data["user_name"],
        "white",
        df_font(40),
        "lt",
    )
    if mode == 1:
        rank_tdm = Util.get_rank_by_score_tdm(int(data["tdmrankpoint"]))
        title_draw.text(
            (290, 150),
            f"全战段位:{rank_tdm}",
            "white",
            df_font(35),
            "lt",
        )
    elif mode == 2:
        rank_sol = Util.get_rank_by_score_sol(int(data["rankpoint"]))
        title_draw.text(
            (290, 150),
            f"烽火段位: {rank_sol}",
            "white",
            df_font(35),
            "lt",
        )
    else:
        rank_sol = Util.get_rank_by_score_sol(int(data["rankpoint"]))
        title_draw.text(
            (290, 150),
            f"烽火段位: {rank_sol}",
            "white",
            df_font(35),
            "lt",
        )
        rank_tdm = Util.get_rank_by_score_tdm(int(data["tdmrankpoint"]))
        title_draw.text(
            (290, 195),
            f"全战段位:{rank_tdm}",
            "white",
            df_font(35),
            "lt",
        )
    title_draw.text(
        (860, 250),
        data["rankpoint"],
        "white",
        df_font(35),
        "mm",
    )
    title_draw.text(
        (860, 290),
        "排位分",
        green,
        df_font(30),
        "mm",
    )

    return title


async def draw_one_msg(
    draw: ID, name: str, value: str, pos: tuple[int, int], size: int = 30
):
    draw.text(
        (pos[0] + 45, pos[1] + 30),
        value,
        "white",
        df_font(size + 5),
        "mm",
    )
    draw.text(
        (pos[0] + 45, pos[1] + 70),
        name,
        green,
        df_font(size),
        "mm",
    )


# @gs_cache()
async def draw_df_info_img(
    data: InfoData, day: DayInfoData, tqc: list[TQCData], ev: Event
):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")

    header = await draw_title(data, await get_event_avatar(ev))

    prop_bg = Image.open(TEXTURE / "banner1.png")
    sol_bg = Image.open(TEXTURE / "banner2.png")
    tdm_bg: ImageFile = Image.open(TEXTURE / "banner3.png")
    day_bg = Image.open(TEXTURE / "banner4.png")
    tqc_bg = Image.open(TEXTURE / "banner6.png")
    # history_bg = Image.open(TEXTURE / "banner5.png")

    # 特勤处
    tqc_tap = 300
    tqc_bar = Image.open(TEXTURE / "物品栏.png").convert("RGBA")
    img.paste(tqc_bg, (0, tqc_tap), tqc_bg)

    for i in range(4):
        tqc_sth = deepcopy(tqc_bar)
        tqc_sth_draw = ImageDraw.Draw(tqc_sth)
        tqc_sth_draw.text(
            (150, 100),
            f"{tqc[i]['place_name']}",
            green,
            df_font(25),
            "mm",
        )
        if tqc[i] == "producing":
            tqc_sth_draw.text(
                (150, 170),
                f"{tqc[i]['object_name']}",
                green,
                df_font(25),
                "mm",
            )
            tqc_sth_draw.text(
                (150, 220),
                f"{tqc[i]['left_time']}",
                green,
                df_font(25),
                "mm",
            )

        else:
            tqc_sth_draw.text(
                (150, 220),
                "空闲中",
                green,
                df_font(25),
                "mm",
            )

        easy_paste(img, tqc_sth, (i * 220 + 20, tqc_tap + 40), "lt")

    img.paste(header, (0, 0), header)

    # 仓库
    prop_tap = 800
    img.paste(prop_bg, (0, prop_tap - 120), prop_bg)

    prop_bar_1 = Image.open(TEXTURE / "仓库bar.png").convert("RGBA")
    prop_bar_2 = deepcopy(prop_bar_1)
    money_1 = (
        Image.open(TEXTURE / "money1.png").convert("RGBA").resize((50, 50))
    )

    money_2 = (
        Image.open(TEXTURE / "money2.png").convert("RGBA").resize((50, 50))
    )

    prop_draw_1 = ImageDraw.Draw(prop_bar_1)
    prop_draw_1.text(
        (90, 30),
        f"现金: {data['money']}",
        "white",
        df_font(30),
        "lt",
    )
    prop_draw_2 = ImageDraw.Draw(prop_bar_2)
    prop_draw_2.text(
        (90, 30),
        f"仓库总资产: {data['propcapital']}",
        "white",
        df_font(30),
        "lt",
    )

    easy_paste(prop_bar_1, money_1, (30, 20), "lt")
    easy_paste(prop_bar_2, money_2, (30, 20), "lt")

    easy_paste(img, prop_bar_1, (60, prop_tap), "lt")
    easy_paste(img, prop_bar_2, (500, prop_tap), "lt")

    # 烽火
    sol_tap = 1020
    sol_indent = 160
    sol_base = 120
    img.paste(sol_bg, (0, sol_tap - 100), sol_bg)

    img_draw = ImageDraw.Draw(img)
    await draw_one_msg(
        img_draw, "撤离率", data["solescaperatio"], (sol_base, sol_tap)
    )
    await draw_one_msg(
        img_draw,
        "总场数",
        data["soltotalfght"],
        (sol_base + sol_indent, sol_tap),
    )
    await draw_one_msg(
        img_draw,
        "撤离数",
        data["solttotalescape"],
        (sol_base + sol_indent * 2, sol_tap),
    )
    await draw_one_msg(
        img_draw,
        "总击杀",
        data["soltotalkill"],
        (sol_base + sol_indent * 3, sol_tap),
    )
    await draw_one_msg(
        img_draw,
        "赚损比",
        data["profitLossRatio"],
        (sol_base + sol_indent * 4, sol_tap),
    )
    await draw_one_msg(
        img_draw, "总带出", data["totalGainedPrice"], (sol_base, sol_tap + 120)
    )
    await draw_one_msg(
        img_draw,
        "游戏时长",
        data["totalGameTime"],
        (sol_base + sol_indent, sol_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "绝密KD",
        data["highKillDeathRatio"],
        (sol_base + sol_indent * 2, sol_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "机密KD",
        data["medKillDeathRatio"],
        (sol_base + sol_indent * 3, sol_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "普通KD",
        data["lowKillDeathRatio"],
        (sol_base + sol_indent * 4, sol_tap + 120),
    )

    # 全面战场

    tdm_tap = 1380
    tdm_indent = 160
    tdm_base = 120
    img.paste(tdm_bg, (0, tdm_tap - 100), tdm_bg)
    await draw_one_msg(
        img_draw, "胜率", data["tdmsuccessratio"], (tdm_base, tdm_tap)
    )
    await draw_one_msg(
        img_draw,
        "总场数",
        data["tdmtotalfight"],
        (tdm_base + tdm_indent, tdm_tap),
    )
    await draw_one_msg(
        img_draw,
        "胜利数",
        data["totalwin"],
        (tdm_base + tdm_indent * 2, tdm_tap),
    )
    await draw_one_msg(
        img_draw,
        "总击杀",
        data["tdmtotalkill"],
        (tdm_base + tdm_indent * 3, tdm_tap),
    )
    await draw_one_msg(
        img_draw,
        "排位分",
        data["tdmrankpoint"],
        (tdm_base + tdm_indent * 4, tdm_tap),
    )

    await draw_one_msg(
        img_draw,
        "击杀/min",
        data["avgkillperminute"],
        (tdm_base, tdm_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "游戏时长",
        data["tdmduration"],
        (tdm_base + tdm_indent, tdm_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "分数/min",
        data["avgScorePerMinute"],
        (tdm_base + tdm_indent * 2, tdm_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "载具摧毁",
        data["totalVehicleDestroyed"],
        (tdm_base + tdm_indent * 3, tdm_tap + 120),
    )
    await draw_one_msg(
        img_draw,
        "载具击杀",
        data["totalVehicleKill"],
        (tdm_base + tdm_indent * 4, tdm_tap + 120),
    )

    # 日报
    day_tap = 1640
    day_bar = Image.open(TEXTURE / "物品栏.png").convert("RGBA")
    img.paste(day_bg, (0, day_tap), day_bg)

    day_money = deepcopy(day_bar)
    day_money_draw = ImageDraw.Draw(day_money)
    day_money_draw.text(
        (150, 100),
        f"收益: {day['profit_str']}",
        green,
        df_font(25),
        "mm",
    )
    easy_paste(day_money, money_1.resize((120, 120)), (90, 170), "lt")

    easy_paste(img, day_money, (30, day_tap + 50), "lt")

    for i in range(min(3, len(day["top_collections"]["details"]))):
        day_sth = deepcopy(day_bar)
        day_sth_draw = ImageDraw.Draw(day_sth)
        day_sth_draw.text(
            (150, 100),
            f"{day['top_collections']['details'][i]['objectName']}",
            green,
            df_font(25),
            "mm",
        )

        st1 = await get_pic(
            day["top_collections"]["details"][i]["pic"], size=(120, 120)
        )
        easy_paste(day_sth, st1, (90, 170), "mm")

        easy_paste(img, day_sth, (i * 220 + 240, day_tap + 50), "lt")

    img.paste(header, (0, 0), header)

    footer = Image.open(TEXTURE / "footer.png").convert("RGBA")
    img.paste(footer, (0, 2000), footer)

    return await convert_img(img)


async def draw_record_sol(
    avatar: Image.Image | None,
    data: list[RecordSolData],
    week_data: WeeklyData,
    msg: InfoData,
):
    if len(data) == 0:
        img = (
            Image.open(TEXTURE / "bg.jpg").convert("RGBA").resize((1000, 2300))
        )
    else:
        img = (
            Image.open(TEXTURE / "bg.jpg").convert("RGBA").resize((2000, 2300))
        )

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
        week_data["GainedPrice_overmillion_num"] + "次",
        (fight_x + fight_x_indent * 4, fight_y),
    )

    # 战斗干员
    def draw_hero(hero: str, times: int, x: int, y: int):
        hero_img = deepcopy(hero_bg)
        hero_avatar = Image.open(avatar_path / f"{hero}.png").resize(
            (245, 255)
        )
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
        hero_name = Util.get_armed_force_name(
            week_data["total_ArmedForceId_num_list"][i]["ArmedForceId"]
        )
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
    footer = Image.open(TEXTURE / "footer.png").convert("RGBA")
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
                green,
                df_font(25),
                "lt",
            )

            # 地图
            img_base = Image.new("RGBA", (1000, 164), (255, 255, 255, 0))
            map_path = TEXTURE / "mapsol" / f"{data[i]['map_name']}.png"
            bg_map = Image.open(map_path).convert("RGBA").resize((844, 120))
            easy_paste(img_base, bg_map, (78, 22), "lt")

            # 头像
            avatar = Image.open(
                avatar_path / f"{data[i]['armed_force']}.png"
            ).resize((120, 120))
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
                f"利润{data[i]['price']}/损失{data[i]['profit']}",
                green,
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


async def draw_record_tdm(
    avatar: Image.Image | None, data: list[RecordTdmData], msg: InfoData
):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    data_one = cast(
        InfoData,
        {
            "user_name": msg["user_name"],
            "tdmrankpoint": msg["tdmrankpoint"],
        },
    )

    header = await draw_title(data_one, avatar, 1)
    img.paste(header, (0, 0), header)
    return await convert_img(img)


async def draw_scb(avatar: Image.Image | None, msg: InfoData):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    data_one = cast(
        InfoData,
        {
            "user_name": msg["user_name"],
            "tdmrankpoint": msg["tdmrankpoint"],
        },
    )
    header = await draw_title(data_one, avatar, 1)
    img.paste(header, (0, 0), header)
    return await convert_img(img)
