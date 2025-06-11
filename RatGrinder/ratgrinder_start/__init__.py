from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.message import send_diff_msg

from .bind import create_player

ss_create = SV('创建角色')
ss_play = SV('账户管理')


@ss_create.on_command(('创建角色', '新建角色'))
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


@ss_play.on_command(('绑定qq'))
async def send_my_stock(bot: Bot, ev: Event):
    """to do以后做多平台绑定"""
    logger.info('[RatGrinder] 开始执行[账号管理操作]')
    await bot.send("")


@ss_play.on_fullmatch(('解除绑定', '解绑'))
async def send_future_stock(bot: Bot, ev: Event):
    """to do以后做多平台绑定"""
    logger.info('[RatGrinder] 开始执行[解除绑定]')
    await bot.send("")
