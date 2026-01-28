import streamlit as st
from llm.qa_processor import QAProcessor


def render_chat_page():
    st.title("💬 智能问答")
    
    # Check if vector store is ready
    if not st.session_state.get('vector_store_ready', False):
        st.warning("请先上传文档并构建知识库！")
        return
    
    # Initialize QA processor and connect to the vector store
    if 'qa_processor' not in st.session_state:
        st.session_state.qa_processor = QAProcessor()
        # Connect to the shared vector store (in a real implementation, we'd have a singleton)
        # For now, we'll assume it's available in session state
        if 'vector_store' in st.session_state:
            st.session_state.qa_processor.set_vector_store(st.session_state.vector_store)
    
    qa_processor = st.session_state.qa_processor
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("请输入您的问题..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Get response from QA processor
            response = qa_processor.process_question(prompt)
            
            # Display response
            message_placeholder.markdown(response)
            
            # Add feedback buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👍 赞同", key=f"like_{len(st.session_state.chat_history)}"):
                    st.success("感谢您的反馈！")
            with col2:
                if st.button("👎 不赞同", key=f"dislike_{len(st.session_state.chat_history)}"):
                    st.info("我们会持续改进！")
            with col3:
                if st.button("🔄 重新生成", key=f"regenerate_{len(st.session_state.chat_history)}"):
                    # Remove last assistant response and regenerate
                    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                        st.session_state.chat_history.pop()
                    
                    # Regenerate response
                    new_response = qa_processor.process_question(prompt)
                    st.rerun()
        
        # Add assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    render_chat_page()