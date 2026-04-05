from typing import Dict, Optional
from pathlib import Path
from functools import lru_cache

from PIL import Image


class ResourceManager:
    """全局资源管理器 - 统一管理静态资源加载与缓存"""

    _instance: Optional["ResourceManager"] = None
    _image_cache: Dict[Path, Image.Image] = {}
    _base_path: Path

    def __new__(cls) -> "ResourceManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._base_path = Path(__file__).parent.parent
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        return cls()

    def get_texture_path(self, name: str) -> Path:
        """获取纹理资源路径"""
        return self._base_path / "Delta_help" / "texture2d" / name

    @lru_cache(maxsize=32)
    def load_image(self, path: Path) -> Image.Image:
        """加载并缓存图片资源"""
        if path not in self._image_cache:
            self._image_cache[path] = Image.open(path).convert("RGBA")
        return self._image_cache[path].copy()

    def get_texture(self, name: str) -> Image.Image:
        """直接获取纹理图片"""
        return self.load_image(self.get_texture_path(name))

    def clear_cache(self) -> None:
        """清空资源缓存"""
        self._image_cache.clear()
        self.load_image.cache_clear()


# 全局实例
resource_manager = ResourceManager.get_instance()
