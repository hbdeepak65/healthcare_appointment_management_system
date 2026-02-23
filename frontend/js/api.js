// API Service
const API = {
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const token = Auth.getAccessToken();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401 && !options.skipRefresh) {
                // Try to refresh token
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    return this.request(endpoint, { ...options, skipRefresh: true });
                } else {
                    Auth.logout();
                    throw new Error('Session expired');
                }
            }

            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async refreshToken() {
        const refreshToken = Auth.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                Auth.setTokens(data.access, refreshToken);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    },

    // Auth endpoints
    async login(credentials) {
        return this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials),
            skipAuth: true
        });
    },

    async register(userData) {
        return this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
            skipAuth: true
        });
    },

    async registerDoctor(doctorData) {
        return this.request('/auth/register/doctor/', {
            method: 'POST',
            body: JSON.stringify(doctorData),
            skipAuth: true
        });
    },

    async getCurrentUser() {
        return this.request('/auth/me/');
    },

    // Doctors endpoints
    async getDoctors(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/users/doctors/?${queryString}`);
    },

    async getDoctorById(id) {
        return this.request(`/users/doctors/${id}/`);
    },

    async getDoctorAvailability(id) {
        return this.request(`/users/doctors/${id}/availability/`);
    },

    // Appointments endpoints
    async getAppointments(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/appointments/appointments/?${queryString}`);
    },

    async createAppointment(data) {
        return this.request('/appointments/appointments/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getAppointmentById(id) {
        return this.request(`/appointments/appointments/${id}/`);
    },

    async confirmAppointment(id) {
        return this.request(`/appointments/appointments/${id}/confirm/`, {
            method: 'POST'
        });
    },

    async completeAppointment(id, notes) {
        return this.request(`/appointments/appointments/${id}/complete/`, {
            method: 'POST',
            body: JSON.stringify({ notes })
        });
    },

    async cancelAppointment(id) {
        return this.request(`/appointments/appointments/${id}/cancel/`, {
            method: 'POST'
        });
    },

    async getUpcomingAppointments() {
        return this.request('/appointments/appointments/upcoming/');
    },

    async getAppointmentStats() {
        return this.request('/appointments/appointments/stats/');
    },

    // Medical Records endpoints
    async getMedicalRecords(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/appointments/medical-records/?${queryString}`);
    },

    async createMedicalRecord(data) {
        return this.request('/appointments/medical-records/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Reviews endpoints
    async getReviews(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/appointments/reviews/?${queryString}`);
    },

    async createReview(data) {
        return this.request('/appointments/reviews/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getDoctorReviewStats(doctorId) {
        return this.request(`/appointments/reviews/doctor/${doctorId}/stats/`);
    }
};