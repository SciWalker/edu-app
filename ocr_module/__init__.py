"""
OCR Module for educational application.
Provides image text extraction and data processing capabilities.
"""

from .ocr_processor import OCRProcessor
from .data_extractor import DataExtractor
from .pipeline import OCRPipeline

__all__ = ['OCRProcessor', 'DataExtractor', 'OCRPipeline']