from ..utils.utils import create_ssplayer
from ..utils.database.models import SsBind


async def create_player(qq_uid: str, name: str):
    """"""
    exists = await SsBind.data_get(qq_uid=qq_uid)
    if exists is not None:
        return 1
    ss_play = await create_ssplayer(qq_uid=qq_uid, name=name)
    return await SsBind.insert_data(qq_uid=qq_uid, name=name, player=ss_play)


async def bind_qq_uid(qq_uid: str, uid: str) -> None:
    """
    绑定QQ UID到其他平台UID。

    参数:
    - qq_uid (str): 要绑定的QQ UID。
    - uid (str): 要绑定的其他平台UID。

    返回值:
    - None
    """
    bind = await SsBind.data_get(qq_uid=qq_uid)
    if bind is None:
        bind = SsBind(qq_uid=qq_uid, uid=[uid])
        await bind.insert_data()
    else:
        if uid not in bind.uid:
            bind.uid.append(uid)
            await bind.update_data()
            await bind.update_data()
            await bind.update_data()
