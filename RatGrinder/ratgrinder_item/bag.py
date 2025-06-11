from ..utils.database.models import SsBind


async def get_bag_info(qq_uid: str):
    """
    获取指定QQ UID的背包信息。

    参数:
    - qq_uid (str): 要获取背包信息的QQ UID。

    返回值:
    - None: 没有绑定。
    - dict: 包含背包信息的字典。
    """
    # 这里可以添加实际的数据库查询逻辑
    # 假设我们有一个函数 `fetch_bag_info_from_db` 来从数据库获取数据
    data_info = await SsBind.data_get(qq_uid)

    if not data_info:
        return None

    bag_info = data_info.player['bag']
    return await bag_into_msg(bag_info)


async def bag_into_msg(bag_info: list):
    """
    将背包信息转换为消息格式。

    参数:
    - bag_info (list): 背包信息列表，每个元素为 (item, count) 元组或字典。

    返回值:
    - str: 格式化的背包信息字符串。
    """
    if not bag_info:
        return "背包为空"

    msg = "背包内容:\n"
    for entry in bag_info:
        if isinstance(entry, dict):
            item = entry.get('name')
            count = entry.get('count')
        else:
            item, count = entry
        msg += f"{item}: {count}\n"

    return msg.strip()
