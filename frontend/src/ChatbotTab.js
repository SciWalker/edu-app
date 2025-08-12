import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, Badge } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';

function ChatbotTab({ isActive }) {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationSummary, setConversationSummary] = useState(null);
  const [currentChatbot, setCurrentChatbot] = useState('langgraph_gemini');
  const [availableChatbots, setAvailableChatbots] = useState(['langgraph_gemini']);
  const [switchingChatbot, setSwitchingChatbot] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat when tab becomes active
  useEffect(() => {
    if (isActive) {
      fetchChatbotStatus();
      if (messages.length === 0) {
        // Add welcome message
        setMessages([{
          role: 'assistant',
          content: 'Hello! I\'m your educational AI assistant with access to your Google Classroom data. I can help you with:\n\n• Creating lesson plans for your specific courses\n• Generating quiz questions tailored to your classes\n• Teaching strategies for your students\n• Course-specific educational guidance\n• Managing your Google Classroom assignments\n\nI can see your current courses and provide personalized advice. What would you like to discuss today?',
          timestamp: Date.now()
        }]);
      }
    }
  }, [isActive]);

  const fetchChatbotStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/chatbot/status`);
      const status = await response.json();
      
      if (status.current_chatbot) {
        setCurrentChatbot(status.current_chatbot);
      }
      if (status.available_chatbots) {
        setAvailableChatbots(status.available_chatbots);
      }
    } catch (err) {
      console.error('Failed to fetch chatbot status:', err);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: Date.now()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/chatbot/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: currentMessage,
          user_id: 'frontend_user',
          chatbot_type: currentChatbot
        })
      });

      const result = await response.json();

      if (result.success) {
        const aiMessage = {
          role: 'assistant',
          content: result.response,
          timestamp: result.timestamp * 1000 // Convert to milliseconds
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        setError(result.error || 'Failed to get response from chatbot');
      }
    } catch (err) {
      setError('Failed to communicate with the chatbot. Please check your connection.');
      console.error('Chatbot error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = async () => {
    try {
      await fetch(`${API_BASE}/api/chatbot/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chatbot_type: currentChatbot
        })
      });
      
      setMessages([{
        role: 'assistant',
        content: 'Conversation cleared! How can I help you today?',
        timestamp: Date.now()
      }]);
      setError(null);
    } catch (err) {
      setError('Failed to clear conversation');
    }
  };

  const switchChatbot = async (newChatbot) => {
    if (newChatbot === currentChatbot) return;
    
    setSwitchingChatbot(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/chatbot/switch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chatbot_type: newChatbot
        })
      });

      const result = await response.json();

      if (result.success) {
        setCurrentChatbot(newChatbot);
        
        // Add system message about the switch
        setMessages(prev => [...prev, {
          role: 'system',
          content: `Switched to ${getChatbotDisplayName(newChatbot)}. Previous conversation history is preserved.`,
          timestamp: Date.now()
        }]);
      } else {
        setError(result.error || 'Failed to switch chatbot');
      }
    } catch (err) {
      setError('Failed to switch chatbot');
    } finally {
      setSwitchingChatbot(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getChatbotDisplayName = (chatbot) => {
    const names = {
      'gemini': 'Gemini 1.5 Pro',
      'claude': 'Claude Haiku',
      'langgraph_gemini': 'LangGraph + Gemini',
      'langgraph_claude': 'LangGraph + Claude'
    };
    return names[chatbot] || chatbot;
  };

  const getQuickPrompts = () => [
    "Help me create a lesson plan for my courses",
    "What are good quiz questions for my classes?",
    "How can I make my classes more engaging?",
    "Show me my Google Classroom courses",
    "What teaching strategies work for my students?",
    "Help me plan assignments for my courses"
  ];

  return (
    <Container fluid className="h-100">
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2>🤖 Educational AI Assistant</h2>
              <p className="text-muted mb-0">
                Chat with {getChatbotDisplayName(currentChatbot)} for educational support and guidance
              </p>
              <small className="text-success">✓ Connected to your Google Classroom data for personalized responses</small>
            </div>
            <div className="d-flex gap-2">
              {availableChatbots.length > 1 && (
                <Form.Select
                  size="sm"
                  value={currentChatbot}
                  onChange={(e) => switchChatbot(e.target.value)}
                  disabled={switchingChatbot || loading}
                  style={{ width: '150px' }}
                >
                  {availableChatbots.map(bot => (
                    <option key={bot} value={bot}>
                      {getChatbotDisplayName(bot)}
                    </option>
                  ))}
                </Form.Select>
              )}
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={clearConversation}
                disabled={loading}
              >
                Clear Chat
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          </Col>
        </Row>
      )}

      <Row className="flex-grow-1">
        <Col md={9}>
          <Card className="h-100 d-flex flex-column">
            <Card.Header className="bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <span>💬 Chat with {getChatbotDisplayName(currentChatbot).split(' ')[0]}</span>
                <div className="d-flex gap-2 align-items-center">
                  {switchingChatbot && <Spinner animation="border" size="sm" />}
                  <Badge bg="light" text="dark">{messages.length} messages</Badge>
                </div>
              </div>
            </Card.Header>
            
            {/* Messages Area */}
            <Card.Body className="flex-grow-1 overflow-auto" style={{ maxHeight: '500px' }}>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`d-flex mb-3 ${message.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                >
                  <div
                    className={`p-3 rounded ${
                      message.role === 'user' 
                        ? 'bg-primary text-white ms-5' 
                        : message.role === 'system'
                        ? 'bg-warning text-dark mx-5'
                        : 'bg-light me-5'
                    }`}
                    style={{ maxWidth: '75%' }}
                  >
                    <div className="mb-1">
                      {message.content.split('\n').map((line, i) => (
                        <React.Fragment key={i}>
                          {line}
                          {i < message.content.split('\n').length - 1 && <br />}
                        </React.Fragment>
                      ))}
                    </div>
                    <small className={
                      message.role === 'user' ? 'text-light' : 
                      message.role === 'system' ? 'text-muted' : 'text-muted'
                    }>
                      {formatTimestamp(message.timestamp)}
                    </small>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="d-flex justify-content-start mb-3">
                  <div className="bg-light p-3 rounded me-5">
                    <Spinner animation="grow" size="sm" className="me-2" />
                    <span className="text-muted">AI is thinking...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </Card.Body>

            {/* Input Area */}
            <Card.Footer>
              <Form onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
                <Row>
                  <Col xs={10}>
                    <Form.Control
                      as="textarea"
                      rows={2}
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                      disabled={loading}
                    />
                  </Col>
                  <Col xs={2}>
                    <Button
                      variant="primary"
                      type="submit"
                      disabled={loading || !currentMessage.trim()}
                      className="w-100 h-100"
                    >
                      {loading ? <Spinner animation="border" size="sm" /> : 'Send'}
                    </Button>
                  </Col>
                </Row>
              </Form>
            </Card.Footer>
          </Card>
        </Col>

        {/* Quick Prompts Sidebar */}
        <Col md={3}>
          <Card>
            <Card.Header>
              <strong>💡 Quick Prompts</strong>
            </Card.Header>
            <Card.Body>
              <p className="small text-muted mb-3">Click on any prompt to get started:</p>
              {getQuickPrompts().map((prompt, index) => (
                <Button
                  key={index}
                  variant="outline-primary"
                  size="sm"
                  className="w-100 mb-2 text-start"
                  onClick={() => setCurrentMessage(prompt)}
                  disabled={loading}
                >
                  {prompt}
                </Button>
              ))}
            </Card.Body>
          </Card>

          {/* Chat Stats */}
          <Card className="mt-3">
            <Card.Header>
              <strong>📊 Chat Stats</strong>
            </Card.Header>
            <Card.Body>
              <ul className="list-unstyled small">
                <li><strong>Total Messages:</strong> {messages.length}</li>
                <li><strong>Your Messages:</strong> {messages.filter(m => m.role === 'user').length}</li>
                <li><strong>AI Responses:</strong> {messages.filter(m => m.role === 'assistant').length}</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default ChatbotTab;