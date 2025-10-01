# Database Models and Relationships

## Entity Relationship Overview

```
User (1) ──────── (N) Schedule
User (1) ──────── (N) Availability
User (1) ──────── (N) TeamMember
Team (1) ──────── (N) TeamMember
Team (1) ──────── (N) Schedule
Schedule (1) ──── (N) ScheduleParticipant
```

## Prisma Schema

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// User model
model User {
  id                String                @id @default(uuid())
  email             String                @unique
  password          String
  firstName         String
  lastName          String
  role              UserRole              @default(MEMBER)
  timezone          String                @default("UTC")
  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  // Relations
  schedules         Schedule[]
  availabilities    Availability[]
  teamMemberships   TeamMember[]
  participations    ScheduleParticipant[]

  @@index([email])
  @@map("users")
}

enum UserRole {
  ADMIN
  MANAGER
  MEMBER
}

// Team model
model Team {
  id          String       @id @default(uuid())
  name        String
  description String?
  createdBy   String
  isActive    Boolean      @default(true)
  createdAt   DateTime     @default(now())
  updatedAt   DateTime     @updatedAt

  // Relations
  members     TeamMember[]
  schedules   Schedule[]

  @@index([createdBy])
  @@map("teams")
}

// Team membership model
model TeamMember {
  id        String   @id @default(uuid())
  teamId    String
  userId    String
  role      TeamRole @default(MEMBER)
  joinedAt  DateTime @default(now())

  // Relations
  team      Team     @relation(fields: [teamId], references: [id], onDelete: Cascade)
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([teamId, userId])
  @@index([userId])
  @@index([teamId])
  @@map("team_members")
}

enum TeamRole {
  OWNER
  ADMIN
  MEMBER
}

// Schedule/Event model
model Schedule {
  id              String                @id @default(uuid())
  title           String
  description     String?
  startTime       DateTime
  endTime         DateTime
  location        String?
  isRecurring     Boolean               @default(false)
  recurrenceRule  String?               // RRULE format
  createdBy       String
  teamId          String?
  type            ScheduleType          @default(MEETING)
  status          ScheduleStatus        @default(SCHEDULED)
  createdAt       DateTime              @default(now())
  updatedAt       DateTime              @updatedAt

  // Relations
  creator         User                  @relation(fields: [createdBy], references: [id])
  team            Team?                 @relation(fields: [teamId], references: [id], onDelete: Cascade)
  participants    ScheduleParticipant[]

  @@index([createdBy])
  @@index([teamId])
  @@index([startTime, endTime])
  @@map("schedules")
}

enum ScheduleType {
  MEETING
  APPOINTMENT
  TASK
  EVENT
  BREAK
}

enum ScheduleStatus {
  SCHEDULED
  CANCELLED
  COMPLETED
  IN_PROGRESS
}

// Schedule participants
model ScheduleParticipant {
  id          String              @id @default(uuid())
  scheduleId  String
  userId      String
  status      ParticipantStatus   @default(PENDING)
  isRequired  Boolean             @default(true)
  addedAt     DateTime            @default(now())

  // Relations
  schedule    Schedule            @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  user        User                @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([scheduleId, userId])
  @@index([userId])
  @@index([scheduleId])
  @@map("schedule_participants")
}

enum ParticipantStatus {
  PENDING
  ACCEPTED
  DECLINED
  TENTATIVE
}

// User availability
model Availability {
  id          String          @id @default(uuid())
  userId      String
  dayOfWeek   Int             // 0-6 (Sunday-Saturday)
  startTime   String          // HH:mm format
  endTime     String          // HH:mm format
  isAvailable Boolean         @default(true)
  effectiveFrom DateTime?
  effectiveUntil DateTime?
  createdAt   DateTime        @default(now())
  updatedAt   DateTime        @updatedAt

  // Relations
  user        User            @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, dayOfWeek])
  @@map("availabilities")
}
```

## Model Descriptions

### User
- **Purpose**: Store user account information
- **Key Fields**: email (unique), password (hashed), role, timezone
- **Relationships**: Has many schedules, availabilities, team memberships

### Team
- **Purpose**: Group users for collaborative scheduling
- **Key Fields**: name, description, createdBy, isActive
- **Relationships**: Has many members and schedules

### TeamMember
- **Purpose**: Junction table for user-team relationships
- **Key Fields**: teamId, userId, role
- **Unique Constraint**: One user can only be in a team once

### Schedule
- **Purpose**: Store events/meetings/appointments
- **Key Fields**: title, startTime, endTime, recurrenceRule
- **Relationships**: Belongs to user (creator) and team, has many participants
- **Indexes**: On startTime/endTime for efficient querying

### ScheduleParticipant
- **Purpose**: Junction table for schedule-user relationships
- **Key Fields**: scheduleId, userId, status, isRequired
- **Statuses**: PENDING, ACCEPTED, DECLINED, TENTATIVE

### Availability
- **Purpose**: Store user's regular availability patterns
- **Key Fields**: dayOfWeek, startTime, endTime, isAvailable
- **Use Case**: Define working hours, lunch breaks, recurring unavailability

## Key Design Decisions

### 1. UUID Primary Keys
- Better for distributed systems
- No sequential ID leakage
- Easier for merging data

### 2. Soft Deletes via Status
- `isActive` flags for teams
- `status` for schedules (CANCELLED vs deleted)
- Preserves audit trail

### 3. Timezone Handling
- Store user's timezone preference
- Store all datetime in UTC
- Convert at application layer

### 4. Recurrence Rules
- Store RRULE format (RFC 5545)
- Parse with rrule.js or similar
- Generate instances on-demand

### 5. Indexes
- Composite index on startTime/endTime for range queries
- Foreign key indexes for join performance
- Email index for auth lookups

## Migration Strategy

### Initial Migration
```bash
npx prisma migrate dev --name init
```

### Seed Data
```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  const hashedPassword = await bcrypt.hash('admin123', 10);

  // Create admin user
  const admin = await prisma.user.create({
    data: {
      email: 'admin@example.com',
      password: hashedPassword,
      firstName: 'Admin',
      lastName: 'User',
      role: 'ADMIN',
      timezone: 'America/New_York',
    },
  });

  // Create sample team
  const team = await prisma.team.create({
    data: {
      name: 'Engineering Team',
      description: 'Software development team',
      createdBy: admin.id,
    },
  });

  console.log('Seed data created successfully');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

## Performance Optimization

### Query Optimization
```typescript
// Use select to limit returned fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    email: true,
    firstName: true,
    lastName: true,
  },
});

// Use include for eager loading
const schedule = await prisma.schedule.findUnique({
  where: { id: scheduleId },
  include: {
    participants: {
      include: {
        user: {
          select: {
            id: true,
            email: true,
            firstName: true,
            lastName: true,
          },
        },
      },
    },
  },
});
```

### Connection Pooling
```typescript
// prisma/client.ts
import { PrismaClient } from '@prisma/client';

export const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  log: ['query', 'error', 'warn'],
});
```
