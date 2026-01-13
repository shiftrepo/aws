import '@testing-library/jest-dom';

// Mock window.alert and window.confirm for tests
global.alert = jest.fn();
global.confirm = jest.fn(() => true);
