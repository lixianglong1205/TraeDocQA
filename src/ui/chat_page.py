import streamlit as st
from src.llm.qa_processor import QAProcessor
from src.utils.logger import get_logger


# 设置日志
logger = get_logger("ui.chat_page")


def render_chat_page():
    """
    渲染智能问答页面
    """
    logger.info("渲染智能问答页面")
    
    st.title("💬 智能问答")
    
    # Check if vector store is ready
    if not st.session_state.get('vector_store_ready', False):
        warning_msg = "向量存储未就绪，请先上传文档"
        logger.warning(warning_msg)
        st.warning("请先上传文档并构建知识库！")
        return
    
    logger.info("向量存储已就绪，可以开始问答")
    
    # Initialize QA processor and connect to the vector store
    if 'qa_processor' not in st.session_state:
        logger.info("初始化问答处理器")
        st.session_state.qa_processor = QAProcessor()
        # Connect to the shared vector store (in a real implementation, we'd have a singleton)
        # For now, we'll assume it's available in session state
        if 'vector_store' in st.session_state:
            st.session_state.qa_processor.set_vector_store(st.session_state.vector_store)
            logger.debug("问答处理器已连接到向量存储")
    
    qa_processor = st.session_state.qa_processor
    
    # Display chat history
    chat_history_count = len(st.session_state.chat_history)
    logger.debug(f"显示聊天历史，共 {chat_history_count} 条记录")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("请输入您的问题..."):
        logger.info(f"用户提问: {prompt}")
        
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Get response from QA processor
                logger.info("开始处理用户问题")
                response = qa_processor.process_question(prompt)
                logger.info("问题处理完成")
                
                # Display response
                message_placeholder.markdown(response)
                logger.debug("助手回复已显示")
                
                # Add feedback buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 赞同", key=f"like_{len(st.session_state.chat_history)}"):
                        logger.info("用户点击赞同按钮")
                        st.success("感谢您的反馈！")
                with col2:
                    if st.button("👎 不赞同", key=f"dislike_{len(st.session_state.chat_history)}"):
                        logger.info("用户点击不赞同按钮")
                        st.info("我们会持续改进！")
                with col3:
                    if st.button("🔄 重新生成", key=f"regenerate_{len(st.session_state.chat_history)}"):
                        logger.info("用户点击重新生成按钮")
                        # Remove last assistant response and regenerate
                        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                            st.session_state.chat_history.pop()
                            logger.debug("移除上一次助手回复")
                        
                        # Regenerate response
                        logger.info("重新生成回答")
                        new_response = qa_processor.process_question(prompt)
                        st.rerun()
                
            except Exception as e:
                error_msg = f"处理问题时发生错误: {str(e)}"
                logger.exception(error_msg)
                message_placeholder.error("抱歉，处理问题时出现了错误，请稍后重试。")
                response = "抱歉，处理问题时出现了错误。"
        
        # Add assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        logger.debug("助手回复已添加到聊天历史")
    else:
        logger.debug("等待用户输入问题")


if __name__ == "__main__":
    render_chat_page()