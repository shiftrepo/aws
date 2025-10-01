# Authentication Middleware Implementation

## Authentication Strategy

### JWT-Based Authentication
- **Stateless**: No server-side session storage required
- **Scalable**: Horizontal scaling without session synchronization
- **Secure**: HMAC SHA256 or RSA signing
- **Portable**: Token can be used across services

## Implementation Components

### 1. JWT Configuration

```typescript
// src/config/jwt.config.ts

export const jwtConfig = {
  secret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
  expiresIn: process.env.JWT_EXPIRES_IN || '24h',
  refreshExpiresIn: '7d',
  issuer: 'schedule-management-api',
  audience: 'schedule-management-client',
};

// Validate JWT configuration on startup
export function validateJwtConfig() {
  if (!process.env.JWT_SECRET || process.env.JWT_SECRET.length < 32) {
    throw new Error('JWT_SECRET must be at least 32 characters long');
  }
}
```

### 2. JWT Service

```typescript
// src/services/jwt.service.ts

import jwt from 'jsonwebtoken';
import { jwtConfig } from '../config/jwt.config';

export interface JwtPayload {
  userId: string;
  email: string;
  role: string;
}

export class JwtService {
  static generateAccessToken(payload: JwtPayload): string {
    return jwt.sign(payload, jwtConfig.secret, {
      expiresIn: jwtConfig.expiresIn,
      issuer: jwtConfig.issuer,
      audience: jwtConfig.audience,
    });
  }

  static generateRefreshToken(payload: JwtPayload): string {
    return jwt.sign(payload, jwtConfig.secret, {
      expiresIn: jwtConfig.refreshExpiresIn,
      issuer: jwtConfig.issuer,
      audience: jwtConfig.audience,
    });
  }

  static verifyToken(token: string): JwtPayload {
    try {
      const decoded = jwt.verify(token, jwtConfig.secret, {
        issuer: jwtConfig.issuer,
        audience: jwtConfig.audience,
      }) as JwtPayload;

      return decoded;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new Error('Token has expired');
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error('Invalid token');
      }
      throw error;
    }
  }

  static decodeToken(token: string): JwtPayload | null {
    try {
      return jwt.decode(token) as JwtPayload;
    } catch {
      return null;
    }
  }
}
```

### 3. Authentication Middleware

```typescript
// src/middleware/auth.middleware.ts

import { Request, Response, NextFunction } from 'express';
import { JwtService } from '../services/jwt.service';

// Extend Express Request type
declare global {
  namespace Express {
    interface Request {
      user?: {
        userId: string;
        email: string;
        role: string;
      };
    }
  }
}

export function authenticate(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  try {
    // Extract token from Authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({
        success: false,
        error: {
          code: 'NO_TOKEN',
          message: 'Authentication token is required',
        },
      });
      return;
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Verify token
    const payload = JwtService.verifyToken(token);

    // Attach user info to request
    req.user = {
      userId: payload.userId,
      email: payload.email,
      role: payload.role,
    };

    next();
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Invalid token';

    res.status(401).json({
      success: false,
      error: {
        code: 'INVALID_TOKEN',
        message,
      },
    });
  }
}

// Optional authentication (doesn't fail if no token)
export function optionalAuthenticate(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  try {
    const authHeader = req.headers.authorization;

    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const payload = JwtService.verifyToken(token);

      req.user = {
        userId: payload.userId,
        email: payload.email,
        role: payload.role,
      };
    }
  } catch {
    // Silently ignore authentication errors
  }

  next();
}
```

### 4. Authorization Middleware

```typescript
// src/middleware/authorize.middleware.ts

import { Request, Response, NextFunction } from 'express';

type UserRole = 'ADMIN' | 'MANAGER' | 'MEMBER';

export function authorize(...allowedRoles: UserRole[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        success: false,
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required',
        },
      });
      return;
    }

    const userRole = req.user.role as UserRole;

    if (!allowedRoles.includes(userRole)) {
      res.status(403).json({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions',
        },
      });
      return;
    }

    next();
  };
}

// Check if user owns the resource
export function authorizeOwnership(getUserIdFromParams: (req: Request) => string) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    if (!req.user) {
      res.status(401).json({
        success: false,
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required',
        },
      });
      return;
    }

    const resourceUserId = getUserIdFromParams(req);

    // Admin can access any resource
    if (req.user.role === 'ADMIN') {
      next();
      return;
    }

    // User can only access their own resources
    if (req.user.userId !== resourceUserId) {
      res.status(403).json({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'You can only access your own resources',
        },
      });
      return;
    }

    next();
  };
}
```

### 5. Password Hashing Service

```typescript
// src/services/password.service.ts

import bcrypt from 'bcrypt';

export class PasswordService {
  private static readonly SALT_ROUNDS = 12;

  static async hash(password: string): Promise<string> {
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }

  static async compare(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  static validate(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
```

### 6. Rate Limiting Middleware

```typescript
// src/middleware/rate-limit.middleware.ts

import rateLimit from 'express-rate-limit';

// General API rate limiter
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Max 100 requests per window
  message: {
    success: false,
    error: {
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many requests, please try again later',
    },
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Strict limiter for auth endpoints
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Max 5 attempts per window
  message: {
    success: false,
    error: {
      code: 'AUTH_RATE_LIMIT_EXCEEDED',
      message: 'Too many authentication attempts, please try again later',
    },
  },
  skipSuccessfulRequests: true, // Don't count successful requests
});
```

### 7. Auth Controller

```typescript
// src/controllers/auth.controller.ts

import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { JwtService } from '../services/jwt.service';
import { PasswordService } from '../services/password.service';
import { z } from 'zod';

const prisma = new PrismaClient();

// Validation schemas
const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  timezone: z.string().optional(),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

export class AuthController {
  static async register(req: Request, res: Response): Promise<void> {
    try {
      // Validate input
      const data = registerSchema.parse(req.body);

      // Validate password strength
      const passwordValidation = PasswordService.validate(data.password);
      if (!passwordValidation.valid) {
        res.status(400).json({
          success: false,
          error: {
            code: 'WEAK_PASSWORD',
            message: 'Password does not meet requirements',
            details: passwordValidation.errors,
          },
        });
        return;
      }

      // Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email: data.email },
      });

      if (existingUser) {
        res.status(409).json({
          success: false,
          error: {
            code: 'USER_EXISTS',
            message: 'User with this email already exists',
          },
        });
        return;
      }

      // Hash password
      const hashedPassword = await PasswordService.hash(data.password);

      // Create user
      const user = await prisma.user.create({
        data: {
          email: data.email,
          password: hashedPassword,
          firstName: data.firstName,
          lastName: data.lastName,
          timezone: data.timezone || 'UTC',
        },
      });

      // Generate token
      const token = JwtService.generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      res.status(201).json({
        success: true,
        data: {
          user: {
            id: user.id,
            email: user.email,
            firstName: user.firstName,
            lastName: user.lastName,
            role: user.role,
            timezone: user.timezone,
          },
          token,
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid input',
            details: error.errors,
          },
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'An error occurred during registration',
        },
      });
    }
  }

  static async login(req: Request, res: Response): Promise<void> {
    try {
      // Validate input
      const data = loginSchema.parse(req.body);

      // Find user
      const user = await prisma.user.findUnique({
        where: { email: data.email },
      });

      if (!user) {
        res.status(401).json({
          success: false,
          error: {
            code: 'INVALID_CREDENTIALS',
            message: 'Invalid email or password',
          },
        });
        return;
      }

      // Verify password
      const isValidPassword = await PasswordService.compare(
        data.password,
        user.password
      );

      if (!isValidPassword) {
        res.status(401).json({
          success: false,
          error: {
            code: 'INVALID_CREDENTIALS',
            message: 'Invalid email or password',
          },
        });
        return;
      }

      // Generate token
      const token = JwtService.generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      res.json({
        success: true,
        data: {
          user: {
            id: user.id,
            email: user.email,
            firstName: user.firstName,
            lastName: user.lastName,
            role: user.role,
          },
          token,
          expiresIn: 86400, // 24 hours in seconds
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid input',
            details: error.errors,
          },
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'An error occurred during login',
        },
      });
    }
  }
}
```

## Usage in Routes

```typescript
// src/routes/schedule.routes.ts

import { Router } from 'express';
import { authenticate } from '../middleware/auth.middleware';
import { authorize } from '../middleware/authorize.middleware';
import { apiLimiter } from '../middleware/rate-limit.middleware';

const router = Router();

// Apply rate limiting to all routes
router.use(apiLimiter);

// Public routes (no authentication)
router.get('/public', (req, res) => {
  // ...
});

// Protected routes (authentication required)
router.get('/schedules', authenticate, (req, res) => {
  // req.user is available
});

// Admin only routes
router.delete('/schedules/:id', authenticate, authorize('ADMIN'), (req, res) => {
  // Only admins can access
});

// Admin or Manager routes
router.post('/teams', authenticate, authorize('ADMIN', 'MANAGER'), (req, res) => {
  // Admins and Managers can access
});

export default router;
```

## Security Best Practices

1. **Environment Variables**: Store JWT secret in environment variables
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Expiration**: Set reasonable token expiration times
4. **Rate Limiting**: Implement rate limiting on auth endpoints
5. **Password Requirements**: Enforce strong password policies
6. **Secure Headers**: Use helmet middleware
7. **CORS Configuration**: Configure CORS appropriately
8. **Input Validation**: Validate and sanitize all inputs
9. **Error Messages**: Don't leak sensitive info in errors
10. **Token Refresh**: Implement token refresh mechanism
