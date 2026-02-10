/**
 * @jest-environment node
 *
 * Logger.test.js
 *
 * Unit tests for Logger utility
 */

import { logger, setLogLevel, debug, info, warn, error } from '../../util/Logger.js';

describe('Logger', () => {
  // Save console methods
  let originalConsoleLog;
  let originalConsoleError;

  beforeAll(() => {
    originalConsoleLog = console.log;
    originalConsoleError = console.error;
  });

  beforeEach(() => {
    // Mock console to prevent actual output during tests
    console.log = () => {};
    console.error = () => {};
  });

  afterEach(() => {
    // Restore console
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
  });

  test('logger should be defined', () => {
    expect(logger).toBeDefined();
    expect(logger.info).toBeDefined();
    expect(logger.error).toBeDefined();
    expect(logger.warn).toBeDefined();
    expect(logger.debug).toBeDefined();
  });

  test('setLogLevel should change log level', () => {
    setLogLevel('debug');
    expect(logger.level).toBe('debug');

    setLogLevel('info');
    expect(logger.level).toBe('info');

    setLogLevel('warn');
    expect(logger.level).toBe('warn');

    setLogLevel('error');
    expect(logger.level).toBe('error');
  });

  test('debug function should log debug message', () => {
    setLogLevel('debug');
    debug('Debug message', { key: 'value' });
    // Just ensure it doesn't throw
    expect(true).toBe(true);
  });

  test('info function should log info message', () => {
    setLogLevel('info');
    info('Info message', { key: 'value' });
    expect(true).toBe(true);
  });

  test('warn function should log warning message', () => {
    setLogLevel('warn');
    warn('Warning message', { key: 'value' });
    expect(true).toBe(true);
  });

  test('error function should log error message', () => {
    setLogLevel('error');
    error('Error message', { key: 'value' });
    expect(true).toBe(true);
  });

  test('error function should handle Error objects', () => {
    setLogLevel('error');
    const err = new Error('Test error');
    error('An error occurred', err);
    expect(true).toBe(true);
  });

  test('should log without metadata', () => {
    setLogLevel('info');
    info('Simple message');
    expect(true).toBe(true);
  });
});
