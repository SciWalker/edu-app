"""
OCR Processor using pytesseract for text extraction from images.
"""

import os
import logging
from typing import Optional, Dict, Any
from PIL import Image
import pytesseract
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    try:
        import PyPDF2
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False


class OCRProcessor:
    """Handles OCR operations using pytesseract."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR processor.
        
        Args:
            tesseract_cmd: Path to tesseract executable if not in PATH
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, image_path: str, config: Optional[str] = None) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image file
            config: Optional tesseract config string
            
        Returns:
            Extracted text from the image
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: For OCR processing errors
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            if config:
                text = pytesseract.image_to_string(image, config=config)
            else:
                text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"OCR processing failed for {image_path}: {str(e)}")
            raise
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data from image including text and metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            image = Image.open(image_path)
            
            # Get basic image info
            metadata = {
                'filename': os.path.basename(image_path),
                'size': image.size,
                'format': image.format,
                'mode': image.mode
            }
            
            # Extract text
            text = self.extract_text(image_path)
            
            # Get bounding box data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            return {
                'text': text,
                'metadata': metadata,
                'ocr_data': data
            }
            
        except Exception as e:
            self.logger.error(f"Data extraction failed for {image_path}: {str(e)}")
            raise
    
    def preprocess_image(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to the input image
            output_path: Optional path for processed image
            
        Returns:
            Path to the processed image
        """
        try:
            image = Image.open(image_path)
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast if needed
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Save processed image
            if not output_path:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_processed{ext}"
            
            image.save(output_path)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
            
        Raises:
            Exception: If PDF processing fails or PDF support not available
        """
        if not PDF_SUPPORT:
            raise Exception("PDF support not available. Please install PyMuPDF (fitz) or PyPDF2")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            text = ""
            
            # Try PyMuPDF first (better text extraction)
            try:
                import fitz
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                return text.strip()
            except ImportError:
                pass
            
            # Fall back to PyPDF2
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text.strip()
            except ImportError:
                raise Exception("No PDF library available")
                
        except Exception as e:
            self.logger.error(f"PDF text extraction failed for {pdf_path}: {str(e)}")
            raise
    
    def extract_data_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF including text and metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Get basic PDF info
            metadata = {
                'filename': os.path.basename(pdf_path),
                'format': 'PDF',
                'type': 'document'
            }
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            return {
                'text': text,
                'metadata': metadata,
                'ocr_data': None  # No OCR data for PDFs, just text extraction
            }
            
        except Exception as e:
            self.logger.error(f"PDF data extraction failed for {pdf_path}: {str(e)}")
            raise