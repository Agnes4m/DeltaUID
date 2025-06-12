import random


async def sign_in_RatGrinder():
    """
    每天签到
    """
    per = random.randint(1, 100)
    if per <= 50:
        return "签到成功，获得10000鼠鼠币"
    elif per <= 80:
        return "签到成功，获得20000鼠鼠币"
    elif per <= 95:
        return "签到成功，获得30000鼠鼠币"
    else:
        return "签到成功，获得50000鼠鼠币"


async def day_mission_RatGrinder():
    """
    每天0点刷新每日任务
    """
    ...


async def week_mission_RatGrinder():
    """每周0点刷新每周任务"""
    ...
    ...
