export class DateFormatter {
  static formatDate(date: Date, format: 'short' | 'long' | 'iso' = 'short'): string {
    if (!(date instanceof Date) || isNaN(date.getTime())) {
      throw new Error('Invalid date');
    }

    switch (format) {
      case 'short':
        return this.formatShort(date);
      case 'long':
        return this.formatLong(date);
      case 'iso':
        return date.toISOString();
      default:
        return this.formatShort(date);
    }
  }

  private static formatShort(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private static formatLong(date: Date): string {
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString('en-US', options);
  }

  static parseDate(dateString: string): Date {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      throw new Error(`Invalid date string: ${dateString}`);
    }
    return date;
  }

  static isValidDate(date: any): boolean {
    return date instanceof Date && !isNaN(date.getTime());
  }

  static getDaysDifference(date1: Date, date2: Date): number {
    if (!this.isValidDate(date1) || !this.isValidDate(date2)) {
      throw new Error('Invalid dates provided');
    }

    const msPerDay = 24 * 60 * 60 * 1000;
    const utc1 = Date.UTC(date1.getFullYear(), date1.getMonth(), date1.getDate());
    const utc2 = Date.UTC(date2.getFullYear(), date2.getMonth(), date2.getDate());

    return Math.floor((utc2 - utc1) / msPerDay);
  }

  static addDays(date: Date, days: number): Date {
    if (!this.isValidDate(date)) {
      throw new Error('Invalid date');
    }

    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  static getYearsSince(date: Date): number {
    if (!this.isValidDate(date)) {
      throw new Error('Invalid date');
    }

    const now = new Date();
    let years = now.getFullYear() - date.getFullYear();

    if (
      now.getMonth() < date.getMonth() ||
      (now.getMonth() === date.getMonth() && now.getDate() < date.getDate())
    ) {
      years--;
    }

    return years;
  }
}
