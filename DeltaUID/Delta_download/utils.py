from ..Delta_user.utils import get_user_id, create_item_json
from ..Delta_user.msg_info import MsgInfo

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
    a = await create_item_json(depot)
    # await download_all_file("DeltaUID", NEW_DICT)
    return a
