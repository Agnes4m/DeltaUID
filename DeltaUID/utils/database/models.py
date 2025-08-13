from typing import Optional

from sqlmodel import Field
from gsuid_core.webconsole import site
from gsuid_core.webconsole.mount_app import GsAdminModel
from fastapi_amis_admin.amis.components import PageSchema
from gsuid_core.utils.database.base_models import Bind, User


class DFBind(Bind, table=True):
    openid: Optional[str] = Field(default=None, title='三角洲uid')


class DFUser(User, table=True):
    openid: Optional[str] = Field(default=None, title='三角洲uid')


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
