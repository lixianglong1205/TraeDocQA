from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import get_logger
from src.utils.config import get_api_key
import json
import re


# 设置日志
logger = get_logger("llm.faq_extractor")


class FAQExtractor:
    """
    FAQ extractor using sliding window approach and DeepSeek Reasoner
    """
    
    def __init__(self):
        logger.info("初始化FAQ提取器")
        
        try:
            # 获取 DeepSeek API 密钥
            api_key = get_api_key()
            if not api_key:
                raise ValueError("DeepSeek API密钥未设置")
            
            # 使用 DeepSeek 模型，显式传递 API 密钥和基础 URL
            self.llm = init_chat_model(
                "deepseek-chat",
                model_provider="deepseek", 
                temperature=0.1,  # 匹配原始温度设置
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            logger.debug("DeepSeek LLM模型初始化成功")
        except Exception as e:
            logger.error(f"FAQ提取器初始化失败: {e}")
            raise
            
        # 由于去掉了分词器，使用字符数进行窗口分割
        self.window_size = 4000  # 4000字符（约等于2000 tokens）
        self.overlap_size = 1000  # 1000字符重叠
        logger.debug(f"窗口大小: {self.window_size}字符, 重叠大小: {self.overlap_size}字符")
    
    # llm call test code
    def test_llm_call(self, question: str) -> str:
        """
        Test LLM call with a simple question
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个FAQ提取助手。请从用户问题中提取相关的问题-答案对。"),
            ("human", question)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content
    
    def extract_faqs(self, text: str) -> list:
        """
        Extract FAQs using sliding window approach
        """
        logger.info(f"开始提取FAQ，文本长度: {len(text)} 字符")
        
        try:
            # Split text into windows
            windows = self._create_sliding_windows(text)
            logger.info(f"文本分割为 {len(windows)} 个窗口")
            
            all_faqs = []
            for i, window in enumerate(windows):
                logger.debug(f"处理第 {i+1}/{len(windows)} 个窗口")
                faqs = self._extract_faqs_from_window(window)
                all_faqs.extend(faqs)
                logger.debug(f"窗口 {i+1} 提取到 {len(faqs)} 个FAQ对")
            
            logger.info(f"FAQ提取完成，共提取到 {len(all_faqs)} 个FAQ对")
            return all_faqs
            
        except Exception as e:
            logger.exception(f"FAQ提取过程中发生错误: {e}")
            return []
    
    def _create_sliding_windows(self, text: str) -> list:
        """
        Create sliding windows from text using character count
        """
        windows = []
        text_length = len(text)
        
        start_idx = 0
        while start_idx < text_length:
            end_idx = min(start_idx + self.window_size, text_length)
            window_text = text[start_idx:end_idx]
            windows.append(window_text)
            
            # Move start index by window_size - overlap_size
            start_idx += (self.window_size - self.overlap_size)
            
            # If the next window would be too small, break
            if start_idx + self.overlap_size >= text_length:
                # Add the remaining text as the final window if it's substantial
                if end_idx < text_length:
                    final_text = text[end_idx - self.overlap_size:]
                    if len(final_text.strip()) > 0:
                        windows.append(final_text)
                break
        
        return windows
    
    def _extract_faqs_from_window(self, window_text: str) -> list:
        """
        Extract FAQs from a single window of text using DeepSeek model
        """
        # 构建提示词
        prompt = f"""你是一个专业的FAQ提取助手。请从给定的文本中提取所有可能的问题-答案对。

请从以下文本中提取问题-答案对：

{window_text}

返回格式为JSON列表，例如：
[
  {{"问题": "示例问题1?", "答案": "示例答案1。"}},
  {{"问题": "示例问题2?", "答案": "示例答案2。"}}
]

只返回JSON格式的内容，不要添加其他解释。"""
        
        try:
            # 使用LangChain模型进行调用
            response = self.llm.invoke(prompt)
            logger.debug(f"LLM模型返回原始响应: {response.content}")
            
            # Extract JSON from response
            try:
                # Look for JSON in the response
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    faq_json = json_match.group(0)
                    faqs = json.loads(faq_json)
                    # Validate FAQ format
                    validated_faqs = []
                    for faq in faqs:
                        if isinstance(faq, dict) and "问题" in faq and "答案" in faq:
                            validated_faqs.append(faq)
                    return validated_faqs
                else:
                    logger.warning("未在响应中找到JSON格式内容")
                    return []
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"JSON解析错误: {e}")
                return []
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return []


if __name__ == "__main__":
    extractor = FAQExtractor()
    # Example usage would go here
    question = "你好"
    import os
    from dotenv import load_dotenv
    load_dotenv()
    response = extractor.test_llm_call(question)
    print(response)