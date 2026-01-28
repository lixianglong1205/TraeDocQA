import os
from dotenv import load_dotenv
from .logger import get_logger


# 设置日志
logger = get_logger("utils.config")


def load_env_vars():
    """
    Load environment variables from .env file
    """
    logger.info("开始加载环境变量")
    
    # 检查.env文件是否存在
    env_file = ".env"
    if os.path.exists(env_file):
        logger.info(f"找到环境变量文件: {env_file}")
    else:
        logger.warning(f"未找到环境变量文件: {env_file}，将使用系统环境变量")
    
    # 加载环境变量
    load_dotenv()
    logger.info("环境变量加载完成")
    
    # 确保必需的环境变量已设置
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"缺少必需的环境变量: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 记录已设置的环境变量（不记录敏感信息）
    for var in required_vars:
        if os.getenv(var):
            # 只记录变量名，不记录实际值
            logger.info(f"环境变量 {var} 已设置")
    
    logger.info("环境变量验证完成")
    return True


def get_api_key():
    """
    Get the OpenAI API key from environment
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        # 记录API密钥的存在但不记录实际值
        logger.debug("成功获取OpenAI API密钥")
        return api_key
    else:
        logger.warning("未找到OpenAI API密钥")
        return None