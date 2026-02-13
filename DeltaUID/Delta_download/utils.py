import sys
import json

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.download_resource.download_file import download

from ..Delta_user.utils import get_user_id
from ..Delta_user.msg_info import MsgInfo

MAIN_PATH = get_res_path() / "DeltaUID"
sys.path.append(str(MAIN_PATH))
RESOURCE_PATH = MAIN_PATH / "res"
RESOURCE_PATH.mkdir(parents=True, exist_ok=True)

# with open(Path(__file__).parent / "item.json", mode="r", encoding="utf-8") as fp:
#     ITEM_DICT: Dict[str, Dict[str, List[str]]] = json.load(fp)
# # 去除空值
# ITEM_DICT = {k: v for k, v in ITEM_DICT.items() if v}

# NEW_DICT = {
#     f"res/{map_name}/{section}": RESOURCE_PATH / f"{map_name}/{section}"
#     for map_name, sections in ITEM_DICT.items()
#     for section, points in sections.items()
#     if points  # 如果 points 非空（即它包含至少一个元素）
# }


async def check_use(bot, ev):
    user_id = await get_user_id(ev)
    data = MsgInfo(user_id, bot.bot_id)
    depot = await data.get_depot_text()
    if depot is None:
        return "用户仓库为空！"
    with open(RESOURCE_PATH.parent / "item.json", mode="w", encoding="utf-8") as f:
        json.dump(depot, f, ensure_ascii=False, indent=4)
    for one in depot:
        await download(one["pic"], RESOURCE_PATH, name=f"{one['objectID']}.png", tag="[DF]")
    # await download_all_file("DeltaUID", NEW_DICT)
    return "ss全部资源下载完成!"
