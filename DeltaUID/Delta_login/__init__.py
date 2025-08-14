import asyncio
import base64
import json
from typing import cast

from gsuid_core.bot import Bot

# from gsuid_core.logger import logger
from gsuid_core.models import Event, Message
from gsuid_core.sv import SV

from ..utils.api.api import DeltaApi
from ..utils.api.util import Util
from ..utils.database.models import DFBind, DFUser
from ..utils.models import UserData

# from gsuid_core.utils.database.api import get_uid


df_login = SV("三角洲登录")


@df_login.on_command(("登录"), block=True)
async def login(bot: Bot, ev: Event):
    platform = ev.text.lower() if ev.text else "qq"

    if platform in ("", "qq"):
        platform = "qq"
    elif platform == "微信":
        platform = "wx"
    else:
        await bot.send("平台参数错误，请使用QQ或微信", at_sender=True)
        return

    deltaapi = DeltaApi(platform)

    if platform == "qq":
        # 获取二维码
        res = await deltaapi.get_sig()
        if not res['status'] or isinstance(res['message'], str):
            await bot.send(f"获取二维码失败：{res['message']}")
            return

        # 解码二维码
        iamgebase64 = res['message']['image']
        cookie = json.dumps(res['message']['cookie'])
        # logger.debug(f"cookie: {cookie},type: {type(cookie)}")
        qrSig = res['message']['qrSig']
        qrToken = res['message']['token']
        loginSig = res['message']['loginSig']

        img = base64.b64decode(iamgebase64)
        await bot.send(
            [
                Message(type="text", data="请打开手机qq使用摄像头扫码"),
                Message(type="image", data=img),
            ],
            at_sender=True,
        )

        # 等待扫码登录
        while True:
            res = await deltaapi.get_login_status(
                cookie, qrSig, qrToken, loginSig
            )
            if res['code'] == 0:
                cookie = json.dumps(res['data']['cookie'])
                res = await deltaapi.get_access_token(cookie)
                if res['status']:
                    access_token = res['data']['access_token']
                    openid = res['data']['openid']
                    qq_id = ev.user_id
                    if ev.group_id:
                        group_id = ev.group_id
                    else:
                        group_id = 0
                    res = await deltaapi.bind(
                        access_token=access_token, openid=openid
                    )
                    if not res['status']:
                        await bot.send(
                            f"绑定失败：{res['message']}", at_sender=True
                        )
                        break
                    res = await deltaapi.get_player_info(
                        access_token=access_token, openid=openid
                    )
                    if res['status']:
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
                        await DFUser.insert_user(bot, user_data)
                        await DFBind.insert_user(ev, bot, user_data)

                        user_name = res['data']['player']['charac_name']

                        await bot.send(
                            f"登录成功，角色名：{user_name}，现金：{Util.trans_num_easy_for_read(res['data']['money'])}\n登录有效期60天，在小程序登录会使这里的登录状态失效",
                            at_sender=True,
                        )
                        break

                    else:
                        await bot.send(
                            f"查询角色信息失败：{res['message']}",
                            at_sender=True,
                        )
                        break
                else:
                    await bot.send(
                        f"登录失败：{res['message']}", at_sender=True
                    )
                    break

            elif res['code'] == -4 or res['code'] == -2 or res['code'] == -3:
                await bot.send(f"登录失败：{res['message']}", at_sender=True)
                break

            elif res['code'] == -1:  # 假设-1表示超时
                await bot.send("登录超时，请重新尝试", at_sender=True)
                break

            await asyncio.sleep(0.5)

    elif platform == "wx":
        # 获取微信登录二维码
        res = await deltaapi.get_wechat_login_qr()
        if not res['status']:
            await bot.send(f"获取二维码失败：{res['message']}")
            return
        img_url = res['data']['qrCode']
        uuid = res['data']['uuid']
        await bot.send(
            [
                Message(type="text", data=("请打开手机微信使用摄像头扫码")),
                Message(type="image", data=img_url),
            ],
            at_sender=True,
        )
        # 等待扫码登录
        max_attempts = 120  # 最多尝试120次，约60秒
        attempts = 0
        while attempts < max_attempts:
            res = await deltaapi.check_wechat_login_status(uuid)
            if res['status'] and res['code'] == 3:
                wx_code = res['data']['wx_code']
                res = await deltaapi.get_wechat_access_token(wx_code)
                if res['status']:
                    access_token = res['data']['access_token']
                    openid = res['data']['openid']
                    qq_id = ev.user_id
                    if ev.group_id:
                        group_id = ev.group_id
                    else:
                        group_id = 0
                    res = await deltaapi.bind(
                        access_token=access_token, openid=openid
                    )
                    if not res['status']:
                        await bot.send(
                            f"绑定失败：{res['message']}", at_sender=True
                        )
                        break
                    res = await deltaapi.get_player_info(
                        access_token=access_token, openid=openid
                    )
                    if res['status']:
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
                        await DFUser.insert_user(bot, user_data)
                        await DFBind.insert_user(ev, bot, user_data)

                        user_name = res['data']['player']['charac_name']

                        await bot.send(
                            f"登录成功，角色名：{user_name}，现金：{Util.trans_num_easy_for_read(res['data']['money'])}\n登录有效期60天，在小程序登录会使这里的登录状态失效",
                            at_sender=True,
                        )
                        break
                    else:
                        await bot.send(
                            f"查询角色信息失败：{res['message']}",
                            at_sender=True,
                        )
                        break
                else:
                    await bot.send(
                        f"登录失败：{res['message']}", at_sender=True
                    )
                    break

            elif not res['status']:
                await bot.send(f"登录失败：{res['message']}", at_sender=True)
                break
            attempts += 1

            if attempts >= max_attempts:
                await bot.send("登录超时，请重新尝试", at_sender=True)
                break
            await asyncio.sleep(0.5)
