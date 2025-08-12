"""
Example usage of the OCR module.
"""

import logging
from pathlib import Path
from pipeline import OCRPipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Demonstrate OCR module usage."""
    
    # Initialize the pipeline
    try:
        pipeline = OCRPipeline(config_path="../config.yml")
        logger.info("OCR Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return
    
    # Example image path (replace with actual image path)
    image_path = "sample_image.jpg"
    
    # Check if image exists
    if not Path(image_path).exists():
        logger.warning(f"Sample image not found: {image_path}")
        logger.info("Please provide a valid image path to test the OCR pipeline")
        return
    
    # Validate image before processing
    validation = pipeline.validate_image(image_path)
    if not validation["valid"]:
        logger.error(f"Image validation failed: {validation['errors']}")
        return
    
    if validation["warnings"]:
        logger.warning(f"Image warnings: {validation['warnings']}")
    
    # Process single image with different extraction types
    extraction_types = pipeline.get_supported_extraction_types()
    
    for extraction_type in extraction_types:
        logger.info(f"Processing with extraction type: {extraction_type}")
        
        result = pipeline.process_image(
            image_path=image_path,
            extraction_type=extraction_type,
            preprocess=True  # Use preprocessing for better results
        )
        
        if result["pipeline_status"] == "success":
            logger.info(f"✓ Processing successful for {extraction_type}")
            logger.info(f"  Confidence: {result['extracted_data']['confidence_score']}")
            logger.info(f"  Text length: {result['extracted_data']['raw_text_length']}")
            
            # Display structured data
            structured_data = result['extracted_data']['structured_data']
            if structured_data:
                logger.info(f"  Structured data keys: {list(structured_data.keys())}")
            
        else:
            logger.error(f"✗ Processing failed for {extraction_type}: {result.get('error', 'Unknown error')}")
        
        print("-" * 50)
    
    # Example batch processing
    image_paths = [image_path]  # Add more image paths as needed
    
    logger.info("Testing batch processing...")
    batch_results = pipeline.process_batch(
        image_paths=image_paths,
        extraction_type="educational_content",
        preprocess=True
    )
    
    for i, result in enumerate(batch_results):
        if result["pipeline_status"] == "success":
            logger.info(f"Batch item {i+1}: Success")
        else:
            logger.error(f"Batch item {i+1}: Failed - {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()