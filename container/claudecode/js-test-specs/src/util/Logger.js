/**
 * Logger.js
 *
 * Structured logging utility using Winston.
 * Provides console and file logging with configurable log levels.
 *
 * @module util/Logger
 */

import winston from 'winston';
import path from 'path';

/**
 * Winston logger configuration
 *
 * Log levels: DEBUG, INFO, WARN, ERROR
 * Outputs to: console and test_spec_generator.log
 */

const { combine, timestamp, printf, colorize, errors } = winston.format;

// Custom log format
const logFormat = printf(({ level, message, timestamp, ...metadata }) => {
  let msg = `${timestamp} [${level}]: ${message}`;

  // Add metadata if present
  if (Object.keys(metadata).length > 0) {
    // Filter out error stack trace from metadata display
    const { stack, ...otherMetadata } = metadata;
    if (Object.keys(otherMetadata).length > 0) {
      msg += ` ${JSON.stringify(otherMetadata)}`;
    }
  }

  return msg;
});

// Create the logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(
    errors({ stack: true }),
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss' })
  ),
  transports: [
    // Console transport with colorization
    new winston.transports.Console({
      format: combine(
        colorize(),
        logFormat
      )
    }),
    // File transport
    new winston.transports.File({
      filename: 'test_spec_generator.log',
      format: logFormat,
      maxsize: 5242880, // 5MB
      maxFiles: 3
    })
  ]
});

/**
 * Set log level dynamically
 * @param {string} level - Log level (debug, info, warn, error)
 */
function setLogLevel(level) {
  const normalizedLevel = level.toLowerCase();
  logger.level = normalizedLevel;
  logger.info('Log level set', { level: normalizedLevel });
}

/**
 * Log debug message
 * @param {string} message - Log message
 * @param {Object} metadata - Additional metadata
 */
function debug(message, metadata = {}) {
  logger.debug(message, metadata);
}

/**
 * Log info message
 * @param {string} message - Log message
 * @param {Object} metadata - Additional metadata
 */
function info(message, metadata = {}) {
  logger.info(message, metadata);
}

/**
 * Log warning message
 * @param {string} message - Log message
 * @param {Object} metadata - Additional metadata
 */
function warn(message, metadata = {}) {
  logger.warn(message, metadata);
}

/**
 * Log error message
 * @param {string} message - Log message
 * @param {Object} metadata - Additional metadata or Error object
 */
function error(message, metadata = {}) {
  if (metadata instanceof Error) {
    logger.error(message, {
      error: metadata.message,
      stack: metadata.stack
    });
  } else {
    logger.error(message, metadata);
  }
}

export { logger, setLogLevel, debug, info, warn, error };
