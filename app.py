import streamlit as st
from src.utils.config import load_env_vars
from src.ui.main import main
from src.utils.logger import setup_logging, get_logger


# 设置日志
logger = get_logger("app")


def initialize_app():
    """
    Initialize the application
    """
    logger.info("开始初始化应用程序")
    
    try:
        # Load environment variables
        logger.info("正在加载环境变量")
        load_env_vars()
        logger.info("环境变量加载成功")
        
    except ValueError as e:
        logger.error(f"环境配置错误: {e}")
        st.error(f"Environment configuration error: {e}")
        st.stop()
    except Exception as e:
        logger.exception("应用程序初始化过程中发生意外错误")
        st.error(f"Application initialization failed: {e}")
        st.stop()


if __name__ == "__main__":
    # 初始化日志系统
    setup_logging()
    logger.info("=" * 50)
    logger.info("智能文档问答系统启动")
    logger.info("=" * 50)
    
    try:
        initialize_app()
        logger.info("应用程序初始化完成，开始运行主界面")
        main()
        logger.info("应用程序正常退出")
        
    except KeyboardInterrupt:
        logger.info("应用程序被用户中断")
    except Exception as e:
        logger.exception("应用程序运行过程中发生未处理的异常")
        st.error(f"Application error: {e}")
    finally:
        logger.info("=" * 50)
        logger.info("智能文档问答系统关闭")
        logger.info("=" * 50)