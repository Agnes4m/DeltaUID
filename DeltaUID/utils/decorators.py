import asyncio
import logging
from typing import Any, Callable, Coroutine
from functools import wraps

from .const import ERROR_MESSAGE

logger = logging.getLogger("DeltaUID")


def handle_errors(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """统一异常处理装饰器 - 捕获异常并返回友好错误消息"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except asyncio.TimeoutError:
            logger.exception(f"[Timeout] 函数 {func.__name__} 执行超时")
            return "请求超时了，鼠鼠再试试？"
        except ConnectionError:
            logger.exception(f"[Connection] 函数 {func.__name__} 连接失败")
            return "网络好像出问题了，等下再试吧~"
        except Exception as e:
            logger.exception(f"[Error] 函数 {func.__name__} 发生异常: {str(e)}")
            return ERROR_MESSAGE

    return wrapper


def retry(retries: int = 3, delay: float = 1.0) -> Callable[..., Any]:
    """重试装饰器 - 失败后自动重试指定次数"""

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"[Retry] 函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper

    return decorator
