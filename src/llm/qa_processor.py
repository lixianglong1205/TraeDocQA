from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from src.database.vector_store import VectorStoreManager
from src.utils.logger import get_logger
from src.utils.config import get_api_key
import re


# 设置日志
logger = get_logger("llm.qa_processor")


class QAProcessor:
    """
    Main QA processing pipeline
    """
    
    def __init__(self):
        logger.info("初始化问答处理器")
        
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
            logger.error(f"LLM模型初始化失败: {e}")
            raise
            
        # We'll need to pass the vector store instance or connect to a shared one
        # For now, we'll use a global reference or pass it as needed
        self.vector_store = None  # Will be set externally
        logger.debug("问答处理器初始化完成")
    
    def set_vector_store(self, vector_store: VectorStoreManager):
        """Set the vector store instance to use"""
        logger.info("设置向量存储实例")
        self.vector_store = vector_store
    
    def process_question(self, question: str) -> str:
        """
        Process a question through the complete pipeline
        """
        logger.info(f"开始处理问题: {question}")
        
        try:
            # Step 1: Question identification - check if it's a real question
            logger.debug("步骤1: 问题识别")
            is_question = self._is_real_question(question)
            logger.debug(f"问题识别结果: {'是问题' if is_question else '非问题'}")
            
            if not is_question:
                logger.info("识别为非问题，进入闲聊处理")
                return self._handle_chitchat(question)
            
            # Step 2: Intent recognition - check if it's a calculation question
            logger.debug("步骤2: 意图识别")
            is_calculation = self._is_calculation_question(question)
            logger.debug(f"计算问题识别结果: {'是计算问题' if is_calculation else '非计算问题'}")
            
            if is_calculation:
                logger.info("识别为计算问题，进入计算处理")
                # TODO 计算器用LLM来抽取计算式子, 然后调计算器来解决.
                return self._handle_calculation(question)
            
            # Step 3: Semantic retrieval (only if vector store is available)
            if self.vector_store:
                logger.debug("步骤3: 语义检索")
                retrieved_faqs = self._semantic_retrieval(question)
                logger.debug(f"检索到 {len(retrieved_faqs)} 个FAQ对")
                
                if not retrieved_faqs:
                    logger.info("未检索到相关内容")
                    return "「未找到相关内容」"
                
                # Step 4: Relevance filtering
                logger.debug("步骤4: 相关性过滤")
                relevant_faqs = self._filter_relevant_faqs(question, retrieved_faqs)
                logger.debug(f"过滤后保留 {len(relevant_faqs)} 个相关FAQ对")
                
                if not relevant_faqs:
                    logger.info("过滤后无相关内容")
                    return "「未找到相关内容」"
                
                # Step 5: Answer generation
                logger.debug("步骤5: 答案生成")
                answer = self._generate_answer(question, relevant_faqs)
                logger.info("答案生成完成")
                
                return answer
            else:
                logger.warning("向量存储未就绪")
                return "知识库尚未准备好，请先上传文档。"
                
        except Exception as e:
            logger.exception(f"处理问题时发生错误: {e}")
            return "抱歉，处理问题时出现了错误，请稍后重试。"
    
    def _is_real_question(self, question: str) -> bool:
        """
        Determine if the input is a real question
        """
        prompt = ChatPromptTemplate.from_template("""你是一个问题识别助手。请判断输入是否为提问句。

判断以下句子是否为提问句：

{question}

请回答：是 或 否""")
        chain = prompt | self.llm
        response = chain.invoke({"question": question})
        
        return "是" in response.content
    
    def _is_calculation_question(self, question: str) -> bool:
        """
        Determine if the question is a calculation problem
        """
        prompt = ChatPromptTemplate.from_template("""你是一个问题分类助手。请判断输入是否为数学计算问题。

判断以下问题是否为数学计算问题：

{question}

请回答：是 或 否""")
        chain = prompt | self.llm
        response = chain.invoke({"question": question})
        
        return "是" in response.content
    
    def _handle_chitchat(self, question: str) -> str:
        """
        Handle chitchat responses
        """
        prompt = ChatPromptTemplate.from_template("""你是一个友好的聊天助手。请以轻松友好的方式回应用户的非问题性话语。

请友好地回应：{question}""")
        chain = prompt | self.llm
        response = chain.invoke({"question": question})
        
        return response.content
    
    def _handle_calculation(self, question: str) -> str:
        """
        Handle calculation problems using a calculator tool
        """
        # Extract calculation from question
        # This is a simplified version - in practice, we'd use a proper calculator tool
        calc_pattern = r'([\d\+\-\*\/\(\)\.\s]+)'
        matches = re.findall(calc_pattern, question)
        
        if matches:
            for expr in matches:
                # Clean up the expression
                expr = re.sub(r'[^\d\+\-\*\/\(\)\.\s]', '', expr).strip()
                if expr and len(expr) > 2:  # Valid expression
                    try:
                        # Evaluate safely (in real implementation, use a safer eval or dedicated calculator)
                        result = eval(expr)
                        return f"计算结果是：{result}"
                    except:
                        pass  # Continue to next match
        
        # If evaluation fails, use LLM to handle
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个数学计算助手。请解决用户提出的数学问题。"),
            ("human", f"请计算：{question}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content
    
    def _semantic_retrieval(self, question: str) -> list:
        """
        Perform semantic retrieval from vector store
        """
        if self.vector_store:
            return self.vector_store.similarity_search(question, top_k=5)
        return []
    
    def _filter_relevant_faqs(self, question: str, faqs: list) -> list:
        """
        Filter FAQs based on relevance to the question
        """
        relevant_faqs = []
        
        for faq in faqs:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个相关性判断助手。请判断FAQ是否与用户问题相关。"),
                ("human", f"""
                用户问题：{question}
                
                FAQ问题：{faq.get('question', '')}
                
                请判断这个FAQ问题是否与用户问题相关。回答：是 或 否
                """)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({})
            
            if "是" in response.content:
                relevant_faqs.append(faq)
        
        return relevant_faqs
    
    def _generate_answer(self, question: str, faqs: list) -> str:
        """
        Generate final answer using retrieved FAQs
        """
        # Format the context from relevant FAQs
        context_parts = []
        for faq in faqs:
            context_parts.append(f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}")
        
        context = "\n\n".join(context_parts)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个问答助手。请根据提供的参考信息回答用户问题。如果参考信息不足，请说明无法回答。"),
            ("human", f"""
            参考信息：
            {context}
            
            用户问题：{question}
            
            请根据以上参考信息回答用户问题，回答要准确、完整、有条理。
            """)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content


if __name__ == "__main__":
    processor = QAProcessor()
    # Example usage would go here