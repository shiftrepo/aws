# Authentication Flow Design - Team Schedule Management System

## Authentication Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Authentication System                             │
│                                                                      │
│  ┌────────────┐      ┌────────────┐      ┌────────────────────┐   │
│  │   Client   │──────│   Nginx    │──────│   Express API      │   │
│  │  (React)   │      │   Proxy    │      │   (Auth Service)   │   │
│  └────────────┘      └────────────┘      └────────────────────┘   │
│        │                                            │               │
│        │                                            │               │
│        │ HTTP-only Cookie                           │               │
│        │ (authToken)                                │               │
│        │                                            ▼               │
│        │                                   ┌────────────────┐       │
│        │                                   │   JWT Token    │       │
│        │                                   │   Validation   │       │
│        │                                   └────────────────┘       │
│        │                                            │               │
│        │                                            ▼               │
│        │                                   ┌────────────────┐       │
│        │                                   │   SQLite DB    │       │
│        │                                   │   users table  │       │
│        │                                   └────────────────┘       │
│        │                                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Login Flow

### Sequence Diagram

```
User          Frontend        API Server      Database
 │                │               │               │
 │  Enter Creds   │               │               │
 │───────────────>│               │               │
 │                │               │               │
 │                │ POST /api/auth/login         │
 │                │──────────────>│               │
 │                │               │               │
 │                │               │ Validate Email│
 │                │               │──────────────>│
 │                │               │<──────────────│
 │                │               │  User Record  │
 │                │               │               │
 │                │               │ Verify Password (bcrypt)
 │                │               │──────────────>│
 │                │               │<──────────────│
 │                │               │  Match: true  │
 │                │               │               │
 │                │               │ Generate JWT  │
 │                │               │<─────────────>│
 │                │               │               │
 │                │               │ Set Cookie    │
 │                │<──────────────│               │
 │                │  Set-Cookie: authToken       │
 │                │  + User Data                  │
 │<───────────────│               │               │
 │  Redirect to   │               │               │
 │  Dashboard     │               │               │
 │                │               │               │
```

### Implementation Details

#### 1. Frontend Login Component

```jsx
// features/auth/LoginPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Input, Toast } from '../../components/ui';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form onSubmit={handleSubmit} className="auth-card">
        <h1>Sign In</h1>

        {error && <Toast type="error" message={error} />}

        <Input
          type="email"
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          autoFocus
        />

        <Input
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />

        <Button
          type="submit"
          variant="primary"
          loading={loading}
          fullWidth
        >
          Sign In
        </Button>
      </form>
    </div>
  );
};
```

#### 2. Authentication Context

```jsx
// contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.me();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await authAPI.login(credentials);
    setUser(response.data.user);
    setIsAuthenticated(true);
    return response.data;
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const hasPermission = (permission) => {
    if (!user?.role?.permissions) return false;
    return user.role.permissions.includes('*') ||
           user.role.permissions.includes(permission);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loading,
      login,
      logout,
      hasPermission,
      checkAuth
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

#### 3. Backend Login Route

```javascript
// backend/src/routes/auth.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const router = express.Router();
const db = require('../database');

// Login endpoint
router.post('/login',
  // Validation middleware
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),

  async (req, res) => {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VAL_001',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { email, password } = req.body;

    try {
      // Find user by email
      const user = db.prepare(`
        SELECT u.*, r.name as role_name, r.permissions
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.email = ? AND u.is_active = 1
      `).get(email);

      if (!user) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'AUTH_001',
            message: 'Invalid credentials'
          }
        });
      }

      // Verify password
      const isValid = await bcrypt.compare(password, user.password_hash);
      if (!isValid) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'AUTH_001',
            message: 'Invalid credentials'
          }
        });
      }

      // Generate JWT token
      const token = jwt.sign(
        {
          userId: user.id,
          email: user.email,
          roleId: user.role_id
        },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
      );

      // Update last login timestamp
      db.prepare('UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?')
        .run(user.id);

      // Create audit log
      db.prepare(`
        INSERT INTO audit_logs (user_id, action, ip_address, user_agent)
        VALUES (?, 'LOGIN', ?, ?)
      `).run(user.id, req.ip, req.get('user-agent'));

      // Set HTTP-only cookie
      res.cookie('authToken', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
      });

      // Remove sensitive data
      delete user.password_hash;

      // Parse permissions JSON
      user.permissions = JSON.parse(user.permissions);

      // Return user data
      res.json({
        success: true,
        data: {
          user: {
            id: user.id,
            email: user.email,
            firstName: user.first_name,
            lastName: user.last_name,
            role: {
              id: user.role_id,
              name: user.role_name,
              permissions: user.permissions
            }
          },
          token
        }
      });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'SYS_001',
          message: 'Internal server error'
        }
      });
    }
  }
);

module.exports = router;
```

#### 4. Authentication Middleware

```javascript
// backend/src/middleware/auth.js
const jwt = require('jsonwebtoken');
const db = require('../database');

// Verify JWT token
const authenticate = async (req, res, next) => {
  try {
    // Get token from cookie or Authorization header
    const token = req.cookies.authToken ||
                  req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'AUTH_002',
          message: 'Authentication required'
        }
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Get user from database
    const user = db.prepare(`
      SELECT u.*, r.name as role_name, r.permissions
      FROM users u
      JOIN roles r ON u.role_id = r.id
      WHERE u.id = ? AND u.is_active = 1
    `).get(decoded.userId);

    if (!user) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'AUTH_002',
          message: 'User not found or inactive'
        }
      });
    }

    // Parse permissions
    user.permissions = JSON.parse(user.permissions);

    // Attach user to request
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        error: {
          code: 'AUTH_002',
          message: 'Token expired'
        }
      });
    }

    return res.status(401).json({
      success: false,
      error: {
        code: 'AUTH_002',
        message: 'Invalid token'
      }
    });
  }
};

// Check permissions
const authorize = (...permissions) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'AUTH_002',
          message: 'Authentication required'
        }
      });
    }

    // Admin has all permissions
    if (req.user.permissions.includes('*')) {
      return next();
    }

    // Check if user has any of the required permissions
    const hasPermission = permissions.some(permission =>
      req.user.permissions.includes(permission)
    );

    if (!hasPermission) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'AUTH_003',
          message: 'Insufficient permissions'
        }
      });
    }

    next();
  };
};

module.exports = { authenticate, authorize };
```

## Logout Flow

### Sequence Diagram

```
User          Frontend        API Server
 │                │               │
 │  Click Logout  │               │
 │───────────────>│               │
 │                │               │
 │                │ POST /api/auth/logout
 │                │──────────────>│
 │                │               │
 │                │               │ Clear Cookie
 │                │               │ Add Token to Blacklist
 │                │               │ Create Audit Log
 │                │               │
 │                │<──────────────│
 │                │  Clear Cookie │
 │<───────────────│               │
 │  Clear State   │               │
 │  Redirect to   │               │
 │  Login         │               │
```

### Logout Implementation

```javascript
// backend/src/routes/auth.js
router.post('/logout', authenticate, async (req, res) => {
  try {
    // Create audit log
    db.prepare(`
      INSERT INTO audit_logs (user_id, action, ip_address)
      VALUES (?, 'LOGOUT', ?)
    `).run(req.user.id, req.ip);

    // Clear cookie
    res.clearCookie('authToken', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict'
    });

    res.json({
      success: true,
      message: 'Logged out successfully'
    });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'SYS_001',
        message: 'Internal server error'
      }
    });
  }
});
```

## Token Refresh Flow

### Refresh Implementation

```javascript
// backend/src/routes/auth.js
router.post('/refresh', authenticate, async (req, res) => {
  try {
    // Generate new token
    const newToken = jwt.sign(
      {
        userId: req.user.id,
        email: req.user.email,
        roleId: req.user.role_id
      },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );

    // Set new cookie
    res.cookie('authToken', newToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000
    });

    res.json({
      success: true,
      data: { token: newToken }
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'SYS_001',
        message: 'Internal server error'
      }
    });
  }
});
```

## Protected Route Component

```jsx
// components/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner } from './ui';

export const ProtectedRoute = ({ children, permission }) => {
  const { isAuthenticated, loading, hasPermission } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
};
```

## API Client with Interceptors

```javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3001',
  withCredentials: true, // Send cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.headers['X-Request-Time'] = Date.now();
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        await apiClient.post('/api/auth/refresh');

        // Retry original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

## Password Requirements

### Validation Rules

```javascript
// utils/validation.js
export const passwordValidation = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumber: true,
  requireSpecialChar: true,

  validate: (password) => {
    const errors = [];

    if (password.length < passwordValidation.minLength) {
      errors.push(`Minimum ${passwordValidation.minLength} characters`);
    }

    if (passwordValidation.requireUppercase && !/[A-Z]/.test(password)) {
      errors.push('At least one uppercase letter');
    }

    if (passwordValidation.requireLowercase && !/[a-z]/.test(password)) {
      errors.push('At least one lowercase letter');
    }

    if (passwordValidation.requireNumber && !/[0-9]/.test(password)) {
      errors.push('At least one number');
    }

    if (passwordValidation.requireSpecialChar && !/[!@#$%^&*]/.test(password)) {
      errors.push('At least one special character (!@#$%^&*)');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
};
```

## Security Best Practices

### Implemented Security Measures

1. **Password Security**
   - Bcrypt hashing with cost factor 12
   - Minimum 8 characters with complexity requirements
   - No password exposure in logs or responses

2. **JWT Security**
   - Short expiration time (24 hours)
   - HTTP-only cookies to prevent XSS
   - Secure flag in production
   - SameSite=strict to prevent CSRF

3. **API Security**
   - Rate limiting on auth endpoints
   - Request validation with express-validator
   - SQL injection prevention via parameterized queries
   - CORS configuration for trusted origins

4. **Session Management**
   - Audit logging for all auth events
   - Token refresh mechanism
   - Automatic logout on token expiration

5. **User Privacy**
   - No sensitive data in JWT payload
   - Password never sent in responses
   - Audit trail for compliance

## Session Persistence

### Remember Me Feature

```javascript
// Extended token expiration for "Remember Me"
const tokenExpiry = rememberMe ? '30d' : '24h';

const token = jwt.sign(payload, secret, { expiresIn: tokenExpiry });

res.cookie('authToken', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: rememberMe ? 30 * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000
});
```

## Error Handling

### Authentication Error Responses

```javascript
// Standardized error responses
const authErrors = {
  INVALID_CREDENTIALS: {
    code: 'AUTH_001',
    message: 'Invalid credentials',
    status: 401
  },
  TOKEN_EXPIRED: {
    code: 'AUTH_002',
    message: 'Token expired',
    status: 401
  },
  INSUFFICIENT_PERMISSIONS: {
    code: 'AUTH_003',
    message: 'Insufficient permissions',
    status: 403
  },
  ACCOUNT_INACTIVE: {
    code: 'AUTH_004',
    message: 'Account is inactive',
    status: 403
  }
};
```
