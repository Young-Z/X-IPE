import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    root: '.',
    include: ['tests/frontend-js/**/*.test.js'],
  },
});
