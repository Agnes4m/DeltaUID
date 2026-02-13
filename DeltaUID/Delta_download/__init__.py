from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .utils import check_use

sv_df_download_config = SV("ss下载资源")


@sv_df_download_config.on_fullmatch("下载全部资源", block=True)
async def send_download_resource_msg(bot: Bot, ev: Event):
    await bot.send("正在开始下载~可能需要较久的时间!")
    im = await check_use(bot, ev)
    await bot.send(im)


# async def startup():
#     await check_use()
