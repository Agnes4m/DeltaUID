# from gsuid_core.logger import logger
from typing import cast

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.message import send_diff_msg

from .login import login_in, out_login
from ..utils.models import UserData
from ..utils.database.models import DFBind, DFUser

# from gsuid_core.utils.database.api import get_uid
MSG_PREFIX = "[DF]"

df_login = SV("三角洲登录")


def get_response_message(retcode: int) -> str:
    """根据返回码获取响应消息"""
    return {
        0: f"{MSG_PREFIX} 删除UID成功！",
        -1: f"{MSG_PREFIX} 该UID不在已绑定列表中！",
    }.get(retcode, f"{MSG_PREFIX} 操作失败，错误码: {retcode}")


@df_login.on_command(
    keyword=(
        "登录",
        "绑定",
        "切换",
        "删除",
    ),
    block=True,
)
async def login(bot: Bot, ev: Event):
    logger.info(f"{MSG_PREFIX} 开始执行[登录用户信息]")
    qid = ev.user_id
    uid = ev.text.strip()
    logger.info(f"{MSG_PREFIX} [绑定/解绑]UserID: {qid}")

    if "登录" in ev.command:
        login_info = await login_in(bot, ev)
        logger.info(f"{MSG_PREFIX} 登录信息: {login_info}")
        if login_info is None:
            logger.error(f"{MSG_PREFIX} 登录失败")
            await bot.send(f"{MSG_PREFIX} 登录失败，请检查输入")
            return

        uid = login_info["openid"]
        data = await DFBind.insert_uid(qid, ev.bot_id, uid, is_digit=False)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f"{MSG_PREFIX} 绑定UID{uid}成功！",
                -1: f"{MSG_PREFIX} UID{uid}的位数不正确！",
                -2: f"{MSG_PREFIX} UID{uid}已经绑定过了！",
                -3: f"{MSG_PREFIX} 你输入了错误的格式!",
            },
        )
    elif "绑定" in ev.command:
        data = await DFBind.insert_uid(qid, ev.bot_id, uid, is_digit=False)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f"{MSG_PREFIX} 绑定UID{uid}成功！",
                -1: f"{MSG_PREFIX} UID{uid}的位数不正确！",
                -2: f"{MSG_PREFIX} UID{uid}已经绑定过了！",
                -3: f"{MSG_PREFIX} 你输入了错误的格式!",
            },
        )
    elif "切换" in ev.command:
        retcode = await DFBind.switch_uid_by_game(qid, ev.bot_id, uid)
        if retcode == 0:
            await bot.send(f"{MSG_PREFIX} 切换UID成功！")
        elif retcode == -3:
            now_uid = await DFBind.get_uid_by_game(qid, ev.bot_id)
            if now_uid:
                await bot.send(f"{MSG_PREFIX} 你目前只绑定了一个UID{now_uid}, 无法切换!")
            else:
                await bot.send(f"{MSG_PREFIX} 你尚未绑定任何UID, 无法切换!")
        else:
            await bot.send(f"{MSG_PREFIX} 尚未绑定该UID")
    elif "删除" in ev.command:
        now_uid = await DFBind.get_uid_by_game(qid, ev.bot_id)
        if now_uid is None:
            await bot.send(f"{MSG_PREFIX} 你尚未绑定任何UID, 无法删除!")
            return

        data = await DFBind.delete_uid(qid, ev.bot_id, now_uid)
        await send_diff_msg(
            bot,
            data,
            {
                0: f"{MSG_PREFIX} 删除UID成功！",
                -1: f"{MSG_PREFIX} 该UID不在已绑定列表中！",
            },
        )


@df_login.on_command(
    keyword=("添加", "添加ck"),
    block=True,
)
async def add_ck(bot: Bot, ev: Event):
    logger.info(f"{MSG_PREFIX} 添加ck")
    text = ev.text.strip()
    text_list = text.split("\n")
    if len(text_list) <= 2:
        return await bot.send(f"{MSG_PREFIX} 请正确输入ck信息!")

    openid = access_token = platform = ""
    for i in text_list:
        if i.startswith("openid:"):
            openid = i.replace("openid:", "").strip()
        elif i.startswith("token:"):
            access_token = i.replace("token:", "").strip()
        elif i.startswith("platform:"):
            platform = i.replace("platform:", "").strip()
    if not all([openid, access_token, platform]):
        return await bot.send(f"{MSG_PREFIX} 请正确输入ck信息!")

    user_data = cast(
        UserData,
        {
            "qq_id": ev.user_id,
            "group_id": ev.group_id,
            "platform": platform,
            "openid": openid,
            "access_token": access_token,
        },
    )
    await DFUser.insert_user(bot.bot_id, user_data)
    await bot.send(f"{MSG_PREFIX} 添加ck成功!")


@df_login.on_command(
    keyword=("导出"),
    block=True,
)
async def out_l(bot: Bot, ev: Event):
    logger.info(f"{MSG_PREFIX} 开始执行[导出用户信息]")

    # 检查是否在私聊中
    if ev.group_id is not None:
        await bot.send(f"{MSG_PREFIX} 请在私聊中使用该命令!")
        return

    qid = ev.user_id
    logger.info(f"{MSG_PREFIX} [导出用户信息]UserID: {qid}")

    login_info = await out_login(bot, ev)
    logger.info(f"{MSG_PREFIX} 导出信息: {login_info}")

    # 确保返回的信息是字符串
    if login_info is None:
        return
    else:
        msg = ""
        for k, v in login_info.items():
            msg += f"{k}: {v}\n"
        return await bot.send(msg)
