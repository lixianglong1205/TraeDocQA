import streamlit as st
from src.ui.upload_page import render_upload_page
from src.ui.chat_page import render_chat_page
from src.utils.logger import get_logger


# 设置日志
logger = get_logger("ui.main")


def main():
    """
    主界面函数
    """
    logger.info("启动主界面")
    
    try:
        st.set_page_config(
            page_title="智能文档问答系统",
            page_icon="📚",
            layout="wide"
        )
        logger.debug("页面配置设置完成")
        
        # Initialize session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'upload'
            logger.debug("初始化当前页面状态: upload")
        if 'uploaded_docs' not in st.session_state:
            st.session_state.uploaded_docs = []
            logger.debug("初始化上传文档状态")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            logger.debug("初始化聊天历史状态")
        if 'vector_store_ready' not in st.session_state:
            st.session_state.vector_store_ready = False
            logger.debug("初始化向量存储状态")
        
        logger.info("会话状态初始化完成")
        
        # Navigation
        with st.sidebar:
            st.title("导航")
            if st.button("文档上传"):
                logger.info("用户点击文档上传按钮")
                st.session_state.current_page = 'upload'
            if st.button("开始问答"):
                logger.info("用户点击开始问答按钮")
                st.session_state.current_page = 'chat'
            
            st.divider()
            st.info("智能文档问答系统 v0.1")
        
        logger.debug(f"当前页面: {st.session_state.current_page}")
        
        # Page routing
        if st.session_state.current_page == 'upload':
            logger.info("渲染文档上传页面")
            render_upload_page()
        elif st.session_state.current_page == 'chat':
            logger.info("渲染问答页面")
            render_chat_page()
        else:
            logger.warning(f"未知页面: {st.session_state.current_page}")
            st.error("页面配置错误")
            
        logger.debug("页面渲染完成")
        
    except Exception as e:
        logger.exception("主界面运行过程中发生错误")
        st.error("界面加载失败，请刷新页面重试")


if __name__ == "__main__":
    main()