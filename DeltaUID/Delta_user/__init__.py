import asyncio
import random
import time
from typing import cast

# from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.sv import SV
from gsuid_core.utils.image.image_tools import (
    get_event_avatar,
)

from ..utils.models import RecordSolData, RecordTdmData
from .image import draw_df_info_img, draw_record_sol, draw_record_tdm
from .msg_info import MsgInfo
from .utils import get_user_id

# 用户调用记录：{user_id: last_call_timestamp}
last_call_times = {}


df_info = SV("三角洲信息")
df_tqc = SV("三角洲特勤处")
df_day = SV("三角洲日报/周报")
df_record = SV("三角洲战绩查询")
df_watch_record = SV("三角洲战绩订阅")


@df_day.on_command(("日报"), block=True)
@df_info.on_command(("信息", "查询"), block=True)
async def login(bot: Bot, ev: Event):
    logger.info("[ss]正在执行三角洲信息功能")
    user_id = await get_user_id(ev)
    data = MsgInfo(user_id, bot.bot_id)
    msg = await data.get_msg_info()
    day = await data.get_daily()
    tqc = await data.get_tqc()

    if isinstance(msg, str):
        await bot.send(msg, at_sender=True)
        return
    if isinstance(day, str):
        await bot.send(day, at_sender=True)
        return
    if isinstance(tqc, str):
        await bot.send(tqc, at_sender=True)
        return
    logger.success("成功获取,正在生成图片")
    info = await draw_df_info_img(msg, day, tqc, ev)

    await bot.send(info, at_sender=True)


@df_day.on_command(("周报"), block=True)
@df_record.on_command(("战绩"), block=True)
async def get_record(
    bot: Bot,
    ev: Event,
):
    logger.info("[ss]正在执行三角洲战绩查询功能")
    await bot.send("正在请求，时间较长请耐心等待")
    user_id = await get_user_id(ev)

    # 60s内最多一次
    current_time = time.time()
    if (
        user_id in last_call_times
        and current_time - last_call_times[user_id] < 60
    ):
        await bot.send("操作过于频繁，请一分钟后再试", at_sender=True)
        return

    data = MsgInfo(user_id, bot.bot_id)
    msg = await data.get_msg_info()
    week_data = await data.get_weekly()

    # current_time2 = time.time()
    # print("apip请求耗时", current_time2 - current_time)
    raw_text = ev.text.strip() if ev.text else ""
    index, record = await data.get_record(raw_text)
    logger.debug("战绩")
    logger.debug(record)
    if index == 0 or isinstance(record, str):
        record_sol = cast(list[RecordSolData], [])
    if isinstance(week_data, str) or isinstance(msg, str):
        await bot.send(str(record), at_sender=True)
        return
    if index == 1:
        record_sol = cast(list[RecordSolData], record)

        await bot.send(
            await draw_record_sol(
                await get_event_avatar(ev), record_sol, week_data, msg
            ),
            at_sender=True,
        )
        # current_time3 = time.time()
        # print("图片生成耗时", current_time3 - current_time2)
        return
    if index == 2:
        await bot.send("to do")
        return

        record_tdm = cast(list[RecordTdmData], record)

        await bot.send(
            await draw_record_tdm(ev, record_tdm, msg), at_sender=True
        )

        return
    last_call_times[user_id] = current_time
    return


@df_tqc.on_command(("特勤处"), block=True)
async def get_tqc(
    bot: Bot,
    ev: Event,
):
    raw_text = ev.text.strip() if ev.text else ""
    if raw_text and "开启" in raw_text:
        logger.info("[ss]正在执行三角洲特勤处推送功能")
        data = MsgInfo(ev.user_id, bot.bot_id)
        await gs_subscribe.add_subscribe(
            "single",
            "ss特勤处订阅",
            ev,
            extra_message=ev.group_id,
        )
        data = await gs_subscribe.get_subscribe("ss订阅")
        logger.info(data)
        await bot.send("订阅成功！")
    elif raw_text and "关闭" in raw_text:
        logger.info("[ss]正在执行关闭三角洲特勤处推送功能")
        await gs_subscribe.delete_subscribe(
            "single",
            "ss特勤处订阅",
            ev,
        )
        await bot.send("取消订阅成功！")

    else:
        logger.info("[ss]正在执行三角洲特勤处功能")
        data = MsgInfo(ev.user_id, bot.bot_id)
        a = await data.get_tqc()
        await bot.send(str(a), at_sender=True)


@df_watch_record.on_command(("订阅"), block=True)
async def watch_record(
    bot: Bot,
    ev: Event,
):
    logger.info("[ss]正在执行三角洲战绩订阅功能")
    raw_text = ev.text.strip() if ev.text else ""
    user_id = ev.user_id
    data = MsgInfo(user_id, bot.bot_id)
    msg = await data.get_msg_info()
    if isinstance(msg, str):
        await bot.send(msg, at_sender=True)
        return

    raw_text = ev.text.strip() if ev.text else ""
    index, record = await data.get_record(raw_text)

    if raw_text == "开启" or raw_text == "":
        await gs_subscribe.add_subscribe(
            "single",
            "三角洲战绩订阅",
            ev,
            extra_message=user_id,
        )
        await bot.send("[ss] 三角洲战绩订阅成功！")
        # return await bot.send("[ss] 三角洲战绩订阅成功！")

    elif raw_text == "关闭":
        await gs_subscribe.delete_subscribe("single", "订阅测试", ev)

    # 测试输出
    logger.debug("测试输出")

    record_sol = await data.watch_record_sol(msg["user_name"], "sol")
    # record_tdm = await data.watch_record_tdm(msg["user_name"], user_id)
    await bot.send(str(record_sol)) if record_sol else None
    # await data.watch_record_tdm(record, user_id)

    ## to do


# @scheduler.scheduled_job("cron", minute="*/2")
async def majsoul_notify_rank():
    await asyncio.sleep(random.randint(0, 1))
    datas = await gs_subscribe.get_subscribe("三角洲战绩订阅")
    if not datas:
        return
    for subscribe in datas:
        user_id = subscribe.user_id
        data = MsgInfo(user_id, subscribe.bot_id)
        # msg = await data.get_msg_info()
        for raw_text in ["烽火", "战场"]:
            index, record = await data.get_record(raw_text)
            ## to do
