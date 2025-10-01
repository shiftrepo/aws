# Backend Quick Start Guide

## Setup Instructions

### 1. Initialize Project

```bash
# Create project directory structure
mkdir -p src/{config,controllers,middleware,models,routes,services,utils,validators}
mkdir -p tests/{unit,integration}
mkdir -p logs

# Initialize TypeScript project
npm init -y
npm install express typescript @types/express @types/node
npx tsc --init
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install express typescript prisma @prisma/client
npm install jsonwebtoken bcrypt zod date-fns luxon
npm install helmet cors express-rate-limit winston dotenv

# Dev dependencies
npm install -D @types/express @types/node @types/bcrypt @types/jsonwebtoken
npm install -D ts-node nodemon jest ts-jest supertest @types/supertest
npm install -D eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### 3. Configure Prisma

```bash
# Initialize Prisma
npx prisma init

# Copy schema from docs/backend/02-database-models.md to prisma/schema.prisma

# Run migrations
npx prisma migrate dev --name init

# Generate Prisma client
npx prisma generate
```

### 4. Environment Variables

Create `.env` file:

```env
# Server
NODE_ENV=development
PORT=3000

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/schedule_db?schema=public"

# JWT
JWT_SECRET="your-super-secret-jwt-key-minimum-32-characters"
JWT_EXPIRES_IN="24h"

# Logging
LOG_LEVEL=debug

# Redis (optional)
REDIS_URL="redis://localhost:6379"
```

### 5. TypeScript Configuration

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 6. Package.json Scripts

```json
{
  "scripts": {
    "dev": "nodemon --exec ts-node src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint . --ext .ts",
    "format": "prettier --write \"src/**/*.ts\"",
    "prisma:generate": "prisma generate",
    "prisma:migrate": "prisma migrate dev",
    "prisma:studio": "prisma studio"
  }
}
```

## Implementation Order

### Phase 1: Infrastructure (Day 1-2)

1. **Setup Express App**
   - Create `src/app.ts`
   - Configure middleware (helmet, cors, json parser)
   - Setup error handlers

2. **Database Connection**
   - Initialize Prisma client
   - Test connection

3. **Basic Routing**
   - Create route files
   - Setup API versioning

### Phase 2: Authentication (Day 3-4)

1. **JWT Service** (`src/services/jwt.service.ts`)
2. **Password Service** (`src/services/password.service.ts`)
3. **Auth Middleware** (`src/middleware/auth.middleware.ts`)
4. **Auth Controller** (`src/controllers/auth.controller.ts`)
5. **Auth Routes** (`src/routes/auth.routes.ts`)

### Phase 3: User Management (Day 5)

1. **User Controller** (`src/controllers/user.controller.ts`)
2. **User Routes** (`src/routes/user.routes.ts`)
3. **User Validators** (`src/validators/user.validator.ts`)

### Phase 4: Team Management (Day 6)

1. **Team Controller** (`src/controllers/team.controller.ts`)
2. **Team Routes** (`src/routes/team.routes.ts`)
3. **Team Validators** (`src/validators/team.validator.ts`)

### Phase 5: Schedule Management (Day 7-9)

1. **Conflict Detection Service** (`src/services/conflict-detection.service.ts`)
2. **Time Overlap Utilities** (`src/utils/time-overlap.util.ts`)
3. **Schedule Controller** (`src/controllers/schedule.controller.ts`)
4. **Schedule Routes** (`src/routes/schedule.routes.ts`)
5. **Schedule Validators** (`src/validators/schedule.validator.ts`)

### Phase 6: Availability & Time Slots (Day 10-12)

1. **Time Slot Finder Service** (`src/services/time-slot-finder.service.ts`)
2. **Smart Scheduler Service** (`src/services/smart-scheduler.service.ts`)
3. **Availability Controller** (`src/controllers/availability.controller.ts`)
4. **Availability Routes** (`src/routes/availability.routes.ts`)

### Phase 7: Testing (Day 13-14)

1. Unit tests for services
2. Integration tests for API endpoints
3. Edge case testing

### Phase 8: Optimization & Documentation (Day 15)

1. Performance optimization
2. API documentation (Swagger)
3. Deployment preparation

## Key Implementation Files

### Minimal Working Example

**src/app.ts**:
```typescript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { errorHandler, notFoundHandler } from './middleware/error-handler.middleware';
import authRoutes from './routes/auth.routes';
import scheduleRoutes from './routes/schedule.routes';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/schedules', scheduleRoutes);

// Error handlers
app.use(notFoundHandler);
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## Testing the API

### 1. Register User
```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "firstName": "Test",
    "lastName": "User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Create Schedule
```bash
curl -X POST http://localhost:3000/api/v1/schedules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Team Meeting",
    "startTime": "2024-01-15T10:00:00Z",
    "endTime": "2024-01-15T11:00:00Z",
    "type": "MEETING",
    "participants": [{"userId": "user-uuid", "isRequired": true}]
  }'
```

## Common Issues & Solutions

### Issue: Prisma Client Not Generated
```bash
npx prisma generate
```

### Issue: Database Connection Failed
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify credentials

### Issue: JWT Secret Too Short
- Ensure JWT_SECRET is at least 32 characters

### Issue: TypeScript Compilation Errors
```bash
npm run build
# Fix errors shown
```

## Development Workflow

```bash
# Terminal 1: Run development server
npm run dev

# Terminal 2: Watch tests
npm run test:watch

# Terminal 3: Prisma Studio (database GUI)
npm run prisma:studio
```

## Production Deployment

### Using Docker

**Dockerfile**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
RUN npx prisma generate
EXPOSE 3000
CMD ["npm", "start"]
```

**Build and run**:
```bash
docker build -t schedule-api .
docker run -p 3000:3000 --env-file .env schedule-api
```

## Next Steps

1. Review all documentation in `/docs/backend/`
2. Follow implementation order above
3. Write tests alongside features
4. Use hooks for coordination with frontend team
5. Store progress in memory for team visibility

## Resources

- **Prisma Docs**: https://www.prisma.io/docs
- **Express Guide**: https://expressjs.com/
- **Zod Validation**: https://zod.dev/
- **JWT.io**: https://jwt.io/

## Support

For questions about the implementation plan:
1. Check documentation in `/docs/backend/`
2. Query memory: `npx claude-flow@alpha memory query "backend"`
3. Review implementation examples in each doc
