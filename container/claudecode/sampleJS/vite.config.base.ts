import { defineConfig } from 'vite';
import path from 'path';

export const baseConfig = defineConfig({
  resolve: {
    alias: {
      '@samplejs/domain': path.resolve(__dirname, './modules/domain/src'),
      '@samplejs/application': path.resolve(__dirname, './modules/application/src'),
      '@samplejs/api': path.resolve(__dirname, './modules/api/src'),
      '@samplejs/ui': path.resolve(__dirname, './modules/ui/src'),
      '@samplejs/util': path.resolve(__dirname, './modules/util/src'),
    },
  },
  build: {
    sourcemap: true,
  },
});
