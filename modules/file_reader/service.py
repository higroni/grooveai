"""
File Reader Service - Core business logic
Reads PDF, DOCX, and TXT files
"""
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
import PyPDF2
import docx


class FileReaderService:
    """
    Service for reading various file formats
    """
    
    SUPPORTED_FORMATS = ["pdf", "docx", "txt"]
    
    def __init__(self):
        """Initialize the file reader service"""
        pass
    
    def read_file(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Read a file and extract text
        
        Args:
            file_path: Path to the file
            file_type: File type (pdf, docx, txt). If None, will be inferred from extension
            
        Returns:
            Dictionary with text, encoding, char_count, page_count, processing_time_ms
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        start_time = time.time()
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Infer file type if not provided
        if file_type is None:
            file_type = Path(file_path).suffix.lower().lstrip('.')
        
        # Validate file type
        if file_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file type: {file_type}. Supported: {self.SUPPORTED_FORMATS}")
        
        # Read based on file type
        if file_type == "pdf":
            result = self._read_pdf(file_path)
        elif file_type == "docx":
            result = self._read_docx(file_path)
        elif file_type == "txt":
            result = self._read_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        result["processing_time_ms"] = processing_time_ms
        
        return result
    
    def _read_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Read PDF file using PyPDF2
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with text, encoding, char_count, page_count
        """
        text_parts = []
        page_count = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            
            return {
                "text": full_text,
                "encoding": "utf-8",
                "char_count": len(full_text),
                "page_count": page_count
            }
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {str(e)}")
    
    def _read_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Read DOCX file using python-docx
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Dictionary with text, encoding, char_count, page_count
        """
        try:
            doc = docx.Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = "\n".join(text_parts)
            
            # DOCX doesn't have explicit page count, estimate based on content
            estimated_pages = max(1, len(full_text) // 3000)
            
            return {
                "text": full_text,
                "encoding": "utf-8",
                "char_count": len(full_text),
                "page_count": estimated_pages
            }
        except Exception as e:
            raise RuntimeError(f"Error reading DOCX: {str(e)}")
    
    def _read_txt(self, file_path: str) -> Dict[str, Any]:
        """
        Read TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Dictionary with text, encoding, char_count, page_count
        """
        try:
            # Try UTF-8 first, then fallback to other encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
            text = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise RuntimeError("Could not decode file with any supported encoding")
            
            # Estimate pages (assuming ~3000 chars per page)
            estimated_pages = max(1, len(text) // 3000)
            
            return {
                "text": text,
                "encoding": used_encoding,
                "char_count": len(text),
                "page_count": estimated_pages
            }
        except Exception as e:
            raise RuntimeError(f"Error reading TXT: {str(e)}")

# Made with Bob
