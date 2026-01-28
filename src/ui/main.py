import streamlit as st
from ui.upload_page import render_upload_page
from ui.chat_page import render_chat_page


def main():
    st.set_page_config(
        page_title="智能文档问答系统",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    if 'uploaded_docs' not in st.session_state:
        st.session_state.uploaded_docs = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False
    
    # Navigation
    with st.sidebar:
        st.title("导航")
        if st.button("文档上传"):
            st.session_state.current_page = 'upload'
        if st.button("开始问答"):
            st.session_state.current_page = 'chat'
        
        st.divider()
        st.info("智能文档问答系统 v0.1")
    
    # Page routing
    if st.session_state.current_page == 'upload':
        render_upload_page()
    elif st.session_state.current_page == 'chat':
        render_chat_page()


if __name__ == "__main__":
    main()