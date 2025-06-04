import React, { useState } from 'react';
import { Container, Nav, Navbar, Tab, Row, Col } from 'react-bootstrap';
import LessonPlanTab from './LessonPlanTab';
import QuizTab from './QuizTab';
import GoogleClassroomTab from './GoogleClassroomTab';
import DatabaseTab from './DatabaseTab';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('lesson');

  return (
    <div className="App">
      <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand href="#home">Milesridge Educational App</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
        </Container>
      </Navbar>
      
      <Container>
        <Row className="mb-4">
          <Col>
            <h1 className="text-center">Edu App Dashboard</h1>
          </Col>
        </Row>
        
        <Row>
          <Col>
            <Nav variant="tabs" className="mb-3">
              <Nav.Item>
                <Nav.Link 
                  active={activeTab === 'lesson'} 
                  onClick={() => setActiveTab('lesson')}
                >
                  Lesson Plan
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link 
                  active={activeTab === 'quiz'} 
                  onClick={() => setActiveTab('quiz')}
                >
                  Quiz
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link 
                  active={activeTab === 'classroom'} 
                  onClick={() => setActiveTab('classroom')}
                >
                  Google Classroom
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link 
                  active={activeTab === 'database'} 
                  onClick={() => setActiveTab('database')}
                >
                  Database
                </Nav.Link>
              </Nav.Item>
            </Nav>
            
            <Tab.Content>
              <Tab.Pane active={activeTab === 'lesson'}>
                <LessonPlanTab isActive={activeTab === 'lesson'} />
              </Tab.Pane>
              <Tab.Pane active={activeTab === 'quiz'}>
                <QuizTab isActive={activeTab === 'quiz'} />
              </Tab.Pane>
              <Tab.Pane active={activeTab === 'classroom'}>
                <GoogleClassroomTab isActive={activeTab === 'classroom'} />
              </Tab.Pane>
              <Tab.Pane active={activeTab === 'database'}>
                <DatabaseTab isActive={activeTab === 'database'} />
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
