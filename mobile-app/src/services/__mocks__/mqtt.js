/**
 * MQTT Service Mock
 */

const mqttService = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  subscribe: jest.fn(),
  publish: jest.fn(),
  addListener: jest.fn(),
  removeListener: jest.fn(),
  isConnected: jest.fn(),
};

export default mqttService;
