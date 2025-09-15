from typing import Any, Dict, List, Optional

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.api import DeltaApi
from ..utils.database.models import DFUser

# 创建服务实例
DF_PASSWORD_SV = SV("三角洲密码")

# 定义常量
NO_VALID_ACCOUNT_MSG = '所有已绑定账号已过期，请先用"三角洲登录"命令登录至少一个账号'


async def _get_password_for_user(user_data: Any) -> Optional[str]:
    """为单个用户获取密码信息
    参数:
        user_data: 用户数据对象
    返回:
        str: 格式化的密码信息字符串，如果获取失败则返回None
    """
    try:
        deltaapi = DeltaApi(user_data.platform)
        res = await deltaapi.get_password(user_data.cookie, user_data.uid)

        # 检查响应状态和数据
        if not res.get("status"):
            logger.warning(f"[DF] 获取密码失败: {res.get('message', '未知错误')}")
            return None

        password_list = res.get("data", {}).get("list", [])
        if not password_list:
            return None

        # 构建密码信息字符串
        msgs = []
        for password in password_list:
            map_name = password.get("mapName", "未知地图")
            secret = password.get("secret", "未知密码")
            msgs.append(f"{map_name}：{secret}")

        return "\n".join(msgs)
    except Exception as e:
        logger.error(f"[DF] 获取用户密码时发生错误: {str(e)}")
        return None


@DF_PASSWORD_SV.on_command("密码", block=True)
async def handle_password_query(bot: Bot, event: Event) -> None:
    """处理密码查询命令
    参数:
        bot: Bot实例，用于发送消息
        event: 事件对象，包含命令和用户信息
    """
    logger.info(f"[DF] 用户 {event.user_id} 正在执行密码查询")

    try:
        # 获取所有用户数据
        user_data_list = await DFUser.get_all_data()
        logger.debug(f"[DF] 获取到 {len(user_data_list)} 条用户数据")

        # 遍历用户数据，尝试获取有效的密码信息
        for user_data in user_data_list:
            password_info = await _get_password_for_user(user_data)
            if password_info:
                await bot.send(password_info)
                return

        # 如果所有账号都无效，发送提示消息
        await bot.send(NO_VALID_ACCOUNT_MSG, at_sender=True)
    except Exception as e:
        logger.error(f"[DF] 处理密码查询时发生错误: {str(e)}")
        await bot.send("查询过程中发生错误，请稍后重试", at_sender=True)
