import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import OrganizationList from '../OrganizationList';
import { organizationsApi } from '../../api/api';

jest.mock('../../api/api');

const mockOrganizations = [
  {
    id: 1,
    name: 'Test Organization 1',
    description: 'Test Description 1',
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Test Organization 2',
    description: 'Test Description 2',
    createdAt: '2024-01-02T00:00:00Z',
  },
];

describe('OrganizationList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    organizationsApi.getAll.mockReturnValue(new Promise(() => {}));

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('renders organizations after successful fetch', async () => {
    organizationsApi.getAll.mockResolvedValue({ data: mockOrganizations });

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Organization 1')).toBeInTheDocument();
      expect(screen.getByText('Test Organization 2')).toBeInTheDocument();
    });
  });

  test('renders error message on fetch failure', async () => {
    organizationsApi.getAll.mockRejectedValue(new Error('Network error'));

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch organizations/)).toBeInTheDocument();
    });
  });

  test('renders empty state when no organizations', async () => {
    organizationsApi.getAll.mockResolvedValue({ data: [] });

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/No organizations found/)).toBeInTheDocument();
    });
  });

  test('calls create API when form is submitted', async () => {
    organizationsApi.getAll.mockResolvedValue({ data: [] });
    organizationsApi.create.mockResolvedValue({ data: { id: 3, name: 'New Org' } });

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Organization Name *')).toBeInTheDocument();
    });

    const nameInput = screen.getByPlaceholderText('Organization Name *');
    const descInput = screen.getByPlaceholderText('Description');
    const submitButton = screen.getByText('Create Organization');

    fireEvent.change(nameInput, { target: { value: 'New Org' } });
    fireEvent.change(descInput, { target: { value: 'New Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(organizationsApi.create).toHaveBeenCalledWith({
        name: 'New Org',
        description: 'New Description',
      });
    });
  });

  test('calls delete API when delete button is clicked with confirmation', async () => {
    organizationsApi.getAll.mockResolvedValue({ data: mockOrganizations });
    organizationsApi.delete.mockResolvedValue({ data: { success: true } });
    window.confirm = jest.fn(() => true);

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Organization 1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith('Delete this organization?');
    await waitFor(() => {
      expect(organizationsApi.delete).toHaveBeenCalledWith(1);
    });
  });

  test('does not delete when confirmation is cancelled', async () => {
    organizationsApi.getAll.mockResolvedValue({ data: mockOrganizations });
    window.confirm = jest.fn(() => false);

    render(
      <BrowserRouter>
        <OrganizationList />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Organization 1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    expect(organizationsApi.delete).not.toHaveBeenCalled();
  });
});
