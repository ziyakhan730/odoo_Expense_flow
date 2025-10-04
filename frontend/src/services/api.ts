const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('accessToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  private async refreshToken(): Promise<string | null> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return null;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        return data.access;
      } else {
        // Refresh failed, clear tokens
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        return null;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  }

  private async makeAuthenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    let response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    });

    // If token expired, try to refresh
    if (response.status === 401) {
      const newToken = await this.refreshToken();
      if (newToken) {
        // Retry the request with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...this.getAuthHeaders(),
            ...options.headers,
          },
        });
      }
    }

    return response;
  }

  async registerCompany(data: any) {
    const response = await fetch(`${API_BASE_URL}/auth/register/company/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    const result = await response.json();
    // Store JWT tokens
    if (result.access) {
      localStorage.setItem('accessToken', result.access);
      localStorage.setItem('refreshToken', result.refresh);
      localStorage.setItem('user', JSON.stringify(result.user));
    }
    return result;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const result = await response.json();
    // Store JWT tokens
    if (result.access) {
      localStorage.setItem('accessToken', result.access);
      localStorage.setItem('refreshToken', result.refresh);
      localStorage.setItem('user', JSON.stringify(result.user));
    }
    return result;
  }

  async logout() {
    const refreshToken = localStorage.getItem('refreshToken');
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Logout failed');
    }

    // Clear tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    return response.json();
  }

  async getUserProfile() {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/profile/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch profile');
    }

    return response.json();
  }

  async getCompanies() {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/companies/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch companies');
    }

    return response.json();
  }

  // Utility method to check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('accessToken');
  }

  // Utility method to get current user
  getCurrentUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  // User Management API methods
  async getUserSets() {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/sets/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch user sets');
    }

    return response.json();
  }

  async createUserSet(data: any) {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/sets/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create user set');
    }

    return response.json();
  }

  async getUsers() {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/users/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch users');
    }

    return response.json();
  }

  async createUser(data: any) {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/users/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('User creation API error:', {
        status: response.status,
        statusText: response.statusText,
        error: error
      });
      throw new Error(error.detail || error.error || `Failed to create user (${response.status})`);
    }

    return response.json();
  }

  async updateUserRole(userId: number, role: string) {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/users/${userId}/role/`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to update user role');
    }

    return response.json();
  }

  async updateUserSet(userId: number, setId: number) {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/users/${userId}/set/`, {
      method: 'PATCH',
      body: JSON.stringify({ set_id: setId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to update user set');
    }

    return response.json();
  }

  async getAvailableManagers() {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/managers/available/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch available managers');
    }

    return response.json();
  }

  async getUsersBySet(setId: number) {
    const response = await this.makeAuthenticatedRequest(`${API_BASE_URL}/auth/sets/${setId}/users/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch users by set');
    }

    return response.json();
  }
}

export const apiService = new ApiService();
