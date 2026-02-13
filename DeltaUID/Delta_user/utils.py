import time

from gsuid_core.models import Event

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
