import random
import asyncio
from typing import cast

from gsuid_core.sv import SV
from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.utils.image.image_tools import get_pic, get_event_avatar

from .image import draw_record_sol, draw_record_tdm, draw_df_info_img
from .utils import get_user_id, check_last_call, update_last_call
from .msg_info import MsgInfo, create_item_json
from ..utils.models import InfoData, WeeklyData, RecordSolData, RecordTdmData

# 用户调用记录：{user_id: last_call_timestamp}
last_call_times = {}


df_info = SV("三角洲信息")
df_tqc = SV("三角洲特勤处")
df_day = SV("三角洲日报/周报")
df_record = SV("三角洲战绩查询")
df_watch_record = SV("三角洲战绩订阅")
df_pa = SV("三角洲仓库")


@df_day.on_command(("日报"), block=True)
@df_info.on_command(("信息", "查询"), block=True)
async def login(bot: Bot, ev: Event):
    logger.info("[DF]正在执行三角洲信息功能")
    user_id = await get_user_id(ev)
    data = MsgInfo(user_id, bot.bot_id)
    msg = await data.get_msg_info()
    day = await data.get_daily()
    tqc = await data.get_tqc()

    if isinstance(msg, str):
        await bot.send(msg, at_sender=True)
        return
    if isinstance(day, str):
        await bot.send(day, at_sender=True)
        return
    if isinstance(tqc, str):
        await bot.send(tqc, at_sender=True)
        return
    logger.success("成功获取,正在生成图片")
    info = await draw_df_info_img(msg, day, tqc, ev)

    await bot.send(info, at_sender=True)


@df_day.on_command(("周报"), block=True)
@df_record.on_command(("战绩"), block=True)
async def get_record(bot: Bot, ev: Event):
    logger.info("[DF]执行战绩查询功能")
    await bot.send("正在检索战绩，请等待", at_sender=True)
    user_id = await get_user_id(ev)

    # 限流检查
    if not check_last_call(user_id):
        await bot.send("操作过于频繁，请一分钟后再试", at_sender=True)
        return

    data = MsgInfo(user_id, bot.bot_id)
    msg = await data.get_msg_info()
    week_data = await data.get_weekly()
    index, record = await data.get_record(ev.text.strip() if ev.text else "")

    if any(isinstance(x, str) for x in [msg, week_data, record]):
        await bot.send(next(x for x in [msg, week_data, record] if isinstance(x, str)), at_sender=True)
        return
    logger.info(record)
    if index == 1:
        record_sol = cast(list[RecordSolData], record)
        img = await draw_record_sol(
            await get_event_avatar(ev),
            record_sol,
            cast(WeeklyData, week_data),
            cast(InfoData, msg),
        )
    elif index == 2:
        record_tdm = cast(list[RecordTdmData], record)
        img = await draw_record_tdm(await get_event_avatar(ev), record_tdm, cast(InfoData, msg))
    else:
        img = None

    if img:
        await bot.send(img, at_sender=True)
    update_last_call(user_id)


@df_tqc.on_command(("特勤处", "tqc"), block=True)
async def get_tqc(
    bot: Bot,
    ev: Event,
):
    raw_text = ev.text.strip() if ev.text else ""
    if "订阅" in raw_text:
        logger.info("[DF]正在执行三角洲特勤处推送功能")
        data = MsgInfo(ev.user_id, bot.bot_id)
        await gs_subscribe.add_subscribe(
            "single",
            "ss特勤处订阅",
            ev,
            extra_message=ev.group_id,
        )
        data = await gs_subscribe.get_subscribe("ss订阅")
        await bot.send("订阅成功！")
    elif raw_text and "取消订阅" in raw_text:
        logger.info("[DF]正在执行关闭三角洲特勤处推送功能")
        await gs_subscribe.delete_subscribe(
            "single",
            "ss特勤处订阅",
            ev,
        )
        await bot.send("取消订阅成功！")

    else:
        logger.info("[DF]正在执行三角洲特勤处功能")
        data = MsgInfo(ev.user_id, bot.bot_id)
        a = await data.get_tqc_text()
        await bot.send(str(a), at_sender=True)


@df_watch_record.on_command(("订阅"), block=True)
async def watch_record(
    bot: Bot,  # Bot对象，用于与机器人交互
    ev: Event,  # 事件对象，包含事件相关信息
):
    logger.info("[DF]正在执行三角洲战绩订阅功能")  # 记录日志，表示正在执行三角洲战绩订阅功能

    user_id = ev.user_id  # 获取用户ID
    data = MsgInfo(user_id, bot.bot_id)  # 创建MsgInfo对象，用于处理消息相关信息
    await data.scheduler_record(ev, bot)  # 调度记录功能，传入事件和机器人对象

    msg = await data.scheduler_record(ev, bot)  # 再次调用调度记录功能，获取返回的消息
    if isinstance(msg, str):  # 检查返回的消息是否为字符串类型
        await bot.send(msg)
    # 测试输出
    # logger.info("测试输出")
    # uid = await DFBind.get_uid_by_game(user_id, bot.bot_id)
    # if msg and uid:
    #     logger.info("执行")
    #     record = await data.watch_record(msg["user_name"], uid, await get_pic(msg["avatar"]))
    #     await bot.send(str(record[0])) if record else None


@df_watch_record.on_command(("取消订阅"), block=True)
async def cancel_watch_record(
    bot: Bot,
    ev: Event,
):
    logger.info("[DF]正在执行取消订阅功能")
    await gs_subscribe.delete_subscribe(
        "single",
        "ss战绩订阅",
        ev,
    )
    await bot.send("取消订阅成功！")


@df_watch_record.on_command(("检查订阅", "清理订阅"), block=True)
async def check_subscriptions(
    bot: Bot,
    ev: Event,
):
    """检查并清理失效的订阅"""
    logger.info("[DF]正在执行检查订阅功能")

    # 解析参数
    raw_text = ev.text.strip() if ev.text else ""
    cleanup_mode = "清理" in raw_text or ev.command in ["清理订阅"]

    # 获取当前用户的所有订阅
    datas = await gs_subscribe.get_subscribe("ss战绩订阅")
    if not datas:
        await bot.send("您当前没有订阅记录。", at_sender=True)
        return

    # 筛选当前用户的订阅
    user_subscriptions = []
    for subscribe in datas:
        if subscribe.user_id == ev.user_id and subscribe.bot_id == bot.bot_id:
            user_subscriptions.append(subscribe)

    if not user_subscriptions:
        await bot.send("您当前没有订阅记录。", at_sender=True)
        return

    await bot.send(f"开始检查您的 {len(user_subscriptions)} 个订阅，每个订阅将进行三次验证...", at_sender=True)

    failed_subscriptions = []
    success_count = 0

    for i, subscribe in enumerate(user_subscriptions):
        uid = subscribe.extra_message
        if uid is None:
            logger.warning(f"[DF]订阅 {i + 1} 没有关联的UID，跳过检查")
            continue

        # 创建MsgInfo对象
        data = MsgInfo(subscribe.user_id, subscribe.bot_id)

        # 进行三次验证
        all_failed = True
        failure_reasons = []

        for attempt in range(3):
            try:
                msg = await data.get_msg_info()
                if isinstance(msg, str):
                    # 失败，记录原因
                    failure_reasons.append(msg)
                    logger.debug(f"[DF]订阅 {i + 1} 第{attempt + 1}次验证失败: {msg}")
                else:
                    # 成功
                    all_failed = False
                    logger.debug(f"[DF]订阅 {i + 1} 第{attempt + 1}次验证成功")
                    break
            except Exception as e:
                failure_reason = f"验证异常: {str(e)}"
                failure_reasons.append(failure_reason)
                logger.error(f"[DF]订阅 {i + 1} 第{attempt + 1}次验证异常: {e}")

            # 如果不是最后一次尝试，等待30秒
            if attempt < 2:
                await asyncio.sleep(30)

        if all_failed:
            failed_subscriptions.append({"subscribe": subscribe, "uid": uid, "reasons": failure_reasons})
            logger.info(f"[DF]订阅 {i + 1} 三次验证均失败，标记为失效")
        else:
            success_count += 1
            logger.debug(f"[DF]订阅 {i + 1} 验证成功")

    # 生成报告
    report = "检查完成！\n"
    report += f"总订阅数: {len(user_subscriptions)}\n"
    report += f"有效订阅: {success_count}\n"
    report += f"失效订阅: {len(failed_subscriptions)}\n"

    if failed_subscriptions:
        report += "\n失效订阅详情：\n"
        for i, failed in enumerate(failed_subscriptions):
            report += f"{i + 1}. UID: {failed['uid']}\n"
            report += f"   失败原因: {failed['reasons'][0] if failed['reasons'] else '未知原因'}\n"

    # 处理失效订阅
    cleaned_count = 0
    if cleanup_mode and failed_subscriptions:
        report += "\n正在清理失效订阅...\n"
        for failed in failed_subscriptions:
            try:
                # 尝试直接使用当前事件删除订阅
                # 注意：这里假设订阅名称是"ss战绩订阅"
                await gs_subscribe.delete_subscribe(
                    "single",
                    "ss战绩订阅",
                    ev,
                )
                cleaned_count += 1
                logger.info(f"[DF]成功清理失效订阅 UID: {failed['uid']}")
            except Exception as e:
                logger.error(f"[DF]清理订阅失败 UID: {failed['uid']}: {e}")
                report += f"清理失败 UID: {failed['uid']}: {str(e)}\n"

        report += f"已清理 {cleaned_count} 个失效订阅。"
    elif failed_subscriptions and not cleanup_mode:
        report += "\n提示：使用'检查订阅 清理'或'清理订阅'命令可以自动清理这些失效订阅。"

    await bot.send(report, at_sender=True)


@df_pa.on_command(("藏馆"), block=True)
async def get_depot(
    bot: Bot,
    ev: Event,
):
    logger.info("[DF]正在执行三角洲藏馆功能")
    data = MsgInfo(ev.user_id, bot.bot_id)
    a = await data.get_depot_red_info()
    await bot.send(message=a, at_sender=True) if a is not None else None


@scheduler.scheduled_job("cron", minute="*/2")
async def df_notify_rank():
    times = 0
    logger.debug("[DF]正在执行战绩推送功能")
    await asyncio.sleep(random.randint(0, 1))
    datas = await gs_subscribe.get_subscribe("ss战绩订阅")
    if not datas:
        return
    for subscribe in datas:
        logger.debug(f"[DF]正在为订阅用户 {subscribe.user_id} 推送战绩")
        uid = subscribe.extra_message
        if uid is None:
            logger.debug(f"[DF]用户 {subscribe.user_id} 未绑定三角洲账号，跳过")
            continue
        user_id = subscribe.user_id
        data = MsgInfo(user_id, subscribe.bot_id)

        msg = await data.get_msg_info()
        if isinstance(msg, str):
            logger.debug(f"[DF]{user_id}账号: {msg}")
            continue

        record_sol = await data.watch_record(msg["user_name"], uid, await get_pic(msg["avatar"]))
        if not record_sol:
            logger.debug(f"[DF]用户 {subscribe.user_id} 未找到新战绩，跳过")
            continue
        elif isinstance(record_sol, list):
            await subscribe.send(str(record_sol[0]))
            times += 1

        elif isinstance(record_sol, str | bytes):
            await subscribe.send(record_sol)
            times += 1
        else:
            logger.debug(f"[DF]用户 {subscribe.user_id} 未找到新战绩，跳过")
            continue
    if times > 0:
        logger.debug(f"[DF] 共为 {times} 个用户推送战绩")


@df_pa.on_command("价格", block=True)
async def handle_price_query(bot: Bot, event: Event) -> None:
    """处理价格查询命令
    参数:
        bot: Bot实例，用于发送消息
        event: 事件对象，包含命令和用户信息
    """
    logger.info(f"[DF] 用户 {event.user_id} 正在执行价格查询")
    data = MsgInfo(event.user_id, bot.bot_id)
    item_name = event.text.strip() if event.text else ""
    # 物品检索id
    a = await create_item_json(event, bot, dl=False)
    item_id: str | None = None
    if isinstance(a, list) and len(a) > 0:
        for item in a:
            if str(item.get("objectName", "")) == item_name:
                item_id = str(item.get("objectID", ""))
                # logger.info(f"[DF] 用户 {event.user_id} 输入物品名称 {item_id} 对应物品id {item_id}")
                break
    else:
        await bot.send(a, at_sender=True)
        return

    if item_id is None:
        await bot.send("请输入物品id", at_sender=True)
        return
    item_price_data = await data.get_item_price(item_id, item_name)
    if item_price_data:
        await bot.send(item_price_data, at_sender=True)
    else:
        await bot.send("未找到该物品", at_sender=True)
