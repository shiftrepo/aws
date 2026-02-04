import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useEmployeeForm } from '@samplejs/application';
import { EmployeeRepository } from '@samplejs/api';
import { Button, Input } from '@samplejs/ui';

const repository = new EmployeeRepository();

const EmployeeFormPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;

  const { employee, loading, error, loadEmployee, createEmployee, updateEmployee } =
    useEmployeeForm(repository);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    department: '',
    position: '',
    hireDate: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isEditMode && id) {
      loadEmployee(id).catch(() => {
        navigate('/');
      });
    }
  }, [id, isEditMode, loadEmployee, navigate]);

  useEffect(() => {
    if (employee) {
      setFormData({
        name: employee.name,
        email: employee.email,
        department: employee.department,
        position: employee.position,
        hireDate: employee.hireDate.toISOString().split('T')[0],
      });
    }
  }, [employee]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) {
      setFormErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    if (!formData.department.trim()) {
      errors.department = 'Department is required';
    }

    if (!formData.position.trim()) {
      errors.position = 'Position is required';
    }

    if (!formData.hireDate) {
      errors.hireDate = 'Hire date is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const employeeData = {
        name: formData.name,
        email: formData.email,
        department: formData.department,
        position: formData.position,
        hireDate: new Date(formData.hireDate),
      };

      if (isEditMode && id) {
        await updateEmployee(id, employeeData);
      } else {
        await createEmployee(employeeData);
      }

      navigate('/');
    } catch (err) {
      console.error('Failed to save employee:', err);
    }
  };

  if (loading && isEditMode) {
    return (
      <div className="container">
        <div className="loading-message" data-testid="loading">
          Loading employee...
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title" data-testid="page-title">
          {isEditMode ? 'Edit Employee' : 'Add New Employee'}
        </h1>
      </div>

      {error && (
        <div className="error-message" data-testid="error-message">
          {error}
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit} data-testid="employee-form">
          <div className="form-group">
            <Input
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              error={formErrors.name}
              required
              fullWidth
              data-testid="input-name"
            />
          </div>

          <div className="form-group">
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              error={formErrors.email}
              required
              fullWidth
              data-testid="input-email"
            />
          </div>

          <div className="form-group">
            <Input
              label="Department"
              name="department"
              value={formData.department}
              onChange={handleChange}
              error={formErrors.department}
              required
              fullWidth
              data-testid="input-department"
            />
          </div>

          <div className="form-group">
            <Input
              label="Position"
              name="position"
              value={formData.position}
              onChange={handleChange}
              error={formErrors.position}
              required
              fullWidth
              data-testid="input-position"
            />
          </div>

          <div className="form-group">
            <Input
              label="Hire Date"
              name="hireDate"
              type="date"
              value={formData.hireDate}
              onChange={handleChange}
              error={formErrors.hireDate}
              required
              fullWidth
              data-testid="input-hire-date"
            />
          </div>

          <div className="button-group">
            <Button type="submit" data-testid="submit-button">
              {isEditMode ? 'Update' : 'Create'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/')}
              data-testid="cancel-button"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmployeeFormPage;
