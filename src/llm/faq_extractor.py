import tiktoken
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import re


class FAQExtractor:
    """
    FAQ extractor using sliding window approach and DeepSeek Reasoner
    """
    
    def __init__(self):
        # Using OpenAI-compatible model as proxy for DeepSeek since we don't have direct access
        # In production, this would be configured for DeepSeek V3.2
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        self.enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.window_size = 2000  # 2K tokens
        self.overlap_size = 500  # 500 tokens overlap
    
    def extract_faqs(self, text: str) -> list:
        """
        Extract FAQs using sliding window approach
        """
        # Split text into windows
        windows = self._create_sliding_windows(text)
        
        all_faqs = []
        for window in windows:
            faqs = self._extract_faqs_from_window(window)
            all_faqs.extend(faqs)
        
        return all_faqs
    
    def _create_sliding_windows(self, text: str) -> list:
        """
        Create sliding windows from text
        """
        tokens = self.enc.encode(text)
        windows = []
        
        start_idx = 0
        while start_idx < len(tokens):
            end_idx = min(start_idx + self.window_size, len(tokens))
            window_tokens = tokens[start_idx:end_idx]
            window_text = self.enc.decode(window_tokens)
            windows.append(window_text)
            
            # Move start index by window_size - overlap_size
            start_idx += (self.window_size - self.overlap_size)
            
            # If the next window would be too small, break
            if start_idx + self.overlap_size >= len(tokens):
                # Add the remaining text as the final window if it's substantial
                if end_idx < len(tokens):
                    final_tokens = tokens[end_idx - self.overlap_size:]
                    final_text = self.enc.decode(final_tokens)
                    if len(final_text.strip()) > 0:
                        windows.append(final_text)
                break
        
        return windows
    
    def _extract_faqs_from_window(self, window_text: str) -> list:
        """
        Extract FAQs from a single window of text
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的FAQ提取助手。请从给定的文本中提取所有可能的问题-答案对。"),
            ("human", f"""
            请从以下文本中提取问题-答案对：
            
            {window_text}
            
            返回格式为JSON列表，例如：
            [
              {{"问题": "示例问题1?", "答案": "示例答案1。"}},
              {{"问题": "示例问题2?", "答案": "示例答案2。"}}
            ]
            
            只返回JSON格式的内容，不要添加其他解释。
            """)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
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
                return []
        except (json.JSONDecodeError, KeyError):
            return []


if __name__ == "__main__":
    extractor = FAQExtractor()
    # Example usage would go here