module.exports = {
  displayName: 'Integration Tests',
  testEnvironment: 'node',
  testMatch: ['**/tests/integration/**/*.test.js'],
  setupFilesAfterEnv: ['<rootDir>/tests/integration/setup.js'],
  testTimeout: 30000,
  verbose: true,
  maxWorkers: 1, // Run serially to avoid database conflicts
};
