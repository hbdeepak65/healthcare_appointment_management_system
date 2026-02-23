// Router
const Router = {
    routes: {
        '/login': LoginPage,
        '/register': RegisterPage,
        '/patient/dashboard': PatientDashboard,
        '/doctor/dashboard': DoctorDashboard,
        '/patient/appointments': AppointmentsPage
    },

    init() {
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    },

    handleRoute() {
        const hash = window.location.hash.slice(1) || '/login';
        
        // Check authentication
        if (!Auth.isAuthenticated() && hash !== '/login' && hash !== '/register') {
            showLoginPage();
            window.location.hash = '#/login';
            return;
        }

        // Redirect authenticated users away from login/register
        if (Auth.isAuthenticated() && (hash === '/login' || hash === '/register')) {
            const role = Auth.getUserRole();
            if (role === 'DOCTOR') {
                window.location.hash = '#/doctor/dashboard';
            } else if (role === 'ADMIN') {
                window.location.hash = '#/admin/dashboard';
            } else {
                window.location.hash = '#/patient/dashboard';
            }
            return;
        }

        // Find matching route
        let route = this.routes[hash];
        
        // Check role-based access
        if (hash.startsWith('/patient/') && Auth.getUserRole() !== 'PATIENT') {
            route = null;
        } else if (hash.startsWith('/doctor/') && Auth.getUserRole() !== 'DOCTOR') {
            route = null;
        }

        if (!route) {
            this.render404();
            return;
        }

        this.renderPage(route);
    },

    renderPage(page) {
        const app = document.getElementById('app');
        const navbar = document.getElementById('navbar');

        // Show/hide navbar based on authentication
        if (Auth.isAuthenticated()) {
            navbar.style.display = 'block';
            const userName = Auth.getUser()?.first_name || Auth.getUser()?.username || 'User';
            document.getElementById('user-name').textContent = userName;
        } else {
            navbar.style.display = 'none';
        }

        // Render page
        app.innerHTML = page.render();
        
        // Initialize page
        if (page.init) {
            page.init();
        }
    },

    render404() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="error-page">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <button class="btn-primary" onclick="Router.navigate('/login')">Go to Login</button>
            </div>
        `;
    },

    navigate(path, state = {}) {
        window.location.hash = `#${path}`;
    }
};