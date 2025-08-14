from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.api import DeltaApi
from ..utils.api.util import Util
from ..utils.database.models import DFUser

# from gsuid_core.utils.database.api import get_uid


df_login = SV("三角洲信息")


@df_login.on_command(("信息"), block=True)
async def login(bot: Bot, ev: Event):

    user_data = await DFUser.select_data(ev.user_id, bot.bot_id)

    if user_data is None:
        await bot.send(
            "未绑定三角洲账号，请先用\"鼠鼠登录\"命令登录",
            at_sender=True,
        )
        return
    deltaapi = DeltaApi(user_data.platform)
    res = await deltaapi.get_player_info(
        access_token=user_data.cookie,
        openid=user_data.uid,
    )
    basic_info = await deltaapi.get_role_basic_info(
        access_token=user_data.cookie, openid=user_data.uid
    )
    sol_info = await deltaapi.get_person_center_info(
        access_token=user_data.cookie,
        openid=user_data.uid,
        resource_type='sol',
    )
    tdm_info = await deltaapi.get_person_center_info(
        access_token=user_data.cookie,
        openid=user_data.uid,
        resource_type='mp',
    )
    if basic_info['status']:
        propcapital = Util.trans_num_easy_for_read(
            basic_info['data']['propcapital']
        )
    else:
        propcapital = 0
    try:
        if res['status'] and sol_info['status'] and tdm_info['status']:
            user_name = res['data']['player']['charac_name']
            money = Util.trans_num_easy_for_read(res['data']['money'])
            rankpoint = res['data']['game']['rankpoint']
            soltotalfght = res['data']['game']['soltotalfght']
            solttotalescape = res['data']['game']['solttotalescape']
            soltotalkill = res['data']['game']['soltotalkill']
            solescaperatio = res['data']['game']['solescaperatio']
            profitLossRatio = Util.trans_num_easy_for_read(
                int(sol_info['data']['solDetail']['profitLossRatio']) // 100
            )
            highKillDeathRatio = f"{int(sol_info['data']['solDetail']['highKillDeathRatio'])/100:.2f}"
            medKillDeathRatio = f"{int(sol_info['data']['solDetail']['medKillDeathRatio'])/100:.2f}"
            lowKillDeathRatio = f"{int(sol_info['data']['solDetail']['lowKillDeathRatio'])/100:.2f}"
            totalGainedPrice = Util.trans_num_easy_for_read(
                sol_info['data']['solDetail']['totalGainedPrice']
            )
            totalGameTime = Util.seconds_to_duration(
                sol_info['data']['solDetail']['totalGameTime']
            )

            tdmrankpoint = res['data']['game']['tdmrankpoint']
            avgkillperminute = (
                f"{int(res['data']['game']['avgkillperminute'])/100:.2f}"
            )
            tdmtotalfight = res['data']['game']['tdmtotalfight']
            totalwin = res['data']['game']['totalwin']
            tdmtotalkill = int(
                int(res['data']['game']['tdmduration'])
                * int(res['data']['game']['avgkillperminute'])
                / 100
            )
            tdmduration = Util.seconds_to_duration(
                int(res['data']['game']['tdmduration']) * 60
            )
            tdmsuccessratio = res['data']['game']['tdmsuccessratio']
            avgScorePerMinute = f"{int(tdm_info['data']['mpDetail']['avgScorePerMinute'])/100:.2f}"
            totalVehicleDestroyed = tdm_info['data']['mpDetail'][
                'totalVehicleDestroyed'
            ]
            totalVehicleKill = tdm_info['data']['mpDetail']['totalVehicleKill']

            # try:
            #     player_data = {
            #         'user_name': user_name,
            #         'money': money,
            #         'propcapital': propcapital,
            #         'rankpoint': rankpoint,
            #         'soltotalfght': soltotalfght,
            #         'solttotalescape': solttotalescape,
            #         'soltotalkill': soltotalkill,
            #         'solescaperatio': solescaperatio,
            #         'profitLossRatio': profitLossRatio,
            #         'highKillDeathRatio': highKillDeathRatio,
            #         'medKillDeathRatio': medKillDeathRatio,
            #         'lowKillDeathRatio': lowKillDeathRatio,
            #         'totalGainedPrice': totalGainedPrice,
            #         'totalGameTime': totalGameTime,
            #         'tdmrankpoint': tdmrankpoint,
            #         'avgkillperminute': avgkillperminute,
            #         'tdmtotalfight': tdmtotalfight,
            #         'totalwin': totalwin,
            #         'tdmtotalkill': tdmtotalkill,
            #         'tdmduration': tdmduration,
            #         'tdmsuccessratio': tdmsuccessratio,
            #         'avgScorePerMinute': avgScorePerMinute,
            #         'totalVehicleDestroyed': totalVehicleDestroyed,
            #         'totalVehicleKill': totalVehicleKill,
            #     }
            #     img_data = await renderer.render_player_info(player_data)
            #     await Image(image=img_data).finish(reply=True)
            # except FinishedException:
            #     raise
            # except Exception as e:
            #     logger.error(f"渲染玩家信息卡片失败: {e}")
            #     # 降级到文本模式

            message_str = f"""【{user_name}的个人信息】
--- 账户信息 ---
现金：{money}
仓库流动资产：{propcapital}

--- 烽火数据 ---
总场数：{soltotalfght} | 总撤离数：{solttotalescape} | 撤离率：{solescaperatio}
总击杀：{soltotalkill} | 排位分：{rankpoint} | 总游戏时长：{totalGameTime}
赚损比{profitLossRatio} | 总带出：{totalGainedPrice}
kd(常规 | 机密 | 绝密)：{highKillDeathRatio} | {medKillDeathRatio} | {lowKillDeathRatio}

--- 战场数据 ---
总场数：{tdmtotalfight} | 总胜场：{totalwin} | 胜率：{tdmsuccessratio}
总击杀：{tdmtotalkill} | 排位分：{tdmrankpoint} | 总游戏时长：{tdmduration}
分均击杀：{avgkillperminute} | 分均得分：{avgScorePerMinute}
总摧毁载具：{totalVehicleDestroyed} | 总载具击杀：{totalVehicleKill}
"""
            await bot.send(message_str)

    except Exception as e:
        logger.exception(f"查询角色信息失败[{e}]")
        await bot.send(
            "查询角色信息失败，可以需要重新登录\n详情请查看日志",
            at_sender=True,
        )
        return
