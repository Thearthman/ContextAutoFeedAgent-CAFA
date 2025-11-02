#!/usr/bin/env python3
"""
CAFA (Context Auto Feed Agent) - 核心模块
提供便捷的导入接口
"""

__version__ = "0.1.0"
__author__ = "CAFA Team"

# 基础设施模块
from .config_manager import ConfigManager, get_config
from .logger import CAFALogger, get_logger, setup_module_logger
from .utils import (
    # 时间工具
    timestamp_now,
    timestamp_to_datetime,
    time_ago,
    
    # 字符串工具
    truncate_string,
    clean_whitespace,
    extract_code_blocks,
    sanitize_filename,
    
    # 数据处理
    deep_get,
    merge_dicts,
    calculate_hash,
    
    # 文件处理
    read_json_file,
    write_json_file,
    
    # 装饰器
    timing_decorator,
    retry_decorator,
    thread_safe,
    
    # 验证工具
    validate_api_key,
    validate_url,
    
    # 缓存
    SimpleCache,
)

from .exceptions import (
    # 基础异常
    CAFAException,
    handle_exception,
    
    # 配置异常
    ConfigError,
    MissingConfigError,
    InvalidConfigError,
    
    # API异常
    APIError,
    APIConnectionError,
    APITimeoutError,
    APIAuthenticationError,
    APIRateLimitError,
    
    # LLM异常
    LLMError,
    LLMGenerationError,
    ModelNotLoadedError,
    InvalidPromptError,
    
    # 记忆异常
    MemoryError,
    MemoryStorageError,
    MemoryRetrievalError,
    EmbeddingError,
    
    # 验证异常
    ValidationError,
    MissingFieldError,
    InvalidFieldError,
    
    # 文件异常
    FileError,
    FileNotFoundError,
    FileReadError,
    FileWriteError,
)

from .validators import (
    Validator,
    LLMRequestValidator,
    MemoryRequestValidator,
    APIKeyValidator,
    ConfigValidator,
)

from .performance import (
    PerformanceMetrics,
    PerformanceMonitor,
    RequestTimer,
    get_monitor,
)

from .cache import (
    LRUCache,
    EmbeddingCache,
    ResponseCache,
    get_embedding_cache,
    get_response_cache,
    cache_decorator,
)

# 记忆系统
try:
    from .memory_tool.memory_store import MemoryStore
    from .memory_tool.enhanced_memory_store import EnhancedMemoryStore
    from .memory_tool.embeddings import EmbeddingGenerator
    from .memory_tool.smart_weight import SmartWeightEvaluator, AdaptiveDecay
except ImportError:
    # 记忆工具可能依赖额外的包，如果导入失败则跳过
    pass

# 版本信息
def get_version():
    """获取版本信息"""
    return __version__

def get_module_info():
    """获取模块信息"""
    return {
        "name": "CAFA",
        "version": __version__,
        "description": "Context Auto Feed Agent - 智能上下文管理代理",
        "modules": {
            "config": "配置管理",
            "logger": "日志系统",
            "utils": "工具函数",
            "exceptions": "异常定义",
            "validators": "数据验证",
            "performance": "性能监控",
            "cache": "缓存系统",
            "memory": "记忆系统",
        }
    }

# 便捷初始化函数
def initialize_cafa(
    config_file: str = "api_config.json",
    log_level: str = "INFO",
    enable_monitoring: bool = False
):
    """
    初始化CAFA环境
    
    Args:
        config_file: 配置文件路径
        log_level: 日志级别
        enable_monitoring: 是否启用性能监控
    
    Returns:
        初始化后的配置和日志对象
    """
    # 初始化配置
    config = ConfigManager(config_file)
    
    # 初始化日志
    logger = get_logger(
        name="CAFA",
        log_level=log_level,
        log_dir=config.get("logging.log_dir", "logs")
    )
    
    logger.info("=" * 70)
    logger.info("CAFA 初始化")
    logger.info(f"版本: {__version__}")
    logger.info("=" * 70)
    
    # 验证配置
    is_valid, errors = config.validate()
    if not is_valid:
        logger.warning("配置验证失败:")
        for error in errors:
            logger.warning(f"  • {error}")
    else:
        logger.info("✅ 配置验证通过")
    
    # 启用性能监控
    if enable_monitoring:
        monitor = get_monitor()
        monitor.start_system_monitoring()
        logger.info("✅ 性能监控已启用")
    
    logger.info("=" * 70)
    
    return config, logger

# 导出所有公开接口
__all__ = [
    # 版本信息
    "__version__",
    "get_version",
    "get_module_info",
    "initialize_cafa",
    
    # 配置管理
    "ConfigManager",
    "get_config",
    
    # 日志系统
    "CAFALogger",
    "get_logger",
    "setup_module_logger",
    
    # 工具函数
    "timestamp_now",
    "time_ago",
    "truncate_string",
    "deep_get",
    "merge_dicts",
    "calculate_hash",
    "timing_decorator",
    "retry_decorator",
    "validate_api_key",
    "validate_url",
    
    # 异常
    "CAFAException",
    "handle_exception",
    "ConfigError",
    "APIError",
    "LLMError",
    "MemoryError",
    "ValidationError",
    
    # 验证器
    "Validator",
    "LLMRequestValidator",
    "MemoryRequestValidator",
    "APIKeyValidator",
    
    # 性能监控
    "PerformanceMonitor",
    "RequestTimer",
    "get_monitor",
    
    # 缓存
    "LRUCache",
    "EmbeddingCache",
    "ResponseCache",
    "get_embedding_cache",
    "get_response_cache",
    "cache_decorator",
]

