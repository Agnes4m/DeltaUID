import json
from typing import Dict
from pathlib import Path

import aiofiles

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.help.model import PluginHelp
from gsuid_core.help.draw_new_plugin_help import get_new_help

from ..version import DeltaUID_version
from ..utils.const import ICON_PATH, PLUGIN_NAME
from ..utils.image import get_footer
from ..utils.resource_manager import resource_manager

HELP_DATA = Path(__file__).parent / "help.json"
ICON_PATH_MODULE = Path(__file__).parent / "icon_path"

PREFIX = get_plugin_available_prefix(PLUGIN_NAME)


async def get_help_data() -> Dict[str, PluginHelp]:
    async with aiofiles.open(HELP_DATA, "rb") as file:
        return json.loads(await file.read())


async def get_help():
    return await get_new_help(
        plugin_name=PLUGIN_NAME,
        plugin_info={f"v{DeltaUID_version}": ""},
        plugin_icon=resource_manager.load_image(ICON_PATH),
        plugin_help=await get_help_data(),
        plugin_prefix=PREFIX,
        help_mode="dark",
        banner_bg=resource_manager.get_texture("banner_bg.jpg"),
        banner_sub_text="鼠鼠我啊，要百万撤离了！",
        help_bg=resource_manager.get_texture("bg.jpg"),
        cag_bg=resource_manager.get_texture("cag_bg.png"),
        item_bg=resource_manager.get_texture("item.png"),
        icon_path=ICON_PATH_MODULE,
        footer=get_footer(),
        enable_cache=True,
    )
