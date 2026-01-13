// Mock API for Jest tests
const mockApi = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

export const organizationsApi = {
  getAll: jest.fn(() => Promise.resolve({ data: [] })),
  getById: jest.fn((id) => Promise.resolve({ data: { id } })),
  create: jest.fn((data) => Promise.resolve({ data })),
  update: jest.fn((id, data) => Promise.resolve({ data: { ...data, id } })),
  delete: jest.fn(() => Promise.resolve({ data: { success: true } })),
};

export const departmentsApi = {
  getAll: jest.fn(() => Promise.resolve({ data: [] })),
  getById: jest.fn((id) => Promise.resolve({ data: { id } })),
  getByOrganization: jest.fn(() => Promise.resolve({ data: [] })),
  create: jest.fn((data) => Promise.resolve({ data })),
  update: jest.fn((id, data) => Promise.resolve({ data: { ...data, id } })),
  delete: jest.fn(() => Promise.resolve({ data: { success: true } })),
};

export const usersApi = {
  getAll: jest.fn(() => Promise.resolve({ data: [] })),
  getById: jest.fn((id) => Promise.resolve({ data: { id } })),
  getByDepartment: jest.fn(() => Promise.resolve({ data: [] })),
  create: jest.fn((data) => Promise.resolve({ data })),
  update: jest.fn((id, data) => Promise.resolve({ data: { ...data, id } })),
  delete: jest.fn(() => Promise.resolve({ data: { success: true } })),
};

export default mockApi;
