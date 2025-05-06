import React, { useState } from 'react';
import { Container, Button, Card, Row, Col, Spinner, Alert, Badge } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';

function GoogleClassroomTab() {
  const [classes, setClasses] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchClasses = () => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/api/google-classroom-classes`)
      .then(res => res.json())
      .then(data => {
        setClasses(data);
        setLoading(false);
      })
      .catch(e => {
        setError('Failed to load classes: ' + e.message);
        setLoading(false);
      });
  };

  return (
    <Container>
      <Card className="shadow-sm mb-4">
        <Card.Header as="h5" className="bg-primary text-white">
          Google Classroom Classes
        </Card.Header>
        <Card.Body className="text-center">
          <Button 
            variant="primary" 
            onClick={fetchClasses} 
            disabled={loading}
            className="px-4 py-2"
          >
            {loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                Loading...
              </>
            ) : 'List Classes'}
          </Button>
        </Card.Body>
      </Card>
      
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      {classes && Array.isArray(classes) && classes.length === 0 && (
        <Alert variant="info" className="text-center mb-4">
          No classes found. Make sure you have access to Google Classroom classes.
        </Alert>
      )}
      
      {classes && Array.isArray(classes) && classes.length > 0 && (
        <div>
          <h3 className="mb-3">Your Classes ({classes.length})</h3>
          <Row xs={1} md={2} className="g-4">
            {classes.map(cls => (
              <Col key={cls.id}>
                <Card className="h-100 shadow-sm">
                  <Card.Body>
                    <Card.Title className="text-primary">{cls.name}</Card.Title>
                    {cls.description && (
                      <Card.Text className="text-muted">
                        {cls.description}
                      </Card.Text>
                    )}
                    <div className="d-flex justify-content-between align-items-center mt-3">
                      <Badge bg={cls.courseState === 'ACTIVE' ? 'success' : 'secondary'}>
                        {cls.courseState || 'Unknown Status'}
                      </Badge>
                      {cls.link && (
                        <Button 
                          variant="outline-primary" 
                          size="sm" 
                          href={cls.link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          Open in Classroom
                        </Button>
                      )}
                    </div>
                  </Card.Body>
                  <Card.Footer className="text-muted small">
                    ID: {cls.id}
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </Container>
  );
}

export default GoogleClassroomTab;
