import sys
from typing import Literal

from gsuid_core.data_store import get_res_path

from ..Delta_user.msg_info import create_item_json

MAIN_PATH = get_res_path() / "DeltaUID"
sys.path.append(str(MAIN_PATH))
RESOURCE_PATH = MAIN_PATH / "res"
RESOURCE_PATH.mkdir(parents=True, exist_ok=True)
last_call_times = {}

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


async def check_use(bot, ev) -> Literal["用户仓库为空！", "ss全部资源下载完成!"]:
    a = await create_item_json(ev, bot, dl=True)
    # await download_all_file("DeltaUID", NEW_DICT)
    return a  # pyright: ignore[reportReturnType]
