import asyncio
import base64
import json
from typing import Any, Dict, Optional, cast

from gsuid_core.bot import Bot
from gsuid_core.models import Event, Message
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_pic

from ..utils.api.api import DeltaApi
from ..utils.api.util import Util
from ..utils.database.models import DFBind, DFUser
from ..utils.models import UserData

# 定义常量
MAX_LOGIN_ATTEMPTS = 120
LOGIN_ATTEMPT_INTERVAL = 0.5


async def _process_login_result(
    bot: Bot, ev: Event, res: Dict[str, Any], platform: str
) -> Optional[UserData]:
    """处理登录结果的通用逻辑"""
    if not res.get("status"):
        await bot.logger.info(f"[DF] 登录失败: {res.get('message', '未知错误')}")
        await bot.send(f"登录失败：{res.get('message', '未知错误')}", at_sender=True)
        return None

    access_token = res["data"]["access_token"]
    openid = res["data"]["openid"]
    qq_id = ev.user_id
    group_id = ev.group_id if ev.group_id else 0

    # 绑定账号
    deltaapi = DeltaApi(platform)
    bind_res = await deltaapi.bind(access_token=access_token, openid=openid)
    if not bind_res["status"]:
        await bot.logger.info(f"[DF] 绑定失败: {bind_res.get('message', '未知错误')}")
        await bot.send(
            f"绑定失败：{bind_res.get('message', '未知错误')}", at_sender=True
        )
        return None

    # 获取玩家信息
    player_info_res = await deltaapi.get_player_info(
        access_token=access_token, openid=openid
    )
    if not player_info_res["status"]:
        await bot.logger.info(
            f"[DF] 查询角色信息失败: {player_info_res.get('message', '未知错误')}"
        )
        await bot.send(
            f"查询角色信息失败：{player_info_res.get('message', '未知错误')}",
            at_sender=True,
        )
        return None

    # 构建用户数据
    user_data = cast(
        UserData,
        {
            "qq_id": qq_id,
            "group_id": group_id,
            "access_token": access_token,
            "openid": openid,
            "platform": platform,
        },
    )

    # 保存用户数据
    await DFUser.insert_user(bot.bot_id, user_data)
    await DFBind.insert_user(ev, bot.bot_id, user_data)

    # 发送登录成功消息
    user_name = player_info_res["data"]["player"]["charac_name"]
    money = Util.trans_num_easy_for_read(player_info_res["data"]["money"])
    await bot.logger.info(f"[DF] 用户 {qq_id} 登录成功，角色名: {user_name}")
    await bot.send(
        f"登录成功，角色名：{user_name}，现金：{money}\n登录有效期60天，在小程序登录会使这里的登录状态失效",
        at_sender=True,
    )

    return user_data


async def _login_with_qq(bot: Bot, ev: Event) -> Optional[UserData]:
    """使用QQ登录的逻辑"""
    deltaapi = DeltaApi("qq")

    # 获取二维码
    res = await deltaapi.get_sig()
    if not res["status"] or isinstance(res["message"], str):
        await bot.logger.info(
            f"[DF] 获取QQ二维码失败: {res.get('message', '未知错误')}"
        )
        await bot.send(f"获取二维码失败：{res.get('message', '未知错误')}")
        return None

    # 解码二维码
    imagebase64 = res["message"]["image"]
    cookie = json.dumps(res["message"]["cookie"])
    qrSig = res["message"]["qrSig"]
    qrToken = res["message"]["token"]
    loginSig = res["message"]["loginSig"]

    img = base64.b64decode(imagebase64)
    await bot.send(
        [
            Message(type="text", data="请打开手机qq使用摄像头扫码"),
            Message(type="image", data=img),
        ],
        at_sender=True,
    )

    # 等待扫码登录
    attempts = 0
    while attempts < MAX_LOGIN_ATTEMPTS:
        res = await deltaapi.get_login_status(cookie, qrSig, qrToken, loginSig)

        if res["code"] == 0:
            cookie = json.dumps(res["data"]["cookie"])
            token_res = await deltaapi.get_access_token(cookie)
            return await _process_login_result(bot, ev, token_res, "qq")
        elif res["code"] in (-4, -2, -3):
            await bot.logger.info(f"[DF] QQ登录失败: {res.get('message', '未知错误')}")
            await bot.send(
                f"登录失败：{res.get('message', '未知错误')}", at_sender=True
            )
            return None
        elif res["code"] == -1:  # 假设-1表示超时
            await bot.logger.info("[DF] QQ登录超时")
            await bot.send("登录超时，请重新尝试", at_sender=True)
            return None

        attempts += 1
        await asyncio.sleep(LOGIN_ATTEMPT_INTERVAL)

    await bot.logger.info("[DF] QQ登录超过最大尝试次数")
    await bot.send("登录超时，请重新尝试", at_sender=True)
    return None


async def _login_with_wechat(bot: Bot, ev: Event) -> Optional[UserData]:
    """使用微信登录的逻辑"""
    deltaapi = DeltaApi("wx")

    # 获取微信登录二维码
    res = await deltaapi.get_wechat_login_qr()
    if not res["status"]:
        await bot.logger.info(
            f"[DF] 获取微信二维码失败: {res.get('message', '未知错误')}"
        )
        await bot.send(f"获取二维码失败：{res.get('message', '未知错误')}")
        return None

    img_url: str = res["data"]["qrCode"]
    uuid = res["data"]["uuid"]

    try:
        img = await get_pic(img_url)
        img_bytes = await convert_img(img)
        await bot.send(
            [
                Message(type="text", data="请打开手机微信使用摄像头扫码"),
                Message(type="image", data=img_bytes),
            ],
            at_sender=True,
        )
    except Exception as e:
        await bot.logger.error(f"[DF] 获取微信二维码图片失败: {str(e)}")
        await bot.send("获取二维码图片失败，请重试", at_sender=True)
        return None

    # 等待扫码登录
    attempts = 0
    while attempts < MAX_LOGIN_ATTEMPTS:
        res = await deltaapi.check_wechat_login_status(uuid)

        if res["status"] and res["code"] == 3:
            wx_code = res["data"]["wx_code"]
            token_res = await deltaapi.get_wechat_access_token(wx_code)
            return await _process_login_result(bot, ev, token_res, "wx")
        elif not res["status"]:
            await bot.logger.info(
                f"[DF] 微信登录失败: {res.get('message', '未知错误')}"
            )
            await bot.send(
                f"登录失败：{res.get('message', '未知错误')}", at_sender=True
            )
            return None

        attempts += 1
        if attempts >= MAX_LOGIN_ATTEMPTS:
            await bot.logger.info("[DF] 微信登录超时")
            await bot.send("登录超时，请重新尝试", at_sender=True)
            return None

        await asyncio.sleep(LOGIN_ATTEMPT_INTERVAL)

    return None


async def login_in(bot: Bot, ev: Event) -> Optional[UserData]:
    """处理用户登录请求
    参数:
        bot: Bot实例
        ev: 事件对象
    返回:
        UserData: 登录成功的用户数据，如果失败则返回None
    """
    platform = ev.text.lower() if ev.text else "qq"

    if platform in ("", "qq"):
        platform = "qq"
    elif platform == "微信":
        platform = "wx"
    else:
        await bot.logger.warning(f"[DF] 平台参数错误: {platform}")
        await bot.send("平台参数错误，请使用QQ或微信", at_sender=True)
        return None

    await bot.logger.info(f"[DF] 用户 {ev.user_id} 请求登录，平台: {platform}")

    try:
        if platform == "qq":
            return await _login_with_qq(bot, ev)
        else:
            return await _login_with_wechat(bot, ev)
    except Exception as e:
        await bot.logger.error(f"[DF] 登录过程发生错误: {str(e)}")
        await bot.send("登录过程发生错误，请稍后重试", at_sender=True)
        return None


async def out_login(bot: Bot, ev: Event) -> Optional[Dict[str, str]]:
    """导出用户登录信息
    参数:
        bot: Bot实例
        ev: 事件对象
    返回:
        Dict: 包含openid、token和platform的字典，如果失败则返回None
    """
    qid = ev.user_id
    await bot.logger.info(f"[DF] [导出用户信息]UserID: {qid}")

    login_info = await DFUser.select_data(ev.user_id, ev.bot_id)
    if login_info is None:
        await bot.logger.warning(f"[DF] 用户 {qid} 导出失败: 未登录")
        await bot.send("[DF] 导出失败! 请先登录!")
        return None

    await bot.logger.info(f"[DF] 用户 {qid} 导出成功")
    return {
        "openid": login_info.uid,
        "token": login_info.cookie,
        "platform": login_info.platform,
    }
