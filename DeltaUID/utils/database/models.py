from typing import Optional, cast

from sqlmodel import Field, select
from sqlalchemy.ext.asyncio import AsyncSession

from gsuid_core.bot import Event
from gsuid_core.logger import logger
from gsuid_core.webconsole import site
from gsuid_core.webconsole.mount_app import GsAdminModel
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.utils.database.base_models import Bind, User, with_session

from ..models import UserData

exec_list.append('ALTER TABLE DFUser ADD COLUMN latest_record TEXT DEFAULT ""')
exec_list.append('ALTER TABLE DFUser ADD COLUMN latest_tdm_record TEXT DEFAULT ""')


class DFBind(Bind, table=True):
    group_id: Optional[str] = Field(default=None, title="群组ID")
    uid: Optional[str] = Field(default=None, title="三角洲uid")

    @classmethod
    @with_session
    async def insert_user(
        cls,
        session: AsyncSession,
        ev: Event,
        bot_id: str,
        data: UserData,
    ):
        return await cls.insert_data(
            user_id=ev.user_id,
            bot_id=bot_id,
            uid=data["openid"],
            group_id=data["group_id"],
        )

    @classmethod
    @with_session
    async def get_uid_by_game(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
    ) -> Optional[str]:
        """根据用户ID和BotID获取三角洲UID"""
        data = await cls.select_data(user_id, bot_id)
        return data.uid if data else None

    @classmethod
    @with_session
    async def insert_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        uid: str,
        is_digit: bool = True,
    ):
        """插入用户UID绑定"""
        return await cls.insert_data(
            user_id,
            bot_id,
            uid=uid,
        )

    @classmethod
    @with_session
    async def switch_uid_by_game(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        uid: str,
    ) -> int:
        """切换用户当前UID"""
        data = await cls.select_data(user_id, bot_id)
        if data is None:
            return -1
        await cls.update_data(
            user_id,
            bot_id,
            uid=uid,
        )
        return 0

    @classmethod
    @with_session
    async def delete_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        uid: str,
    ):
        """删除指定UID"""
        await cls.delete_data(
            user_id,
            bot_id,
            uid=uid,
        )


class DFUser(User, table=True):
    uid: str = Field(default="", title="三角洲uid")
    platform: str = Field(default="qq", title="平台")
    latest_record: str | None = Field(default="", title="最新烽火战绩id")
    latest_tdm_record: str | None = Field(default="", title="最新战场战绩id")

    @classmethod
    @with_session
    async def insert_user(
        cls,
        session: AsyncSession,
        bot_id: str,
        data: UserData,
    ):
        return await cls.insert_data(
            user_id=data["qq_id"],
            bot_id=bot_id,
            uid=data["openid"],
            platform=data["platform"],
            cookie=data["access_token"],
        )

    @classmethod
    @with_session
    async def get_all_cookie(cls, session: AsyncSession) -> list["DFUser"]:
        """获取所有用户的cookie数据"""
        logger.debug(f"get_all_cookie called with session: {session}")
        try:
            result = await session.execute(select(cls))
            result = result.scalars().all()
            logger.debug(f"get_all_cookie result type: {type(result)}, value: {result}")
            return list(result) if result is not None else []
        except Exception as e:
            logger.error(f"get_all_cookie error: {e}")
            return []

    @classmethod
    @with_session
    async def get_all_data(cls, session: AsyncSession) -> list["DFUser"]:
        """获取所有用户数据"""
        logger.debug(f"get_all_data called with session: {session}")
        try:
            result = await session.execute(select(cls))
            result = result.scalars().all()
            logger.debug(f"get_all_data result type: {type(result)}, value: {result}")
            return list(result) if result is not None else []
        except Exception as e:
            logger.error(f"get_all_data error: {e}")
            return []

    @classmethod
    @with_session
    async def get_user_cookie_by_uid(
        cls,
        session: AsyncSession,
        uid: str,
    ) -> Optional[str]:
        """根据三角洲UID获取用户cookie"""
        data = await cls.select_data_by_uid(uid=uid)
        return data.cookie if data else None

    @classmethod
    @with_session
    async def get_latest_record(
        cls,
        session: AsyncSession,
        uid: str,
        mode: str = "sol",
    ) -> str | None:
        data = await cls.select_data_by_uid(uid=uid)
        if data is None:
            return None
        data = cast(DFUser, data)
        if mode == "sol":
            return data.latest_record
        elif mode == "tdm":
            return data.latest_tdm_record
        else:
            return None

    @classmethod
    @with_session
    async def update_record(
        cls,
        session: AsyncSession,
        bot_id: str,
        uid: str,
        latest_record: Optional[str] = None,
        latest_tdm_record: Optional[str] = None,
    ):
        data = await cls.select_data_by_uid(uid=uid)
        if data is None:
            logger.debug(f"未找到用户 {uid}，无法更新战绩")
            return None
        data = cast(DFUser, data)
        if data is None:
            raise ValueError(f"未找到用户 {uid}")
        # 如果参数为 None，保留原有数据
        if latest_record is None:
            latest_record = data.latest_record
        if latest_tdm_record is None:
            latest_tdm_record = data.latest_tdm_record
        await cls.update_data_by_uid(
            uid=uid,
            bot_id=bot_id,
            latest_record=latest_record,
            latest_tdm_record=latest_tdm_record,
        )


@site.register_admin
class DFBindadmin(GsAdminModel):
    pk_name = "id"

    # 配置管理模型
    model = DFBind


@site.register_admin
class DFUseradmin(GsAdminModel):
    pk_name = "id"

    # 配置管理模型
    model = DFUser
