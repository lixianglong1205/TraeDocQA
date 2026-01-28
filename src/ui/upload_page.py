import streamlit as st
import os
from pathlib import Path
import tempfile
from data.parser import DocumentParser
from llm.faq_extractor import FAQExtractor
from database.vector_store import VectorStoreManager


def render_upload_page():
    st.title("📚 文档上传")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "选择要上传的文档",
        type=['pdf', 'txt'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Validate file type
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ['pdf', 'txt']:
            st.error(f"不支持的文件格式: {file_ext}. 仅支持 PDF 和 TXT 文件。")
            return
        
        st.success(f"已选择文件: {uploaded_file.name}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        try:
            # Parse document
            parser = DocumentParser()
            st.info("正在解析文档...")
            
            if file_ext == 'pdf':
                text_content = parser.parse_pdf(temp_path)
            else:  # txt
                text_content = parser.parse_txt(temp_path)
            
            st.success("文档解析完成！")
            
            # Extract FAQs
            st.info("正在提取FAQ...")
            faq_extractor = FAQExtractor()
            faqs = faq_extractor.extract_faqs(text_content)
            
            if faqs:
                st.success(f"成功提取 {len(faqs)} 个FAQ对！")
                
                # Store FAQs in vector database
                st.info("正在构建知识库...")
                
                # Create and store vector store in session state
                if 'vector_store' not in st.session_state:
                    st.session_state.vector_store = VectorStoreManager()
                
                st.session_state.vector_store.add_faqs(faqs)
                
                st.session_state.vector_store_ready = True
                st.success("知识库构建完成！")
                
                # Show sample FAQs
                st.subheader("提取的FAQ样本:")
                for i, faq in enumerate(faqs[:3]):  # Show first 3
                    with st.expander(f"FAQ {i+1}"):
                        st.write(f"**问题:** {faq['问题']}")
                        st.write(f"**答案:** {faq['答案']}")
            else:
                st.warning("未能从文档中提取到任何FAQ对，请检查文档内容。")
        
        except Exception as e:
            st.error(f"处理文档时发生错误: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    render_upload_page()