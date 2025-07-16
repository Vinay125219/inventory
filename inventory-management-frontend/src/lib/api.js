// API utility functions for the inventory management system

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Authentication endpoints
  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: credentials,
    });
  }

  async register(data) {
    return this.request('/auth/register', {
      method: 'POST',
      body: data,
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Dashboard endpoints
  async getDashboardStats() {
    return this.request('/reports/dashboard');
  }

  // Product endpoints
  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/products${queryString ? `?${queryString}` : ''}`);
  }

  async createProduct(productData) {
    return this.request('/products', {
      method: 'POST',
      body: productData,
    });
  }

  async updateProduct(productId, productData) {
    return this.request(`/products/${productId}`, {
      method: 'PUT',
      body: productData,
    });
  }

  // Inventory endpoints
  async getInventory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/inventory${queryString ? `?${queryString}` : ''}`);
  }

  async createInventoryMovement(movementData) {
    return this.request('/inventory/movements', {
      method: 'POST',
      body: movementData,
    });
  }

  async getInventoryMovements(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/inventory/movements${queryString ? `?${queryString}` : ''}`);
  }

  // Warehouse endpoints
  async getWarehouses() {
    return this.request('/warehouses');
  }

  async createWarehouse(warehouseData) {
    return this.request('/warehouses', {
      method: 'POST',
      body: warehouseData,
    });
  }

  // Category endpoints
  async getCategories() {
    return this.request('/categories');
  }

  async createCategory(categoryData) {
    return this.request('/categories', {
      method: 'POST',
      body: categoryData,
    });
  }

  // Reports endpoints
  async getInventorySummary(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/inventory-summary${queryString ? `?${queryString}` : ''}`);
  }

  async getLowStockReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/low-stock${queryString ? `?${queryString}` : ''}`);
  }

  async getMovementAnalysis(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/movement-analysis${queryString ? `?${queryString}` : ''}`);
  }

  async getInventoryValuation(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/valuation${queryString ? `?${queryString}` : ''}`);
  }

  // Alert endpoints
  async getAlerts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/alerts${queryString ? `?${queryString}` : ''}`);
  }

  async markAlertRead(alertId) {
    return this.request(`/alerts/${alertId}/read`, {
      method: 'PUT',
    });
  }
}

export const apiClient = new ApiClient();

// Utility functions for formatting
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount || 0);
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getStockStatus = (quantity, minLevel) => {
  if (quantity === 0) return { status: 'out-of-stock', color: 'red' };
  if (quantity <= minLevel) return { status: 'low-stock', color: 'orange' };
  if (quantity <= minLevel * 2) return { status: 'medium-stock', color: 'yellow' };
  return { status: 'in-stock', color: 'green' };
};

export const getMovementTypeColor = (type) => {
  const colors = {
    'in': 'green',
    'out': 'red',
    'adjustment': 'blue',
    'transfer': 'purple',
  };
  return colors[type] || 'gray';
};

export const getSeverityColor = (severity) => {
  const colors = {
    'info': 'blue',
    'warning': 'orange',
    'error': 'red',
    'critical': 'red',
  };
  return colors[severity] || 'gray';
};

