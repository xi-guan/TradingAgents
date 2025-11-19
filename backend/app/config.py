"""应用配置"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # 应用基本配置
    app_name: str = Field(default="TradingAgents", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    secret_key: str = Field(..., description="密钥")

    # 数据库配置
    database_url: str = Field(..., description="数据库连接 URL")
    database_echo: bool = Field(default=False, description="是否打印 SQL")

    # Redis 配置
    redis_url: str = Field(default="redis://localhost:6385/0", description="Redis URL")
    redis_password: Optional[str] = Field(default=None, description="Redis 密码")

    # Qdrant 配置
    qdrant_url: str = Field(default="http://localhost:6435", description="Qdrant URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API Key")

    # JWT 配置
    jwt_secret_key: str = Field(..., description="JWT 密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")

    # CORS 配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3005", "http://localhost:5173"],
        description="允许的跨域源"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS 配置（支持字符串和列表）"""
        if isinstance(v, str):
            # 处理类似 '["http://localhost:3000"]' 的字符串
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # 如果不是 JSON，按逗号分割
                return [origin.strip() for origin in v.split(",")]
        return v

    # OpenAI API
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI Base URL"
    )
    openai_model_name: str = Field(
        default="gpt-4",
        description="OpenAI Model Name"
    )

    # Alpha Vantage API
    alpha_vantage_api_key: str = Field(..., description="Alpha Vantage API Key")

    # Tushare API
    tushare_token: Optional[str] = Field(default=None, description="Tushare Token")

    # Celery 配置
    celery_broker_url: str = Field(
        default="redis://localhost:6385/1",
        description="Celery Broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6385/2",
        description="Celery Result Backend"
    )

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="logs/app.log", description="日志文件")

    # 数据目录
    data_dir: str = Field(default="./data", description="数据目录")

    # 默认语言
    default_language: str = Field(default="zh_CN", description="默认语言")

    # 速率限制
    rate_limit_enabled: bool = Field(default=True, description="是否启用速率限制")
    rate_limit_per_minute: int = Field(default=60, description="每分钟请求限制")

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return not self.debug


# 全局配置实例
settings = Settings()
