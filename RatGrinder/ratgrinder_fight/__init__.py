from cgitb import text

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger

ss_mission = SV('副本')
ss_player_fight = SV('战斗')


@ss_mission.on_command(('猛攻'))
async def send_stock_info(bot: Bot, ev: Event):
    logger.info('[RatGrinder] 开始执行[进入副本]')
    if not ev.text.strip():
        resp = await bot.receive_resp(
            '请输入你要进入的副本名称',
        )
        if resp is not None:
            tap = resp.text.strip()
            if tap in ["大坝"]:
                await bot.send("进入大坝副本")
            else:
                await bot.send("副本不存在，请检查输入是否正确")
    else:
        tap = ev.text.strip()
        if tap in ["大坝"]:
            await bot.send("进入大坝副本")
        else:
            await bot.send("副本不存在，请检查输入是否正确")


@ss_player_fight.on_command(('射击'))
async def send_my_stock(bot: Bot, ev: Event):
    """这里执行穿上，放下操作"""
    logger.info('[RatGrinder] 开始执行[装备管理操作]')
    await bot.send("")


# 每天0点刷新每日任务
@scheduler.scheduled_job('cron', hour=0, minute=0)
async def update_day_mission_RatGrinder(): ...
