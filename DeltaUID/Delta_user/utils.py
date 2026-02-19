import sys
import json
import time
from typing import cast

from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path

from ..utils.models import ItemIdData

MAIN_PATH = get_res_path() / "DeltaUID"
sys.path.append(str(MAIN_PATH))
RESOURCE_PATH = MAIN_PATH / "res"
RESOURCE_PATH.mkdir(parents=True, exist_ok=True)
last_call_times = {}


async def get_user_id(ev: Event) -> str:
    if ev.at:
        return ev.at
    return ev.user_id


def check_last_call(user_id: str, limit: int = 60) -> bool:
    now = time.time()
    if user_id in last_call_times and now - last_call_times[user_id] < limit:
        return False
    return True


def update_last_call(user_id: str):
    last_call_times[user_id] = time.time()


def read_item_json():
    with open(RESOURCE_PATH.parent / "item.json", mode="r", encoding="utf-8") as f:
        data = json.load(f)
    return cast(list[ItemIdData], data)
