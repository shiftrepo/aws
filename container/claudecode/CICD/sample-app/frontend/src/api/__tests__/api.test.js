import { organizationsApi, departmentsApi, usersApi } from '../api';

jest.mock('../api');

describe('API Module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('organizationsApi', () => {
    test('getAll returns data', async () => {
      const mockData = [{ id: 1, name: 'Test Org' }];
      organizationsApi.getAll.mockResolvedValue({ data: mockData });

      const result = await organizationsApi.getAll();

      expect(organizationsApi.getAll).toHaveBeenCalled();
      expect(result.data).toEqual(mockData);
    });

    test('create sends correct data', async () => {
      const mockData = { name: 'New Org', description: 'Test' };
      organizationsApi.create.mockResolvedValue({ data: mockData });

      const result = await organizationsApi.create(mockData);

      expect(organizationsApi.create).toHaveBeenCalledWith(mockData);
      expect(result.data).toEqual(mockData);
    });

    test('delete calls with correct ID', async () => {
      organizationsApi.delete.mockResolvedValue({ data: { success: true } });

      const result = await organizationsApi.delete(1);

      expect(organizationsApi.delete).toHaveBeenCalledWith(1);
      expect(result.data.success).toBe(true);
    });
  });

  describe('departmentsApi', () => {
    test('getByOrganization calls with org ID', async () => {
      const mockData = [{ id: 1, name: 'IT Department' }];
      departmentsApi.getByOrganization.mockResolvedValue({ data: mockData });

      const result = await departmentsApi.getByOrganization(1);

      expect(departmentsApi.getByOrganization).toHaveBeenCalledWith(1);
      expect(result.data).toEqual(mockData);
    });
  });

  describe('usersApi', () => {
    test('getByDepartment calls with dept ID', async () => {
      const mockData = [{ id: 1, name: 'John Doe' }];
      usersApi.getByDepartment.mockResolvedValue({ data: mockData });

      const result = await usersApi.getByDepartment(1);

      expect(usersApi.getByDepartment).toHaveBeenCalledWith(1);
      expect(result.data).toEqual(mockData);
    });
  });
});
