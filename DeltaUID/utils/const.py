from pathlib import Path

# 插件基础信息
PLUGIN_NAME = "DeltaUID"
PLUGIN_PREFIX = ["鼠鼠", "ss"]

# 路径配置
BASE_PATH = Path(__file__).parent.parent
TEXTURE_PATH = BASE_PATH / "utils" / "texture2d"
ICON_PATH = BASE_PATH.parent / "icon.png"

# API 配置
DEFAULT_REQUEST_TIMEOUT = 30
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 1

# 缓存配置
IMAGE_CACHE_SIZE = 32
HELP_CACHE_TTL = 3600

# 消息配置
ERROR_MESSAGE = "鼠鼠我啊，出问题了，请稍后再试~"
LOADING_MESSAGE = "鼠鼠正在努力加载中..."
