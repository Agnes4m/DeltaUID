from plugins.RatGrinder.RatGrinder.utils.models import SsPlayer

from ..utils.utils import create_ssplayer
from ..utils.database.models import SsBind


async def create_player(user_id: str, bot_id: str, name: str):
    """"""
    exists = await SsBind.data_get(user_id=user_id)
    if exists is not None:
        return 1
    ss_play: SsPlayer = create_ssplayer(name=name)
    return await SsBind.insert_data(
        user_id=user_id, bot_id=bot_id, name=name, player=ss_play
    )


async def bind_user_id(user_id: str, uid: str):
    """
    绑定QQ UID到其他平台UID。

    参数:
    - user_id: 要绑定的QQ UID。
    - uid: 要绑定的其他平台UID。

    返回值:
    - 1 绑定成功
    - 0 该qq号未创建
    - -1  其他错误
    """
    bind = await SsBind.data_get(user_id=user_id)
    if bind is None:
        return 0
    bind.uid_list.append(uid)
    return await SsBind.data_update(user_id, uid_list=bind.uid_list)
