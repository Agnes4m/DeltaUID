import random
import asyncio

from gsuid_core.aps import scheduler

# from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe

from ..Delta_user.msg_info import MsgInfo
from ..utils.database.models import DFUser


@scheduler.scheduled_job("cron", minute="*/2")
async def df_tqc_rank():
    await asyncio.sleep(random.randint(0, 1))
    datas = await gs_subscribe.get_subscribe("ss特勤处订阅")
    if not datas:
        return

    for subscribe in datas:
        user_data = await DFUser.select_data(subscribe.user_id, subscribe.bot_id)
        if user_data is None:
            return
        msg = MsgInfo(user_data.user_id, user_data.bot_id)
        tqc = await msg.get_tqc()
        await subscribe.send(tqc)
