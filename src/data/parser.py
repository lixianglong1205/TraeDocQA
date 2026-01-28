from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pathlib import Path
import chardet


class DocumentParser:
    """
    Document parser class that handles PDF and TXT file parsing using LangChain
    """
    
    def parse_pdf(self, file_path: str) -> str:
        """
        Parse PDF file and extract text content using LangChain
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            # Combine all pages' text
            text_content = " ".join([doc.page_content for doc in documents])
            return text_content
        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")
    
    def parse_txt(self, file_path: str) -> str:
        """
        Parse TXT file with encoding detection using LangChain
        """
        try:
            # First, detect encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding_result = chardet.detect(raw_data)
                detected_encoding = encoding_result['encoding']
            
            # Try to load with detected encoding, fallback to common encodings
            encodings_to_try = [detected_encoding, 'utf-8', 'gbk', 'latin-1']
            
            for encoding in encodings_to_try:
                if encoding is None:
                    continue
                try:
                    loader = TextLoader(file_path, encoding=encoding)
                    documents = loader.load()
                    return " ".join([doc.page_content for doc in documents])
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with error handling
            loader = TextLoader(file_path, encoding='utf-8', errors='replace')
            documents = loader.load()
            return " ".join([doc.page_content for doc in documents])
                
        except Exception as e:
            raise Exception(f"TXT parsing failed: {str(e)}")


if __name__ == "__main__":
    parser = DocumentParser()
    # Example usage would go here