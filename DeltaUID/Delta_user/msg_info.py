# import asyncio
import datetime

# from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger

from ..utils.api.api import DeltaApi
from ..utils.api.util import Util
from ..utils.database.models import DFUser

# import json

# from gsuid_core.utils.database.models import Subscribe

# from ..utils.models import SafehouseRecord

SAFEHOUSE_CHECK_INTERVAL = 600


class MsgInfo:
    async def __init__(self, user_id: str, bot_id: str):
        self.user_data = await DFUser.select_data(user_id, bot_id)

    async def get_msg_info(self):

        if self.user_data is None:

            return "未绑定三角洲账号，请先用\"鼠鼠登录\"命令登录"

        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_player_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
        )
        basic_info = await deltaapi.get_role_basic_info(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )
        sol_info = await deltaapi.get_person_center_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
            resource_type='sol',
        )
        tdm_info = await deltaapi.get_person_center_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
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
                    int(sol_info['data']['solDetail']['profitLossRatio'])
                    // 100
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
                totalVehicleKill = tdm_info['data']['mpDetail'][
                    'totalVehicleKill'
                ]

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
                return message_str

        except Exception as e:
            logger.exception(f"查询角色信息失败[{e}]")
            return "查询角色信息失败，可以需要重新登录\n详情请查看日志"
        return "查询角色信息失败，可以需要重新登录\n详情请查看日志"

    async def get_record(self, raw_text):
        if self.user_data is None:
            return "未绑定三角洲账号，请先用\"三角洲登录\"命令登录"

        # 解析参数，支持：
        # [模式] [页码] L[战绩条数上限]
        # 默认：模式=烽火(type_id=4)，页码=1，条数上限=50

        type_id = 4
        page = 1
        line_limit = 50

        if raw_text:
            tokens = raw_text.split()
            seen_page = False
            seen_mode = False
            seen_limit = False

            for token in tokens:
                # 处理条数上限 L<number>
                if token.startswith(('L', 'l')):
                    if seen_limit:
                        return "参数过多"

                    limit_str = token[1:]
                    if not limit_str.isdigit():
                        return "参数错误"

                    value = int(limit_str)
                    if value <= 0:
                        return "参数错误"
                    line_limit = value
                    seen_limit = True
                    continue

                # 处理模式
                if token in ["烽火", "烽火行动"]:
                    if seen_mode:
                        return "参数过多"
                    type_id = 4
                    seen_mode = True
                    continue
                if token in ["战场", "大战场", "全面战场"]:
                    if seen_mode:
                        return "参数过多"

                    type_id = 5
                    seen_mode = True
                    continue

                # 处理页码（正整数）
                try:
                    page_value = int(token)
                    if page_value <= 0:
                        return "参数错误"
                    if seen_page:
                        return "参数过多"
                    page = page_value
                    seen_page = True
                except ValueError:
                    # 非法的词元（既不是模式、也不是数字、也不是L上限）
                    return "请输入正确参数，格式：三角洲战绩 [模式] [页码] L[战绩条数上限]"

        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_player_info(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )
        if not res['status']:
            return "获取玩家信息失败，可能需要重新登录"
        user_name = res['data']['player']['charac_name']

        res = await deltaapi.get_record(
            self.user_data.cookie, self.user_data.uid, type_id, page
        )
        if not res['status']:
            return "获取战绩失败，可能需要重新登录"

        if type_id == 4:
            if not res['data']['gun']:
                return "本页没有战绩"

            index = 1
            msgs = f"{user_name}烽火战绩 第{page}页"

            for record in res['data']['gun']:
                # 捕获当前循环变量至局部，避免闭包引用问题
                cur_index = index
                index += 1

                if cur_index > line_limit:
                    break
                # 解析时间
                event_time = record.get('dtEventTime', '')
                # 解析地图
                map_id = record.get('MapId', '')
                map_name = Util.get_map_name(map_id)
                # 解析结果
                escape_fail_reason = record.get('EscapeFailReason', 0)
                result_str = (
                    "撤离成功" if escape_fail_reason == 1 else "撤离失败"
                )
                # 解析时长
                duration_seconds = record.get('DurationS', 0)
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                duration_str = f"{minutes}分{seconds}秒"
                # 解析击杀数
                kill_count = record.get('KillCount', 0)
                # 解析收益
                final_price = record.get('FinalPrice', '0')
                if final_price is None:
                    final_price = "未知"
                # 解析纯利润
                flow_cal_gained_price = record.get('flowCalGainedPrice', 0)
                flow_cal_gained_price_str = f"{'' if flow_cal_gained_price >= 0 else '-'}{Util.trans_num_easy_for_read(abs(flow_cal_gained_price))}"
                # 格式化收益
                try:
                    price_int = int(final_price)
                    price_str = Util.trans_num_easy_for_read(price_int)
                except Exception:
                    price_str = final_price

                # 解析干员
                ArmedForceId = record.get('ArmedForceId', '')
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                fallback_message = (
                    f"#{cur_index} {event_time}\n"
                    f"🗺️ 地图: {map_name} | 干员: {ArmedForce}\n"
                    f"📊 结果: {result_str} | 存活时长: {duration_str}\n"
                    f"💀 击杀干员: {kill_count}\n"
                    f"💰 带出: {price_str}\n"
                    f"💸 利润: {flow_cal_gained_price_str}"
                )

                # card_data = {
                #     'user_name': user_name,
                #     'time': event_time,
                #     'map_name': map_name,
                #     'armed_force': ArmedForce,
                #     'result': result_str,
                #     'duration': duration_str,
                #     'kill_count': kill_count,
                #     'price': price_str,
                #     'profit': flow_cal_gained_price_str,
                #     'title': f"#{cur_index}",
                # }

                msgs += '/n' + fallback_message
            return msgs

        elif type_id == 5:
            if not res['data']['operator']:
                return "本页没有战绩"

            index = 1
            msgs = f"{user_name}战场战绩 第{page}页"

            for record in res['data']['operator']:
                cur_index = index
                index += 1
                # 解析时间
                event_time = record.get('dtEventTime', '')
                # 解析地图
                map_id = record.get('MapID', '')
                map_name = Util.get_map_name(map_id)
                # 解析结果
                MatchResult = record.get('MatchResult', 0)
                if MatchResult == 1:
                    result_str = "胜利"
                elif MatchResult == 2:
                    result_str = "失败"
                elif MatchResult == 3:
                    result_str = "中途退出"
                else:
                    result_str = f"未知{MatchResult}"
                # 解析时长
                gametime = record.get('gametime', 0)
                minutes = gametime // 60
                seconds = gametime % 60
                duration_str = f"{minutes}分{seconds}秒"
                # 解析KDA
                KillNum = record.get('KillNum', 0)
                Death = record.get('Death', 0)
                Assist = record.get('Assist', 0)

                # 解析救援数
                RescueTeammateCount = record.get('RescueTeammateCount', 0)
                RoomId = record.get('RoomId', '')
                res = await deltaapi.get_tdm_detail(
                    self.user_data.cookie, self.user_data.uid, RoomId
                )
                if res['status'] and res['data']:
                    mpDetailList = res['data'].get('mpDetailList', [])
                    for mpDetail in mpDetailList:
                        if mpDetail.get('isCurrentUser', False):
                            rescueTeammateCount = mpDetail.get(
                                'rescueTeammateCount', 0
                            )
                            if rescueTeammateCount > 0:
                                RescueTeammateCount = rescueTeammateCount
                                break
                else:
                    logger.error(f"获取战绩详情失败: {res['message']}")

                # 解析总得分
                TotalScore = record.get('TotalScore', 0)
                avgScorePerMinute = (
                    int(TotalScore * 60 / gametime)
                    if gametime and gametime > 0
                    else 0
                )

                # 解析干员
                ArmedForceId = record.get('ArmedForceId', '')
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                fallback_message = (
                    f"#{cur_index} {event_time}\n"
                    f"🗺️ 地图: {map_name} | 干员: {ArmedForce}\n"
                    f"📊 结果: {result_str} | 时长: {duration_str}\n"
                    f"💀 K/D/A: {KillNum}/{Death}/{Assist} | 救援: {RescueTeammateCount}\n"
                    f"🥇 总得分: {TotalScore} | 分均得分: {avgScorePerMinute}"
                )

                # card_data = {
                #     'title': f"#{cur_index}",
                #     'time': event_time,
                #     'user_name': user_name,
                #     'map_name': map_name,
                #     'armed_force': ArmedForce,
                #     'result': result_str,
                #     'gametime': duration_str,
                #     'kill_count': KillNum,
                #     'death_count': Death,
                #     'assist_count': Assist,
                #     'rescue_count': RescueTeammateCount,
                #     'total_score': TotalScore,
                #     'avg_score_per_minute': avgScorePerMinute,
                # }

                msgs += '/n' + fallback_message
            return msgs

    async def get_tqc(self):

        if not self.user_data:
            return "未绑定三角洲账号，请先用\"三角洲登录\"命令登录"
        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_safehousedevice_status(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )

        if res['status']:
            place_data = res['data'].get('placeData', [])
            relate_map = res['data'].get('relateMap', {})
            devices = []

            for device in place_data:
                object_id = device.get('objectId', 0)
                left_time = device.get('leftTime', 0)
                push_time = device.get('pushTime', 0)
                place_name = device.get('placeName', '')

                if object_id > 0 and left_time > 0:
                    # 正在生产
                    object_name = relate_map.get(str(object_id), {}).get(
                        'objectName', f'物品{object_id}'
                    )
                    # 计算进度百分比
                    total_time = device.get('totalTime', 0)
                    progress = (
                        100 - (left_time / total_time * 100)
                        if total_time > 0
                        else 0
                    )

                    devices.append(
                        {
                            'place_name': place_name,
                            'status': 'producing',
                            'object_name': object_name,
                            'left_time': Util.seconds_to_duration(left_time),
                            'finish_time': datetime.datetime.fromtimestamp(
                                push_time
                            ).strftime('%m-%d %H:%M:%S'),
                            'progress': progress,
                        }
                    )
                else:
                    # 闲置状态
                    devices.append(
                        {'place_name': place_name, 'status': 'idle'}
                    )

            # if devices:

            # 文本模式
            message = None
            for device_data in devices:
                if device_data['status'] == 'producing':
                    text = f"{device_data['place_name']}：{device_data['object_name']}，剩余时间：{device_data['left_time']}，完成时间：{device_data['finish_time']}"
                else:
                    text = f"{device_data['place_name']}：闲置中"

                if not message:
                    message = text
                else:
                    message += f"\n{text}"

            if message:
                return message
            else:
                return "特勤处状态获取成功，但没有数据"
        else:
            return "获取特勤处状态失败：{res['message']}"

    # async def send_safehouse_message(
    #     self, qq_id: int, object_name: str, left_time: int
    # ):
    #     await asyncio.sleep(left_time)

    #     if self.user_data is None:
    #         return
    #     logger.info(f"特勤处生产完成提醒: {qq_id} - {object_name}")
    #     return f" {object_name}生产完成！"

    # async def get_tqc_push(self):

    #     if not self.user_data:
    #         return ""

    #     try:
    #         deltaapi = DeltaApi(self.user_data.platform)
    #         res = await deltaapi.get_safehousedevice_status(
    #             self.user_data.cookie, self.user_data.uid
    #         )

    #         if not res['status']:
    #             logger.error(f"获取特勤处状态失败: {res['message']}")
    #             return

    #         place_data = res['data'].get('placeData', [])
    #         relate_map = res['data'].get('relateMap', {})

    #         # 获取当前用户的特勤处记录
    #         path = get_res_path(
    #             [
    #                 'DeltaUID',
    #                 'tqc',
    #             ]
    #         )
    #         path.mkdir(parents=True, exist_ok=True)
    #         if not path.joinpath(f'{self.user_data.user_id}.json').is_file():
    #             with open(
    #                 path.joinpath(f'{self.user_data.user_id}.json'),
    #                 'w',
    #                 encoding='utf-8',
    #             ) as f:
    #                 json.dump({}, f)

    #         with open(
    #             path.joinpath(f'{self.user_data.user_id}.json'),
    #             'r',
    #             encoding='utf-8',
    #         ) as f:
    #             current_records = json.load(f)
    #         current_device_ids = {current_records.device_id}
    #         info = ""

    #         # 处理每个设备的状态
    #         for device in place_data:
    #             device_id = device.get('Id', '')
    #             left_time = device.get('leftTime', 0)
    #             object_id = device.get('objectId', 0)
    #             place_name = device.get('placeName', '')

    #             # 如果设备正在生产且有剩余时间
    #             if left_time > 0 and object_id > 0:
    #                 # 获取物品信息
    #                 object_info = relate_map.get(str(object_id), {})
    #                 object_name = object_info.get(
    #                     'objectName', f'物品{object_id}'
    #                 )

    #                 # 创建或更新记录
    #                 safehouse_record = SafehouseRecord(
    #                     qq_id=self.user_data.user_id,
    #                     device_id=device_id,
    #                     object_id=object_id,
    #                     object_name=object_name,
    #                     place_name=place_name,
    #                     left_time=left_time,
    #                     push_time=device.get('pushTime', 0),
    #                 )
    #                 info += (
    #                     f"{place_name} - {object_name} - 剩余{left_time}秒\n"
    #                 )

    #                 with open(
    #                     path.joinpath(f'{self.user_data.user_id}.json'),
    #                     'w',
    #                     encoding='utf-8',
    #                 ) as f:
    #                     safehouse_record.current_records
    #                     json.dump(safehouse_record, f)

    #                 current_device_ids.discard(device_id)

    #                 # 剩余时间小于检查间隔加60s，启动发送提醒任务
    #                 if left_time <= SAFEHOUSE_CHECK_INTERVAL + 60:
    #                     logger.info(
    #                         f"{left_time}秒后启动发送提醒任务: {self.user_data.user_id} - {device_id}"
    #                     )
    #                     # 启动发送提醒任务
    #                     msg = (
    #                         await self.send_safehouse_message(
    #                             int(self.user_data.user_id),
    #                             object_name,
    #                             left_time,
    #                         ),
    #                     )
    #                     # 删除记录
    #                     await user_data_database.delete_safehouse_record(
    #                         qq_id, device_id
    #                     )

    #         # 删除已完成的记录（设备不再生产）
    #         for device_id in current_device_ids:
    #             await user_data_database.delete_safehouse_record(
    #                 qq_id, device_id
    #             )

    #         await user_data_database.commit()
    #         if info != "":
    #             logger.info(f"{qq_id}特勤处状态: {info}")
    #         else:
    #             logger.info(f"{qq_id}特勤处状态: 闲置中")

    #     except Exception as e:
    #         logger.exception(f"监控特勤处状态失败: {e}")
    #     finally:
    #         await session.close()
    #     return msg
