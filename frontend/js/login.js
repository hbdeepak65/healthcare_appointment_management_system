// Login Page
const LoginPage = {
    render() {
        return `
            <div class="auth-container">
                <div class="auth-card">
                    <h2>Login to Healthcare System</h2>
                    <div id="login-error" class="error-message" style="display: none;"></div>
                    
                    <form id="login-form">
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input type="text" id="username" name="username" required>
                        </div>

                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" required>
                        </div>

                        <button type="submit" class="btn-primary">
                            <span id="login-btn-text">Login</span>
                        </button>
                    </form>

                    <div class="auth-links">
                        <p>Don't have an account? <a href="#/register">Register as Patient</a></p>
                        <p>Are you a doctor? <a href="#/register/doctor">Register as Doctor</a></p>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        const form = document.getElementById('login-form');
        form.addEventListener('submit', this.handleSubmit.bind(this));
    },

    async handleSubmit(e) {
        e.preventDefault();
        
        const errorDiv = document.getElementById('login-error');
        const btnText = document.getElementById('login-btn-text');
        
        errorDiv.style.display = 'none';
        btnText.textContent = 'Logging in...';

        const formData = new FormData(e.target);
        const credentials = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const response = await API.login(credentials);
            
            Auth.setTokens(response.tokens.access, response.tokens.refresh);
            Auth.setUser(response.user);

            // Redirect based on role
            const role = response.user.role;
            if (role === 'DOCTOR') {
                window.location.hash = '#/doctor/dashboard';
            } else if (role === 'ADMIN') {
                window.location.hash = '#/admin/dashboard';
            } else {
                window.location.hash = '#/patient/dashboard';
            }
        } catch (error) {
            errorDiv.textContent = error.error || 'Login failed. Please try again.';
            errorDiv.style.display = 'block';
            btnText.textContent = 'Login';
        }
    }
};