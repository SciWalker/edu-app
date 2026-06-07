import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Container, Row, Col, Spinner, Alert, ProgressBar } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';

function LessonPlanTab() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [aiProvider, setAiProvider] = useState('gemini');

  // Load Google Classroom courses on component mount
  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/google-classroom-classes`);
      const data = await response.json();
      setCourses(data);
      if (data.length > 0) {
        setSelectedCourse(data[0].id); // Auto-select first course
      }
    } catch (err) {
      setError('Failed to load Google Classroom courses');
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setSuccess(null);
      setOcrResult(null);
      
      // Create preview for image files
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(file);
      } else {
        setPreview(null);
      }
    }
  };

  const processImage = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setProcessing(true);
    setError(null);
    setSuccess(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('extractionType', 'educational_content');
      formData.append('aiProvider', aiProvider);

      const response = await fetch(`${API_BASE}/api/ocr/process-upload`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (result.pipeline_status === 'success') {
        setOcrResult(result);
        setSuccess('✅ File processed successfully! Review the extracted content below.');
      } else {
        setError(`OCR processing failed: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      setError(`Processing failed: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const uploadToClassroom = async () => {
    if (!ocrResult || !selectedCourse) {
      setError('Please process a file and select a course first');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE}/api/classroom/upload-material`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          courseId: selectedCourse,
          materialData: ocrResult.extracted_data
        })
      });

      const result = await response.json();

      if (result.success) {
        setSuccess(`🎉 Successfully uploaded to Google Classroom! Assignment: "${result.title}"`);
        
        // Clear the form after successful upload
        setTimeout(() => {
          setSelectedFile(null);
          setPreview(null);
          setOcrResult(null);
        }, 3000);
      } else {
        setError(`Upload failed: ${result.error}`);
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container>
      <Card className="shadow-sm mb-4">
        <Card.Header as="h5" className="bg-primary text-white">
          📚 Lesson Plan Creator - Upload & Process Files
        </Card.Header>
        <Card.Body>
          {/* File Upload Section */}
          <Row className="mb-4">
            <Col md={6}>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>1. Upload File</strong>
                </Card.Header>
                <Card.Body>
                  <Form.Group className="mb-3">
                    <Form.Label>Select educational content file:</Form.Label>
                    <Form.Control
                      type="file"
                      accept="image/*,.pdf"
                      onChange={handleFileSelect}
                      className="mb-2"
                    />
                    <Form.Text className="text-muted">
                      Supported formats: JPG, PNG, GIF, WebP, PDF
                    </Form.Text>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>AI Provider for Text Analysis:</Form.Label>
                    <Form.Select
                      value={aiProvider}
                      onChange={(e) => setAiProvider(e.target.value)}
                    >
                      <option value="gemini">🤖 Google Gemini</option>
                      <option value="claude">🧠 Anthropic Claude</option>
                    </Form.Select>
                    <Form.Text className="text-muted">
                      Choose the AI model for analyzing extracted content
                    </Form.Text>
                  </Form.Group>

                  {selectedFile && (
                    <Alert variant="info">
                      <strong>Selected:</strong> {selectedFile.name} 
                      <br />
                      <small>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</small>
                    </Alert>
                  )}

                  <Button
                    variant="success"
                    onClick={processImage}
                    disabled={!selectedFile || processing}
                    className="w-100"
                  >
                    {processing ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                        Processing File...
                      </>
                    ) : (
                      '🔍 Extract Content'
                    )}
                  </Button>
                </Card.Body>
              </Card>
            </Col>

            <Col md={6}>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>File Preview</strong>
                </Card.Header>
                <Card.Body className="text-center">
                  {selectedFile ? (
                    selectedFile.type === 'application/pdf' ? (
                      <div className="text-muted py-5">
                        <i className="bi bi-file-earmark-pdf" style={{ fontSize: '3rem', color: '#dc3545' }}></i>
                        <p className="mt-2">{selectedFile.name}</p>
                        <small>PDF file selected - ready for text extraction</small>
                      </div>
                    ) : preview ? (
                      <img 
                        src={preview} 
                        alt="Preview" 
                        style={{ 
                          maxWidth: '100%', 
                          maxHeight: '300px', 
                          objectFit: 'contain',
                          border: '1px solid #ddd',
                          borderRadius: '4px'
                        }} 
                      />
                    ) : (
                      <div className="text-muted py-5">
                        <i className="bi bi-file-earmark" style={{ fontSize: '3rem' }}></i>
                        <p className="mt-2">{selectedFile.name}</p>
                      </div>
                    )
                  ) : (
                    <div className="text-muted py-5">
                      <i className="bi bi-file-earmark" style={{ fontSize: '3rem' }}></i>
                      <p>No file selected</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Processing Progress */}
          {processing && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Body>
                    <div className="text-center mb-3">
                      <Spinner animation="border" variant="primary" />
                      <p className="mt-2 mb-0">Processing file with text extraction and AI analysis...</p>
                    </div>
                    <ProgressBar animated now={100} />
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* OCR Results Section */}
          {ocrResult && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header className="bg-success text-white">
                    <strong>2. Extracted Content</strong>
                  </Card.Header>
                  <Card.Body>
                    {/* Lesson Plan Header */}
                    <Row className="mb-4">
                      <Col>
                        <div className="text-center">
                          <h4 className="mb-1">{ocrResult.extracted_data.structured_data.title || 'Lesson Plan'}</h4>
                          <p className="text-muted mb-2">
                            <strong>{ocrResult.extracted_data.structured_data.subject || 'N/A'}</strong> | 
                            <span className="ms-1">{ocrResult.extracted_data.structured_data.grade_level || 'N/A'}</span> | 
                            <span className="ms-1">Duration: {ocrResult.extracted_data.structured_data.duration || 'N/A'}</span>
                          </p>
                          <small className="text-success">
                            Confidence: {(ocrResult.extracted_data.confidence_score * 100).toFixed(1)}% | 
                            Difficulty: {ocrResult.extracted_data.structured_data.difficulty_level || 'N/A'}
                          </small>
                        </div>
                      </Col>
                    </Row>

                    {/* Learning Objectives */}
                    <Row className="mb-3">
                      <Col md={6}>
                        <h6>🎯 Learning Objectives</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.learning_objectives?.map((obj, idx) => (
                            <li key={idx}>{obj}</li>
                          )) || <li>No objectives specified</li>}
                        </ul>
                      </Col>
                      
                      <Col md={6}>
                        <h6>📚 Key Topics</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.key_topics?.map((topic, idx) => (
                            <li key={idx}>{topic}</li>
                          )) || <li>No topics specified</li>}
                        </ul>
                      </Col>
                    </Row>

                    {/* Lesson Structure */}
                    {ocrResult.extracted_data.structured_data.lesson_structure && (
                      <Row className="mb-3">
                        <Col>
                          <h6>🏗️ Lesson Structure</h6>
                          <div className="small">
                            <div className="mb-2">
                              <strong>Introduction:</strong> {ocrResult.extracted_data.structured_data.lesson_structure.introduction}
                            </div>
                            <div className="mb-2">
                              <strong>Main Activities:</strong>
                              <ul className="mt-1">
                                {ocrResult.extracted_data.structured_data.lesson_structure.main_activities?.map((activity, idx) => (
                                  <li key={idx}>{activity}</li>
                                )) || <li>No activities specified</li>}
                              </ul>
                            </div>
                            <div className="mb-2">
                              <strong>Assessment:</strong> {ocrResult.extracted_data.structured_data.lesson_structure.assessment}
                            </div>
                            <div className="mb-2">
                              <strong>Conclusion:</strong> {ocrResult.extracted_data.structured_data.lesson_structure.conclusion}
                            </div>
                          </div>
                        </Col>
                      </Row>
                    )}

                    {/* Materials and Resources */}
                    <Row className="mb-3">
                      <Col md={6}>
                        <h6>📦 Materials Needed</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.materials_needed?.map((material, idx) => (
                            <li key={idx}>{material}</li>
                          )) || <li>No materials specified</li>}
                        </ul>
                      </Col>
                      
                      <Col md={6}>
                        <h6>📖 Vocabulary</h6>
                        <div className="small">
                          {ocrResult.extracted_data.structured_data.vocabulary?.join(', ') || 'No vocabulary specified'}
                        </div>
                      </Col>
                    </Row>

                    {/* Assessment and Differentiation */}
                    <Row className="mb-3">
                      <Col md={6}>
                        <h6>✅ Assessment Criteria</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.assessment_criteria?.map((criteria, idx) => (
                            <li key={idx}>{criteria}</li>
                          )) || <li>No criteria specified</li>}
                        </ul>
                      </Col>
                      
                      <Col md={6}>
                        <h6>🔄 Differentiation</h6>
                        <div className="small">
                          {ocrResult.extracted_data.structured_data.differentiation || 'No differentiation specified'}
                        </div>
                      </Col>
                    </Row>

                    {/* Homework and Extensions */}
                    <Row>
                      <Col md={6}>
                        <h6>📝 Homework Assignments</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.homework_assignments?.map((hw, idx) => (
                            <li key={idx}>{hw}</li>
                          )) || <li>No homework specified</li>}
                        </ul>
                      </Col>
                      
                      <Col md={6}>
                        <h6>🚀 Extension Activities</h6>
                        <ul className="small">
                          {ocrResult.extracted_data.structured_data.extension_activities?.map((ext, idx) => (
                            <li key={idx}>{ext}</li>
                          )) || <li>No extensions specified</li>}
                        </ul>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* Google Classroom Upload Section */}
          {ocrResult && (
            <Row>
              <Col>
                <Card>
                  <Card.Header className="bg-warning">
                    <strong>3. Upload to Google Classroom</strong>
                  </Card.Header>
                  <Card.Body>
                    <Form.Group className="mb-3">
                      <Form.Label>Select Course:</Form.Label>
                      <Form.Select
                        value={selectedCourse}
                        onChange={(e) => setSelectedCourse(e.target.value)}
                      >
                        {courses.map(course => (
                          <option key={course.id} value={course.id}>
                            {course.name} {course.section && `(${course.section})`}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>

                    <Button
                      variant="primary"
                      onClick={uploadToClassroom}
                      disabled={!selectedCourse || uploading}
                      className="w-100"
                      size="lg"
                    >
                      {uploading ? (
                        <>
                          <Spinner as="span" animation="border" size="sm" className="me-2" />
                          Uploading to Classroom...
                        </>
                      ) : (
                        '🚀 Create Lesson in Google Classroom'
                      )}
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* Status Messages */}
          {error && (
            <Alert variant="danger" className="mt-3">
              <strong>Error:</strong> {error}
            </Alert>
          )}

          {success && (
            <Alert variant="success" className="mt-3">
              {success}
            </Alert>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}

export default LessonPlanTab;