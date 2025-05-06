import React, { useEffect, useState } from 'react';
import { Form, Button, Card, Container, Row, Col, Spinner, Alert } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';

function LessonPlanTab() {
  const [lessonPlan, setLessonPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/lesson-plan`)
      .then(res => res.json())
      .then(data => {
        setLessonPlan(data);
        setLoading(false);
      })
      .catch(e => {
        setError('Failed to load lesson plan');
        setLoading(false);
      });
  }, []);

  const handleChange = (key, value) => {
    setLessonPlan({ ...lessonPlan, [key]: value });
  };

  const handleSave = () => {
    setSaving(true);
    fetch(`${API_BASE}/api/lesson-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lessonPlan),
    })
      .then(res => res.json())
      .then(() => setSaving(false))
      .catch(() => {
        setError('Failed to save lesson plan');
        setSaving(false);
      });
  };

  const handleGenerate = () => {
    setGenerating(true);
    fetch(`${API_BASE}/api/generate-quiz`, {
      method: 'POST',
    })
      .then(res => res.json())
      .then((data) => {
        setGenerating(false);
        if (data.success) {
          alert('Quiz generated successfully!');
        } else {
          alert('Failed to generate quiz: ' + (data.error || 'Unknown error'));
        }
      })
      .catch((err) => {
        setGenerating(false);
        alert('Failed to generate quiz: ' + err);
      });
  };

  if (loading) return (
    <div className="d-flex justify-content-center my-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );
  
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!lessonPlan) return <Alert variant="warning">No lesson plan data.</Alert>;

  return (
    <Container>
      <Card className="shadow-sm">
        <Card.Header as="h5" className="bg-primary text-white">
          Lesson Plan
        </Card.Header>
        <Card.Body>
          <Form>
            {Object.keys(lessonPlan).map(key => (
              <Form.Group as={Row} key={key} className="mb-3">
                <Form.Label column sm={3} className="text-sm-end">
                  {key}:
                </Form.Label>
                <Col sm={9}>
                  <Form.Control
                    type="text"
                    value={lessonPlan[key]}
                    onChange={e => handleChange(key, e.target.value)}
                  />
                </Col>
              </Form.Group>
            ))}
          </Form>
          
          <div className="d-flex justify-content-end mt-4">
            <Button 
              variant="success" 
              onClick={handleSave} 
              disabled={saving}
              className="me-2"
            >
              {saving ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Saving...
                </>
              ) : 'Save'}
            </Button>
            <Button 
              variant="primary" 
              onClick={handleGenerate} 
              disabled={generating}
            >
              {generating ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Generating...
                </>
              ) : 'Generate Quiz'}
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default LessonPlanTab;
