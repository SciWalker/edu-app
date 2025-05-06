import React, { useEffect, useState } from 'react';
import { Container, Form, Button, Card, Row, Col, Spinner, Alert, Badge } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';

function QuizTab({ isActive }) {
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [lastFetchTime, setLastFetchTime] = useState(null);

  const fetchQuizData = () => {
    setLoading(true);
    setError(null);
    
    fetch(`${API_BASE}/api/quiz?t=${new Date().getTime()}`) // Add cache-busting parameter
      .then(res => res.json())
      .then(data => {
        setQuiz(data);
        setLoading(false);
        setLastFetchTime(new Date());
      })
      .catch(e => {
        setError('Failed to load quiz');
        setLoading(false);
      });
  };

  // Initial fetch on component mount
  useEffect(() => {
    fetchQuizData();
  }, []);

  // Refetch when tab becomes active
  useEffect(() => {
    if (isActive) {
      fetchQuizData();
    }
  }, [isActive]);

  const handleTitleChange = (value) => {
    setQuiz({ ...quiz, title: value });
  };

  const handleQuestionChange = (index, field, value) => {
    const updatedQuestions = [...quiz.questions];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setQuiz({ ...quiz, questions: updatedQuestions });
  };

  const handleOptionChange = (questionIndex, optionIndex, value) => {
    const updatedQuestions = [...quiz.questions];
    const updatedOptions = [...updatedQuestions[questionIndex].options];
    updatedOptions[optionIndex] = value;
    updatedQuestions[questionIndex] = { 
      ...updatedQuestions[questionIndex], 
      options: updatedOptions 
    };
    setQuiz({ ...quiz, questions: updatedQuestions });
  };

  const handleAnswerChange = (questionIndex, value) => {
    const updatedQuestions = [...quiz.questions];
    updatedQuestions[questionIndex] = { 
      ...updatedQuestions[questionIndex], 
      answer: value 
    };
    setQuiz({ ...quiz, questions: updatedQuestions });
  };

  const handleSave = () => {
    setSaving(true);
    fetch(`${API_BASE}/api/quiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(quiz),
    })
      .then(res => res.json())
      .then(() => setSaving(false))
      .catch(() => {
        setError('Failed to save quiz');
        setSaving(false);
      });
  };

  const handleRefresh = () => {
    fetchQuizData();
  };

  if (loading) return (
    <div className="d-flex justify-content-center my-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );
  
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!quiz) return <Alert variant="warning">No quiz data.</Alert>;

  return (
    <Container>
      <Card className="shadow-sm mb-4">
        <Card.Header as="h5" className="bg-primary text-white d-flex justify-content-between align-items-center">
          <span>Quiz Editor</span>
          <Button 
            variant="outline-light" 
            size="sm" 
            onClick={handleRefresh}
            title="Refresh quiz data"
          >
            <i className="bi bi-arrow-clockwise"></i> Refresh
          </Button>
        </Card.Header>
        <Card.Body>
          {lastFetchTime && (
            <Alert variant="info" className="mb-3 py-2">
              <small>Last updated: {lastFetchTime.toLocaleTimeString()}</small>
            </Alert>
          )}
          
          <Form>
            <Form.Group as={Row} className="mb-3">
              <Form.Label column sm={2} className="fw-bold">Title:</Form.Label>
              <Col sm={10}>
                <Form.Control
                  type="text"
                  value={quiz.title}
                  onChange={e => handleTitleChange(e.target.value)}
                />
              </Col>
            </Form.Group>
          </Form>
          
          <h4 className="mt-4 mb-3">Questions:</h4>
          {quiz.questions && quiz.questions.map((question, qIndex) => (
            <Card key={qIndex} className="mb-4 shadow-sm">
              <Card.Header className="bg-light">
                <Badge bg="secondary" className="me-2">#{qIndex + 1}</Badge>
                <span className="fw-bold">Question {qIndex + 1}</span>
              </Card.Header>
              <Card.Body>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold">Question text:</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    value={question.question}
                    onChange={e => handleQuestionChange(qIndex, 'question', e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold">Options:</Form.Label>
                  {question.options && question.options.map((option, oIndex) => (
                    <Row key={oIndex} className="mb-2 align-items-center">
                      <Col xs={9}>
                        <Form.Control
                          type="text"
                          value={option}
                          onChange={e => handleOptionChange(qIndex, oIndex, e.target.value)}
                        />
                      </Col>
                      <Col xs={3}>
                        <Form.Check
                          type="radio"
                          id={`correct-${qIndex}-${oIndex}`}
                          name={`correct-${qIndex}`}
                          label="Correct"
                          checked={option === question.answer}
                          onChange={() => handleAnswerChange(qIndex, option)}
                        />
                      </Col>
                    </Row>
                  ))}
                </Form.Group>
                
                <Form.Group as={Row} className="mb-0">
                  <Form.Label column sm={2} className="fw-bold">Type:</Form.Label>
                  <Col sm={10}>
                    <Form.Control
                      type="text"
                      value={question.type}
                      onChange={e => handleQuestionChange(qIndex, 'type', e.target.value)}
                      disabled
                      plaintext
                      readOnly
                    />
                  </Col>
                </Form.Group>
              </Card.Body>
            </Card>
          ))}
          
          <div className="d-flex justify-content-end mt-4">
            <Button 
              variant="success" 
              onClick={handleSave} 
              disabled={saving}
              size="lg"
            >
              {saving ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Saving...
                </>
              ) : 'Save Quiz'}
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default QuizTab;
