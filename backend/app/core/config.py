import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    """应用配置类，从 .env 文件读取配置"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campus_qa.db")
    
    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # DashScope 配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 跨域配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # 额外字段（对应 .env 中的其他变量）
    APP_SECRET: Optional[str] = os.getenv("APP_SECRET", None)
    DATABASE_PATH: Optional[str] = os.getenv("DATABASE_PATH", "./data/campus_qa.db")
    UPLOAD_DIR: Optional[str] = os.getenv("UPLOAD_DIR", "./data/uploads")
    DATA_DIR: Optional[str] = os.getenv("DATA_DIR", "./data")
    FRONTEND_ORIGIN: Optional[str] = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    FRONTEND_ORIGINS: Optional[str] = os.getenv("FRONTEND_ORIGINS", None)
    DASHSCOPE_BASE_URL: Optional[str] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com")
    EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    EMBEDDING_MODEL: Optional[str] = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
    EMBEDDING_DIM: int = os.getenv("EMBEDDING_DIM", "1024")
    LLM_MODEL: Optional[str] = os.getenv("LLM_MODEL", "qwen-turbo")
    LLM_BASE_URL: Optional[str] = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    TOP_K: Optional[int] = int(os.getenv("TOP_K", "5"))
    CHUNK_SIZE: Optional[int] = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: Optional[int] = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()