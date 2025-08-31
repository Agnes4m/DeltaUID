from copy import deepcopy
from pathlib import Path
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

from ..utils.models import DayInfoData, InfoData, RecordSolData, RecordTdmData

TEXTURE = Path(__file__).parent / "texture"
green = (28, 241, 161)


async def draw_title(data: InfoData, ev: Event):
    title = Image.open(TEXTURE / "header.png")

    header_center = Image.open(TEXTURE / "头像背景.png").convert("RGBA")
    avatar = await draw_pic_with_ring(
        (await get_event_avatar(ev)).convert("RGBA").resize((150, 150)), 200
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
    title_draw.text(
        (290, 150),
        "烽火段位:",
        "white",
        df_font(35),
        "lt",
    )
    title_draw.text(
        (290, 195),
        "全战段位:",
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
    draw: ID, name: str, value: str, pos: tuple[int, int], size: int = 33
):
    draw.text(
        (pos[0] + 45, pos[1] + 30),
        value,
        "white",
        df_font(size + 5),
        "mm",
    )
    draw.text(
        (pos[0] + 45, pos[1] + 100),
        name,
        green,
        df_font(size),
        "mm",
    )


# @gs_cache()
async def draw_df_info_img(data: InfoData, day: DayInfoData, ev: Event):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")

    header = await draw_title(data, ev)

    prop_bg = Image.open(TEXTURE / "banner1.png")
    sol_bg = Image.open(TEXTURE / "banner2.png")
    tdm_bg: ImageFile = Image.open(TEXTURE / "banner3.png")
    day_bg = Image.open(TEXTURE / "banner4.png")
    # history_bg = Image.open(TEXTURE / "banner5.png")

    # 仓库
    img.paste(prop_bg, (0, 350), prop_bg)
    prop_tap = 500

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
    img.paste(sol_bg, (0, 650), sol_bg)
    sol_tap = 770
    img_draw = ImageDraw.Draw(img)
    await draw_one_msg(
        img_draw, "撤离率", data["solescaperatio"], (90, sol_tap)
    )
    await draw_one_msg(
        img_draw, "总场数", data["soltotalfght"], (270, sol_tap)
    )
    await draw_one_msg(
        img_draw, "撤离数", data["solttotalescape"], (450, sol_tap)
    )
    await draw_one_msg(
        img_draw, "总击杀", data["soltotalkill"], (620, sol_tap)
    )
    await draw_one_msg(
        img_draw, "赚损比", data["profitLossRatio"], (790, sol_tap)
    )
    await draw_one_msg(
        img_draw, "总带出", data["totalGainedPrice"], (90, sol_tap + 150)
    )
    await draw_one_msg(
        img_draw, "游戏时长", data["totalGameTime"], (270, sol_tap + 150)
    )
    await draw_one_msg(
        img_draw, "绝密KD", data["highKillDeathRatio"], (450, sol_tap + 150)
    )
    await draw_one_msg(
        img_draw, "机密KD", data["medKillDeathRatio"], (620, sol_tap + 150)
    )
    await draw_one_msg(
        img_draw, "普通KD", data["lowKillDeathRatio"], (790, sol_tap + 150)
    )
    # 全面战场
    img.paste(tdm_bg, (0, 1100), tdm_bg)
    tdm_tap = 1220
    await draw_one_msg(
        img_draw, "胜率", data["tdmsuccessratio"], (90, tdm_tap)
    )
    await draw_one_msg(
        img_draw, "总场数", data["tdmtotalfight"], (270, tdm_tap)
    )
    await draw_one_msg(img_draw, "胜利数", data["totalwin"], (450, tdm_tap))
    await draw_one_msg(
        img_draw, "总击杀", data["tdmtotalkill"], (620, tdm_tap)
    )
    await draw_one_msg(
        img_draw, "排位分", data["tdmrankpoint"], (790, tdm_tap)
    )

    await draw_one_msg(
        img_draw, "击杀/min", data["avgkillperminute"], (90, tdm_tap + 150)
    )
    await draw_one_msg(
        img_draw, "游戏时长", data["tdmduration"], (270, tdm_tap + 150)
    )
    await draw_one_msg(
        img_draw, "分数/min", data["avgScorePerMinute"], (450, tdm_tap + 150)
    )
    await draw_one_msg(
        img_draw,
        "载具摧毁",
        data["totalVehicleDestroyed"],
        (620, tdm_tap + 150),
    )
    await draw_one_msg(
        img_draw, "载具击杀", data["totalVehicleKill"], (790, tdm_tap + 150)
    )

    # 日报
    day_tap = 1550
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

    easy_paste(img, day_money, (30, day_tap + 80), "lt")

    for i in range(3):
        day_sth = deepcopy(day_bar)
        if len(day["top_collections"]["details"]) != i:
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

        easy_paste(img, day_sth, (i * 220 + 240, day_tap + 80), "lt")

    img.paste(header, (0, 0), header)

    # img.paste(history_bg, (0, 1600), history_bg)

    footer = Image.open(TEXTURE / "footer.png").convert("RGBA")
    img.paste(footer, (0, 2000), footer)

    return await convert_img(img)


async def draw_record_sol(ev: Event, data: list[RecordSolData]):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    data_one = cast(
        InfoData,
        {
            "user_name": data[0]["user_name"],
            "rankpoint": "114514",
        },
    )
    header = await draw_title(data_one, ev)
    img.paste(header, (0, 0), header)
    img_draw = ImageDraw.Draw(img)

    history_bg = Image.open(TEXTURE / "banner5.png")
    easy_paste(img, history_bg, (0, 400), "lt")

    # 战绩
    record_win = Image.open(TEXTURE / "frame_win.png")
    record_fail = Image.open(TEXTURE / "frame_fail.png")

    for i in range(min(len(data), 10)):
        xy = (0, 550 + i * 200)
        # 时间
        img_draw.text(
            (80, 500 + i * 200),
            data[i]["time"],
            "black",
            df_font(25),
            "lt",
        )

        # 地图
        img_base = Image.new("RGBA", (1000, 164), (255, 255, 255, 0))
        map_path = TEXTURE / "mapsol" / f"{data[i]['map_name']}.png"
        bg_map = Image.open(map_path).convert("RGBA").resize((844, 120))
        easy_paste(img_base, bg_map, (78, 22), "lt")

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
    footer = Image.open(TEXTURE / "footer.png").convert("RGBA")
    img.paste(footer, (0, 2000), footer)
    return await convert_img(img)


async def draw_record_tdm(ev: Event, data: list[RecordTdmData]):
    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    data_one = cast(
        InfoData,
        {
            "user_name": "测试用户",
            "rankpoint": "1234",
        },
    )

    header = await draw_title(data_one, ev)
    img.paste(header, (0, 0), header)
    # history_bg = Image.open(TEXTURE / "banner5.png")
    # img.paste(history_bg, (0, 1600), history_bg)
    return await convert_img(img)
