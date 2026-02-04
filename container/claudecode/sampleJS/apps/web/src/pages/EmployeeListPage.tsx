import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEmployees } from '@samplejs/application';
import { EmployeeRepository } from '@samplejs/api';
import { Button, Table, TableColumn } from '@samplejs/ui';
import { DateFormatter } from '@samplejs/util';
import { Employee } from '@samplejs/domain';

const repository = new EmployeeRepository();

const EmployeeListPage: React.FC = () => {
  const navigate = useNavigate();
  const { employees, loading, error, deleteEmployee } = useEmployees(repository);

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await deleteEmployee(id);
      } catch (err) {
        console.error('Failed to delete employee:', err);
      }
    }
  };

  const columns: TableColumn<Employee>[] = useMemo(
    () => [
      {
        key: 'name',
        header: 'Name',
        width: '20%',
      },
      {
        key: 'email',
        header: 'Email',
        width: '25%',
      },
      {
        key: 'department',
        header: 'Department',
        width: '15%',
      },
      {
        key: 'position',
        header: 'Position',
        width: '15%',
      },
      {
        key: 'hireDate',
        header: 'Hire Date',
        width: '15%',
        render: (employee: Employee) => DateFormatter.formatDate(employee.hireDate, 'short'),
      },
      {
        key: 'actions',
        header: 'Actions',
        width: '10%',
        render: (employee: Employee) => (
          <div className="action-buttons">
            <Button
              size="small"
              variant="secondary"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/employees/${employee.id}/edit`);
              }}
              data-testid={`edit-button-${employee.id}`}
            >
              Edit
            </Button>
            <Button
              size="small"
              variant="danger"
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(employee.id);
              }}
              data-testid={`delete-button-${employee.id}`}
            >
              Delete
            </Button>
          </div>
        ),
      },
    ],
    [navigate]
  );

  if (loading) {
    return (
      <div className="container">
        <div className="loading-message" data-testid="loading">
          Loading employees...
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 className="page-title" data-testid="page-title">
            Employee Management
          </h1>
          <Button
            onClick={() => navigate('/employees/new')}
            data-testid="add-employee-button"
          >
            Add Employee
          </Button>
        </div>
      </div>

      {error && (
        <div className="error-message" data-testid="error-message">
          {error}
        </div>
      )}

      <div className="card">
        <Table
          columns={columns}
          data={employees}
          keyExtractor={(employee) => employee.id}
          emptyMessage="No employees found. Click 'Add Employee' to create one."
        />
      </div>
    </div>
  );
};

export default EmployeeListPage;
