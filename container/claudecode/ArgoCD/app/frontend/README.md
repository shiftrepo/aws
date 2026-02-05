# Organization Management System - Frontend

A modern React 18 + Vite 5 frontend application for managing organizations, departments, and users.

## Features

- **Organizations Management**: Create, view, edit, and delete organizations
- **Departments Management**: Hierarchical department structure with tree view
- **Users Management**: User profiles with department assignments
- **Modern UI**: Clean, responsive design with modern CSS
- **Search & Pagination**: Efficient data browsing
- **Form Validation**: Client-side validation for all forms
- **Error Handling**: User-friendly error messages

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite 5**: Lightning-fast build tool
- **React Router 6**: Client-side routing
- **Axios**: HTTP client for API calls
- **ESLint**: Code linting

## Prerequisites

- Node.js 18+ and npm/yarn

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```
VITE_API_URL=http://localhost:8080
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Testing

Run tests:
```bash
npm test
```

Run linting:
```bash
npm run lint
```

## Project Structure

```
src/
├── api/                    # API client and endpoints
│   ├── axios.js           # Axios configuration
│   ├── organizationApi.js # Organization API calls
│   ├── departmentApi.js   # Department API calls
│   └── userApi.js         # User API calls
├── components/            # React components
│   ├── Layout.jsx        # Main layout wrapper
│   ├── Navigation.jsx    # Top navigation bar
│   ├── organizations/    # Organization components
│   ├── departments/      # Department components
│   └── users/           # User components
├── pages/               # Page components
│   ├── HomePage.jsx    # Dashboard
│   ├── OrganizationsPage.jsx
│   ├── DepartmentsPage.jsx
│   └── UsersPage.jsx
├── App.jsx             # Main app component
├── App.css            # App styles
├── index.css          # Global styles
└── main.jsx           # App entry point
```

## API Integration

The frontend communicates with the backend REST API. Configure the API URL in the `.env` file.

### API Endpoints Used

- `GET /api/organizations` - List organizations
- `POST /api/organizations` - Create organization
- `GET /api/organizations/{id}` - Get organization details
- `PUT /api/organizations/{id}` - Update organization
- `DELETE /api/organizations/{id}` - Delete organization

Similar endpoints exist for departments and users.

## Features Overview

### Organizations
- List view with search and pagination
- Create/edit forms with validation
- Detail view with department list
- Active/inactive status toggle

### Departments
- List view with pagination
- Tree view showing hierarchy
- Parent department selection
- Organization assignment

### Users
- List view with search
- User profile management
- Department assignment
- Contact information

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | http://localhost:8080 |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Write meaningful commit messages
3. Add tests for new features
4. Update documentation as needed

## License

MIT
