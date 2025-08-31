from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

# from gsuid_core.logger import logger
from gsuid_core.sv import SV
from gsuid_core.utils.message import send_diff_msg

from ..utils.database.models import DFBind
from .login import login_in, out_login

# from gsuid_core.utils.database.api import get_uid


df_login = SV("三角洲登录")


@df_login.on_command(
    keyword=(
        "登录",
        "切换",
        "删除",
    ),
    block=True,
)
async def login(bot: Bot, ev: Event):
    await bot.logger.info("[DF] 开始执行[登录用户信息]")
    qid = ev.user_id
    await bot.logger.info("[DF] [绑定/解绑]UserID: {}".format(qid))

    if "登录" in ev.command:
        login_info = await login_in(bot, ev)
        print(login_info)
        if login_info is None:
            logger.error("[DF] 登录失败")
            return
        uid = login_info["openid"]
        data = await DFBind.insert_uid(qid, ev.bot_id, uid, ev.group_id)
        return
    elif "切换" in ev.command:
        retcode = await DFBind.switch_uid_by_game(qid, ev.bot_id)
        if retcode == 0:
            return await bot.send("[DF] 切换UID成功！")
        elif retcode == -3:
            now_uid = await DFBind.get_uid_by_game(qid, ev.bot_id)
            if now_uid:
                return await bot.send(
                    f"[DF] 你目前只绑定了一个UID{now_uid}, 无法切换!"
                )
            else:
                return await bot.send("[DF] 你尚未绑定任何UID, 无法切换!")
        else:
            return await bot.send("[DF] 尚未绑定该UID")
    else:
        now_uid = await DFBind.get_uid_by_game(qid, ev.bot_id)
        if now_uid is None:
            return await bot.send("[DF] 你尚未绑定任何UID, 无法删除!")
        data = await DFBind.delete_uid(qid, ev.bot_id, now_uid)
        return await send_diff_msg(
            bot,
            data,
            {
                0: "[DF] 删除UID成功！",
                -1: "[DF] 该UID不在已绑定列表中！",
            },
        )


@df_login.on_command(
    keyword=("导出"),
    block=True,
)
async def out_l(bot: Bot, ev: Event):
    await bot.logger.info("[DF] 开始执行[导出用户信息]")
    if ev.group_id is not None:
        return await bot.send("[DF] 请在私聊中使用该命令!")
    qid = ev.user_id
    await bot.logger.info("[DF] [导出用户信息]UserID: {}".format(qid))

    login_info = await out_login(bot, ev)
    print(login_info)
    return await bot.send(str(login_info))
