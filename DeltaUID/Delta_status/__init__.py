from pathlib import Path

from PIL import Image

from gsuid_core.subscribe import gs_subscribe
from gsuid_core.status.plugin_status import register_status

from ..utils.database.models import DFBind, DFUser

ICON = Path(__file__).parent.parent.parent / "icon.png"


def get_ICON():
    icon = Image.open(ICON)
    if icon.mode != "RGBA":
        icon = icon.convert("RGBA")
        r, g, b, a = icon.split()
        a = a.point(lambda x: 255 if x > 0 else 0)
        icon = Image.merge("RGBA", (r, g, b, a))
    return icon


async def get_user_num():
    from gsuid_core.logger import logger

    logger.debug("get_user_num called")
    datas = await DFUser.get_all_cookie()
    logger.debug(f"get_user_num got datas: type={type(datas)}, value={datas}")
    if datas is None:
        return 0
    return len(datas)


async def get_add_num():
    datas = await DFBind.get_all_data()
    all_uid = []
    for data in datas:
        if data.uid:
            all_uid.extend(data.user_id.split("_"))
    return len(set(all_uid))


async def get_sign_num():
    datas = await gs_subscribe.get_subscribe("ss特勤处订阅")
    # if not datas:
    #     return 0

    # for subscribe in datas:

    #     user_data = await DFUser.select_data(
    #         subscribe.user_id, subscribe.bot_id
    #     )
    #     if user_data is None:
    #         return
    #     msg = MsgInfo(user_data.user_id, user_data.bot_id)
    #     tqc = await msg.get_tqc()
    #     await subscribe.send(tqc)
    return len(datas) if datas else 0


register_status(
    get_ICON(),
    "DeltaUID",
    {
        "账户数量": get_add_num,
        "用户数量": get_user_num,
        "推送数量": get_sign_num,
    },
)
