import time
import datetime
from typing import Any, Dict, Literal
from pathlib import Path
from functools import lru_cache
from urllib.parse import unquote

from PIL import Image

from gsuid_core.logger import logger

BROADCAST_EXPIRED_MINUTES = 7

API_CONSTANTS: Dict[str, Any] = {
    "SIG": "https://xui.ptlogin2.qq.com/ssl/ptqrshow",
    "GETLOGINTICKET": "https://xui.ptlogin2.qq.com/cgi-bin/xlogin",
    "GETLOGINSTATUS": "https://ssl.ptlogin2.qq.com/ptqrlogin",
    "GAMEBASEURL": "https://ams.shallow.ink/ide/",
    # "GAMEBASEURL": "https://comm.ams.game.qq.com/ide/", 测试
    "GAME_API_URL": "https://ams.shallow.ink/ide/",
    # "GAME_API_URL": "https://comm.aci.game.qq.com/main", 测试
    "REQUEST_HEADERS_BASE": {
        "platform": "android",
        "Content-Type": "application/x-www-form-urlencoded",
    },
}

APP_ID = "101491592"
LOGIN_APP_ID = "716027609"

armed_dict = {
    "深蓝": "Alexei",
    "疾风": "Claire",
    "乌鲁鲁": "David",
    "无名": "Elio",
    "红狼": "Kai",
    "露娜": "Luna",
    "骇爪": "Mai",
    "蜂医": "Roy",
    "牧羊人": "Terry",
    "威龙": "Wang",
    "蛊": "Zoya",
}


TEXT_PATH = Path(__file__).parent.parent / "texture2d/record/armed"


class Util:
    @staticmethod
    def get_gtk(p_skey: str, h: int = 5381) -> int:
        """计算g_tk值"""
        for c in p_skey:
            h += (h << 5) + ord(c)
        return h & 0x7FFFFFFF

    @staticmethod
    def get_micro_time() -> int:
        """获取微秒时间戳"""
        return int(time.time() * 1000000)

    @staticmethod
    def create_cookie(openid: str, access_token: str, is_qq: bool = True) -> dict:
        """创建API请求所需的cookie"""
        return {
            "openid": openid,
            "access_token": access_token,
            "acctype": "qc" if is_qq else "wx",
            "appid": APP_ID,
        }

    @staticmethod
    def parse_api_response(data: dict, success_key: str = "ret", data_key: str = "jData") -> Dict[str, Any]:
        """解析API响应，返回标准化格式"""
        ret = data.get(success_key, -1)
        if ret == 0:
            return {
                "status": True,
                "message": "获取成功",
                "data": data.get(data_key, {}).get("data", {}),
            }
        else:
            return {
                "status": False,
                "message": f"请求失败，错误码: {ret}",
                "data": {},
            }

    @staticmethod
    def build_game_params(chart_id: int, sub_chart_id: int, token: str, method: str = "", **extra) -> Dict[str, Any]:
        """构建游戏API通用参数"""
        params = {
            "iChartId": chart_id,
            "iSubChartId": sub_chart_id,
            "sIdeToken": token,
        }
        if method:
            params["method"] = method
        params.update(extra)
        return params

    @staticmethod
    def trans_num_easy_for_read(num: int | str) -> str:
        if isinstance(num, str):
            num = int(num)
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num / 1000:.1f}K"
        else:
            return f"{num / 1000000:.1f}M"

    @staticmethod
    def get_qr_token(qrsig: str) -> int:
        """生成QR token，对应PHP中的getQrToken方法"""
        if not qrsig:
            return 0

        # 对应PHP的getQrToken算法
        length = len(qrsig)
        hash_val = 0
        for i in range(length):
            # 对应PHP: $hash += (($hash << 5) & 2147483647) + ord($qrSig[$i]) & 2147483647;
            hash_val += ((hash_val << 5) & 2147483647) + ord(qrsig[i]) & 2147483647
            # 对应PHP: $hash &= 2147483647;
            hash_val &= 2147483647

        # 对应PHP: return $hash & 2147483647;
        return hash_val & 2147483647

    @staticmethod
    def get_map_name(map_id: str | int) -> str:
        if isinstance(map_id, int):
            map_id = str(map_id)
        map_dict = {
            "2231": "零号大坝-前夜",
            "2232": "零号大坝-永夜",
            "2201": "零号大坝-常规",
            "2202": "零号大坝-机密",
            "1901": "长弓溪谷-常规",
            "1902": "长弓溪谷-机密",
            "1912": "长弓溪谷-机密(单排模式)",
            "3901": "航天基地-机密",
            "3902": "航天基地-绝密",
            "8102": "巴克什-机密",
            "8103": "巴克什-绝密",
            "8803": "潮汐监狱-绝密",
            "2212": "零号大坝-机密(单排模式)",
            "34": "烬区-占领",
            "33": "烬区-攻防",
            "54": "攀升-攻防",
            "75": "临界点-攻防",
            "103": "攀升-占领",
            "107": "沟壕战-攻防",
            "108": "沟壕战-占领",
            "111": "断轨-攻防",
            "112": "断轨-占领",
            "113": "贯穿-攻防",
            "114": "贯穿-占领",
            "117": "攀升-钢铁洪流",
            "121": "刀锋-攻防",
            "122": "刀锋-占领",
            "210": "临界点-占领",
            "227": "沟壕战-钢铁洪流",
            "302": "风暴眼-攻防",
            "303": "风暴眼-占领",
            "516": "沟壕战-霰弹风暴",
            "517": "攀升-霰弹风暴",
            "526": "断轨-钢铁洪流",
        }
        return map_dict.get(map_id, f"未知地图{map_id}")

    @staticmethod
    def timestamp_to_readable(timestamp: int) -> str:
        """将时间戳转换为易读的时间格式

        Args:
            timestamp: Unix时间戳（秒）

        Returns:
            格式化的时间字符串，如 "2025-01-21 14:30:00"
        """
        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "未知时间"

    @staticmethod
    def seconds_to_duration(seconds: int | str) -> str:
        """将秒数转换为易读的时长格式

        Args:
            seconds: 秒数

        Returns:
            格式化的时长字符串，如 "2小时30分钟"
        """
        if isinstance(seconds, str):
            seconds = int(seconds)
        if seconds <= 0:
            return "已完成"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        second = seconds % 60

        if hours > 0:
            if minutes > 0:
                return f"{hours}h{minutes}m"
            else:
                return f"{hours}h"
        else:
            if minutes > 0:
                return f"{minutes}m{second}s"
            else:
                return f"{second}s"

    @staticmethod
    def get_Sunday_date(which_week: int = 1) -> tuple[str, str]:
        """获取指定周的周日日期

        Args:
            which_week: 第几周，1为上周，2为上上周

        Returns:
            指定周周日的日期字符串，格式为"YYYYMMDD"
        """
        today = datetime.datetime.now()

        # 获取今天是星期几（0=周一, 6=周日）
        weekday = today.weekday()

        # 计算到上个周日需要减去的天数
        # 如果今天是周日(weekday=6)，那么上个周日是7天前
        # 如果今天是周一(weekday=0)，那么上个周日是1天前
        # 如果今天是周二(weekday=1)，那么上个周日是2天前
        # ...
        # 如果今天是周六(weekday=5)，那么上个周日是6天前

        if weekday == 6:  # 今天是周日
            days_to_last_sunday = 7 * which_week
        else:  # 今天不是周日
            days_to_last_sunday = (weekday + 1) + 7 * (which_week - 1)

        sunday = today - datetime.timedelta(days=days_to_last_sunday)
        return sunday.strftime("%Y%m%d"), sunday.strftime("%Y-%m-%d")

    @staticmethod
    def get_armed_force_name(armed_force_id: int | str) -> str:
        if isinstance(armed_force_id, str):
            armed_force_id = int(armed_force_id)
        armed_force_dict = {
            30009: "乌鲁鲁",
            10010: "威龙",
            10011: "无名",
            30010: "深蓝",
            30008: "牧羊人",
            10012: "疾风",
            10007: "红狼",
            20004: "蛊",
            20003: "蜂医",
            40005: "露娜",
            40010: "骇爪",
            40011: "银翼",
        }

        return armed_force_dict.get(armed_force_id, "未知干员")

    @staticmethod
    def get_tdm_match_result(result: int | str) -> str:
        if isinstance(result, str):
            result = int(result)
        result_dict = {1: "胜利", 2: "失败", 3: "中途退出"}
        return result_dict.get(result, f"未知结果{result}")

    @staticmethod
    def get_rank_by_score_sol(score: int) -> str:
        """根据分数计算段位"""
        if score <= 1000:
            return "无段位"

        rank_params = [
            ("青铜", 3, 1000, 150, 3),
            ("白银", 3, 1450, 150, 3),
            ("黄金", 4, 1900, 200, 4),
            ("铂金", 4, 2700, 200, 4),
            ("钻石", 5, 3500, 250, 5),
            ("黑鹰", 5, 4750, 250, 5),
        ]

        for (
            rank_name,
            sub_ranks,
            start_score,
            interval,
            stars_per_sub,
        ) in rank_params:
            max_score = start_score + sub_ranks * interval
            if score < max_score:
                sub_rank = sub_ranks - int((score - start_score) // interval)
                sub_rank = max(sub_rank, 1)
                score_in_sub = score - (start_score + (sub_ranks - sub_rank) * interval)
                stars = (score_in_sub // 50) + 1
                return f"{rank_name}{sub_rank}★{stars}"
            start_score = max_score

        # 三角洲巅峰，每50分一颗星
        delta_peak_score = score - 6000
        stars = delta_peak_score // 50
        return f"三角洲巅峰⭐{stars}"

    @staticmethod
    def get_rank_by_score_tdm(score: int) -> str:
        """根据分数计算段位"""
        if score <= 1000:
            return "无段位"

        rank_params = [
            ("列兵", 3, 1000, 150, 3),
            ("上等兵", 3, 1450, 150, 3),
            ("军士长", 4, 1900, 200, 4),
            ("尉官", 4, 2700, 200, 4),
            ("校官", 5, 3500, 250, 5),
            ("将军", 5, 4750, 250, 5),
        ]

        for (
            rank_name,
            sub_ranks,
            start_score,
            interval,
            stars_per_sub,
        ) in rank_params:
            max_score = start_score + sub_ranks * interval
            if score < max_score:
                sub_rank = sub_ranks - int((score - start_score) // interval)
                sub_rank = max(sub_rank, 1)
                score_in_sub = score - (start_score + (sub_ranks - sub_rank) * interval)
                stars = score_in_sub // 50 + 1
                return f"{rank_name}{sub_rank}★{stars}"
            start_score = max_score

        # 三角洲巅峰，每50分一颗星
        delta_peak_score = score - 6000
        stars = delta_peak_score // 50
        return f"统帅⭐{stars}"

    @staticmethod
    def avatar_trans(avatar: str) -> str:
        """头像url转换"""
        encoded_url = avatar

        decoded_url = unquote(encoded_url)
        return decoded_url

    @staticmethod
    def parse_event_time(
        event_time_str: str,
        game_time: int = 0,
        mode: Literal["sol", "tdm"] = "sol",
    ) -> datetime.datetime:
        """解析事件时间字符串，并根据游戏时间调整"""
        cleaned_time_str = event_time_str.replace(" : ", ":")  # 清理空格
        event_time = datetime.datetime.strptime(cleaned_time_str, "%Y-%m-%d %H:%M:%S")

        if mode == "tdm":
            event_time += datetime.timedelta(seconds=game_time)

        return event_time

    @staticmethod
    def is_record_within_time_limit(
        record_data: dict,
        max_age_minutes: int = BROADCAST_EXPIRED_MINUTES,
        mode: Literal["sol", "tdm"] = "sol",
    ) -> bool:
        """检查战绩是否在时间限制内"""
        try:
            event_time_str = record_data.get("dtEventTime", "")
            if not event_time_str:
                return False

            game_time = record_data.get("GameTime", 0)
            event_time = Util.parse_event_time(event_time_str, game_time, mode)
            current_time = datetime.datetime.now()
            time_diff_minutes = (current_time - event_time).total_seconds() / 60

            return time_diff_minutes <= max_age_minutes

        except Exception as e:
            logger.error(f"检查战绩时间限制失败: {e}")
            return False

    @staticmethod
    def generate_record_id(record_data: dict) -> str:
        """生成战绩唯一标识"""
        return record_data.get("dtEventTime", "")

    @staticmethod
    @lru_cache(maxsize=20)
    async def armed_to_img(armed: str) -> Image.Image:
        name = armed_dict.get(armed, "Default")
        if name != "Default":
            name += "_Default_C"
        else:
            name += "_C"
        name = f"Card_{name}"
        img = Image.open(TEXT_PATH / f"{name}.png")
        return img


if __name__ == "__main__":
    print(Util.get_Sunday_date())
    print(Util.get_Sunday_date(2))
