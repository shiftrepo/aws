import { createBrowserRouter } from 'react-router-dom';
import EmployeeListPage from '../pages/EmployeeListPage';
import EmployeeFormPage from '../pages/EmployeeFormPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <EmployeeListPage />,
  },
  {
    path: '/employees/new',
    element: <EmployeeFormPage />,
  },
  {
    path: '/employees/:id/edit',
    element: <EmployeeFormPage />,
  },
]);
