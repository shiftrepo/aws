import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.ts', 'src/**/*.tsx'],
      exclude: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    },
  },
  resolve: {
    alias: {
      '@samplejs/domain': path.resolve(__dirname, '../../modules/domain/src'),
      '@samplejs/application': path.resolve(__dirname, '../../modules/application/src'),
      '@samplejs/util': path.resolve(__dirname, '../../modules/util/src'),
    },
  },
});
