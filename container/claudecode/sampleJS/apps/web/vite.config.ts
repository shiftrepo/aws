import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import istanbul from 'vite-plugin-istanbul';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    istanbul({
      include: ['src/*', '../../modules/*/src/*'],
      exclude: ['node_modules', 'tests/', '**/*.test.ts', '**/*.test.tsx'],
      extension: ['.ts', '.tsx'],
      forceBuildInstrument: process.env.VITE_COVERAGE === 'true',
    }),
  ],
  resolve: {
    alias: {
      '@samplejs/domain': path.resolve(__dirname, '../../modules/domain/src'),
      '@samplejs/application': path.resolve(__dirname, '../../modules/application/src'),
      '@samplejs/api': path.resolve(__dirname, '../../modules/api/src'),
      '@samplejs/ui': path.resolve(__dirname, '../../modules/ui/src'),
      '@samplejs/util': path.resolve(__dirname, '../../modules/util/src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: true,
    outDir: 'dist',
  },
});
