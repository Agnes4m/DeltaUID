from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from .msg_info import MsgInfo

# from gsuid_core.utils.database.api import get_uid


df_login = SV("三角洲信息")


@df_login.on_command(("信息"), block=True)
async def login(bot: Bot, ev: Event):
    logger.info("[ss]正在执行三角洲信息功能")
    data = MsgInfo(ev.user_id, bot.bot_id)
    await bot.send(await data.get_msg_info(), at_sender=True)


@df_login.on_command(("战绩"), block=True)
async def get_record(
    bot: Bot,
    ev: Event,
):
    logger.info("[ss]正在执行三角洲战绩查询功能")
    data = MsgInfo(ev.user_id, bot.bot_id)
    raw_text = ev.text.strip() if ev.text else ""
    await bot.send(await data.get_record(raw_text), at_sender=True)
