/**
 * MQTT Service (Mock Implementation)
 * Real-time messaging simulation for development
 * 
 * For production, use WebSocket or REST polling
 * Alternative: react-native-paho-mqtt or native modules
 */

class MQTTService {
  constructor() {
    this.isConnected = false;
    this.listeners = {};
    this.pollingInterval = null;
    this.mockData = {
      temperature: 22.5,
      humidity: 45,
      light: 350,
      noise: 40,
      motion: false,
    };
  }

  /**
   * Connect to MQTT broker (mock)
   */
  async connect() {
    try {
      console.log('MQTT Mock: Connecting...');
      
      // Simulate connection delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      this.isConnected = true;
      console.log('MQTT Mock: Connected');
      
      // Start polling for mock data
      this.startPolling();
      
      return true;
    } catch (error) {
      console.error('MQTT Connect Error:', error);
      return false;
    }
  }

  /**
   * Start polling for sensor data updates
   */
  startPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    // Poll every 2 seconds
    this.pollingInterval = setInterval(() => {
      this.generateMockData();
    }, 2000);
  }

  /**
   * Generate realistic mock sensor data
   */
  generateMockData() {
    // Gradually change values for realism
    this.mockData.temperature += (Math.random() - 0.5) * 0.5;
    this.mockData.temperature = Math.max(18, Math.min(30, this.mockData.temperature));
    
    this.mockData.humidity += (Math.random() - 0.5) * 2;
    this.mockData.humidity = Math.max(30, Math.min(70, this.mockData.humidity));
    
    this.mockData.light += (Math.random() - 0.5) * 50;
    this.mockData.light = Math.max(100, Math.min(800, this.mockData.light));
    
    this.mockData.noise += (Math.random() - 0.5) * 5;
    this.mockData.noise = Math.max(30, Math.min(80, this.mockData.noise));
    
    this.mockData.motion = Math.random() > 0.7;

    // Emit environment data
    this.emitMessage('sensors/environment', {
      temperature: this.mockData.temperature,
      humidity: this.mockData.humidity,
      timestamp: new Date().toISOString(),
    });

    // Emit light data
    this.emitMessage('sensors/light', {
      lux: this.mockData.light,
      timestamp: new Date().toISOString(),
    });

    // Emit noise data
    this.emitMessage('sensors/noise', {
      noise_level: this.mockData.noise,
      timestamp: new Date().toISOString(),
    });

    // Emit motion data
    this.emitMessage('sensors/motion', {
      motion_detected: this.mockData.motion,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Emit message to listeners
   */
  emitMessage(topic, data) {
    // Notify topic-specific listeners
    if (this.listeners[topic]) {
      this.listeners[topic].forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${topic}:`, error);
        }
      });
    }

    // Notify wildcard listeners
    if (this.listeners['*']) {
      this.listeners['*'].forEach((callback) => {
        try {
          callback(topic, data);
        } catch (error) {
          console.error('Error in wildcard listener:', error);
        }
      });
    }
  }

  /**
   * Add message listener
   */
  addListener(topic, callback) {
    if (!this.listeners[topic]) {
      this.listeners[topic] = [];
    }
    this.listeners[topic].push(callback);
  }

  /**
   * Remove message listener
   */
  removeListener(topic, callback) {
    if (this.listeners[topic]) {
      this.listeners[topic] = this.listeners[topic].filter((cb) => cb !== callback);
    }
  }

  /**
   * Publish message to topic (mock)
   */
  publish(topic, message) {
    if (!this.isConnected) {
      console.warn('MQTT not connected');
      return false;
    }

    console.log(`MQTT Mock: Publishing to ${topic}:`, message);
    return true;
  }

  /**
   * Send command to IoT device (mock)
   */
  sendCommand(command, params = {}) {
    console.log(`MQTT Mock: Sending command ${command}:`, params);
    return this.publish('commands/device', {
      command,
      params,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Disconnect from MQTT broker
   */
  disconnect() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    
    this.isConnected = false;
    this.listeners = {};
    console.log('MQTT Mock: Disconnected');
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      connected: this.isConnected,
      mode: 'mock',
    };
  }
}

// Export singleton instance
export default new MQTTService();
