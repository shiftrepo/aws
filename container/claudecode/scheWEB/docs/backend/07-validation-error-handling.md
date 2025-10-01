# Data Validation and Error Handling Strategy

## Overview

Robust validation and error handling ensures:
1. **Data integrity**: Invalid data never reaches the database
2. **User experience**: Clear, actionable error messages
3. **Security**: Prevent injection attacks and malicious input
4. **Debugging**: Detailed logs for troubleshooting
5. **Consistency**: Standardized error response format

## Validation Strategy

### 1. Zod Schema Validation

```typescript
// src/validators/schedule.validator.ts

import { z } from 'zod';

// Base schedule validation
export const createScheduleSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be 200 characters or less'),

  description: z
    .string()
    .max(2000, 'Description must be 2000 characters or less')
    .optional(),

  startTime: z
    .string()
    .datetime({ message: 'Start time must be a valid ISO datetime' })
    .refine(
      (val) => new Date(val) > new Date(),
      'Start time must be in the future'
    ),

  endTime: z
    .string()
    .datetime({ message: 'End time must be a valid ISO datetime' }),

  location: z
    .string()
    .max(500, 'Location must be 500 characters or less')
    .optional(),

  type: z.enum(['MEETING', 'APPOINTMENT', 'TASK', 'EVENT', 'BREAK']),

  teamId: z.string().uuid().optional(),

  participants: z
    .array(
      z.object({
        userId: z.string().uuid(),
        isRequired: z.boolean().optional().default(true),
      })
    )
    .min(1, 'At least one participant is required')
    .max(100, 'Maximum 100 participants allowed'),

  isRecurring: z.boolean().optional().default(false),

  recurrenceRule: z
    .string()
    .regex(/^FREQ=(DAILY|WEEKLY|MONTHLY|YEARLY)/, 'Invalid RRULE format')
    .optional(),
}).refine(
  (data) => new Date(data.endTime) > new Date(data.startTime),
  {
    message: 'End time must be after start time',
    path: ['endTime'],
  }
).refine(
  (data) => {
    const duration = new Date(data.endTime).getTime() - new Date(data.startTime).getTime();
    const maxDuration = 24 * 60 * 60 * 1000; // 24 hours
    return duration <= maxDuration;
  },
  {
    message: 'Schedule duration cannot exceed 24 hours',
    path: ['endTime'],
  }
);

export const updateScheduleSchema = createScheduleSchema.partial();

// Availability validation
export const availabilitySchema = z.object({
  dayOfWeek: z.number().min(0).max(6),

  startTime: z
    .string()
    .regex(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Time must be in HH:mm format'),

  endTime: z
    .string()
    .regex(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Time must be in HH:mm format'),

  isAvailable: z.boolean().optional().default(true),

  effectiveFrom: z.string().datetime().optional(),

  effectiveUntil: z.string().datetime().optional(),
}).refine(
  (data) => {
    const [startH, startM] = data.startTime.split(':').map(Number);
    const [endH, endM] = data.endTime.split(':').map(Number);
    return startH * 60 + startM < endH * 60 + endM;
  },
  {
    message: 'End time must be after start time',
    path: ['endTime'],
  }
);

// User validation
export const registerUserSchema = z.object({
  email: z.string().email('Invalid email address'),

  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be 128 characters or less')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(
      /[!@#$%^&*(),.?":{}|<>]/,
      'Password must contain at least one special character'
    ),

  firstName: z
    .string()
    .min(1, 'First name is required')
    .max(50, 'First name must be 50 characters or less')
    .regex(/^[a-zA-Z\s'-]+$/, 'First name contains invalid characters'),

  lastName: z
    .string()
    .min(1, 'Last name is required')
    .max(50, 'Last name must be 50 characters or less')
    .regex(/^[a-zA-Z\s'-]+$/, 'Last name contains invalid characters'),

  timezone: z
    .string()
    .optional()
    .refine(
      (tz) => {
        if (!tz) return true;
        try {
          Intl.DateTimeFormat(undefined, { timeZone: tz });
          return true;
        } catch {
          return false;
        }
      },
      'Invalid timezone'
    ),
});

export const updateUserSchema = registerUserSchema.partial().omit({ password: true });

// Team validation
export const createTeamSchema = z.object({
  name: z
    .string()
    .min(1, 'Team name is required')
    .max(100, 'Team name must be 100 characters or less'),

  description: z
    .string()
    .max(500, 'Description must be 500 characters or less')
    .optional(),
});

// Query parameter validation
export const paginationSchema = z.object({
  page: z
    .string()
    .optional()
    .default('1')
    .transform(Number)
    .pipe(z.number().min(1)),

  limit: z
    .string()
    .optional()
    .default('20')
    .transform(Number)
    .pipe(z.number().min(1).max(100)),
});

export const dateRangeSchema = z.object({
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
}).refine(
  (data) => new Date(data.endDate) > new Date(data.startDate),
  'End date must be after start date'
);
```

### 2. Validation Middleware

```typescript
// src/middleware/validate.middleware.ts

import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';

/**
 * Middleware to validate request data against a Zod schema
 */
export function validate(schema: AnyZodObject) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // Validate request body, query, and params
      const validated = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });

      // Replace request data with validated data
      req.body = validated.body;
      req.query = validated.query;
      req.params = validated.params;

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            details: error.errors.map((err) => ({
              field: err.path.join('.'),
              message: err.message,
            })),
          },
        });
        return;
      }

      next(error);
    }
  };
}

/**
 * Validate only request body
 */
export function validateBody(schema: AnyZodObject) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      req.body = await schema.parseAsync(req.body);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request body',
            details: error.errors.map((err) => ({
              field: err.path.join('.'),
              message: err.message,
            })),
          },
        });
        return;
      }

      next(error);
    }
  };
}

/**
 * Validate query parameters
 */
export function validateQuery(schema: AnyZodObject) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      req.query = await schema.parseAsync(req.query);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid query parameters',
            details: error.errors.map((err) => ({
              field: err.path.join('.'),
              message: err.message,
            })),
          },
        });
        return;
      }

      next(error);
    }
  };
}
```

## Error Handling

### 1. Custom Error Classes

```typescript
// src/utils/errors.ts

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: unknown) {
    super(400, 'VALIDATION_ERROR', message, details);
  }
}

export class AuthenticationError extends AppError {
  constructor(message = 'Authentication required') {
    super(401, 'AUTHENTICATION_ERROR', message);
  }
}

export class AuthorizationError extends AppError {
  constructor(message = 'Insufficient permissions') {
    super(403, 'AUTHORIZATION_ERROR', message);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id?: string) {
    const message = id
      ? `${resource} with id ${id} not found`
      : `${resource} not found`;
    super(404, 'NOT_FOUND', message);
  }
}

export class ConflictError extends AppError {
  constructor(message: string, details?: unknown) {
    super(409, 'CONFLICT', message, details);
  }
}

export class BusinessLogicError extends AppError {
  constructor(message: string, details?: unknown) {
    super(422, 'BUSINESS_LOGIC_ERROR', message, details);
  }
}

export class InternalServerError extends AppError {
  constructor(message = 'An internal server error occurred') {
    super(500, 'INTERNAL_SERVER_ERROR', message);
  }
}
```

### 2. Error Handler Middleware

```typescript
// src/middleware/error-handler.middleware.ts

import { Request, Response, NextFunction } from 'express';
import { AppError } from '../utils/errors';
import { logger } from '../utils/logger';
import { Prisma } from '@prisma/client';

/**
 * Global error handler middleware
 */
export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Log error
  logger.error('Error occurred:', {
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method,
    userId: req.user?.userId,
  });

  // Handle known application errors
  if (error instanceof AppError) {
    res.status(error.statusCode).json({
      success: false,
      error: {
        code: error.code,
        message: error.message,
        ...(error.details && { details: error.details }),
      },
    });
    return;
  }

  // Handle Prisma errors
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    const prismaError = handlePrismaError(error);
    res.status(prismaError.statusCode).json({
      success: false,
      error: prismaError,
    });
    return;
  }

  // Handle unexpected errors
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_SERVER_ERROR',
      message:
        process.env.NODE_ENV === 'production'
          ? 'An unexpected error occurred'
          : error.message,
    },
  });
}

/**
 * Convert Prisma errors to application errors
 */
function handlePrismaError(error: Prisma.PrismaClientKnownRequestError): {
  statusCode: number;
  code: string;
  message: string;
} {
  switch (error.code) {
    case 'P2002':
      // Unique constraint violation
      return {
        statusCode: 409,
        code: 'DUPLICATE_ENTRY',
        message: 'A record with this data already exists',
      };

    case 'P2025':
      // Record not found
      return {
        statusCode: 404,
        code: 'NOT_FOUND',
        message: 'Record not found',
      };

    case 'P2003':
      // Foreign key constraint violation
      return {
        statusCode: 400,
        code: 'INVALID_REFERENCE',
        message: 'Referenced record does not exist',
      };

    case 'P2014':
      // Invalid ID
      return {
        statusCode: 400,
        code: 'INVALID_ID',
        message: 'Invalid identifier provided',
      };

    default:
      return {
        statusCode: 500,
        code: 'DATABASE_ERROR',
        message: 'A database error occurred',
      };
  }
}

/**
 * 404 handler for unknown routes
 */
export function notFoundHandler(req: Request, res: Response): void {
  res.status(404).json({
    success: false,
    error: {
      code: 'ROUTE_NOT_FOUND',
      message: `Route ${req.method} ${req.path} not found`,
    },
  });
}

/**
 * Async error wrapper to catch async errors
 */
export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>
) {
  return (req: Request, res: Response, next: NextFunction): void => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
```

### 3. Logger Configuration

```typescript
// src/utils/logger.ts

import winston from 'winston';

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'schedule-api' },
  transports: [
    // Write errors to error.log
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    }),

    // Write all logs to combined.log
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880,
      maxFiles: 5,
    }),
  ],
});

// Console logging for development
if (process.env.NODE_ENV !== 'production') {
  logger.add(
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
    })
  );
}

// Request logger middleware
export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const startTime = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - startTime;

    logger.info('HTTP Request', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      userId: req.user?.userId,
      ip: req.ip,
    });
  });

  next();
}
```

### 4. Usage in Controllers

```typescript
// src/controllers/schedule.controller.ts

import { Request, Response, NextFunction } from 'express';
import { asyncHandler } from '../middleware/error-handler.middleware';
import { NotFoundError, ConflictError, BusinessLogicError } from '../utils/errors';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class ScheduleController {
  static createSchedule = asyncHandler(async (req: Request, res: Response) => {
    const data = req.body; // Already validated by middleware

    // Business logic validation
    const hasConflicts = await checkScheduleConflicts(
      data.participants,
      data.startTime,
      data.endTime
    );

    if (hasConflicts) {
      throw new ConflictError(
        'Schedule conflicts with existing appointments',
        hasConflicts
      );
    }

    // Create schedule
    const schedule = await prisma.schedule.create({
      data: {
        ...data,
        createdBy: req.user!.userId,
      },
    });

    res.status(201).json({
      success: true,
      data: schedule,
    });
  });

  static getSchedule = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const schedule = await prisma.schedule.findUnique({
      where: { id },
      include: {
        participants: {
          include: { user: true },
        },
      },
    });

    if (!schedule) {
      throw new NotFoundError('Schedule', id);
    }

    res.json({
      success: true,
      data: schedule,
    });
  });

  static deleteSchedule = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const schedule = await prisma.schedule.findUnique({
      where: { id },
    });

    if (!schedule) {
      throw new NotFoundError('Schedule', id);
    }

    // Check authorization
    if (schedule.createdBy !== req.user!.userId && req.user!.role !== 'ADMIN') {
      throw new AuthorizationError('You can only delete your own schedules');
    }

    // Soft delete by updating status
    await prisma.schedule.update({
      where: { id },
      data: { status: 'CANCELLED' },
    });

    res.json({
      success: true,
      message: 'Schedule cancelled successfully',
    });
  });
}
```

## API Response Formats

### Success Response

```typescript
{
  "success": true,
  "data": {
    // Response data
  }
}
```

### Error Response

```typescript
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Optional additional details
    }
  }
}
```

### Paginated Response

```typescript
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

## Testing Validation

```typescript
// tests/validation.test.ts

import { createScheduleSchema } from '../validators/schedule.validator';

describe('Schedule Validation', () => {
  it('should accept valid schedule data', () => {
    const validData = {
      title: 'Team Meeting',
      startTime: '2024-01-15T10:00:00Z',
      endTime: '2024-01-15T11:00:00Z',
      type: 'MEETING',
      participants: [{ userId: 'uuid', isRequired: true }],
    };

    expect(() => createScheduleSchema.parse(validData)).not.toThrow();
  });

  it('should reject end time before start time', () => {
    const invalidData = {
      title: 'Meeting',
      startTime: '2024-01-15T11:00:00Z',
      endTime: '2024-01-15T10:00:00Z',
      type: 'MEETING',
      participants: [{ userId: 'uuid' }],
    };

    expect(() => createScheduleSchema.parse(invalidData)).toThrow();
  });
});
```
