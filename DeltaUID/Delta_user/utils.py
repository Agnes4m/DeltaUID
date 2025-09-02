from gsuid_core.models import Event


async def get_user_id(ev: Event) -> str:
    if ev.at:
        return ev.at
    return ev.user_id
