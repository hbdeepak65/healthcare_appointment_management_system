// Authentication utilities
const Auth = {
    setTokens(accessToken, refreshToken) {
        localStorage.setItem(CONFIG.TOKEN_KEY, accessToken);
        localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
    },

    getAccessToken() {
        return localStorage.getItem(CONFIG.TOKEN_KEY);
    },

    getRefreshToken() {
        return localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
    },

    setUser(user) {
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    },

    getUser() {
        const userData = localStorage.getItem(CONFIG.USER_KEY);
        return userData ? JSON.parse(userData) : null;
    },

    isAuthenticated() {
        return !!this.getAccessToken();
    },

    getUserRole() {
        const user = this.getUser();
        return user ? user.role : null;
    },

    clear() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
    },

    logout() {
        this.clear();
        window.location.hash = '#/login';
    }
};

// Global logout function
function logout() {
    Auth.logout();
}