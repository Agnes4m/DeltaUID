import datetime
import json
import urllib.parse
from typing import Any, cast

from gsuid_core.logger import logger

from ..utils.api.api import DeltaApi
from ..utils.api.util import Util
from ..utils.database.models import DFUser
from ..utils.models import (
    DayInfoData,
    DayListData,
    InfoData,
    RecordSolData,
    RecordTdmData,
    WeeklyData,
)

SAFEHOUSE_CHECK_INTERVAL = 600


class MsgInfo:
    def __init__(self, user_id: str, bot_id: str):
        self.user_id = user_id
        self.bot_id = bot_id
        self.user_data = None

    async def _fetch_user_data(self):
        self.user_data = await DFUser.select_data(self.user_id, self.bot_id)
        return self.user_data

    async def get_msg_info(self):
        self.user_data = await self._fetch_user_data()

        if self.user_data is None:
            return '未绑定三角洲账号，请先用"鼠鼠登录"命令登录'

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
            resource_type="sol",
        )
        try:
            if sol_info["data"].get("rat") == 101:
                return "登录信息已过期，请重新登录"
            if not sol_info["data"]:
                return "服务器忙碌,请稍后重试"
        except Exception as _:
            ...

        tdm_info = await deltaapi.get_person_center_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
            resource_type="mp",
        )

        if basic_info["status"]:
            propcapital = Util.trans_num_easy_for_read(
                basic_info["data"]["propcapital"]
            )
        else:
            propcapital = "0"

        if res["status"] and sol_info["status"] and tdm_info["status"]:
            user_name: str = res["data"]["player"]["charac_name"]
            money = Util.trans_num_easy_for_read(res["data"]["money"])
            rankpoint: str = res["data"]["game"]["rankpoint"]
            soltotalfght = res["data"]["game"]["soltotalfght"]
            solttotalescape = res["data"]["game"]["solttotalescape"]
            soltotalkill = res["data"]["game"]["soltotalkill"]
            solescaperatio = res["data"]["game"]["solescaperatio"]
            if sol_info["data"]:
                profitLossRatio = Util.trans_num_easy_for_read(
                    int(sol_info["data"]["solDetail"]["profitLossRatio"])
                    // 100
                )
                highKillDeathRatio = f"{int(sol_info['data']['solDetail']['highKillDeathRatio']) / 100:.2f}"
                medKillDeathRatio = f"{int(sol_info['data']['solDetail']['medKillDeathRatio']) / 100:.2f}"
                lowKillDeathRatio = f"{int(sol_info['data']['solDetail']['lowKillDeathRatio']) / 100:.2f}"
                totalGainedPrice = Util.trans_num_easy_for_read(
                    sol_info["data"]["solDetail"]["totalGainedPrice"]
                )
                totalGameTime = Util.seconds_to_duration(
                    sol_info["data"]["solDetail"]["totalGameTime"]
                )
            else:
                profitLossRatio = "未知"
                highKillDeathRatio = "未知"
                medKillDeathRatio = "未知"
                lowKillDeathRatio = "未知"
                totalGainedPrice = "未知"
                totalGameTime = "未知"

            avatar_url = res["data"]["player"]["picurl"]
            avatar = Util.avatar_trans(avatar_url)

            tdmrankpoint = res["data"]["game"]["tdmrankpoint"]
            avgkillperminute = (
                f"{int(res['data']['game']['avgkillperminute']) / 100:.2f}"
            )
            tdmtotalfight = res["data"]["game"]["tdmtotalfight"]
            totalwin = res["data"]["game"]["totalwin"]
            tdmtotalkill = int(
                int(res["data"]["game"]["tdmduration"])
                * int(res["data"]["game"]["avgkillperminute"])
                / 100
            )
            tdmduration = Util.seconds_to_duration(
                int(res["data"]["game"]["tdmduration"]) * 60
            )
            tdmsuccessratio = res["data"]["game"]["tdmsuccessratio"]

            try:
                avgScorePerMinute = f"{int(tdm_info['data']['mpDetail']['avgScorePerMinute']) / 100:.2f}"
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取avgScorePerMinute: {e}")
                avgScorePerMinute = "未知"

            try:
                totalVehicleDestroyed = tdm_info["data"]["mpDetail"][
                    "totalVehicleDestroyed"
                ]
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取totalVehicleDestroyed: {e}")
                totalVehicleDestroyed = "未知"
            try:
                totalVehicleKill = tdm_info["data"]["mpDetail"][
                    "totalVehicleKill"
                ]
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取totalVehicleKill: {e}")
                totalVehicleKill = "未知"

            # try:
            player_data = cast(
                InfoData,
                {
                    "user_name": user_name,
                    "avatar": avatar,
                    "money": money,
                    "propcapital": propcapital,
                    "rankpoint": rankpoint,
                    "soltotalfght": soltotalfght,
                    "solttotalescape": solttotalescape,
                    "soltotalkill": soltotalkill,
                    "solescaperatio": solescaperatio,
                    "profitLossRatio": profitLossRatio,
                    "highKillDeathRatio": highKillDeathRatio,
                    "medKillDeathRatio": medKillDeathRatio,
                    "lowKillDeathRatio": lowKillDeathRatio,
                    "totalGainedPrice": totalGainedPrice,
                    "totalGameTime": totalGameTime,
                    "tdmrankpoint": tdmrankpoint,
                    "avgkillperminute": avgkillperminute,
                    "tdmtotalfight": tdmtotalfight,
                    "totalwin": totalwin,
                    "tdmtotalkill": str(tdmtotalkill),
                    "tdmduration": tdmduration,
                    "tdmsuccessratio": tdmsuccessratio,
                    "avgScorePerMinute": avgScorePerMinute,
                    "totalVehicleDestroyed": totalVehicleDestroyed,
                    "totalVehicleKill": totalVehicleKill,
                },
            )
            return player_data
        return '未绑定三角洲账号，请先用"鼠鼠登录"命令登录'

    async def get_record(self, raw_text: str):
        self.user_data = await self._fetch_user_data()
        if self.user_data is None:
            return 0, '未绑定三角洲账号，请先用"三角洲登录"命令登录'

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
                if token.startswith(("L", "l")):
                    if seen_limit:
                        return 0, "参数过多"

                    limit_str = token[1:]
                    if not limit_str.isdigit():
                        return 0, "参数错误"

                    value = int(limit_str)
                    if value <= 0:
                        return 0, "参数错误"
                    line_limit = value
                    seen_limit = True
                    continue

                # 处理模式
                if token in ["烽火", "烽火行动"]:
                    if seen_mode:
                        return 0, "参数过多"
                    type_id = 4
                    seen_mode = True
                    continue
                if token in ["战场", "大战场", "全面战场"]:
                    if seen_mode:
                        return 0, "参数过多"

                    type_id = 5
                    seen_mode = True
                    continue

                # 处理页码（正整数）
                try:
                    page_value = int(token)
                    if page_value <= 0:
                        return 0, "参数错误"
                    if seen_page:
                        return 0, "参数过多"
                    page = page_value
                    seen_page = True
                except ValueError:
                    # 非法的词元（既不是模式、也不是数字、也不是L上限）
                    return (
                        0,
                        "请输入正确参数，格式：三角洲战绩 [模式] [页码] L[战绩条数上限]",
                    )
        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_player_info(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )
        if not res["status"] or not res["data"].get("player"):
            return 0, "获取玩家信息失败，可能需要重新登录"
        user_name: Any = res["data"]["player"]["charac_name"]
        res = await deltaapi.get_record(
            self.user_data.cookie, self.user_data.uid, type_id, page
        )
        # print(res)
        if not res["status"]:
            return 0, res["message"]
        card_list: list[RecordTdmData | RecordSolData] = []

        if type_id == 4:
            if not res["data"]["gun"]:
                return 0, "最近7天没有战绩"

            index = 1
            # msgs = f"{user_name}烽火战绩 第{page}页"

            for record in res["data"]["gun"]:
                # 捕获当前循环变量至局部，避免闭包引用问题
                if not record:
                    continue
                cur_index = index
                index += 1

                if cur_index > line_limit:
                    break
                # 解析时间
                event_time = record.get("dtEventTime", "")
                # 解析地图
                map_id = record.get("MapId", "")
                map_name = Util.get_map_name(map_id)
                # 解析结果
                escape_fail_reason = record.get("EscapeFailReason", 0)
                result_str = (
                    "撤离成功" if escape_fail_reason == 1 else "撤离失败"
                )
                # 解析时长
                duration_seconds = record.get("DurationS", 0)
                if not duration_seconds:
                    duration_seconds = 0
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                duration_str = f"{minutes}分{seconds}秒"
                # 解析击杀数
                kill_count = record.get("KillCount", 0)
                # 解析收益
                final_price = record.get("FinalPrice", "0")
                if final_price is None:
                    final_price = "未知"
                # 解析纯利润
                flow_cal_gained_price = record.get("flowCalGainedPrice", 0)
                flow_cal_gained_price_str = f"{'' if flow_cal_gained_price >= 0 else '-'}{Util.trans_num_easy_for_read(abs(flow_cal_gained_price))}"
                # 格式化收益
                try:
                    price_int = int(final_price)
                    price_str = Util.trans_num_easy_for_read(price_int)
                except Exception:
                    price_str = final_price

                # 解析干员
                ArmedForceId = record.get("ArmedForceId", "")
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                # fallback_message = (
                #     f"#{cur_index} {event_time}\n"
                #     f"🗺️ 地图: {map_name} | 干员: {ArmedForce}\n"
                #     f"📊 结果: {result_str} | 存活时长: {duration_str}\n"
                #     f"💀 击杀干员: {kill_count}\n"
                #     f"💰 带出: {price_str}\n"
                #     f"💸 利润: {flow_cal_gained_price_str}"
                # )

                card_data_sol: RecordSolData = {
                    "user_name": user_name,
                    "time": event_time,
                    "map_name": map_name,
                    "armed_force": ArmedForce,
                    "result": result_str,
                    "duration": duration_str,
                    "kill_count": kill_count,
                    "price": price_str,
                    "profit": flow_cal_gained_price_str,
                    "title": f"#{cur_index}",
                }
                card_list.append(card_data_sol)

                # msgs += "/n" + fallback_message
            return 1, card_list
        elif type_id == 5:
            if not res["data"]["operator"]:
                return 0, "最近7天没有战绩"

            index = 1
            # msgs = f"{user_name}战场战绩 第{page}页"

            for record in res["data"]["operator"]:
                cur_index = index
                index += 1
                # 解析时间
                event_time = record.get("dtEventTime", "")
                # 解析地图
                map_id = record.get("MapID", "")
                map_name = Util.get_map_name(map_id)
                # 解析结果
                MatchResult = record.get("MatchResult", 0)
                if MatchResult == 1:
                    result_str = "胜利"
                elif MatchResult == 2:
                    result_str = "失败"
                elif MatchResult == 3:
                    result_str = "中途退出"
                else:
                    result_str = f"未知{MatchResult}"
                # 解析时长
                gametime = record.get("gametime", 0)
                minutes = gametime // 60
                seconds = gametime % 60
                duration_str = f"{minutes}分{seconds}秒"
                # 解析KDA
                KillNum = record.get("KillNum", 0)
                Death = record.get("Death", 0)
                Assist = record.get("Assist", 0)

                # 解析救援数
                RescueTeammateCount = record.get("RescueTeammateCount", 0)
                RoomId = record.get("RoomId", "")
                res = await deltaapi.get_tdm_detail(
                    self.user_data.cookie, self.user_data.uid, RoomId
                )
                if res["status"] and res["data"]:
                    mpDetailList = res["data"].get("mpDetailList", [])
                    for mpDetail in mpDetailList:
                        if mpDetail.get("isCurrentUser", False):
                            rescueTeammateCount = mpDetail.get(
                                "rescueTeammateCount", 0
                            )
                            if rescueTeammateCount > 0:
                                RescueTeammateCount = rescueTeammateCount
                                break
                else:
                    logger.error(f"获取战绩详情失败: {res['message']}")

                # 解析总得分
                TotalScore = record.get("TotalScore", 0)
                avgScorePerMinute = (
                    int(TotalScore * 60 / gametime)
                    if gametime and gametime > 0
                    else 0
                )

                # 解析干员
                ArmedForceId = record.get("ArmedForceId", "")
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                # fallback_message = (
                #     f"#{cur_index} {event_time}\n"
                #     f"🗺️ 地图: {map_name} | 干员: {ArmedForce}\n"
                #     f"📊 结果: {result_str} | 时长: {duration_str}\n"
                #     f"💀 K/D/A: {KillNum}/{Death}/{Assist} | 救援: {RescueTeammateCount}\n"
                #     f"🥇 总得分: {TotalScore} | 分均得分: {avgScorePerMinute}"
                # )

                card_data: RecordTdmData = {
                    "title": f"#{cur_index}",
                    "time": event_time,
                    "user_name": user_name,
                    "map_name": map_name,
                    "armed_force": ArmedForce,
                    "result": result_str,
                    "gametime": duration_str,
                    "kill_count": KillNum,
                    "death_count": Death,
                    "assist_count": Assist,
                    "rescue_count": RescueTeammateCount,
                    "total_score": TotalScore,
                    "avg_score_per_minute": avgScorePerMinute,
                }
                card_list.append(card_data)
                # msgs += "/n" + fallback_message
            return 2, card_list
        return 0, "请求超时，请稍后重试"

    async def get_tqc(self):
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"三角洲登录"命令登录'
        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_safehousedevice_status(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )

        if res["status"]:
            place_data = res["data"].get("placeData", [])
            relate_map = res["data"].get("relateMap", {})
            devices = []

            for device in place_data:
                object_id = device.get("objectId", 0)
                left_time = device.get("leftTime", 0)
                push_time = device.get("pushTime", 0)
                place_name = device.get("placeName", "")

                if object_id > 0 and left_time > 0:
                    # 正在生产
                    object_name = relate_map.get(str(object_id), {}).get(
                        "objectName", f"物品{object_id}"
                    )
                    # 计算进度百分比
                    total_time = device.get("totalTime", 0)
                    progress = (
                        100 - (left_time / total_time * 100)
                        if total_time > 0
                        else 0
                    )

                    devices.append(
                        {
                            "place_name": place_name,
                            "status": "producing",
                            "object_name": object_name,
                            "left_time": Util.seconds_to_duration(left_time),
                            "finish_time": datetime.datetime.fromtimestamp(
                                push_time
                            ).strftime("%m-%d %H:%M:%S"),
                            "progress": progress,
                        }
                    )
                else:
                    # 闲置状态
                    devices.append(
                        {"place_name": place_name, "status": "idle"}
                    )

            if devices:
                return devices

            # 文本模式
            message = None
            for device_data in devices:
                if device_data["status"] == "producing":
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
            return f"获取特勤处状态失败：{res['message']}"

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

    async def get_daily(self) -> DayInfoData | str:
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"三角洲登录"命令登录'

        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_daily_report(
            self.user_data.cookie, self.user_data.uid
        )
        if res["status"]:
            solDetail = res["data"].get("solDetail", None)
            if solDetail:
                recentGainDate = solDetail.get("recentGainDate", "未知")
                recentGain = solDetail.get("recentGain", 0)
                gain_str = f"{'-' if recentGain < 0 else ''}{Util.trans_num_easy_for_read(abs(recentGain))}"
                userCollectionTop = solDetail.get("userCollectionTop", None)
                if userCollectionTop:
                    userCollectionList = userCollectionTop.get("list", None)
                    if userCollectionList:
                        userCollectionListStr = ""
                        collection_details = []

                        for item in userCollectionList:
                            objectID = item.get("objectID", 0)
                            res = await deltaapi.get_object_info(
                                access_token=self.user_data.cookie,
                                openid=self.user_data.uid,
                                object_id=objectID,
                            )
                            if res["status"]:
                                obj_list = res["data"].get("list", [])
                                if obj_list:
                                    obj_name = obj_list[0].get(
                                        "objectName", "未知藏品"
                                    )
                                    pic = obj_list[0].get("pic", "")
                                    avgPrice = obj_list[0].get("avgPrice", 0)
                                    collection_details.append(
                                        {
                                            "objectID": objectID,
                                            "objectName": obj_name,
                                            "pic": pic,
                                            "avgPrice": f"{'-' if recentGain < 0 else ''}{Util.trans_num_easy_for_read(abs(avgPrice))}",
                                        }
                                    )
                                    if userCollectionListStr == "":
                                        userCollectionListStr = obj_name
                                    else:
                                        userCollectionListStr += (
                                            f"、{obj_name}"
                                        )
                            else:
                                collection_details.append(
                                    {
                                        "objectID": objectID,
                                        "error": res["message"],
                                    }
                                )
                                userCollectionListStr += (
                                    f"未知藏品：{objectID}"
                                )
                        userCollectionData: DayListData = {
                            "list_str": userCollectionListStr,
                            "details": collection_details,
                        }
                    else:
                        userCollectionData = {
                            "list_str": "未知",
                            "details": [],
                        }
                else:
                    userCollectionData = {"list_str": "未知", "details": []}
                # 返回原始数据字典
                return {
                    "daily_report_date": recentGainDate,
                    "profit": recentGain,
                    "profit_str": gain_str,
                    "top_collections": userCollectionData,
                }
            else:
                return "获取三角洲日报失败，没有数据"
        else:
            return f"获取三角洲日报失败：{res['message']}"

    async def get_weekly(self):
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"三角洲登录"命令登录'
        access_token = self.user_data.cookie
        openid = self.user_data.uid
        platform = self.user_data.platform

        deltaapi = DeltaApi(platform)
        res = await deltaapi.get_player_info(
            access_token=access_token, openid=openid
        )

        if not (res["status"] and "charac_name" in res["data"]["player"]):
            return "获取角色信息失败，可能需要重新登录"

        user_name = res["data"]["player"]["charac_name"]
        for i in range(1, 3):
            statDate, statDate_str = Util.get_Sunday_date(i)
            res = await deltaapi.get_weekly_report(
                access_token=access_token, openid=openid, statDate=statDate
            )
            logger.info(res)
            if res["status"] and res["data"]:
                # 解析总带出
                Gained_Price = int(res["data"].get("Gained_Price", 0))
                Gained_Price_Str = Util.trans_num_easy_for_read(Gained_Price)

                # 解析总带入
                consume_Price = int(res["data"].get("consume_Price", 0))
                consume_Price_Str = Util.trans_num_easy_for_read(consume_Price)

                # 解析总利润
                profit = Gained_Price - consume_Price
                # profit_str = f"{'-' if profit < 0 else ''}{Util.trans_num_easy_for_read(abs(profit))}"

                # 解析使用干员信息
                total_ArmedForceId_num = res["data"].get(
                    "total_ArmedForceId_num", ""
                )
                total_ArmedForceId_num = total_ArmedForceId_num.replace(
                    "'", '"'
                )
                total_ArmedForceId_num_list = list(
                    map(json.loads, total_ArmedForceId_num.split("#"))
                )
                total_ArmedForceId_num_list.sort(
                    key=lambda x: x["inum"], reverse=True
                )

                # 解析资产变化
                Total_Price = res["data"].get("Total_Price", "")
                import re

                def extract_price(text: str) -> str:
                    m = re.match(r"(\w+)-(\d+)-(\d+)", text)
                    if m:
                        return m.group(3)
                    return ""

                price_list = list(map(extract_price, Total_Price.split(",")))

                # 解析资产净增
                rise_Price = int(price_list[-1]) - int(price_list[0])
                rise_Price_Str = f"{'-' if rise_Price < 0 else ''}{Util.trans_num_easy_for_read(abs(rise_Price))}"

                # 解析总场次
                total_sol_num = res["data"].get("total_sol_num", "0")

                # 解析总击杀
                total_Kill_Player = res["data"].get("total_Kill_Player", "0")

                # 解析总死亡
                total_Death_Count = res["data"].get("total_Death_Count", "0")

                # 解析总在线时间
                total_Online_Time = res["data"].get("total_Online_Time", "0")
                total_Online_Time_str = Util.seconds_to_duration(
                    total_Online_Time
                )

                # 解析撤离成功次数
                total_exacuation_num = res["data"].get(
                    "total_exacuation_num", "0"
                )

                # 解析百万撤离次数
                GainedPrice_overmillion_num = res["data"].get(
                    "GainedPrice_overmillion_num", "0"
                )

                # 解析游玩地图信息
                total_mapid_num = res["data"].get("total_mapid_num", "")
                total_mapid_num = total_mapid_num.replace("'", '"')
                total_mapid_num_list = list(
                    map(json.loads, total_mapid_num.split("#"))
                )
                total_mapid_num_list.sort(
                    key=lambda x: x["inum"], reverse=True
                )

                res = await deltaapi.get_weekly_friend_report(
                    access_token=access_token, openid=openid, statDate=statDate
                )

                friend_list = []
                if res["status"] and res["data"]:
                    friends_sol_record = res["data"].get(
                        "friends_sol_record", []
                    )
                    if friends_sol_record:
                        for friend in friends_sol_record:
                            friend_dict = {}
                            Friend_is_Escape1_num = friend.get(
                                "Friend_is_Escape1_num", 0
                            )
                            Friend_is_Escape2_num = friend.get(
                                "Friend_is_Escape2_num", 0
                            )
                            if (
                                Friend_is_Escape1_num + Friend_is_Escape2_num
                                <= 0
                            ):
                                continue

                            friend_openid = friend.get("friend_openid", "")
                            res = await deltaapi.get_user_info(
                                access_token=access_token,
                                openid=openid,
                                user_openid=friend_openid,
                            )
                            if res["status"]:
                                charac_name = res["data"].get(
                                    "charac_name", ""
                                )
                                charac_name = (
                                    urllib.parse.unquote(charac_name)
                                    if charac_name
                                    else "未知好友"
                                )
                                Friend_Escape1_consume_Price = friend.get(
                                    "Friend_Escape1_consume_Price", 0
                                )
                                Friend_Escape2_consume_Price = friend.get(
                                    "Friend_Escape2_consume_Price", 0
                                )
                                Friend_Sum_Escape1_Gained_Price = friend.get(
                                    "Friend_Sum_Escape1_Gained_Price", 0
                                )
                                Friend_Sum_Escape2_Gained_Price = friend.get(
                                    "Friend_Sum_Escape2_Gained_Price", 0
                                )
                                Friend_is_Escape1_num = friend.get(
                                    "Friend_is_Escape1_num", 0
                                )
                                Friend_is_Escape2_num = friend.get(
                                    "Friend_is_Escape2_num", 0
                                )
                                Friend_total_sol_KillPlayer = friend.get(
                                    "Friend_total_sol_KillPlayer", 0
                                )
                                Friend_total_sol_DeathCount = friend.get(
                                    "Friend_total_sol_DeathCount", 0
                                )
                                Friend_total_sol_num = friend.get(
                                    "Friend_total_sol_num", 0
                                )

                                friend_dict["charac_name"] = charac_name
                                friend_dict["sol_num"] = Friend_total_sol_num
                                friend_dict["kill_num"] = (
                                    Friend_total_sol_KillPlayer
                                )
                                friend_dict["death_num"] = (
                                    Friend_total_sol_DeathCount
                                )
                                friend_dict["escape_num"] = (
                                    Friend_is_Escape1_num
                                )
                                friend_dict["fail_num"] = Friend_is_Escape2_num
                                friend_dict["gained_str"] = (
                                    Util.trans_num_easy_for_read(
                                        Friend_Sum_Escape1_Gained_Price
                                        + Friend_Sum_Escape2_Gained_Price
                                    )
                                )
                                friend_dict["consume_str"] = (
                                    Util.trans_num_easy_for_read(
                                        Friend_Escape1_consume_Price
                                        + Friend_Escape2_consume_Price
                                    )
                                )
                                profit = (
                                    Friend_Sum_Escape1_Gained_Price
                                    + Friend_Sum_Escape2_Gained_Price
                                    - Friend_Escape1_consume_Price
                                    - Friend_Escape2_consume_Price
                                )
                                friend_dict["profit_str"] = (
                                    f"{'-' if profit < 0 else ''}{Util.trans_num_easy_for_read(abs(profit))}"
                                )
                                friend_list.append(friend_dict)
                        friend_list.sort(
                            key=lambda x: x["sol_num"], reverse=True
                        )

                msgs = []
                message = f"【{user_name}烽火周报 - 日期：{statDate_str}】"

                msgs.append(message)
                message = "--- 基本信息 ---\n"
                message += f"总览：{total_sol_num}场 | {total_exacuation_num}成功撤离 | {GainedPrice_overmillion_num}百万撤离\n"
                message += (
                    f"KD： {total_Kill_Player}杀/{total_Death_Count}死\n"
                )
                message += f"在线时间：{total_Online_Time_str}\n"
                message += f"总带出：{Gained_Price_Str} | 总带入：{consume_Price_Str}\n"
                message += f"资产变化：{Util.trans_num_easy_for_read(price_list[0])} -> {Util.trans_num_easy_for_read(price_list[-1])} | 资产净增：{rise_Price_Str}\n"
                msgs.append(message)
                message = "--- 干员使用情况 ---\n"
                message += f"资产变化：{Util.trans_num_easy_for_read(price_list[0])} -> {Util.trans_num_easy_for_read(price_list[-1])} | 资产净增：{rise_Price_Str}\n"
                msgs.append(message)
                message = "--- 干员使用情况 ---"
                for armed_force in total_ArmedForceId_num_list:
                    armed_force_name = Util.get_armed_force_name(
                        armed_force.get("ArmedForceId", 0)
                    )
                    armed_force_num = armed_force.get("inum", 0)
                    message += f"\n{armed_force_name}：{armed_force_num}场"
                msgs.append(message)
                message = "--- 地图游玩情况 ---"
                for map_info in total_mapid_num_list:
                    map_name = Util.get_map_name(map_info.get("MapId", 0))
                    map_num = map_info.get("inum", 0)
                    message += f"\n{map_name}：{map_num}场"
                msgs.append(message)
                message = "--- 队友协作情况 ---\n注：KD为好友KD，带出和带入为本人的数据"
                for friend in friend_list:
                    message += f"\n[{friend['charac_name']}]"
                    message += f"\n  总览：{friend['sol_num']}场 | {friend['escape_num']}撤离/{friend['fail_num']}失败 | {friend['kill_num']}杀/{friend['death_num']}死"
                    message += f"\n  带出：{friend['gained_str']} | 战损：{friend['consume_str']} | 利润：{friend['profit_str']}"
                msgs.append(message)

                img_data = cast(
                    WeeklyData,
                    {
                        "user_name": user_name,
                        "statDate_str": statDate_str,
                        "Gained_Price_Str": Gained_Price_Str,
                        "consume_Price_Str": consume_Price_Str,
                        "rise_Price_Str": rise_Price_Str,
                        # "profit_str": profit_str,
                        "total_ArmedForceId_num_list": total_ArmedForceId_num_list,
                        "total_mapid_num_list": total_mapid_num_list,
                        "friend_list": friend_list,
                        "profit": profit,
                        "rise_Price": rise_Price,
                        "total_sol_num": total_sol_num,
                        "total_Online_Time_str": total_Online_Time_str,
                        "total_Kill_Player": total_Kill_Player,
                        "total_Death_Count": total_Death_Count,
                        "total_exacuation_num": total_exacuation_num,
                        "GainedPrice_overmillion_num": GainedPrice_overmillion_num,
                        "price_list": price_list,
                    },
                )
                logger.debug(img_data)

                #     "user_name",
                #     statDate_str,
                #     Gained_Price_Str,
                #     consume_Price_Str,
                #     rise_Price_Str,
                #     total_ArmedForceId_num_list,
                #     total_mapid_num_list,
                #     friend_list,
                #     profit,
                #     rise_Price,
                #     total_sol_num,
                #     total_Online_Time_str,
                #     total_Kill_Player,
                #     total_Death_Count,
                #     total_exacuation_num,
                #     GainedPrice_overmillion_num,
                #     price_list,
                # )

                #     await Image(image=img_data).finish()
                # return msgs
                return img_data

            else:
                continue

        return "获取三角洲周报失败，可能需要重新登录或上周对局次数过少"
