/**
 * Jest Configuration for Mobile App
 * Simple config for file-based validation tests
 */

module.exports = {
  testMatch: ['**/__tests__/**/*.test.js'],
  testEnvironment: 'node',
  transform: {},
  transformIgnorePatterns: ['node_modules'],
};
