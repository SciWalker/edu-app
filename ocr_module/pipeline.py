"""
OCR Pipeline that combines image processing and data extraction.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .ocr_processor import OCRProcessor
from .data_extractor import DataExtractor


class OCRPipeline:
    """Complete OCR pipeline for processing images and extracting structured data."""
    
    def __init__(self, config_path: str = "config.yml", tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR pipeline.
        
        Args:
            config_path: Path to configuration file
            tesseract_cmd: Optional path to tesseract executable
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            self.ocr_processor = OCRProcessor(tesseract_cmd=tesseract_cmd)
            self.data_extractor = DataExtractor(config_path=config_path)
        except Exception as e:
            self.logger.error(f"Failed to initialize OCR pipeline: {str(e)}")
            raise
    
    def process_image(
        self, 
        image_path: str, 
        extraction_type: str = "general",
        preprocess: bool = False
    ) -> Dict[str, Any]:
        """
        Process an image through the complete OCR pipeline.
        
        Args:
            image_path: Path to the image file
            extraction_type: Type of data extraction to perform
            preprocess: Whether to preprocess the image for better OCR
            
        Returns:
            Dictionary containing OCR results and extracted structured data
        """
        try:
            # Validate image path
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Preprocess image if requested
            processed_image_path = image_path
            if preprocess:
                self.logger.info(f"Preprocessing image: {image_path}")
                processed_image_path = self.ocr_processor.preprocess_image(image_path)
            
            # Extract text using OCR
            self.logger.info(f"Extracting text from: {processed_image_path}")
            ocr_result = self.ocr_processor.extract_data(processed_image_path)
            
            # Extract structured data using Gemini
            self.logger.info(f"Extracting structured data using type: {extraction_type}")
            extracted_data = self.data_extractor.extract_data(
                text=ocr_result["text"],
                extraction_type=extraction_type
            )
            
            # Combine results
            result = {
                "image_path": image_path,
                "preprocessed": preprocess,
                "processed_image_path": processed_image_path if preprocess else None,
                "ocr_result": ocr_result,
                "extracted_data": extracted_data,
                "pipeline_status": "success"
            }
            
            self.logger.info(f"Pipeline processing completed for: {image_path}")
            return result
            
        except Exception as e:
            error_msg = f"Pipeline processing failed for {image_path}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "image_path": image_path,
                "preprocessed": preprocess,
                "processed_image_path": None,
                "ocr_result": {},
                "extracted_data": {"errors": [error_msg]},
                "pipeline_status": "failed",
                "error": str(e)
            }
    
    def process_batch(
        self, 
        image_paths: List[str], 
        extraction_type: str = "general",
        preprocess: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images through the OCR pipeline.
        
        Args:
            image_paths: List of paths to image files
            extraction_type: Type of data extraction to perform
            preprocess: Whether to preprocess images for better OCR
            
        Returns:
            List of dictionaries containing results for each image
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            self.logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
            
            try:
                result = self.process_image(
                    image_path=image_path,
                    extraction_type=extraction_type,
                    preprocess=preprocess
                )
                results.append(result)
                
            except Exception as e:
                error_result = {
                    "image_path": image_path,
                    "pipeline_status": "failed",
                    "error": str(e)
                }
                results.append(error_result)
                self.logger.error(f"Failed to process {image_path}: {str(e)}")
        
        return results
    
    def get_supported_extraction_types(self) -> List[str]:
        """Get list of supported extraction types."""
        return ["general", "educational_content", "form_data", "student_work"]
    
    def validate_image(self, image_path: str) -> Dict[str, Any]:
        """
        Validate an image file before processing.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            path = Path(image_path)
            
            # Check if file exists
            if not path.exists():
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # Check file extension
            supported_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}
            if path.suffix.lower() not in supported_extensions:
                validation_result["warnings"].append(
                    f"File extension {path.suffix} may not be supported"
                )
            
            # Check file size (warn if very large)
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > 10:
                validation_result["warnings"].append(
                    f"Large file size: {file_size_mb:.1f}MB may slow processing"
                )
            
            # Try to open with PIL
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    validation_result["image_info"] = {
                        "size": img.size,
                        "mode": img.mode,
                        "format": img.format
                    }
            except Exception as e:
                validation_result["errors"].append(f"Cannot open image: {str(e)}")
                return validation_result
            
            validation_result["valid"] = True
            
        except Exception as e:
            validation_result["errors"].append(f"Validation failed: {str(e)}")
        
        return validation_result