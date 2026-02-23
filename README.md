🏥Healthcare Appointment Management System
A comprehensive, full-stack healthcare appointment booking system built with Django REST Framework and vanilla JavaScript. This production-ready application enables seamless appointment scheduling between patients and doctors with role-based access control.✨ Key Features
🎯 Core Functionality

Appointment Management - Complete CRUD operations for appointment scheduling
Multi-Role System - Separate interfaces for Patients, Doctors, and Administrators
Real-Time Statistics - Dynamic dashboard with appointment analytics
Doctor Profiles - Detailed profiles with specializations, experience, and fees
Medical Records - Secure storage of diagnoses, prescriptions, and lab results
Review System - Patient feedback and rating system for healthcare providers

🔐 Security Features

JWT Token Authentication with automatic refresh
Role-based access control (RBAC)
Secure password handling with Django's built-in encryption
CORS protection for API endpoints
Input validation and sanitization

💻 Technical Highlights

RESTful API Design - Clean, documented API endpoints
Responsive UI - Mobile-first design approach
Zero Framework Frontend - Pure HTML/CSS/JavaScript (no React/Vue overhead)
Database Optimization - Efficient queries with proper indexing
Scalable Architecture - Modular design for easy feature additions


🛠️ Technology Stack
Backend

Framework: Django 4.2.7
API: Django REST Framework 3.14.0
Authentication: JWT (djangorestframework-simplejwt)
Database: SQLite (Development) / PostgreSQL (Production)
CORS: django-cors-headers

Frontend

Languages: HTML5, CSS3, Vanilla JavaScript (ES6+)
Architecture: Single Page Application (SPA) with hash routing
HTTP Client: Fetch API
Storage: LocalStorage for token management

DevOps

Version Control: Git
Documentation: Markdown
API Testing: Django REST Framework Browsable API


📋 System Requirements

Python 3.8 or higher
pip (Python package manager)
Modern web browser (Chrome, Firefox, Safari, Edge)
100MB free disk space
