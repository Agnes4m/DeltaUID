from typing import List, Optional

from sqlmodel import Field, select
from gsuid_core.webconsole import site
from sqlalchemy.ext.asyncio import AsyncSession
from gsuid_core.webconsole.mount_app import GsAdminModel
from fastapi_amis_admin.amis.components import PageSchema
from gsuid_core.utils.database.base_models import BaseModel, with_session

from ..models import SsPlayer
from ..utils import create_ssplayer


class SsBind(BaseModel, table=True):
    __table_args__ = {'extend_existing': True}
    qq_uid: str = Field(default=None, title='qqUID')
    uid: List[str] = Field(default=None, title='其他平台UID')
    player: SsPlayer = Field(default=create_ssplayer(), title='角色信息')

    @classmethod
    @with_session
    async def insert_data(
        cls,
        session: AsyncSession,
        qq_uid: str,
        name: str,
        player: SsPlayer,
    ) -> int:
        return await cls.full_insert_data(
            qq_uid=qq_uid, name=name, player=player
        )

    @classmethod
    @with_session
    async def data_get(
        cls, session: AsyncSession, qq_uid: str
    ) -> "SsBind | None":
        """
        输出指定QQ UID的数据，否则输出None。

        参数:
        - session (AsyncSession): 数据库会话对象。
        - qq_uid (str): 要检查的QQ UID。

        返回值:
        - bool: 如果存在数据则返回数据，否则返回False。
        """
        stmt = select(cls).where(cls.qq_uid == qq_uid)
        result = await session.execute(stmt)
        data = result.scalars().first()
        return data


@site.register_admin
class SsPushAdmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='游戏信息管理',
        icon='fa fa-bullhorn',
    )  # type: ignore

    model = SsBind

    model = SsBind
