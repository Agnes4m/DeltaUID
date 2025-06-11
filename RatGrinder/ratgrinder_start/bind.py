from ..utils.utils import create_ssplayer
from ..utils.database.models import SsBind


async def create_player(qq_uid: str, name: str):
    """"""
    exists = await SsBind.data_get(qq_uid=qq_uid)
    if exists is not None:
        return 1
    ss_play = await create_ssplayer(name=name)
    return await SsBind.insert_data(qq_uid=qq_uid, name=name, player=ss_play)


async def bind_qq_uid(qq_uid: str, uid: str):
    """
    绑定QQ UID到其他平台UID。

    参数:
    - qq_uid: 要绑定的QQ UID。
    - uid: 要绑定的其他平台UID。

    返回值:
    - 1 绑定成功
    - 0 该qq号未创建
    - -1  其他错误
    """
    bind = await SsBind.data_get(qq_uid=qq_uid)
    if bind is None:
        return 0
    bind.uid_list.append(uid)
    return await SsBind.data_update(qq_uid, uid_list=bind.uid_list)
