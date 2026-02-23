// Patient Dashboard Page
const PatientDashboard = {
    data: {
        stats: null,
        upcomingAppointments: [],
        doctors: []
    },

    render() {
        const user = Auth.getUser();
        const userName = user.first_name || user.username;

        return `
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h1>Welcome, ${userName}!</h1>
                    <p>Patient Dashboard</p>
                </div>

                <div id="dashboard-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        `;
    },

    async init() {
        await this.loadData();
        this.renderContent();
    },

    async loadData() {
        try {
            const [stats, appointments, doctors] = await Promise.all([
                API.getAppointmentStats(),
                API.getUpcomingAppointments(),
                API.getDoctors()
            ]);

            this.data.stats = stats;
            this.data.upcomingAppointments = appointments;
            this.data.doctors = doctors.results || doctors;
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    },

    renderContent() {
        const content = document.getElementById('dashboard-content');
        const { stats, upcomingAppointments, doctors } = this.data;

        content.innerHTML = `
            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Appointments</h3>
                    <p class="stat-number">${stats?.total_appointments || 0}</p>
                </div>
                <div class="stat-card">
                    <h3>Pending</h3>
                    <p class="stat-number">${stats?.pending_appointments || 0}</p>
                </div>
                <div class="stat-card">
                    <h3>Confirmed</h3>
                    <p class="stat-number">${stats?.confirmed_appointments || 0}</p>
                </div>
                <div class="stat-card">
                    <h3>Completed</h3>
                    <p class="stat-number">${stats?.completed_appointments || 0}</p>
                </div>
            </div>

            <!-- Upcoming Appointments -->
            <div class="section">
                <div class="section-header">
                    <h2>Upcoming Appointments</h2>
                    <button class="btn-primary" onclick="Router.navigate('/patient/appointments/new')">
                        Book New Appointment
                    </button>
                </div>
                
                ${this.renderAppointments(upcomingAppointments)}
            </div>

            <!-- Available Doctors -->
            <div class="section">
                <div class="section-header">
                    <h2>Available Doctors</h2>
                    <button class="btn-secondary" onclick="Router.navigate('/patient/doctors')">
                        View All Doctors
                    </button>
                </div>
                
                ${this.renderDoctors(doctors)}
            </div>
        `;

        this.attachEventListeners();
    },

    renderAppointments(appointments) {
        if (appointments.length === 0) {
            return '<p class="empty-state">No upcoming appointments</p>';
        }

        return `
            <div class="appointments-list">
                ${appointments.map(apt => `
                    <div class="appointment-card">
                        <div class="appointment-info">
                            <h3>Dr. ${apt.doctor_name}</h3>
                            <p>Date: ${apt.appointment_date}</p>
                            <p>Time: ${apt.appointment_time}</p>
                            <p>Status: <span class="status-badge ${apt.status.toLowerCase()}">${apt.status}</span></p>
                            ${apt.reason ? `<p>Reason: ${apt.reason}</p>` : ''}
                        </div>
                        <div class="appointment-actions">
                            <button class="btn-secondary" onclick="PatientDashboard.viewAppointment(${apt.id})">
                                View Details
                            </button>
                            ${apt.status !== 'CANCELLED' ? `
                                <button class="btn-danger" onclick="PatientDashboard.cancelAppointment(${apt.id})">
                                    Cancel
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    renderDoctors(doctors) {
        return `
            <div class="doctors-grid">
                ${doctors.slice(0, 4).map(doctor => `
                    <div class="doctor-card">
                        <h3>Dr. ${doctor.doctor_name}</h3>
                        <p class="specialization">${doctor.specialization}</p>
                        <p class="experience">${doctor.years_of_experience} years experience</p>
                        <p class="fee">Fee: $${doctor.consultation_fee}</p>
                        <button class="btn-primary" onclick="PatientDashboard.bookWithDoctor(${doctor.id})">
                            Book Appointment
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    },

    attachEventListeners() {
        // Event listeners are attached via onclick in HTML
    },

    async cancelAppointment(id) {
        if (confirm('Are you sure you want to cancel this appointment?')) {
            try {
                await API.cancelAppointment(id);
                await this.loadData();
                this.renderContent();
                alert('Appointment cancelled successfully');
            } catch (error) {
                alert('Failed to cancel appointment');
            }
        }
    },

    viewAppointment(id) {
        Router.navigate(`/patient/appointments/${id}`);
    },

    bookWithDoctor(doctorId) {
        Router.navigate('/patient/appointments/new', { doctorId });
    }
};