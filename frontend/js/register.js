// Register Page
const RegisterPage = {
    render() {
        return `
            <div class="auth-container">
                <div class="auth-card">
                    <h2>Register as Patient</h2>
                    <div id="register-error" class="error-message" style="display: none;"></div>
                    
                    <form id="register-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="first_name">First Name</label>
                                <input type="text" id="first_name" name="first_name" required>
                            </div>

                            <div class="form-group">
                                <label for="last_name">Last Name</label>
                                <input type="text" id="last_name" name="last_name" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="reg_username">Username</label>
                            <input type="text" id="reg_username" name="username" required>
                        </div>

                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" required>
                        </div>

                        <div class="form-group">
                            <label for="phone">Phone Number</label>
                            <input type="tel" id="phone" name="phone">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="reg_password">Password</label>
                                <input type="password" id="reg_password" name="password" required>
                            </div>

                            <div class="form-group">
                                <label for="password2">Confirm Password</label>
                                <input type="password" id="password2" name="password2" required>
                            </div>
                        </div>

                        <button type="submit" class="btn-primary">
                            <span id="register-btn-text">Register</span>
                        </button>
                    </form>

                    <div class="auth-links">
                        <p>Already have an account? <a href="#/login">Login</a></p>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        const form = document.getElementById('register-form');
        form.addEventListener('submit', this.handleSubmit.bind(this));
    },

    async handleSubmit(e) {
        e.preventDefault();
        
        const errorDiv = document.getElementById('register-error');
        const btnText = document.getElementById('register-btn-text');
        
        errorDiv.style.display = 'none';
        btnText.textContent = 'Registering...';

        const formData = new FormData(e.target);
        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            password2: formData.get('password2'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            phone: formData.get('phone') || '',
            role: 'PATIENT'
        };

        if (userData.password !== userData.password2) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
            btnText.textContent = 'Register';
            return;
        }

        try {
            const response = await API.register(userData);
            
            Auth.setTokens(response.tokens.access, response.tokens.refresh);
            Auth.setUser(response.user);

            window.location.hash = '#/patient/dashboard';
        } catch (error) {
            let errorMessage = 'Registration failed. Please try again.';
            if (error.username) {
                errorMessage = error.username.join('. ');
            } else if (error.email) {
                errorMessage = error.email.join('. ');
            } else if (typeof error === 'object') {
                errorMessage = Object.values(error).flat().join('. ');
            }
            
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = 'block';
            btnText.textContent = 'Register';
        }
    }
};