import datetime


class Util:
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
            hash_val += ((hash_val << 5) & 2147483647) + ord(
                qrsig[i]
            ) & 2147483647
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
        import datetime

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
        }

        return armed_force_dict.get(armed_force_id, "未知干员")

    @staticmethod
    def get_tdm_match_result(result: int | str) -> str:
        if isinstance(result, str):
            result = int(result)
        result_dict = {1: "胜利", 2: "失败", 3: "中途退出"}
        return result_dict.get(result, f"未知结果{result}")


if __name__ == "__main__":
    print(Util.get_Sunday_date())
    print(Util.get_Sunday_date(2))
