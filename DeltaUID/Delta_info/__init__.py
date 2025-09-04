from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.api import DeltaApi
from ..utils.database.models import DFUser

# from gsuid_core.utils.database.api import get_uid


df_pw = SV("三角洲密码")


@df_pw.on_command(("密码"), block=True)
async def _(bot: Bot, event: Event):
    logger.info("[ss正在执行密码查询]")

    user_data_list = await DFUser.get_all_data()
    print(user_data_list)
    for user_data in user_data_list:
        deltaapi = DeltaApi(user_data.platform)
        res = await deltaapi.get_password(user_data.cookie, user_data.uid)
        msgs = None
        password_list = res["data"].get("list", [])
        if password_list:
            for password in password_list:
                if msgs is None:
                    msgs = f"{password.get('mapName', '未知地图')}：{password.get('secret', '未知密码')}"

                else:
                    msgs += f"\n{password.get('mapName', '未知地图')}：{password.get('secret', '未知密码')}"
            if msgs is not None:
                await bot.send(msgs)
            return
    await bot.send(
        '所有已绑定账号已过期，请先用"三角洲登录"命令登录至少一个账号',
        at_sender=True,
    )
