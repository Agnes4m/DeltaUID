from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger

ss_player_info = SV('角色信息')
ss_player_item = SV('装备')


@ss_player_info.on_command(('我的信息'))
async def send_stock_info(bot: Bot, ev: Event):
    logger.info('[RatGrinder] 开始执行[我的信息]')
    await bot.send("")


@ss_player_item.on_command(('装备'))
async def send_my_stock(bot: Bot, ev: Event):
    """这里执行穿上，放下操作"""
    logger.info('[RatGrinder] 开始执行[装备管理操作]')
    await bot.send("")


# 每天0点刷新每日任务
@scheduler.scheduled_job('cron', hour=0, minute=0)
async def update_day_mission_RatGrinder(): ...
