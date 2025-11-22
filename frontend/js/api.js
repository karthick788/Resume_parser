/**
 * API Client for Resume Parser Backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class API {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('access_token');
    }

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    /**
     * Get authentication token
     */
    getToken() {
        return this.token || localStorage.getItem('access_token');
    }

    /**
     * Clear authentication token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = this.getToken();

        const headers = {
            ...options.headers,
        };

        // Add auth token if available
        if (token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Add Content-Type for JSON if body is present and not FormData
        if (options.body && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized
            if (response.status === 401) {
                this.clearToken();
                window.location.href = 'index.html';
                throw new Error('Unauthorized');
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(data?.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'GET',
        });
    }

    /**
     * POST request
     */
    async post(endpoint, body, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: body instanceof FormData ? body : JSON.stringify(body),
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, body, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(body),
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'DELETE',
        });
    }

    // ========== Auth Endpoints ==========

    async register(username, email, password, role = 'recruiter') {
        return this.post('/auth/register', {
            username,
            email,
            password,
            role
        }, { skipAuth: true });
    }

    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        return this.post('/auth/login', formData, { skipAuth: true });
    }

    async getCurrentUser() {
        return this.get('/auth/me');
    }

    async logout() {
        return this.post('/auth/logout');
    }

    // ========== Resume Endpoints ==========

    async uploadResume(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.post('/resumes/upload', formData);
    }

    async listResumes(skip = 0, limit = 100, statusFilter = null) {
        let endpoint = `/resumes?skip=${skip}&limit=${limit}`;
        if (statusFilter) {
            endpoint += `&status_filter=${statusFilter}`;
        }
        return this.get(endpoint);
    }

    async getResume(id) {
        return this.get(`/resumes/${id}`);
    }

    async parseResume(id) {
        return this.post(`/resumes/${id}/parse`);
    }

    async deleteResume(id) {
        return this.delete(`/resumes/${id}`);
    }

    // ========== Candidate Endpoints ==========

    async listCandidates(skip = 0, limit = 100) {
        return this.get(`/candidates?skip=${skip}&limit=${limit}`);
    }

    async getCandidate(id) {
        return this.get(`/candidates/${id}`);
    }

    async updateCandidate(id, data) {
        return this.put(`/candidates/${id}`, data);
    }

    async deleteCandidate(id) {
        return this.delete(`/candidates/${id}`);
    }

    async searchCandidates(searchParams) {
        return this.post('/candidates/search', searchParams);
    }

    async exportCandidate(id, format = 'json') {
        const endpoint = `/candidates/${id}/export?format=${format}`;
        const url = `${this.baseURL}${endpoint}`;
        const token = this.getToken();

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Export failed');
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `candidate_${id}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    }

    // ========== Analytics Endpoints ==========

    async getOverview() {
        return this.get('/analytics/overview');
    }

    async getSkillsDistribution(limit = 20) {
        return this.get(`/analytics/skills-distribution?limit=${limit}`);
    }

    async getTrends(days = 30) {
        return this.get(`/analytics/trends?days=${days}`);
    }

    async getExperienceDistribution() {
        return this.get('/analytics/experience-distribution');
    }
}

// Create global API instance
const api = new API();
