from pathlib import Path

from PIL import Image

from gsuid_core.status.plugin_status import register_status
from gsuid_core.subscribe import gs_subscribe

from ..Delta_user.msg_info import MsgInfo
from ..utils.database.models import DFBind, DFUser

ICON = Path(__file__).parent.parent.parent / "icon.png"


def get_ICON():
    return Image.open(ICON)


async def get_user_num():
    datas = await DFUser.get_all_cookie()
    return len(datas)


async def get_add_num():
    datas = await DFBind.get_all_data()
    all_uid = []
    for data in datas:
        if data.uid:
            all_uid.extend(data.user_id.split("_"))
    return len(set(all_uid))


async def get_sign_num():
    datas = await gs_subscribe.get_subscribe('ss特勤处订阅')
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
