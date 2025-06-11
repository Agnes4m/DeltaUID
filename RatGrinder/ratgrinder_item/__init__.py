from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.message import send_diff_msg

from .bind import bind_qq_uid, create_player

ss_bag = SV('背包')


@ss_bag.on_command(('背包查看'))
async def send_stock_info(bot: Bot, ev: Event):
    logger.info('[RatGrinder] 开始执行[创建角色]')
    qq_uid = str(ev.user_id)
    name = ev.sender['nickname']
    data = await create_player(qq_uid=qq_uid, name=name)
    await send_diff_msg(
        bot,
        code=data,
        data={
            0: f"[RatG] 创建角色{name}({qq_uid})成功！",
            1: f"[RatG] 角色{name}({qq_uid})已经创建过了！",
        },
    )
