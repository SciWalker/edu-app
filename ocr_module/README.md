# OCR Module

A comprehensive OCR (Optical Character Recognition) module for the edu-app that combines image text extraction with AI-powered data processing.

## Features

- **Text Extraction**: Uses pytesseract for robust OCR text extraction from images
- **Image Preprocessing**: Automatic image enhancement for better OCR results
- **AI Data Extraction**: Leverages Gemini LLM with LangGraph for intelligent structured data extraction
- **Multiple Extraction Types**: Supports different extraction modes for various document types
- **Batch Processing**: Process multiple images efficiently
- **Validation**: Built-in image validation and quality checks

## Installation

Install the required dependencies:

```bash
pip install pytesseract Pillow
```

Note: You'll also need to install tesseract on your system:
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Quick Start

```python
from ocr_module import OCRPipeline

# Initialize the pipeline
pipeline = OCRPipeline(config_path="../config.yml")

# Process a single image
result = pipeline.process_image(
    image_path="document.jpg",
    extraction_type="educational_content",
    preprocess=True
)

# Check results
if result["pipeline_status"] == "success":
    extracted_data = result["extracted_data"]["structured_data"]
    confidence = result["extracted_data"]["confidence_score"]
    print(f"Extraction successful! Confidence: {confidence}")
    print(f"Structured data: {extracted_data}")
```

## Extraction Types

The module supports different extraction types optimized for various document types:

1. **`educational_content`** - For worksheets, quizzes, assignments, and educational materials
2. **`form_data`** - For forms, surveys, and structured documents
3. **`student_work`** - For student assignments and graded work
4. **`general`** - For general-purpose text extraction

## API Reference

### OCRPipeline

Main class that orchestrates the complete OCR and data extraction workflow.

#### Methods

- `process_image(image_path, extraction_type="general", preprocess=False)` - Process a single image
- `process_batch(image_paths, extraction_type="general", preprocess=False)` - Process multiple images
- `validate_image(image_path)` - Validate an image before processing
- `get_supported_extraction_types()` - Get list of supported extraction types

### OCRProcessor

Handles OCR operations using pytesseract.

#### Methods

- `extract_text(image_path, config=None)` - Extract plain text from image
- `extract_data(image_path)` - Extract text with metadata and bounding boxes
- `preprocess_image(image_path, output_path=None)` - Enhance image for better OCR

### DataExtractor

Handles AI-powered data extraction using Gemini LLM with LangGraph.

#### Methods

- `extract_data(text, extraction_type="general")` - Extract structured data from text

## Configuration

The module uses the main application's `config.yml` file. Ensure you have:

```yaml
google_ai_studio_api_key: "your-gemini-api-key"
```

## Example Output

```python
{
    "image_path": "worksheet.jpg",
    "pipeline_status": "success",
    "ocr_result": {
        "text": "Math Quiz\n1. What is 2+2?\nA) 3 B) 4 C) 5",
        "metadata": {...}
    },
    "extracted_data": {
        "structured_data": {
            "title": "Math Quiz",
            "subject": "Mathematics",
            "questions": ["What is 2+2?"],
            "content_type": "quiz",
            ...
        },
        "confidence_score": 0.85,
        "extraction_type": "educational_content"
    }
}
```

## Error Handling

The module includes comprehensive error handling:
- Image validation before processing
- OCR failure recovery
- API error handling for Gemini
- Detailed error reporting in results

## Supported Image Formats

- PNG
- JPEG/JPG  
- TIFF
- BMP
- GIF

## Performance Tips

1. **Preprocessing**: Enable preprocessing for low-quality or scanned images
2. **Image Quality**: Higher resolution images generally produce better results
3. **File Size**: Very large images may slow processing - consider resizing
4. **Batch Processing**: Use batch processing for multiple files to optimize API usage