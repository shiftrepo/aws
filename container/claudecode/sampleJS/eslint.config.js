import js from '@eslint/js';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import importPlugin from 'eslint-plugin-import';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Layer dependency rules (Maven-like architecture enforcement)
const allowedDependencies = {
  domain: [],                                    // No dependencies
  application: ['domain'],                       // Can depend on domain only
  api: ['domain', 'application'],               // Can depend on domain and application
  ui: ['domain', 'application', 'util'],        // Can depend on domain, application, and util
  util: [],                                      // No dependencies
};

// Custom rule to enforce layer dependencies
const layerDependencyRule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce Maven-like layer dependency rules',
      category: 'Architecture',
    },
    messages: {
      invalidDependency: '{{layer}} cannot depend on {{dependency}}. Allowed dependencies: {{allowed}}',
    },
  },
  create(context) {
    return {
      ImportDeclaration(node) {
        const filename = context.getFilename();
        const importPath = node.source.value;

        // Determine current layer from file path
        const layerMatch = filename.match(/modules\/([^/]+)\//);
        if (!layerMatch) return; // Not in a module

        const currentLayer = layerMatch[1];
        const allowed = allowedDependencies[currentLayer];
        if (!allowed) return; // Unknown layer

        // Check if importing from another layer
        const importMatch = importPath.match(/@samplejs\/([^/]+)/);
        if (!importMatch) return; // Not an internal import

        const importedLayer = importMatch[1];
        if (currentLayer === importedLayer) return; // Self-import is OK

        // Check if dependency is allowed
        if (!allowed.includes(importedLayer)) {
          context.report({
            node,
            messageId: 'invalidDependency',
            data: {
              layer: currentLayer,
              dependency: importedLayer,
              allowed: allowed.length > 0 ? allowed.join(', ') : 'none',
            },
          });
        }
      },
    };
  },
};

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.nyc_output/**',
      '**/coverage/**',
      '**/*.config.js',
      '**/*.config.ts',
    ],
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        console: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        process: 'readonly',
        module: 'readonly',
        require: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        exports: 'readonly',
        global: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        vi: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      'import': importPlugin,
      'layer-dependency': {
        rules: {
          'enforce-architecture': layerDependencyRule,
        },
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...tsPlugin.configs.recommended.rules,
      'layer-dependency/enforce-architecture': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
    },
  },
];
