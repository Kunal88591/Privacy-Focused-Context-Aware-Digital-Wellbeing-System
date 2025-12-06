# .eslintrc.js
module.exports = {
  root: true,
  extends: '@react-native',
  rules: {
    'prettier/prettier': 'off',
    'react-native/no-inline-styles': 'off',
    'react-hooks/exhaustive-deps': 'warn',
  },
};
