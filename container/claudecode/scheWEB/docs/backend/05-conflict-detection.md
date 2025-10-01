# Schedule Conflict Detection Algorithms

## Overview

Conflict detection identifies overlapping schedules to prevent double-booking and scheduling conflicts. The system must handle:

1. **Time overlap detection**: Check if two time ranges overlap
2. **User conflicts**: Detect when a user has multiple events at the same time
3. **Required participant conflicts**: Identify conflicts for required attendees
4. **Recurring event conflicts**: Handle recurring schedule patterns
5. **Timezone handling**: Convert times to UTC for comparison

## Core Algorithms

### 1. Time Overlap Detection

```typescript
// src/utils/time-overlap.util.ts

export interface TimeRange {
  startTime: Date;
  endTime: Date;
}

/**
 * Check if two time ranges overlap
 * Two ranges overlap if one starts before the other ends
 */
export function hasTimeOverlap(range1: TimeRange, range2: TimeRange): boolean {
  return range1.startTime < range2.endTime && range2.startTime < range1.endTime;
}

/**
 * Check if a time range is completely within another
 */
export function isTimeRangeWithin(inner: TimeRange, outer: TimeRange): boolean {
  return inner.startTime >= outer.startTime && inner.endTime <= outer.endTime;
}

/**
 * Calculate overlap duration in minutes
 */
export function getOverlapDuration(range1: TimeRange, range2: TimeRange): number {
  if (!hasTimeOverlap(range1, range2)) {
    return 0;
  }

  const overlapStart = range1.startTime > range2.startTime
    ? range1.startTime
    : range2.startTime;

  const overlapEnd = range1.endTime < range2.endTime
    ? range1.endTime
    : range2.endTime;

  return (overlapEnd.getTime() - overlapStart.getTime()) / (1000 * 60);
}

/**
 * Merge overlapping time ranges
 */
export function mergeTimeRanges(ranges: TimeRange[]): TimeRange[] {
  if (ranges.length === 0) return [];

  // Sort by start time
  const sorted = [...ranges].sort((a, b) =>
    a.startTime.getTime() - b.startTime.getTime()
  );

  const merged: TimeRange[] = [sorted[0]];

  for (let i = 1; i < sorted.length; i++) {
    const current = sorted[i];
    const last = merged[merged.length - 1];

    if (hasTimeOverlap(current, last)) {
      // Merge overlapping ranges
      last.endTime = new Date(
        Math.max(last.endTime.getTime(), current.endTime.getTime())
      );
    } else {
      merged.push(current);
    }
  }

  return merged;
}
```

### 2. Conflict Detection Service

```typescript
// src/services/conflict-detection.service.ts

import { PrismaClient } from '@prisma/client';
import { hasTimeOverlap } from '../utils/time-overlap.util';

const prisma = new PrismaClient();

export interface ConflictCheckParams {
  userIds: string[];
  startTime: Date;
  endTime: Date;
  excludeScheduleId?: string;
}

export interface Conflict {
  userId: string;
  schedule: {
    id: string;
    title: string;
    startTime: Date;
    endTime: Date;
    type: string;
  };
}

export interface ConflictCheckResult {
  hasConflicts: boolean;
  conflicts: Conflict[];
}

export class ConflictDetectionService {
  /**
   * Check for scheduling conflicts for multiple users
   */
  static async checkConflicts(
    params: ConflictCheckParams
  ): Promise<ConflictCheckResult> {
    const { userIds, startTime, endTime, excludeScheduleId } = params;

    // Query all schedules for users in the time range
    const schedules = await prisma.schedule.findMany({
      where: {
        AND: [
          {
            participants: {
              some: {
                userId: { in: userIds },
                status: { in: ['ACCEPTED', 'PENDING'] },
              },
            },
          },
          {
            status: { not: 'CANCELLED' },
          },
          {
            OR: [
              // Schedule starts during the new time range
              {
                startTime: {
                  gte: startTime,
                  lt: endTime,
                },
              },
              // Schedule ends during the new time range
              {
                endTime: {
                  gt: startTime,
                  lte: endTime,
                },
              },
              // Schedule completely encompasses the new time range
              {
                AND: [
                  { startTime: { lte: startTime } },
                  { endTime: { gte: endTime } },
                ],
              },
            ],
          },
        ],
      },
      include: {
        participants: {
          where: {
            userId: { in: userIds },
          },
        },
      },
    });

    // Filter out the schedule being edited (if any)
    const conflictingSchedules = schedules.filter(
      (schedule) => schedule.id !== excludeScheduleId
    );

    // Build conflict list
    const conflicts: Conflict[] = [];

    for (const schedule of conflictingSchedules) {
      for (const participant of schedule.participants) {
        conflicts.push({
          userId: participant.userId,
          schedule: {
            id: schedule.id,
            title: schedule.title,
            startTime: schedule.startTime,
            endTime: schedule.endTime,
            type: schedule.type,
          },
        });
      }
    }

    return {
      hasConflicts: conflicts.length > 0,
      conflicts,
    };
  }

  /**
   * Check if a user is available during a time range
   */
  static async isUserAvailable(
    userId: string,
    startTime: Date,
    endTime: Date
  ): Promise<boolean> {
    const result = await this.checkConflicts({
      userIds: [userId],
      startTime,
      endTime,
    });

    return !result.hasConflicts;
  }

  /**
   * Get user's busy time ranges for a date range
   */
  static async getUserBusyTimes(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<TimeRange[]> {
    const schedules = await prisma.schedule.findMany({
      where: {
        participants: {
          some: {
            userId,
            status: { in: ['ACCEPTED', 'PENDING'] },
          },
        },
        status: { not: 'CANCELLED' },
        startTime: { gte: startDate },
        endTime: { lte: endDate },
      },
      select: {
        startTime: true,
        endTime: true,
      },
      orderBy: {
        startTime: 'asc',
      },
    });

    return schedules.map((schedule) => ({
      startTime: schedule.startTime,
      endTime: schedule.endTime,
    }));
  }

  /**
   * Check conflicts for recurring events
   */
  static async checkRecurringConflicts(
    userIds: string[],
    occurrences: TimeRange[]
  ): Promise<Map<number, ConflictCheckResult>> {
    const conflictMap = new Map<number, ConflictCheckResult>();

    // Check each occurrence separately
    for (let i = 0; i < occurrences.length; i++) {
      const occurrence = occurrences[i];
      const result = await this.checkConflicts({
        userIds,
        startTime: occurrence.startTime,
        endTime: occurrence.endTime,
      });

      if (result.hasConflicts) {
        conflictMap.set(i, result);
      }
    }

    return conflictMap;
  }

  /**
   * Get conflict summary for multiple users
   */
  static async getConflictSummary(
    userIds: string[],
    startTime: Date,
    endTime: Date
  ): Promise<{
    totalConflicts: number;
    userConflictCounts: Map<string, number>;
    criticalUsers: string[]; // Users with most conflicts
  }> {
    const result = await this.checkConflicts({ userIds, startTime, endTime });

    const userConflictCounts = new Map<string, number>();

    for (const conflict of result.conflicts) {
      const count = userConflictCounts.get(conflict.userId) || 0;
      userConflictCounts.set(conflict.userId, count + 1);
    }

    // Find users with most conflicts
    const criticalUsers = Array.from(userConflictCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([userId]) => userId);

    return {
      totalConflicts: result.conflicts.length,
      userConflictCounts,
      criticalUsers,
    };
  }
}
```

### 3. Recurring Event Expansion

```typescript
// src/utils/recurrence.util.ts

import { RRule, RRuleSet, rrulestr } from 'rrule';

export interface RecurrenceOptions {
  rrule: string; // RRULE string
  dtstart: Date; // Start datetime of first occurrence
  duration: number; // Duration in minutes
  until?: Date; // Optional end date
  count?: number; // Optional occurrence count
}

/**
 * Generate occurrence dates from RRULE
 */
export function generateOccurrences(options: RecurrenceOptions): Date[] {
  const { rrule, dtstart, until, count } = options;

  try {
    const rule = rrulestr(rrule, {
      dtstart,
    });

    // Generate occurrences
    if (count) {
      return rule.all((date, i) => i < count);
    } else if (until) {
      return rule.between(dtstart, until, true);
    } else {
      // Default: next 100 occurrences
      return rule.all((date, i) => i < 100);
    }
  } catch (error) {
    throw new Error(`Invalid RRULE: ${rrule}`);
  }
}

/**
 * Convert occurrence dates to time ranges
 */
export function occurrencesToTimeRanges(
  occurrenceDates: Date[],
  duration: number
): TimeRange[] {
  return occurrenceDates.map((startTime) => ({
    startTime,
    endTime: new Date(startTime.getTime() + duration * 60 * 1000),
  }));
}

/**
 * Check if a recurring event has conflicts
 */
export async function checkRecurringEventConflicts(
  userIds: string[],
  options: RecurrenceOptions
): Promise<{
  hasConflicts: boolean;
  conflictOccurrences: number[];
  totalOccurrences: number;
}> {
  const occurrenceDates = generateOccurrences(options);
  const timeRanges = occurrencesToTimeRanges(occurrenceDates, options.duration);

  const conflictMap = await ConflictDetectionService.checkRecurringConflicts(
    userIds,
    timeRanges
  );

  return {
    hasConflicts: conflictMap.size > 0,
    conflictOccurrences: Array.from(conflictMap.keys()),
    totalOccurrences: occurrenceDates.length,
  };
}

/**
 * Common RRULE patterns
 */
export const RecurrencePatterns = {
  DAILY: 'FREQ=DAILY',
  WEEKDAYS: 'FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR',
  WEEKLY: 'FREQ=WEEKLY',
  BIWEEKLY: 'FREQ=WEEKLY;INTERVAL=2',
  MONTHLY: 'FREQ=MONTHLY',
  YEARLY: 'FREQ=YEARLY',
};
```

### 4. Conflict Detection Controller

```typescript
// src/controllers/conflict.controller.ts

import { Request, Response } from 'express';
import { z } from 'zod';
import { ConflictDetectionService } from '../services/conflict-detection.service';

const checkConflictsSchema = z.object({
  userIds: z.array(z.string().uuid()),
  startTime: z.string().datetime(),
  endTime: z.string().datetime(),
  excludeScheduleId: z.string().uuid().optional(),
});

export class ConflictController {
  static async checkConflicts(req: Request, res: Response): Promise<void> {
    try {
      const data = checkConflictsSchema.parse(req.body);

      const result = await ConflictDetectionService.checkConflicts({
        userIds: data.userIds,
        startTime: new Date(data.startTime),
        endTime: new Date(data.endTime),
        excludeScheduleId: data.excludeScheduleId,
      });

      res.json({
        success: true,
        data: result,
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
          message: 'Failed to check conflicts',
        },
      });
    }
  }
}
```

## Performance Optimization

### 1. Database Indexes

```sql
-- Index on schedule time range for efficient range queries
CREATE INDEX idx_schedules_time_range ON schedules(start_time, end_time);

-- Index on schedule status
CREATE INDEX idx_schedules_status ON schedules(status);

-- Composite index for participant queries
CREATE INDEX idx_schedule_participants_user_status
ON schedule_participants(user_id, status);
```

### 2. Caching Strategy

```typescript
// Cache user busy times for frequently checked users
import { Redis } from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export async function getCachedBusyTimes(
  userId: string,
  startDate: Date,
  endDate: Date
): Promise<TimeRange[] | null> {
  const cacheKey = `busy_times:${userId}:${startDate.toISOString()}:${endDate.toISOString()}`;

  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  const busyTimes = await ConflictDetectionService.getUserBusyTimes(
    userId,
    startDate,
    endDate
  );

  // Cache for 5 minutes
  await redis.setex(cacheKey, 300, JSON.stringify(busyTimes));

  return busyTimes;
}
```

## Algorithm Complexity

- **Time Overlap Check**: O(1) - constant time comparison
- **Single User Conflict**: O(n) - where n is number of user's schedules in range
- **Multiple User Conflict**: O(u * n) - where u is users, n is schedules per user
- **Recurring Event Check**: O(o * u * n) - where o is occurrences

## Testing Conflict Detection

```typescript
// tests/conflict-detection.test.ts

describe('ConflictDetectionService', () => {
  it('should detect overlapping schedules', async () => {
    const result = await ConflictDetectionService.checkConflicts({
      userIds: ['user-1'],
      startTime: new Date('2024-01-15T10:00:00Z'),
      endTime: new Date('2024-01-15T11:00:00Z'),
    });

    expect(result.hasConflicts).toBe(true);
  });

  it('should not detect conflicts for different users', async () => {
    // Test implementation
  });

  it('should handle timezone conversions correctly', async () => {
    // Test implementation
  });
});
```
