import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Nav, Button, Alert, Spinner } from 'react-bootstrap';

function DatabaseTab({ isActive }) {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState({ data: [], schema: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch list of tables when component mounts or becomes active
  useEffect(() => {
    if (isActive) {
      fetchTables();
    }
  }, [isActive]);

  // Fetch list of tables from the API
  const fetchTables = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/database/tables');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setTables(data);
      
      // If tables exist and no table is selected, select the first one
      if (data.length > 0 && !selectedTable) {
        setSelectedTable(data[0].name);
        fetchTableData(data[0].name);
      }
    } catch (err) {
      console.error('Error fetching tables:', err);
      setError('Failed to fetch database tables. Please make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch data for a specific table
  const fetchTableData = async (tableName) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/database/table/${tableName}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setTableData(data);
    } catch (err) {
      console.error(`Error fetching data for table ${tableName}:`, err);
      setError(`Failed to fetch data for table ${tableName}.`);
    } finally {
      setLoading(false);
    }
  };

  // Handle table selection
  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    fetchTableData(tableName);
  };

  // Render column headers based on schema
  const renderColumnHeaders = () => {
    return tableData.schema.map((column) => (
      <th key={column.name}>{column.name}</th>
    ));
  };

  // Render table rows based on data
  const renderTableRows = () => {
    return tableData.data.map((row, rowIndex) => (
      <tr key={rowIndex}>
        {tableData.schema.map((column) => (
          <td key={`${rowIndex}-${column.name}`}>{row[column.name]}</td>
        ))}
      </tr>
    ));
  };

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2>Database Tables</h2>
          <p className="text-muted">View and explore the database tables and their contents</p>
        </Col>
      </Row>

      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger">
              {error}
              <Button 
                variant="outline-danger" 
                size="sm" 
                className="ms-3"
                onClick={fetchTables}
              >
                Retry
              </Button>
            </Alert>
          </Col>
        </Row>
      )}

      <Row>
        <Col md={3}>
          <Card>
            <Card.Header>Tables</Card.Header>
            <Card.Body>
              {loading && !tables.length ? (
                <div className="text-center p-3">
                  <Spinner animation="border" role="status" size="sm" />
                  <span className="ms-2">Loading tables...</span>
                </div>
              ) : (
                <Nav className="flex-column" variant="pills">
                  {tables.map((table) => (
                    <Nav.Item key={table.name}>
                      <Nav.Link 
                        active={selectedTable === table.name}
                        onClick={() => handleTableSelect(table.name)}
                      >
                        {table.name}
                      </Nav.Link>
                    </Nav.Item>
                  ))}
                </Nav>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={9}>
          <Card>
            <Card.Header>
              {selectedTable ? `Table: ${selectedTable}` : 'Select a table'}
            </Card.Header>
            <Card.Body>
              {loading && selectedTable ? (
                <div className="text-center p-5">
                  <Spinner animation="border" role="status" />
                  <p className="mt-2">Loading table data...</p>
                </div>
              ) : selectedTable ? (
                tableData.data.length > 0 ? (
                  <div className="table-responsive">
                    <Table striped bordered hover>
                      <thead>
                        <tr>
                          {renderColumnHeaders()}
                        </tr>
                      </thead>
                      <tbody>
                        {renderTableRows()}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <Alert variant="info">This table is empty.</Alert>
                )
              ) : (
                <Alert variant="info">Select a table from the list to view its data.</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default DatabaseTab;
