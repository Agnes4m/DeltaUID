from typing import Optional

from fastapi_amis_admin.amis.components import PageSchema
from sqlmodel import Field

from gsuid_core.bot import Bot, Event
from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.webconsole import site
from gsuid_core.webconsole.mount_app import GsAdminModel

from ..models import UserData


class DFBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='三角洲uid')

    @classmethod
    async def insert_user(cls, ev: Event, bot: Bot, data: UserData):
        return await cls.insert_data(
            user_id=ev.user_id,
            bot_id=bot.bot_id,
            uid=data['openid'],
            group_id=data['group_id'],
        )


class DFUser(User, table=True):
    uid: str = Field(default="", title='三角洲uid')
    platform: str = Field(default="qq", title='平台')

    @classmethod
    async def insert_user(cls, bot: Bot, data: UserData):
        return await cls.insert_data(
            user_id=data['qq_id'],
            bot_id=bot.bot_id,
            uid=data['openid'],
            platform=data['platform'],
            cookie=data['access_token'],
        )


@site.register_admin
class VABindadmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='三角洲绑定管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = DFBind


@site.register_admin
class VAUseradmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='三角洲用户管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = DFUser
