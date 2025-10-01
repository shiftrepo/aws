# Available Time Slot Calculation Logic

## Overview

The time slot calculation algorithm finds available meeting times when all required participants are free. This is a complex scheduling problem that requires:

1. **Availability aggregation**: Combine multiple users' availability
2. **Busy time exclusion**: Remove scheduled time blocks
3. **Working hours respect**: Consider user-defined working hours
4. **Timezone conversion**: Handle users in different timezones
5. **Duration matching**: Find slots that fit the required duration
6. **Buffer time**: Optional padding between meetings

## Core Algorithms

### 1. Time Slot Finder Service

```typescript
// src/services/time-slot-finder.service.ts

import { PrismaClient } from '@prisma/client';
import { ConflictDetectionService } from './conflict-detection.service';
import { mergeTimeRanges, TimeRange } from '../utils/time-overlap.util';
import { DateTime } from 'luxon';

const prisma = new PrismaClient();

export interface FindSlotsParams {
  userIds: string[];
  startDate: Date;
  endDate: Date;
  duration: number; // in minutes
  timezone: string;
  bufferTime?: number; // in minutes (default: 0)
  workingHoursOnly?: boolean; // default: true
  minSlots?: number; // minimum slots to return (default: 5)
}

export interface TimeSlot {
  startTime: Date;
  endTime: Date;
  availableUsers: string[];
  score: number; // 0-1, higher is better
}

export class TimeSlotFinderService {
  /**
   * Find available time slots for multiple users
   */
  static async findAvailableSlots(
    params: FindSlotsParams
  ): Promise<TimeSlot[]> {
    const {
      userIds,
      startDate,
      endDate,
      duration,
      timezone,
      bufferTime = 0,
      workingHoursOnly = true,
      minSlots = 5,
    } = params;

    // Step 1: Get all users' availabilities and busy times
    const userAvailabilityMap = new Map<string, TimeRange[]>();
    const userBusyTimesMap = new Map<string, TimeRange[]>();

    for (const userId of userIds) {
      // Get user's working hours
      const availabilities = await this.getUserAvailability(
        userId,
        startDate,
        endDate
      );
      userAvailabilityMap.set(userId, availabilities);

      // Get user's busy times
      const busyTimes = await ConflictDetectionService.getUserBusyTimes(
        userId,
        startDate,
        endDate
      );
      userBusyTimesMap.set(userId, busyTimes);
    }

    // Step 2: Find common availability windows
    const commonAvailability = this.findCommonAvailability(
      userAvailabilityMap,
      workingHoursOnly
    );

    // Step 3: Remove busy times from availability
    const freeSlots = this.excludeBusyTimes(
      commonAvailability,
      userBusyTimesMap,
      bufferTime
    );

    // Step 4: Split into slots of required duration
    const availableSlots = this.generateSlots(freeSlots, duration, bufferTime);

    // Step 5: Score and rank slots
    const rankedSlots = this.scoreSlots(availableSlots, userIds.length);

    // Return top slots
    return rankedSlots.slice(0, Math.max(minSlots, 10));
  }

  /**
   * Get user's availability windows for a date range
   */
  private static async getUserAvailability(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<TimeRange[]> {
    const user = await prisma.user.findUnique({
      where: { id: userId },
      include: {
        availabilities: true,
      },
    });

    if (!user) {
      throw new Error(`User ${userId} not found`);
    }

    const availabilities: TimeRange[] = [];

    // Convert date range to user's timezone
    const userTimezone = user.timezone || 'UTC';
    let currentDate = DateTime.fromJSDate(startDate).setZone(userTimezone);
    const endDateTime = DateTime.fromJSDate(endDate).setZone(userTimezone);

    // Iterate through each day in the range
    while (currentDate <= endDateTime) {
      const dayOfWeek = currentDate.weekday % 7; // Luxon uses 1-7, we need 0-6

      // Find availability for this day of week
      const dayAvailability = user.availabilities.filter(
        (av) => av.dayOfWeek === dayOfWeek && av.isAvailable
      );

      for (const av of dayAvailability) {
        // Parse time strings (HH:mm)
        const [startHour, startMinute] = av.startTime.split(':').map(Number);
        const [endHour, endMinute] = av.endTime.split(':').map(Number);

        // Create datetime for this availability
        const startTime = currentDate
          .set({ hour: startHour, minute: startMinute, second: 0 })
          .toJSDate();

        const endTime = currentDate
          .set({ hour: endHour, minute: endMinute, second: 0 })
          .toJSDate();

        availabilities.push({ startTime, endTime });
      }

      currentDate = currentDate.plus({ days: 1 });
    }

    return mergeTimeRanges(availabilities);
  }

  /**
   * Find time ranges where all users are available
   */
  private static findCommonAvailability(
    userAvailabilityMap: Map<string, TimeRange[]>,
    workingHoursOnly: boolean
  ): TimeRange[] {
    const userIds = Array.from(userAvailabilityMap.keys());

    if (userIds.length === 0) {
      return [];
    }

    // Start with first user's availability
    let commonRanges = userAvailabilityMap.get(userIds[0]) || [];

    // Intersect with each subsequent user's availability
    for (let i = 1; i < userIds.length; i++) {
      const userRanges = userAvailabilityMap.get(userIds[i]) || [];
      commonRanges = this.intersectTimeRanges(commonRanges, userRanges);
    }

    return commonRanges;
  }

  /**
   * Find intersection of two sets of time ranges
   */
  private static intersectTimeRanges(
    ranges1: TimeRange[],
    ranges2: TimeRange[]
  ): TimeRange[] {
    const intersections: TimeRange[] = [];

    for (const range1 of ranges1) {
      for (const range2 of ranges2) {
        // Check if ranges overlap
        if (range1.startTime < range2.endTime && range2.startTime < range1.endTime) {
          // Calculate intersection
          const startTime = new Date(
            Math.max(range1.startTime.getTime(), range2.startTime.getTime())
          );
          const endTime = new Date(
            Math.min(range1.endTime.getTime(), range2.endTime.getTime())
          );

          intersections.push({ startTime, endTime });
        }
      }
    }

    return mergeTimeRanges(intersections);
  }

  /**
   * Remove busy times from available ranges
   */
  private static excludeBusyTimes(
    availableRanges: TimeRange[],
    busyTimesMap: Map<string, TimeRange[]>,
    bufferTime: number
  ): TimeRange[] {
    let freeRanges = [...availableRanges];

    // Combine all busy times from all users
    const allBusyTimes: TimeRange[] = [];
    for (const busyTimes of busyTimesMap.values()) {
      for (const busyTime of busyTimes) {
        // Add buffer time around busy times
        allBusyTimes.push({
          startTime: new Date(busyTime.startTime.getTime() - bufferTime * 60000),
          endTime: new Date(busyTime.endTime.getTime() + bufferTime * 60000),
        });
      }
    }

    const mergedBusyTimes = mergeTimeRanges(allBusyTimes);

    // Subtract each busy time from available ranges
    for (const busyTime of mergedBusyTimes) {
      freeRanges = this.subtractTimeRange(freeRanges, busyTime);
    }

    return freeRanges;
  }

  /**
   * Subtract a time range from a set of ranges
   */
  private static subtractTimeRange(
    ranges: TimeRange[],
    subtract: TimeRange
  ): TimeRange[] {
    const result: TimeRange[] = [];

    for (const range of ranges) {
      // No overlap - keep the range
      if (
        range.endTime <= subtract.startTime ||
        range.startTime >= subtract.endTime
      ) {
        result.push(range);
        continue;
      }

      // Subtract overlaps completely - skip this range
      if (
        range.startTime >= subtract.startTime &&
        range.endTime <= subtract.endTime
      ) {
        continue;
      }

      // Subtract overlaps start - keep the end part
      if (
        range.startTime >= subtract.startTime &&
        range.endTime > subtract.endTime
      ) {
        result.push({
          startTime: subtract.endTime,
          endTime: range.endTime,
        });
        continue;
      }

      // Subtract overlaps end - keep the start part
      if (
        range.startTime < subtract.startTime &&
        range.endTime <= subtract.endTime
      ) {
        result.push({
          startTime: range.startTime,
          endTime: subtract.startTime,
        });
        continue;
      }

      // Subtract is in the middle - split into two ranges
      if (
        range.startTime < subtract.startTime &&
        range.endTime > subtract.endTime
      ) {
        result.push({
          startTime: range.startTime,
          endTime: subtract.startTime,
        });
        result.push({
          startTime: subtract.endTime,
          endTime: range.endTime,
        });
      }
    }

    return result;
  }

  /**
   * Generate individual time slots from free ranges
   */
  private static generateSlots(
    freeRanges: TimeRange[],
    duration: number,
    bufferTime: number
  ): TimeSlot[] {
    const slots: TimeSlot[] = [];
    const slotDuration = (duration + bufferTime) * 60000; // Convert to milliseconds

    for (const range of freeRanges) {
      const rangeStart = range.startTime.getTime();
      const rangeEnd = range.endTime.getTime();

      // Generate slots within this range
      let currentStart = rangeStart;

      while (currentStart + slotDuration <= rangeEnd) {
        slots.push({
          startTime: new Date(currentStart),
          endTime: new Date(currentStart + duration * 60000), // Without buffer
          availableUsers: [], // Will be filled later
          score: 0, // Will be calculated later
        });

        // Move to next slot (with buffer)
        currentStart += slotDuration;
      }
    }

    return slots;
  }

  /**
   * Score and rank time slots based on various factors
   */
  private static scoreSlots(
    slots: TimeSlot[],
    totalUsers: number
  ): TimeSlot[] {
    const now = new Date();

    return slots
      .map((slot) => {
        let score = 1.0;

        // Factor 1: Prefer slots during typical working hours (9 AM - 5 PM)
        const hour = slot.startTime.getHours();
        if (hour >= 9 && hour < 17) {
          score += 0.2;
        } else if (hour >= 8 && hour < 18) {
          score += 0.1;
        }

        // Factor 2: Prefer slots earlier in the day (morning focus)
        if (hour >= 9 && hour < 12) {
          score += 0.15;
        }

        // Factor 3: Prefer slots not too far in the future
        const daysAway = (slot.startTime.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
        if (daysAway <= 7) {
          score += 0.1;
        }

        // Factor 4: Avoid slots right before lunch or end of day
        if (hour === 11 || hour === 16) {
          score -= 0.1;
        }

        // Factor 5: Prefer weekdays over weekends
        const dayOfWeek = slot.startTime.getDay();
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {
          score += 0.1;
        }

        return { ...slot, score };
      })
      .sort((a, b) => b.score - a.score);
  }

  /**
   * Find optimal meeting time (highest score)
   */
  static async findOptimalSlot(params: FindSlotsParams): Promise<TimeSlot | null> {
    const slots = await this.findAvailableSlots(params);
    return slots.length > 0 ? slots[0] : null;
  }

  /**
   * Check if a specific time slot is available for all users
   */
  static async isSlotAvailable(
    userIds: string[],
    startTime: Date,
    endTime: Date
  ): Promise<boolean> {
    const result = await ConflictDetectionService.checkConflicts({
      userIds,
      startTime,
      endTime,
    });

    return !result.hasConflicts;
  }
}
```

### 2. Smart Scheduling Algorithm

```typescript
// src/services/smart-scheduler.service.ts

import { TimeSlotFinderService } from './time-slot-finder.service';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export interface SmartScheduleParams {
  title: string;
  duration: number;
  participants: string[];
  preferredDays?: number[]; // 0-6 (Sun-Sat)
  preferredTimeRange?: {
    startHour: number;
    endHour: number;
  };
  deadline?: Date; // Must be scheduled before this date
  priority?: 'low' | 'medium' | 'high';
}

export class SmartSchedulerService {
  /**
   * Automatically find and suggest best meeting times
   */
  static async suggestMeetingTimes(
    params: SmartScheduleParams
  ): Promise<TimeSlot[]> {
    const {
      duration,
      participants,
      preferredDays,
      preferredTimeRange,
      deadline,
    } = params;

    // Calculate search range
    const startDate = new Date();
    const endDate = deadline || new Date(Date.now() + 14 * 24 * 60 * 60 * 1000); // 2 weeks

    // Find available slots
    const slots = await TimeSlotFinderService.findAvailableSlots({
      userIds: participants,
      startDate,
      endDate,
      duration,
      timezone: 'UTC', // Will be converted per user
      minSlots: 10,
    });

    // Filter by preferences
    let filteredSlots = slots;

    if (preferredDays && preferredDays.length > 0) {
      filteredSlots = filteredSlots.filter((slot) =>
        preferredDays.includes(slot.startTime.getDay())
      );
    }

    if (preferredTimeRange) {
      filteredSlots = filteredSlots.filter((slot) => {
        const hour = slot.startTime.getHours();
        return (
          hour >= preferredTimeRange.startHour &&
          hour < preferredTimeRange.endHour
        );
      });
    }

    return filteredSlots.slice(0, 5);
  }

  /**
   * Auto-schedule a meeting at the best available time
   */
  static async autoSchedule(params: SmartScheduleParams): Promise<string> {
    const slots = await this.suggestMeetingTimes(params);

    if (slots.length === 0) {
      throw new Error('No available time slots found');
    }

    // Use the highest-scored slot
    const bestSlot = slots[0];

    // Create the schedule
    const schedule = await prisma.schedule.create({
      data: {
        title: params.title,
        startTime: bestSlot.startTime,
        endTime: bestSlot.endTime,
        type: 'MEETING',
        status: 'SCHEDULED',
        createdBy: params.participants[0], // First participant is organizer
        participants: {
          create: params.participants.map((userId) => ({
            userId,
            status: 'PENDING',
            isRequired: true,
          })),
        },
      },
    });

    return schedule.id;
  }
}
```

### 3. Time Slot Controller

```typescript
// src/controllers/time-slot.controller.ts

import { Request, Response } from 'express';
import { z } from 'zod';
import { TimeSlotFinderService } from '../services/time-slot-finder.service';

const findSlotsSchema = z.object({
  userIds: z.array(z.string().uuid()),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  duration: z.number().min(15).max(480), // 15 min to 8 hours
  timezone: z.string(),
  bufferTime: z.number().min(0).max(60).optional(),
  workingHoursOnly: z.boolean().optional(),
});

export class TimeSlotController {
  static async findSlots(req: Request, res: Response): Promise<void> {
    try {
      const data = findSlotsSchema.parse(req.body);

      const slots = await TimeSlotFinderService.findAvailableSlots({
        userIds: data.userIds,
        startDate: new Date(data.startDate),
        endDate: new Date(data.endDate),
        duration: data.duration,
        timezone: data.timezone,
        bufferTime: data.bufferTime,
        workingHoursOnly: data.workingHoursOnly,
      });

      res.json({
        success: true,
        data: { slots },
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
          message: 'Failed to find time slots',
        },
      });
    }
  }
}
```

## Algorithm Complexity

- **Find Available Slots**: O(d * u * (a + b)) where:
  - d = days in search range
  - u = number of users
  - a = availability records per user
  - b = busy times per user

- **Time Range Intersection**: O(n * m) where n and m are range counts
- **Slot Generation**: O(r * s) where r is free ranges, s is slots per range

## Performance Optimization

### 1. Parallel Processing

```typescript
// Process users in parallel
const userDataPromises = userIds.map(async (userId) => {
  const [availability, busyTimes] = await Promise.all([
    getUserAvailability(userId, startDate, endDate),
    ConflictDetectionService.getUserBusyTimes(userId, startDate, endDate),
  ]);
  return { userId, availability, busyTimes };
});

const userData = await Promise.all(userDataPromises);
```

### 2. Caching

```typescript
// Cache availability patterns
const cacheKey = `availability:${userId}:${dayOfWeek}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);
```

### 3. Early Termination

```typescript
// Stop searching after finding enough slots
if (slots.length >= minSlots) break;
```

## Testing

```typescript
describe('TimeSlotFinderService', () => {
  it('should find common available slots', async () => {
    const slots = await TimeSlotFinderService.findAvailableSlots({
      userIds: ['user-1', 'user-2'],
      startDate: new Date('2024-01-15'),
      endDate: new Date('2024-01-19'),
      duration: 60,
      timezone: 'America/New_York',
    });

    expect(slots.length).toBeGreaterThan(0);
    expect(slots[0].score).toBeGreaterThan(0);
  });
});
```
