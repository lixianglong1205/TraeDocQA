import streamlit as st
import os
from pathlib import Path
import tempfile
from src.data.parser import DocumentParser
from src.llm.faq_extractor import FAQExtractor
from src.database.vector_store import VectorStoreManager
from src.utils.logger import get_logger


# 设置日志
logger = get_logger("ui.upload_page")


def render_upload_page():
    """
    渲染文档上传页面
    """
    logger.info("渲染文档上传页面")
    
    st.title("📚 文档上传")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "选择要上传的文档",
        type=['pdf', 'txt'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        logger.info(f"用户上传文件: {uploaded_file.name}")
        
        # Validate file type
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ['pdf', 'txt']:
            error_msg = f"不支持的文件格式: {file_ext}"
            logger.warning(error_msg)
            st.error(f"{error_msg}. 仅支持 PDF 和 TXT 文件。")
            return
        
        logger.info(f"文件格式验证通过: {file_ext}")
        st.success(f"已选择文件: {uploaded_file.name}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        logger.debug(f"临时文件保存路径: {temp_path}")
        
        try:
            # Parse document
            parser = DocumentParser()
            st.info("正在解析文档...")
            logger.info("开始解析文档")
            
            if file_ext == 'pdf':
                logger.debug("解析PDF文档")
                text_content = parser.parse_pdf(temp_path)
            else:  # txt
                logger.debug("解析TXT文档")
                text_content = parser.parse_txt(temp_path)
            
            logger.info(f"文档解析完成，内容长度: {len(text_content)} 字符")
            st.success("文档解析完成！")
            
            # Extract FAQs
            st.info("正在提取FAQ...")
            logger.info("开始提取FAQ")
            
            faq_extractor = FAQExtractor()
            faqs = faq_extractor.extract_faqs(text_content)
            
            logger.info(f"FAQ提取完成，提取到 {len(faqs)} 个FAQ对")
            
            if faqs:
                st.success(f"成功提取 {len(faqs)} 个FAQ对！")
                
                # Store FAQs in vector database
                st.info("正在构建知识库...")
                logger.info("开始构建向量知识库")
                
                # Create and store vector store in session state
                if 'vector_store' not in st.session_state:
                    st.session_state.vector_store = VectorStoreManager()
                    logger.debug("初始化向量存储管理器")
                
                st.session_state.vector_store.add_faqs(faqs)
                logger.info("FAQ对已添加到向量存储")
                
                st.session_state.vector_store_ready = True
                st.success("知识库构建完成！")
                logger.info("知识库构建完成，向量存储已就绪")
                
                # Show sample FAQs
                st.subheader("提取的FAQ样本:")
                for i, faq in enumerate(faqs[:3]):  # Show first 3
                    with st.expander(f"FAQ {i+1}"):
                        st.write(f"**问题:** {faq['问题']}")
                        st.write(f"**答案:** {faq['答案']}")
                logger.debug("显示FAQ样本")
            else:
                warning_msg = "未能从文档中提取到任何FAQ对"
                logger.warning(warning_msg)
                st.warning(f"{warning_msg}，请检查文档内容。")
        
        except Exception as e:
            error_msg = f"处理文档时发生错误: {str(e)}"
            logger.exception(error_msg)
            st.error(error_msg)
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.debug("临时文件已清理")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")
    else:
        logger.debug("等待用户上传文件")


if __name__ == "__main__":
    render_upload_page()