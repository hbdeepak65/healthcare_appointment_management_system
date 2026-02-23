// Doctor Dashboard Page
const DoctorDashboard = {
    render() {
        const user = Auth.getUser();
        return `
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h1>Welcome, Dr. ${user.last_name || user.username}!</h1>
                    <p>Doctor Dashboard</p>
                </div>

                <div class="section">
                    <h2>Coming Soon</h2>
                    <p>Doctor dashboard features will be available soon.</p>
                    <ul>
                        <li>View patient appointments</li>
                        <li>Confirm/Complete appointments</li>
                        <li>Manage medical records</li>
                        <li>Set availability schedule</li>
                    </ul>
                </div>
            </div>
        `;
    },

    init() {
    }
};