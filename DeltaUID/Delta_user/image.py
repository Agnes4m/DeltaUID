from copy import deepcopy
from pathlib import Path
from typing import Optional

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
)

from ..utils.models import InfoData

TEXTURE = Path(__file__).parent / "texture"

async def draw_title(data: InfoData,ev: Event):
    title = Image.open(TEXTURE / "header.png")
    
    
    header_center = Image.open(TEXTURE / "头像背景.png").convert("RGBA")
    avatar = await draw_pic_with_ring((await get_event_avatar(ev)).convert("RGBA").resize((150, 150)), 200)

    easy_paste(header_center, avatar, (150, 150),"cc")
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
        (860, 250),
        data["rankpoint"],
        "white",
        df_font(35),
        "mm",
    )
    title_draw.text(
        (860, 290),
        "排位分",
        (28,241,161),
        df_font(30),
        "mm",
    )


    return title


async def draw_one_msg(draw: ID,name: str, value: str,pos: tuple[int,int], size: int=25):

 
    draw.text(
        (pos[0]+45, pos[1]+30),

        value,
        "white",
        df_font(size+5),
        "mm",
    )
    draw.text(
        (pos[0]+45, pos[1]+80),

        name,
        (28,241,161),
        df_font(size),
        "mm",
    )



# @gs_cache()
async def draw_df_info_img(data: InfoData, day, ev: Event):

    img = Image.open(TEXTURE / "bg.jpg").convert("RGBA")
    
    
    header = await draw_title(data, ev)

    prop_bg = Image.open(TEXTURE / "banner1.png")
    sol_bg = Image.open(TEXTURE / "banner2.png")
    tdm_bg: ImageFile = Image.open(TEXTURE / "banner3.png")
    day_bg = Image.open(TEXTURE / "banner4.png")
    history_bg = Image.open(TEXTURE / "banner5.png")

    # 仓库
    prop_bar_1 = Image.open(TEXTURE / "仓库bar.png").convert("RGBA")
    prop_bar_2 = deepcopy(prop_bar_1)
    money_1 = Image.open(TEXTURE / "money1.png").convert("RGBA").resize((50, 50))
    
    money_2 = Image.open(TEXTURE / "money2.png").convert("RGBA").resize((50, 50))
    

    prop_draw_1 = ImageDraw.Draw(prop_bar_1)
    prop_draw_1.text(
        (90, 33),
        f"现金: {data['money']}",
        "white",
        df_font(25),
        "lt",
    )
    prop_draw_2 = ImageDraw.Draw(prop_bar_2)
    prop_draw_2.text(
        (90, 33),
        f"仓库总资产: {data['propcapital']}",
        "white",
        df_font(25),
        "lt",
    )


    easy_paste(prop_bar_1, money_1, (30, 20), "lt")
    easy_paste(prop_bar_2, money_2, (30, 20), "lt")

    easy_paste(img, prop_bar_1, (60, 435), "lt")
    easy_paste(img, prop_bar_2, (500, 435), "lt")
    
    # 烽火
    img_draw = ImageDraw.Draw(img)
    await draw_one_msg(img_draw, "撤离率", data["solescaperatio"], (90, 640))
    await draw_one_msg(img_draw, "总场数", data["soltotalfght"], (270, 640))
    await draw_one_msg(img_draw, "撤离数", data["solttotalescape"], (450, 640))
    await draw_one_msg(img_draw, "总击杀", data["soltotalkill"], (620, 640))
    await draw_one_msg(img_draw, "赚损比", data["profitLossRatio"], (790, 640))
    await draw_one_msg(img_draw, "总带出", data["totalGainedPrice"], (90, 750))
    await draw_one_msg(img_draw, "游戏时长", data["totalGameTime"], (270, 750))
    await draw_one_msg(img_draw, "绝密KD", data["highKillDeathRatio"], (450, 750))
    await draw_one_msg(img_draw, "机密KD", data["medKillDeathRatio"], (620, 750))
    await draw_one_msg(img_draw, "普通KD", data["lowKillDeathRatio"], (790, 750))
    # 全面战场
    await draw_one_msg(img_draw, "胜率", data["tdmsuccessratio"], (90, 980))
    await draw_one_msg(img_draw, "总场数", data["tdmtotalfight"], (270, 980))
    await draw_one_msg(img_draw, "胜利数", data["totalwin"], (450, 980))
    await draw_one_msg(img_draw, "总击杀", data["tdmtotalkill"], (620, 980))
    await draw_one_msg(img_draw, "排位分", data["tdmrankpoint"], (790, 980))

    await draw_one_msg(img_draw, "击杀/min", data["avgkillperminute"], (90, 1090))
    await draw_one_msg(img_draw, "游戏时长", data["tdmduration"], (270, 1090))
    await draw_one_msg(img_draw, "分数/min", data["avgScorePerMinute"], (450, 1090))
    await draw_one_msg(img_draw, "载具摧毁", data["totalVehicleDestroyed"], (620, 1090))
    await draw_one_msg(img_draw, "载具击杀", data["totalVehicleKill"], (790, 1090))


    # 日报
    day_bar = Image.open(TEXTURE / "物品栏.png").convert("RGBA")
    easy_paste(img, day_bar, (30, 1250), "lt")
    easy_paste(img, day_bar, (240, 1250), "lt")
    easy_paste(img, day_bar, (460, 1250), "lt")
    easy_paste(img, day_bar, (680, 1250), "lt")
    

    img.paste(header, (0, 0), header)
    img.paste(prop_bg, (0, 320), prop_bg)
    img.paste(sol_bg, (0, 550), sol_bg)

    img.paste(tdm_bg, (0, 880), tdm_bg)
    img.paste(day_bg, (0, 1220), day_bg)
    img.paste(history_bg, (0, 1600), history_bg)

    return await convert_img(img)

