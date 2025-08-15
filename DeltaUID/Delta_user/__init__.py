# import asyncio

# from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.sv import SV

from .msg_info import MsgInfo

# from gsuid_core.utils.database.api import get_uid


df_info = SV("三角洲信息")
df_tqc = SV("三角洲特勤处")


@df_info.on_command(("信息"), block=True)
async def login(bot: Bot, ev: Event):
    logger.info("[ss]正在执行三角洲信息功能")
    data = MsgInfo(ev.user_id, bot.bot_id)
    await bot.send(await data.get_msg_info(), at_sender=True)


@df_info.on_command(("战绩"), block=True)
async def get_record(
    bot: Bot,
    ev: Event,
):
    logger.info("[ss]正在执行三角洲战绩查询功能")
    data = MsgInfo(ev.user_id, bot.bot_id)
    raw_text = ev.text.strip() if ev.text else ""
    await bot.send(await data.get_record(raw_text), at_sender=True)


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
            'single',
            'ss特勤处订阅',
            ev,
            extra_message=ev.group_id,
        )
        data = await gs_subscribe.get_subscribe('ss订阅')
        logger.info(data)
        await bot.send('订阅成功！')
    elif raw_text and "关闭" in raw_text:
        logger.info("[ss]正在执行关闭三角洲特勤处推送功能")
        await gs_subscribe.delete_subscribe(
            'single',
            'ss特勤处订阅',
            ev,
        )
        await bot.send('取消订阅成功！')

    else:
        logger.info("[ss]正在执行三角洲特勤处功能")
        data = MsgInfo(ev.user_id, bot.bot_id)
        await bot.send(await data.get_tqc(), at_sender=True)
