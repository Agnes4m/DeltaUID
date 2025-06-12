from typing import List, Optional

from gsuid_core.webconsole import site
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import JSON, Field, Column, select
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.webconsole.mount_app import GsAdminModel
from fastapi_amis_admin.amis.components import PageSchema
from gsuid_core.utils.database.base_models import BaseModel, with_session

from ..models import SsPlayer
from ...utils.utils import create_ssplayer


class SsBind(BaseModel, table=True):
    __table_args__ = {'extend_existing': True}
    uid: Optional[str] = Field(default=None, title="ssuid")
    uid_list: List[str] = Field(
        default_factory=list, sa_column=Column(JSON), title='其他平台UID'
    )
    player: SsPlayer = Field(
        default_factory=create_ssplayer,
        sa_column=Column(JSON),
        title='角色信息',
    )

    @classmethod
    @with_session
    async def insert_data(
        cls,
        session: AsyncSession,
        bot_id: str,
        user_id: str,
        name: str,
        player: SsPlayer,
    ) -> int:
        return await cls.full_insert_data(
            user_id=user_id,
            uid="",
            bot_id=bot_id,
            name=name,
            player=player,
        )

    @classmethod
    @with_session
    async def data_get(
        cls, session: AsyncSession, user_id: str
    ) -> "SsBind | None":
        """
        输出指定QQ UID的数据，否则输出None。

        参数:
        - session (AsyncSession): 数据库会话对象。
        - user_id (str): 要检查的QQ UID。

        返回值:
        - bool: 如果存在数据则返回数据，否则返回False。
        """
        stmt = select(cls).where(cls.user_id == user_id)
        result = await session.execute(stmt)
        data = result.scalars().first()
        return data

    @classmethod
    @with_session
    async def data_update(
        cls,
        session: AsyncSession,
        user_id: str,
        name: str = "",
        uid_list: List[str] = [],
        player: Optional[SsPlayer] = None,
    ) -> int:
        """
        更新指定QQ UID的数据。

        参数:
        - session (AsyncSession): 数据库会话对象。
        - user_id (str): 要更新的QQ UID。
        - name (str): 新的名称。
        - player (SsPlayer): 新的角色信息。

        返回值:
        - int: 影响的行数（1为成功，0为未找到，-1为失败）。
        """
        stmt = select(cls).where(cls.user_id == user_id)
        result = await session.execute(stmt)
        data = result.scalars().first()
        if data is None:
            return 0
        for attr, value in {
            'name': name,
            'uid_list': uid_list,
            'player': player,
        }.items():
            if value:
                setattr(data, attr, value)
        session.add(data)
        await session.commit()
        return 1


exec_list.extend(
    [
        'ALTER TABLE SsBind ADD COLUMN uid_list JSON DEFAULT "[]"',
        'ALTER TABLE SsBind ADD COLUMN player JSON DEFAULT \'{"name": "鼠鼠", "money": 50000, "level": 1, "exp": 0.0, "bag": []}\'',
    ]
)


@site.register_admin
class SsPushAdmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='游戏信息管理',
        icon='fa fa-bullhorn',
    )  # type: ignore

    model = SsBind
    model = SsBind
    model = SsBind
