from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.message import send_diff_msg

from .bag import get_bag_info

ss_bag = SV('背包')


@ss_bag.on_command(('仓库查看'))
async def send_stock_info(bot: Bot, ev: Event):
    logger.info('[RatGrinder] 开始执行[仓库查看]')
    qq_uid = str(ev.user_id)
    data = await get_bag_info(qq_uid=qq_uid)
    if data is None:
        await bot.send("没有绑定，请先绑定账号")
        return
    await bot.send(data)
