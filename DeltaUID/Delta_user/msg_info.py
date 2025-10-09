import json
import datetime
import urllib.parse
from typing import Union, Optional, cast

from PIL import Image
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe

from ..utils.api.util import Util
from .image import draw_sol_record
from ..utils.api.api import DeltaApi
from ..utils.database.models import DFBind, DFUser
from ..utils.models import (
    TQCData,
    InfoData,
    RecordSol,
    RecordTdm,
    WeeklyData,
    DayInfoData,
    DayListData,
)

interval = 120
BROADCAST_EXPIRED_MINUTES = 7
SAFEHOUSE_CHECK_INTERVAL = 600  # 特勤处检查间隔（秒）


class MsgInfo:
    def __init__(self, user_id: str, bot_id: str):
        self.user_id = user_id
        self.bot_id = bot_id

        self.user_data = None

    async def _fetch_user_data(self):
        """获取用户数据"""
        uid = await DFBind.get_uid_by_game(self.user_id, self.bot_id)
        if uid is None:
            return None
        return cast(DFUser, await DFUser.select_data_by_uid(uid))

    async def _get_delta_api(self):
        """初始化并返回DeltaApi实例"""
        if not self.user_data:
            await self._fetch_user_data()
            if not self.user_data:
                raise ValueError('未绑定三角洲账号，请先用"鼠鼠登录"命令登录')
        return DeltaApi(self.user_data.platform)

    async def _get_player_info(self, deltaapi: DeltaApi):
        """获取玩家基本信息"""
        if self.user_data:
            res = await deltaapi.get_player_info(
                access_token=self.user_data.cookie,
                openid=self.user_data.uid,
            )
            if not res["status"] or not res["data"].get("player"):
                logger.warning("获取玩家信息失败，可能需要重新登录")
                return None
            return res

    async def _get_lastest_id(self, uid: str):
        """获取最新战绩id"""
        data = await DFUser.select_data_by_uid(uid)
        return cast(DFUser, data) if data else None

    async def _validate_user(self) -> bool:
        """验证用户是否已绑定账号

        Returns:
            bool: 验证结果
        """
        self.user_data = await self._fetch_user_data()
        return bool(self.user_data)

    async def _process_daily_data(
        self, deltaapi: DeltaApi, sol_detail: dict
    ) -> Union[DayInfoData, str]:
        """处理日报原始数据

        Args:
            deltaapi: DeltaAPI实例
            sol_detail: 原始日报数据

        Returns:
            Union[DayInfoData, str]: 处理后的数据或错误信息
        """
        try:
            recent_gain_date = sol_detail.get("recentGainDate", "未知")
            recent_gain = sol_detail.get("recentGain", 0)
            gain_str = f"{'-' if recent_gain < 0 else ''}{Util.trans_num_easy_for_read(abs(recent_gain))}"

            user_collection = await self._get_user_collections(
                deltaapi, sol_detail.get("userCollectionTop", {})
            )

            return {
                "daily_report_date": recent_gain_date,
                "profit": recent_gain,
                "profit_str": gain_str,
                "top_collections": user_collection,
            }

        except Exception as e:
            logger.error(f"处理日报数据异常: {str(e)}")
            return "处理日报数据时发生异常"

    async def _get_user_collections(
        self, deltaapi: DeltaApi, collection_top: dict
    ) -> DayListData:
        """获取用户藏品信息

        Args:
            deltaapi: DeltaAPI实例
            collection_top: 藏品顶部数据

        Returns:
            DayListData: 处理后的藏品数据
        """
        if not collection_top:
            return {"list_str": "未知", "details": []}

        collection_list = collection_top.get("list", [])
        if not collection_list:
            return {"list_str": "未知", "details": []}

        collection_details = []
        user_collection_list_str = ""

        for item in collection_list:
            object_id = item.get("objectID", 0)
            try:
                collection_info = await self._fetch_collection_info(
                    deltaapi, object_id
                )
                if collection_info:
                    collection_details.append(collection_info)
                    if not user_collection_list_str:
                        user_collection_list_str = collection_info[
                            "objectName"
                        ]
                    else:
                        user_collection_list_str += (
                            f"、{collection_info['objectName']}"
                        )

            except Exception as e:
                logger.error(f"获取藏品{object_id}信息失败: {str(e)}")
                collection_details.append(
                    {"objectID": object_id, "error": str(e)}
                )
                user_collection_list_str += f"未知藏品：{object_id}"

        return {
            "list_str": user_collection_list_str or "未知",
            "details": collection_details,
        }

    async def _fetch_collection_info(
        self, deltaapi: DeltaApi, object_id: str
    ) -> Optional[dict]:
        """获取单个藏品详细信息

        Args:
            deltaapi: DeltaAPI实例
            object_id: 藏品ID

        Returns:
            Optional[dict]: 藏品详细信息或None
        """
        if self.user_data is None:
            return None
        res = await deltaapi.get_object_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
            object_id=object_id,
        )

        if not res.get("status"):
            return None

        obj_list = res["data"].get("list", [])
        if not obj_list:
            return None

        obj_data = obj_list[0]
        return {
            "objectID": object_id,
            "objectName": obj_data.get("objectName", "未知藏品"),
            "pic": obj_data.get("pic", ""),
            "avgPrice": f"{'-' if int(obj_data.get('avgPrice', 0)) < 0 else ''}"
            f"{Util.trans_num_easy_for_read(abs(int(obj_data.get('avgPrice', 0))))}",
        }

    async def get_msg_info(self):
        self.user_data = await self._fetch_user_data()

        if self.user_data is None:
            return '未绑定三角洲账号，请先用"鼠鼠登录"命令登录'

        deltaapi = DeltaApi(self.user_data.platform)
        player_info_res = await self._get_player_info(deltaapi)
        if player_info_res is None:
            return "过期的登陆信息，请重新登录"

        basic_info = await deltaapi.get_role_basic_info(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )
        sol_info = await deltaapi.get_person_center_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
            resource_type="sol",
        )
        if not sol_info["data"]:
            return "服务器忙碌,请稍后重试"

        try:
            if sol_info["data"].get("rat") == 101:
                return "登录信息已过期，请重新登录"
        except Exception as _:
            ...

        tdm_info = await deltaapi.get_person_center_info(
            access_token=self.user_data.cookie,
            openid=self.user_data.uid,
            resource_type="mp",
        )
        if not tdm_info["data"]:
            return "服务器忙碌,请稍后重试"
        # 处理基本数据
        propcapital = (
            Util.trans_num_easy_for_read(basic_info["data"]["propcapital"])
            if basic_info["status"]
            else "0"
        )

        # 处理响应数据
        if (
            player_info_res
            and player_info_res["status"]
            and sol_info["status"]
            and tdm_info["status"]
        ):
            # 提取玩家信息
            user_name: str = player_info_res["data"]["player"]["charac_name"]
            money = Util.trans_num_easy_for_read(
                player_info_res["data"]["money"]
            )
            rankpoint: str = player_info_res["data"]["game"]["rankpoint"]
            soltotalfght = player_info_res["data"]["game"]["soltotalfght"]
            solttotalescape = player_info_res["data"]["game"][
                "solttotalescape"
            ]
            soltotalkill = player_info_res["data"]["game"]["soltotalkill"]
            solescaperatio = player_info_res["data"]["game"]["solescaperatio"]

            # 提取sol信息
            sol_data = sol_info["data"]["solDetail"]
            profitLossRatio = (
                Util.trans_num_easy_for_read(
                    int(sol_data["profitLossRatio"]) // 100
                )
                if sol_info["data"]
                else "未知"
            )
            highKillDeathRatio = (
                f"{int(sol_data['highKillDeathRatio']) / 100:.2f}"
            )
            medKillDeathRatio = (
                f"{int(sol_data['medKillDeathRatio']) / 100:.2f}"
            )
            lowKillDeathRatio = (
                f"{int(sol_data['lowKillDeathRatio']) / 100:.2f}"
            )
            totalGainedPrice = Util.trans_num_easy_for_read(
                sol_data["totalGainedPrice"]
            )
            totalGameTime = Util.seconds_to_duration(sol_data["totalGameTime"])

            # 提取tdm信息
            tdm_data = tdm_info["data"]["mpDetail"]
            try:
                avgScorePerMinute = (
                    f"{int(tdm_data['avgScorePerMinute']) / 100:.2f}"
                )
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取avgScorePerMinute: {e}")
                avgScorePerMinute = "未知"

            try:
                totalVehicleDestroyed = tdm_data["totalVehicleDestroyed"]
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取totalVehicleDestroyed: {e}")
                totalVehicleDestroyed = "未知"
            try:
                totalVehicleKill = tdm_data["totalVehicleKill"]
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"无法获取totalVehicleKill: {e}")
                totalVehicleKill = "未知"

            # 构建玩家数据对象
            player_data = cast(
                InfoData,
                {
                    "user_name": user_name,
                    "avatar": Util.avatar_trans(
                        player_info_res["data"]["player"]["picurl"]
                    ),
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
                    "tdmrankpoint": player_info_res["data"]["game"][
                        "tdmrankpoint"
                    ],
                    "avgkillperminute": f"{int(player_info_res['data']['game']['avgkillperminute']) / 100:.2f}",
                    "tdmtotalfight": player_info_res["data"]["game"][
                        "tdmtotalfight"
                    ],
                    "totalwin": player_info_res["data"]["game"]["totalwin"],
                    "tdmtotalkill": str(
                        int(
                            int(player_info_res["data"]["game"]["tdmduration"])
                            * int(
                                player_info_res["data"]["game"][
                                    "avgkillperminute"
                                ]
                            )
                            / 100
                        )
                    ),
                    "tdmduration": Util.seconds_to_duration(
                        int(player_info_res["data"]["game"]["tdmduration"])
                        * 60
                    ),
                    "tdmsuccessratio": player_info_res["data"]["game"][
                        "tdmsuccessratio"
                    ],
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
            return 0, '未绑定三角洲账号，请先用"ss登录"命令登录'

        # 参数解析
        type_id = 4  # 默认模式为烽火
        page = 1  # 默认页码为1
        line_limit = 50  # 默认条数上限为50

        if raw_text:
            tokens = raw_text.split()
            seen_page = seen_mode = seen_limit = False

            for token in tokens:
                # 处理条数上限 L<number>
                if token.lower().startswith("l"):
                    if seen_limit:
                        return 0, "参数过多"
                    limit_str = token[1:]
                    if not limit_str.isdigit() or int(limit_str) <= 0:
                        return 0, "参数错误"
                    line_limit = int(limit_str)
                    seen_limit = True

                # 处理模式
                elif token in ["烽火", "烽火行动"]:
                    if seen_mode:
                        return 0, "参数过多"
                    type_id = 4
                    seen_mode = True
                elif token in ["战场", "大战场", "全面战场"]:
                    if seen_mode:
                        return 0, "参数过多"
                    type_id = 5
                    seen_mode = True

                # 处理页码
                elif token.isdigit():
                    if seen_page:
                        return 0, "参数过多"
                    page_value = int(token)
                    if page_value <= 0:
                        return 0, "参数错误"
                    page = page_value
                    seen_page = True

                # 无效参数
                else:
                    return (
                        0,
                        "请输入正确参数，格式：三角洲战绩 [模式] [页码] L[战绩条数上限]",
                    )

        # 获取玩家信息
        deltaapi = DeltaApi(self.user_data.platform)
        res = await deltaapi.get_player_info(
            access_token=self.user_data.cookie, openid=self.user_data.uid
        )
        if not res["status"] or not res["data"].get("player"):
            return 0, "获取玩家信息失败，可能需要重新登录"
        user_name = res["data"]["player"]["charac_name"]

        # 获取战绩数据
        res = await deltaapi.get_record(
            self.user_data.cookie, self.user_data.uid, type_id, page
        )
        if not res["status"]:
            return 0, res["message"]

        card_list = []
        # 处理烽火模式战绩
        if type_id == 4:
            if not res["data"]["gun"]:
                return 1, "最近7天没有战绩"

            for index, record in enumerate(res["data"]["gun"], start=1):
                if index > line_limit:
                    break
                # 解析战绩数据
                event_time = record.get("dtEventTime", "")
                map_id = record.get("MapId", "")
                map_name = Util.get_map_name(map_id)
                escape_fail_reason = record.get("EscapeFailReason", 0)
                result_str = (
                    "撤离成功" if escape_fail_reason == 1 else "撤离失败"
                )
                duration_seconds = record.get("DurationS", 0)
                minutes, seconds = divmod(duration_seconds, 60)
                duration_str = f"{minutes}分{seconds}秒"
                kill_count: int = record.get("KillCount", 0)
                final_price: Optional[str] = record.get("FinalPrice", "0")
                price_str = (
                    Util.trans_num_easy_for_read(int(final_price))
                    if final_price is not None and final_price.isdigit()
                    else "未知"
                )
                flow_cal_gained_price = record.get("flowCalGainedPrice", 0)
                profit_str = f"{'' if flow_cal_gained_price >= 0 else '-'}{Util.trans_num_easy_for_read(abs(flow_cal_gained_price))}"
                ArmedForceId = record.get("ArmedForceId", "")
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                card_data_sol = {
                    "user_name": user_name,
                    "time": event_time,
                    "map_name": map_name,
                    "armed_force": ArmedForce,
                    "result": result_str,
                    "duration": duration_str,
                    "kill_count": kill_count,
                    "price": price_str,
                    "profit": profit_str,
                    "title": f"#{index}",
                }
                card_list.append(card_data_sol)

            return 1, card_list

        # 处理战场模式战绩
        elif type_id == 5:
            if not res["data"]["operator"]:
                return 2, "最近7天没有战绩"

            for index, record in enumerate(res["data"]["operator"], start=1):
                if index > line_limit:
                    break

                # 解析战绩数据
                event_time = record.get("dtEventTime", "")
                map_id = record.get("MapID", "")
                map_name = Util.get_map_name(map_id)
                MatchResult = record.get("MatchResult", 0)
                result_str = {
                    1: "胜利",
                    2: "失败",
                    3: "中途退出",
                }.get(MatchResult, f"未知{MatchResult}")
                gametime = record.get("gametime", 0)
                minutes, seconds = divmod(gametime, 60)
                duration_str = f"{minutes}分{seconds}秒"
                KillNum = record.get("KillNum", 0)
                Death = record.get("Death", 0)
                Assist = record.get("Assist", 0)
                RescueTeammateCount = record.get("RescueTeammateCount", 0)
                RoomId = record.get("RoomId", "")

                # 获取战绩详情
                res_detail = await deltaapi.get_tdm_detail(
                    self.user_data.cookie, self.user_data.uid, RoomId
                )
                if res_detail["status"] and res_detail["data"]:
                    mpDetailList = res_detail["data"].get("mpDetailList", [])
                    for mpDetail in mpDetailList:
                        if mpDetail.get("isCurrentUser", False):
                            rescueTeammateCount = mpDetail.get(
                                "rescueTeammateCount", 0
                            )
                            if rescueTeammateCount > 0:
                                RescueTeammateCount = rescueTeammateCount
                                break
                else:
                    logger.error(f"获取战绩详情失败: {res_detail}")

                TotalScore = record.get("TotalScore", 0)
                avgScorePerMinute = (
                    int(TotalScore * 60 / gametime) if gametime > 0 else 0
                )
                ArmedForceId = record.get("ArmedForceId", "")
                ArmedForce = Util.get_armed_force_name(ArmedForceId)

                card_data = {
                    "title": f"#{index}",
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

            return 2, card_list

        return 0, "请求超时，请稍后重试"

    async def get_tqc(self) -> list[TQCData] | str:
        """获取特勤处设备状态

        Returns:
            list[dict] | str: 设备状态列表或错误信息
        """
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'

        try:
            deltaapi = DeltaApi(self.user_data.platform)
            res = await deltaapi.get_safehousedevice_status(
                access_token=self.user_data.cookie, openid=self.user_data.uid
            )

            if not res.get("status"):
                return f"获取特勤处状态失败：{res.get('message', '未知错误')}"

            return self._process_tqc_data(res["data"])

        except Exception as e:
            logger.error(f"获取特勤处状态异常: {e}")
            return f"获取特勤处状态时发生异常: {str(e)}"

    def _process_tqc_data(self, data: dict) -> list[TQCData] | str:
        """处理特勤处原始数据

        Args:
            data (dict): 原始API响应数据

        Returns:
            list[dict] | str: 处理后的设备状态或错误信息
        """
        place_data = data.get("placeData", [])
        relate_map = data.get("relateMap", {})
        devices = []

        for device in place_data:
            object_id = device.get("objectId", 0)
            left_time = device.get("leftTime", 0)
            push_time = device.get("pushTime", 0)
            place_name = device.get("placeName", "")

            if object_id > 0 and left_time > 0:
                object_name = relate_map.get(str(object_id), {}).get(
                    "objectName", f"物品{object_id}"
                )
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
                        "progress": round(progress, 2),  # 保留两位小数
                    }
                )
            else:
                devices.append({"place_name": place_name, "status": "idle"})

        if not devices:
            return "特勤处状态获取成功，但没有数据"

        # 默认返回结构化数据
        return devices

    async def get_tqc_text(self) -> str:
        devices = await self.get_tqc()
        if isinstance(devices, str):
            return devices

        messages = []
        for device in devices:
            if device["status"] == "producing":
                msg = (
                    f"{device['place_name']}："
                    f"{device['object_name']}，剩余时间："
                    f"{device['left_time']}，完成时间："
                    f"{device['finish_time']}"
                )
            else:
                msg = f"{device['place_name']}：闲置中"
            messages.append(msg)

        return "\n".join(messages) if messages else "没有特勤处设备数据"

    async def get_daily(self) -> Union[DayInfoData, str]:
        """优化后的日报获取方法

        Returns:
            Union[DayInfoData, str]: 成功时返回日报数据，失败时返回错误信息
        """
        if not await self._validate_user() or not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'

        try:
            deltaapi = DeltaApi(self.user_data.platform)
            res = await deltaapi.get_daily_report(
                self.user_data.cookie, self.user_data.uid
            )

            if not res.get("status"):
                return f"获取日报失败：{res.get('message', '未知错误')}"

            sol_detail = res["data"].get("solDetail")
            if not sol_detail:
                return "获取三角洲日报失败，没有数据"

            return await self._process_daily_data(deltaapi, sol_detail)

        except Exception as e:
            logger.error(f"获取日报异常: {str(e)}")
            return f"获取日报时发生异常: {str(e)}"

    # async def get_daily(self) -> DayInfoData | str:
    #     if not await self._validate_user():
    #         return '未绑定三角洲账号，请先用"ss登录"命令登录'

    #     deltaapi = DeltaApi(self.user_data.platform)
    #     res = await deltaapi.get_daily_report(self.user_data.cookie, self.user_data.uid)
    #     if res["status"]:
    #         solDetail = res["data"].get("solDetail", None)
    #         if solDetail:
    #             recentGainDate = solDetail.get("recentGainDate", "未知")
    #             recentGain = solDetail.get("recentGain", 0)
    #             gain_str = f"{'-' if recentGain < 0 else ''}{Util.trans_num_easy_for_read(abs(recentGain))}"
    #             userCollectionTop = solDetail.get("userCollectionTop", None)
    #             if userCollectionTop:
    #                 userCollectionList = userCollectionTop.get("list", None)
    #                 if userCollectionList:
    #                     userCollectionListStr = ""
    #                     collection_details = []

    #                     for item in userCollectionList:
    #                         objectID = item.get("objectID", 0)
    #                         res = await deltaapi.get_object_info(
    #                             access_token=self.user_data.cookie,
    #                             openid=self.user_data.uid,
    #                             object_id=objectID,
    #                         )
    #                         if res["status"]:
    #                             obj_list = res["data"].get("list", [])
    #                             if obj_list:
    #                                 obj_name = obj_list[0].get("objectName", "未知藏品")
    #                                 pic = obj_list[0].get("pic", "")
    #                                 avgPrice = obj_list[0].get("avgPrice", 0)
    #                                 collection_details.append(
    #                                     {
    #                                         "objectID": objectID,
    #                                         "objectName": obj_name,
    #                                         "pic": pic,
    #                                         "avgPrice": f"{'-' if recentGain < 0 else ''}{Util.trans_num_easy_for_read(abs(avgPrice))}",
    #                                     }
    #                                 )
    #                                 if userCollectionListStr == "":
    #                                     userCollectionListStr = obj_name
    #                                 else:
    #                                     userCollectionListStr += f"、{obj_name}"
    #                         else:
    #                             collection_details.append(
    #                                 {
    #                                     "objectID": objectID,
    #                                     "error": res["message"],
    #                                 }
    #                             )
    #                             userCollectionListStr += f"未知藏品：{objectID}"
    #                     userCollectionData: DayListData = {
    #                         "list_str": userCollectionListStr,
    #                         "details": collection_details,
    #                     }
    #                 else:
    #                     userCollectionData = {
    #                         "list_str": "未知",
    #                         "details": [],
    #                     }
    #             else:
    #                 userCollectionData = {"list_str": "未知", "details": []}
    #             # 返回原始数据字典
    #             return {
    #                 "daily_report_date": recentGainDate,
    #                 "profit": recentGain,
    #                 "profit_str": gain_str,
    #                 "top_collections": userCollectionData,
    #             }
    #         else:
    #             return "获取三角洲日报失败，没有数据"
    #     else:
    #         return f"获取三角洲日报失败：{res['message']}"

    async def get_weekly(self):
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'
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

                if (
                    total_ArmedForceId_num_list
                    and total_ArmedForceId_num_list[0] != 0
                ):
                    total_ArmedForceId_num_list.sort(
                        key=lambda x: x["inum"], reverse=True
                    )
                else:
                    total_ArmedForceId_num_list = []

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
                if total_mapid_num_list and total_mapid_num_list[0] != 0:
                    total_mapid_num_list.sort(
                        key=lambda x: x["inum"], reverse=True
                    )
                else:
                    total_mapid_num_list = []

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

                # msgs = []
                # message = f"【{user_name}烽火周报 - 日期：{statDate_str}】"

                # msgs.append(message)
                # message = "--- 基本信息 ---\n"
                # message += f"总览：{total_sol_num}场 | {total_exacuation_num}成功撤离 | {GainedPrice_overmillion_num}百万撤离\n"
                # message += (
                #     f"KD： {total_Kill_Player}杀/{total_Death_Count}死\n"
                # )
                # message += f"在线时间：{total_Online_Time_str}\n"
                # message += f"总带出：{Gained_Price_Str} | 总带入：{consume_Price_Str}\n"
                # message += f"资产变化：{Util.trans_num_easy_for_read(price_list[0])} -> {Util.trans_num_easy_for_read(price_list[-1])} | 资产净增：{rise_Price_Str}\n"
                # msgs.append(message)
                # message = "--- 干员使用情况 ---\n"
                # message += f"资产变化：{Util.trans_num_easy_for_read(price_list[0])} -> {Util.trans_num_easy_for_read(price_list[-1])} | 资产净增：{rise_Price_Str}\n"
                # msgs.append(message)
                # message = "--- 干员使用情况 ---"
                # for armed_force in total_ArmedForceId_num_list:
                #     if armed_force == 0:
                #         break
                #     armed_force_name = Util.get_armed_force_name(
                #         armed_force.get("ArmedForceId", 0)
                #     )
                #     armed_force_num = armed_force.get("inum", 0)
                #     message += f"\n{armed_force_name}：{armed_force_num}场"
                # msgs.append(message)
                # message = "--- 地图游玩情况 ---"
                # for map_info in total_mapid_num_list:
                #     map_name = Util.get_map_name(map_info.get("MapId", 0))
                #     map_num = map_info.get("inum", 0)
                #     message += f"\n{map_name}：{map_num}场"
                # msgs.append(message)
                # message = "--- 队友协作情况 ---\n注：KD为好友KD，带出和带入为本人的数据"
                # for friend in friend_list:
                #     message += f"\n[{friend['charac_name']}]"
                #     message += f"\n  总览：{friend['sol_num']}场 | {friend['escape_num']}撤离/{friend['fail_num']}失败 | {friend['kill_num']}杀/{friend['death_num']}死"
                #     message += f"\n  带出：{friend['gained_str']} | 战损：{friend['consume_str']} | 利润：{friend['profit_str']}"
                # msgs.append(message)

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
                return img_data

            else:
                continue

        return "获取三角洲周报失败，可能需要重新登录或上周对局次数过少"

    async def watch_record(
        self, user_name: str, uid: str, avatar: Image.Image
    ):
        self.cookie = await DFUser.get_user_cookie_by_uid(uid)
        if not self.cookie:
            logger.warning(f"获取三角洲账号{uid}的cookie失败")
            return '未绑定三角洲账号，请先用"ss登录"命令登录'
        if not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'

        deltaapi = DeltaApi(self.user_data.platform)
        logger.debug(f"开始获取玩家{user_name}的战绩")

        msg_info = []
        record_id = record_id_tdm = None
        # 获取之前的最新战绩ID
        latest_record_data = await self._get_lastest_id(uid)
        for mode in ["sol", "tdm"]:
            if mode == "sol":
                type_id = 4
            elif mode == "tdm":
                type_id = 5
            else:
                type_id = 4
            res = await deltaapi.get_record(
                self.user_data.cookie, uid, type_id, 1
            )

            if res["status"]:
                # sol模式
                if mode == "sol":
                    # 处理gun模式战绩
                    gun_records = res["data"].get("gun", [])
                    if not gun_records:
                        # logger.debug(f"玩家{user_name}没有gun模式战绩")
                        continue

                    # 获取最新战绩
                    if gun_records:
                        latest_record: dict = gun_records[0]  # 第一条是最新的
                        # logger.debug(f"最新战绩：{latest_record}")

                        # 检查时间限制
                        if not Util.is_record_within_time_limit(latest_record):
                            logger.debug(
                                f"最新战绩时间超过{BROADCAST_EXPIRED_MINUTES}分钟，跳过播报"
                            )
                            continue

                        # 生成战绩ID
                        record_id = Util.generate_record_id(latest_record)
                        logger.debug(f"[DF][sol]最新战绩ID：{record_id}")

                        # 如果是新战绩（ID不同）
                        if (
                            not latest_record_data
                            or latest_record_data.latest_record != record_id
                        ):
                            RoomId = latest_record.get("RoomId", "")
                            res = await deltaapi.get_tdm_detail(
                                self.user_data.cookie,
                                self.user_data.uid,
                                RoomId,
                            )
                            logger.info(f"[DF][sol]获取战绩详情：{res}")
                            if res["status"] and res["data"]:
                                mpDetailList = res["data"].get(
                                    "mpDetailList", []
                                )
                                for mpDetail in mpDetailList:
                                    if mpDetail.get("isCurrentUser", False):
                                        rescueTeammateCount = mpDetail.get(
                                            "rescueTeammateCount", 0
                                        )
                                        if rescueTeammateCount > 0:
                                            latest_record[
                                                "RescueTeammateCount"
                                            ] = rescueTeammateCount
                                            break
                            else:
                                logger.error(f"获取战绩详情失败: {res}")

                        else:
                            logger.debug(
                                f"[DF][sol]没有新战绩需要播报: {user_name}"
                            )
                            continue
                        logger.info(f"[DF][sol]最近：{latest_record}")
                        msg = await self.format_record_message(
                            latest_record, user_name
                        )
                        if isinstance(msg, str) or msg is None:
                            return msg
                        else:
                            msg["user_name"] = user_name
                            msg_info = await draw_sol_record(
                                avatar.resize((150, 150)), msg
                            )
                        # logger.info(f"[DF][sol]格式化战绩消息：{msg}")
                        # msg_info.append(a)
                    else:
                        continue
                # tdm模式
                elif mode == "tdm":
                    # logger.debug(f"玩家{user_name}的战绩：{res['data']}")

                    # 处理operator模式战绩
                    operator_records = res["data"].get("operator", [])
                    if not operator_records:
                        # logger.debug(f"玩家{user_name}没有operator模式战绩")
                        continue

                    # 获取最新战绩
                    if operator_records:
                        latest_record = operator_records[0]  # 第一条是最新的
                        # logger.debug(f"最新战绩：{latest_record}")
                        # 生成战绩ID
                        record_id_tdm = Util.generate_record_id(latest_record)

                        # 检查时间限制
                        if not record_id_tdm:
                            logger.debug(
                                f"[DF][tdm]最新战绩ID：{record_id_tdm}最新战绩时间超过{BROADCAST_EXPIRED_MINUTES}分钟，跳过播报"
                            )
                            continue

                        # 如果是新战绩（ID不同）
                        if (
                            not latest_record_data
                            or latest_record_data.latest_tdm_record
                            != record_id_tdm
                        ):
                            # 格式化播报消息
                            result_tdm = await self.format_tdm_record_message(
                                latest_record, user_name
                            )
                            msg_info = result_tdm

                        else:
                            logger.debug(
                                f"[DF][tdm]没有新战绩需要播报: {user_name}"
                            )

        # 更新最新战绩记录

        await self.update_record(
            record_id,
            record_id_tdm,
            user_name,
            uid=uid,
        )
        return msg_info

    async def update_record(
        self,
        latest_record_sol: str | None,
        latest_record_tdm: str | None,
        user_name: str,
        uid: str,
    ):
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'
        if latest_record_sol is None:
            logger.debug(f"玩家{user_name}没有sol模式战绩")
            latest_record_sol = self.user_data.latest_record

        if latest_record_tdm is None:
            logger.debug(f"玩家{user_name}没有tdm模式战绩")
            latest_record_tdm = self.user_data.latest_tdm_record
        try:
            await self.user_data.update_record(
                uid=uid,
                bot_id=self.bot_id,
                latest_record=latest_record_sol,
                latest_tdm_record=latest_record_tdm,
            )
            logger.debug(
                f"更新最新战绩记录成功: {user_name} - {latest_record_sol}"
            )
        except Exception as e:
            logger.error(
                f"更新最新战绩记录失败: {user_name} - {latest_record_sol}"
            )
            logger.warning(e)
            return f"更新最新战绩记录失败: {user_name} - {latest_record_sol}"
        logger.debug(f"没有新战绩需要播报: {user_name}")

    @staticmethod
    async def format_record_message(
        record_data: dict, user_name: str
    ) -> RecordSol | str | None:
        """格式化战绩播报消息"""
        try:
            # 解析时间
            event_time = record_data.get("dtEventTime", "")
            # 解析地图ID
            map_id = record_data.get("MapId", "")
            # 解析结果
            escape_fail_reason = record_data.get("EscapeFailReason", 0)
            # 解析时长（秒）
            duration_seconds = record_data.get("DurationS", 0)
            if not duration_seconds:
                return None
            # 解析击杀数
            kill_count = record_data.get("KillCount", 0)
            # 解析收益
            final_price = record_data.get("FinalPrice", "0")
            final_price = 0 if final_price is None else final_price
            # 解析纯利润
            flow_cal_gained_price = record_data.get("flowCalGainedPrice", 0)

            # 格式化时长
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            duration_str = f"{minutes}分{seconds}秒"

            # 格式化结果
            if escape_fail_reason == 1:
                result_str = "撤离成功"
            else:
                result_str = "撤离失败"

            # 格式化收益
            price_int = int(final_price)
            try:
                price_str = Util.trans_num_easy_for_read(price_int)
            except Exception:
                price_str = final_price
            # 解析干员
            ArmedForceId = record_data.get("ArmedForceId", "")
            ArmedForce = Util.get_armed_force_name(ArmedForceId)
            # 计算战损
            loss_int = int(final_price) - int(flow_cal_gained_price)
            loss_str = Util.trans_num_easy_for_read(loss_int)

            # logger.debug(f"获取到玩家{user_name}的战绩：时间：{event_time}，地图：{get_map_name(map_id)}，结果：{result_str}，存活时长：{duration_str}，击杀干员：{kill_count}，带出：{price_str}，战损：{loss_str}")
            # if price_int > 100:
            if price_int > 1000000:
                # 构建消息
                message = f"🎯 {user_name} 百万撤离！\n"
                message += f"⏰ 时间: {event_time}\n"
                message += f"🗺️ 地图: {Util.get_map_name(map_id)}\n"
                message += f"📊 结果: {result_str}\n"
                message += f"⏱️ 存活时长: {duration_str}\n"
                message += f"💀 击杀干员: {kill_count}\n"
                message += f"💰 带出: {price_str}\n"
                message += f"💸 战损: {loss_str}"
                try:
                    img_data = cast(
                        RecordSol,
                        {
                            "user_name": user_name,
                            "title": "百万撤离！",
                            "time": event_time,
                            "map_name": Util.get_map_name(map_id),
                            "result": result_str,
                            "duration": duration_str,
                            "kill_count": kill_count,
                            "price": price_str,
                            "loss": loss_str,
                            "is_gain": True,
                            "main_value": price_str,
                            "armedforceid": ArmedForce,
                        },
                    )
                    return img_data
                except Exception as e:
                    logger.exception(f"渲染战绩卡片失败: {e}")
                    # 降级到文本模式
                return message
            elif loss_int > 1000000:
                message = f"🎯 {user_name} 百万战损！\n"
                message += f"⏰ 时间: {event_time}\n"
                message += f"🗺️ 地图: {Util.get_map_name(map_id)}\n"
                message += f"📊 结果: {result_str}\n"
                message += f"⏱️ 存活时长: {duration_str}\n"
                message += f"💀 击杀干员: {kill_count}\n"
                message += f"💰 带出: {price_str}\n"
                message += f"💸 战损: {loss_str}"
                try:
                    img_data = cast(
                        RecordSol,
                        {
                            "user_name": user_name,
                            "title": "百万战损！",
                            "time": event_time,
                            "map_name": Util.get_map_name(map_id),
                            "result": result_str,
                            "duration": duration_str,
                            "kill_count": kill_count,
                            "price": price_str,
                            "loss": loss_str,
                            "is_gain": False,
                            "main_value": loss_str,
                        },
                    )
                    return img_data
                except Exception as e:
                    logger.exception(f"渲染战绩卡片失败: {e}")
                    # 降级到文本模式
                return message
            else:
                return None

        except Exception as e:
            logger.exception(f"格式化战绩消息失败: {e}")
            return None

    @staticmethod
    async def format_tdm_record_message(
        record_data: dict, user_name: str
    ) -> RecordTdm | str | None:
        """格式化战场战绩播报消息"""
        try:
            # 解析时间
            event_time = record_data.get("dtEventTime", "")
            # 解析地图
            map_id = record_data.get("MapID", "")
            map_name = Util.get_map_name(map_id)
            # 解析结果
            match_result = Util.get_tdm_match_result(
                record_data.get("MatchResult", 0)
            )
            # 解析KDA
            kill_num: int = record_data.get("KillNum", 0)
            death_num: int = record_data.get("Death", 0)
            assist_num: int = record_data.get("Assist", 0)
            # 分数与时长
            total_score: int = record_data.get("TotalScore", 0)
            game_time: int = record_data.get("gametime", 0)  # 秒
            game_time_str = Util.seconds_to_duration(game_time)
            # 分均得分（避免除零）
            avg_score_per_minute: int = (
                int(total_score * 60 / game_time)
                if game_time and game_time > 0
                else 0
            )

            # 触发条件
            trigger_kill = kill_num >= 100
            trigger_avg = avg_score_per_minute >= 1000
            if not (trigger_kill or trigger_avg):
                return None

            # 文本播报（回退或同时使用）
            if trigger_kill:
                message = f"🎯 {user_name} 捞薯大师！\n"
            else:
                message = f"🎯 {user_name} 刷分大王！\n"
            message += f"⏰ 时间: {event_time}\n"
            message += f"👤 干员: {Util.get_armed_force_name(record_data.get('ArmedForceId', 0))}\n"
            message += f"🗺️ 地图: {map_name}\n"
            message += f"📊 结果: {match_result}\n"
            message += f"⏱️ 时长: {game_time_str}\n"
            message += f"💀 KDA: {kill_num}/{death_num}/{assist_num}\n"
            message += f"💰 总得分: {total_score}\n"
            message += f"🎖️ 分均得分: {avg_score_per_minute}"

            # 构建卡片数据
            if trigger_kill:
                main_label = "捞薯大师"
                main_value = str(kill_num)
                badge_text = "100+杀"
            else:
                main_label = "刷分大王"
                main_value = str(avg_score_per_minute)
                badge_text = "1000+分均得分"

            card_data = cast(
                RecordTdm,
                {
                    "user_name": user_name,
                    "title": "战场高光！",
                    "time": event_time,
                    "map_name": map_name,
                    "result": match_result,
                    "gametime": game_time_str,
                    "armed_force": Util.get_armed_force_name(
                        record_data.get("ArmedForceId", 0)
                    ),
                    "kill_count": kill_num,
                    "death_count": death_num,
                    "assist_count": assist_num,
                    "total_score": total_score,
                    "avg_score_per_minute": avg_score_per_minute,
                    "is_good": True,
                    "main_label": main_label,
                    "main_value": main_value,
                    "badge_text": badge_text,
                },
            )
            return card_data

        except Exception as e:
            logger.exception(f"格式化战场战绩消息失败: {e}")
            return None

    async def scheduler_record(self, ev: Event, bot: Bot):
        self.user_data = await self._fetch_user_data()
        if not self.user_data:
            return '未绑定三角洲账号，请先用"ss登录"命令登录'
        raw_text = ev.text.strip() if ev.text else ""
        msg = await self.get_msg_info()
        if isinstance(msg, str):
            await bot.send(msg, at_sender=True)
            return

        # index, record = await self.get_record(raw_text)

        if raw_text == "开启" or raw_text == "":
            await gs_subscribe.add_subscribe(
                "single",
                "三角洲战绩订阅",
                ev,
                extra_message=self.user_data.uid,
            )
            await bot.send("[DF] 三角洲战绩订阅成功！")
            # return await bot.send("[DF] 三角洲战绩订阅成功！")

        elif raw_text == "关闭":
            await gs_subscribe.delete_subscribe("single", "三角洲战绩订阅", ev)
            await bot.send("[DF] 三角洲战绩订阅已关闭！")
        return msg
