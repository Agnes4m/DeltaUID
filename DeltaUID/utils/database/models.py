from typing import Optional

from fastapi_amis_admin.amis.components import PageSchema
from sqlmodel import Field

from gsuid_core.bot import Event
from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.webconsole import site
from gsuid_core.webconsole.mount_app import GsAdminModel

from ..models import UserData

exec_list.append('ALTER TABLE DFUser ADD COLUMN latest_record TEXT DEFAULT ""')
exec_list.append(
    'ALTER TABLE DFUser ADD COLUMN latest_tdm_record TEXT DEFAULT ""'
)


class DFBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title="三角洲uid")

    @classmethod
    async def insert_user(cls, ev: Event, bot_id: str, data: UserData):
        return await cls.insert_data(
            user_id=ev.user_id,
            bot_id=bot_id,
            uid=data["openid"],
            group_id=data["group_id"],
        )


class DFUser(User, table=True):
    uid: str = Field(default="", title="三角洲uid")
    platform: str = Field(default="qq", title="平台")
    latest_record: str = Field(default="", title="最新烽火战绩id")
    latest_tdm_record: str = Field(default="", title="最新战场战绩id")

    @classmethod
    async def insert_user(cls, bot_id: str, data: UserData):
        return await cls.insert_data(
            user_id=data["qq_id"],
            bot_id=bot_id,
            uid=data["openid"],
            platform=data["platform"],
            cookie=data["access_token"],
            # latest_record="",
            # latest_tdm_record="",
        )

    @classmethod
    async def update_record(
        cls,
        bot_id: str,
        user_id: str,
        latest_record: str,
        latest_tdm_record: str,
    ):
        data = await cls.select_data(user_id)
        if data is None:
            raise ValueError(f"未找到用户 {user_id}")

        await cls.update_data(
            user_id=user_id,
            bot_id=bot_id,
            uid=data.uid,
            platform=data.platform,
            cookie=data.cookie,
            latest_record=latest_record,
            latest_tdm_record=latest_tdm_record,
        )


@site.register_admin
class VABindadmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="三角洲绑定管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = DFBind


@site.register_admin
class VAUseradmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="三角洲用户管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = DFUser
