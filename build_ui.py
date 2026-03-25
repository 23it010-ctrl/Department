import os

templates = {
    'templates/base.html': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GATE 2026 Style - Department Portal</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

    <!-- Top Header Bar -->
    <div class="top-header-bar py-3">
        <div class="container-fluid px-4 px-md-5">
            <div class="row align-items-center text-center text-md-start">
                <div class="col-md-2 mb-3 mb-md-0 mx-auto justify-content-center d-flex">
                    <img src="{{ url_for('static', filename='images/dept_logo_left.png') }}" alt="Department Left Logo" class="header-logo">
                </div>
                <div class="col-md-8 text-center header-text-group">
                    <h1 class="header-title mb-1">DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</h1>
                    <h3 class="header-subtitle mb-1">कंप्यूटर विज्ञान और इंजीनियरिंग विभाग</h3>
                    <p class="header-tagline mb-0">Organizing Institute : INDIAN INSTITUTE OF TECHNOLOGY NATIONAL (IITN)</p>
                </div>
                <div class="col-md-2 mt-3 mt-md-0 mx-auto justify-content-center d-flex">
                    <img src="{{ url_for('static', filename='images/dept_logo_right.png') }}" alt="Department Right Logo" class="header-logo">
                </div>
            </div>
        </div>
    </div>

    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg sticky-top custom-navbar">
        <div class="container-fluid px-4 px-md-5">
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"><i class="fas fa-bars text-white"></i></span>
            </button>
            <div class="collapse navbar-collapse justify-content-center" id="mainNav">
                <ul class="navbar-nav mb-2 mb-lg-0">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">HOME</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('students') }}">STUDENTS</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('faculty') }}">FACULTY</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('achievements') }}">ACHIEVEMENTS</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('news') }}">NEWS</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('notes') }}">NOTES</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('contact') }}">CONTACT</a></li>
                </ul>
                <ul class="navbar-nav ms-auto">
                    {% if session.get('user_id') %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle login-btn" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user-circle"></i> {{ session.get('user_name') }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                {% if session.get('user_role') == 'admin' %}
                                <li><a class="dropdown-item" href="{{ url_for('admin_dashboard') }}">Dashboard</a></li>
                                {% elif session.get('user_role') == 'faculty' %}
                                <li><a class="dropdown-item" href="{{ url_for('faculty_dashboard') }}">Dashboard</a></li>
                                {% else %}
                                <li><a class="dropdown-item" href="{{ url_for('student_dashboard') }}">Dashboard</a></li>
                                {% endif %}
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{{ url_for('logout') }}">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link login-btn" href="{{ url_for('login') }}">APPROVAL PORTAL <i class="fas fa-external-link-alt"></i></a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Announcement Bar -->
    <div class="announcement-bar">
        <div class="d-flex w-100">
            <div class="announcement-label px-3 py-2 fw-bold flex-shrink-0">NOTIFICATIONS <i class="fas fa-angle-double-right"></i></div>
            <div class="marquee-container py-2 w-100 overflow-hidden">
                <div class="marquee-content fw-medium">{{ marquee_text }}</div>
            </div>
        </div>
    </div>

    <!-- Flash Messages -->
    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show shadow-sm" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    <main class="min-vh-100">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer py-5 mt-5">
        <div class="container">
            <div class="row g-4">
                <div class="col-lg-4 col-md-6 mb-4 mb-lg-0">
                    <h5 class="text-uppercase mb-4 fw-bold">Department of CSE</h5>
                    <p class="text-white-50">Striving for excellence in education and research in Computer Science.</p>
                    <div class="social-icons mt-3">
                        <a href="#"><i class="fab fa-facebook-f"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-linkedin-in"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4 mb-lg-0">
                    <h5 class="text-uppercase mb-4 fw-bold">Quick Links</h5>
                    <ul class="list-unstyled mb-0">
                        <li><a href="#" class="text-white-50 text-decoration-none">Privacy Policy</a></li>
                        <li><a href="#" class="text-white-50 text-decoration-none">Terms of use</a></li>
                        <li><a href="#" class="text-white-50 text-decoration-none">Research</a></li>
                        <li><a href="#" class="text-white-50 text-decoration-none">Alumni</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-6 mb-4 mb-lg-0">
                    <h5 class="text-uppercase mb-4 fw-bold">Contact</h5>
                    <ul class="list-unstyled mb-0">
                        <li class="mb-2 text-white-50"><i class="fas fa-map-marker-alt me-2"></i> IITN Campus, Tech Road, City</li>
                        <li class="mb-2 text-white-50"><i class="fas fa-phone me-2"></i> +91 123 456 7890</li>
                        <li class="mb-2 text-white-50"><i class="fas fa-envelope me-2"></i> info@cse.iitn.ac.in</li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-6">
                    <h5 class="text-uppercase mb-4 fw-bold">Newsletter</h5>
                    <form>
                        <div class="input-group mb-3">
                            <input type="email" class="form-control bg-transparent text-white border-secondary" placeholder="Email Address">
                            <button class="btn btn-primary btn-gold" type="button">Subscribe</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="text-center mt-5 pt-4 border-top border-secondary text-white-50">
                <p class="mb-0">&copy; 2026 Department of CSE. All Rights Reserved.</p>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""",

    'static/css/style.css': """:root {
    --primary-color: #6a1b9a; /* Purple theme */
    --primary-dark: #4a148c;
    --secondary-color: #ffca28; /* Yellow/Gold */
    --secondary-dark: #ffb300;
    --text-color: #333333;
    --bg-light: #f8f9fa;
    --footer-bg: #2d2d2d;
    --marquee-bg: #e1bee7;
}

body {
    font-family: 'Poppins', sans-serif;
    color: var(--text-color);
    background-color: var(--bg-light);
}

/* Top Header */
.top-header-bar {
    background-color: #ffffff;
    border-bottom: 2px solid var(--primary-color);
}
.header-logo {
    max-height: 100px;
    object-fit: contain;
}
.header-title {
    color: var(--primary-color);
    font-weight: 700;
    font-size: 1.8rem;
    letter-spacing: 0.5px;
}
.header-subtitle {
    color: var(--primary-color);
    font-weight: 500;
    font-size: 1.4rem;
}
.header-tagline {
    color: #2e7d32;
    font-weight: 600;
    font-size: 1.1rem;
}

/* Navbar */
.custom-navbar {
    background-color: var(--primary-color);
    padding: 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.custom-navbar .nav-link {
    color: #e0e0e0;
    font-weight: 600;
    padding: 1rem 1.5rem !important;
    transition: all 0.3s ease;
    text-transform: uppercase;
    font-size: 0.95rem;
}
.custom-navbar .nav-link:hover, .custom-navbar .nav-link.active {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.1);
}
.custom-navbar .login-btn {
    background-color: var(--secondary-color) !important;
    color: #000000 !important;
    font-weight: 700;
}
.custom-navbar .login-btn:hover {
    background-color: var(--secondary-dark) !important;
}

/* Announcement Bar */
.announcement-bar {
    background-color: var(--marquee-bg);
    border-bottom: 1px solid #ce93d8;
}
.announcement-label {
    background-color: var(--secondary-color);
    color: #000;
    z-index: 2;
    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}
.marquee-container {
    position: relative;
    white-space: nowrap;
}
.marquee-content {
    display: inline-block;
    padding-left: 100%;
    animation: marquee 20s linear infinite;
    color: var(--primary-color);
}
@keyframes marquee {
    0% { transform: translate(0, 0); }
    100% { transform: translate(-100%, 0); }
}

/* Hero Section */
.hero-section {
    position: relative;
    background-image: url('../images/campus_hero_bg.png');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    height: 60vh;
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.85);
}
.hero-content {
    position: relative;
    z-index: 10;
    text-align: center;
    max-width: 800px;
    padding: 2rem;
    animation: fadeIn 1.5s ease;
}
.hero-content h2 {
    color: #000;
    font-weight: 700;
    font-size: 3rem;
    margin-bottom: 1.5rem;
}
.hero-content p, .hero-content li {
    font-size: 1.1rem;
    color: #333;
    font-weight: 500;
    text-align: left;
    margin-bottom: 0.5rem;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Buttons */
.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    border-radius: 50px;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s;
}
.btn-primary:hover {
    background-color: var(--primary-dark);
    border-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.btn-gold {
    background-color: var(--secondary-color) !important;
    border-color: var(--secondary-color) !important;
    color: #000 !important;
    font-weight: 600;
}
.btn-gold:hover {
    background-color: var(--secondary-dark) !important;
}

/* Cards */
.card {
    border: none;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.card-header {
    background-color: var(--primary-color);
    color: white;
    border-radius: 12px 12px 0 0 !important;
    font-weight: 600;
}

/* Forms */
.form-control {
    border-radius: 8px;
    padding: 0.7rem 1rem;
}
.form-control:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.25rem rgba(106, 27, 154, 0.25);
}

/* Footer */
.footer {
    background-color: var(--footer-bg);
    color: #fff;
}
.social-icons a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: rgba(255,255,255,0.1);
    color: #fff;
    margin-right: 10px;
    transition: all 0.3s;
}
.social-icons a:hover {
    background-color: var(--secondary-color);
    color: #000;
    transform: translateY(-3px);
}""",

    'templates/index.html': """{% extends 'base.html' %}
{% block content %}
<section class="hero-section">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <h2>GATE 2026 Style Department Portal</h2>
        <ul class="list-unstyled">
            <li><i class="fas fa-check-circle text-success me-2"></i> The Department of Computer Science & Engineering aims to be a global center of excellence.</li>
            <li><i class="fas fa-check-circle text-success me-2"></i> Offers undergraduate, postgraduate, and doctoral programs with comprehensive curricula.</li>
            <li><i class="fas fa-check-circle text-success me-2"></i> Funded by major national boards and features state-of-the-art laboratories.</li>
            <li><i class="fas fa-check-circle text-success me-2"></i> Active collaboration with industries and top-tier institutes globally.</li>
        </ul>
    </div>
</section>

<div class="container py-5 mt-4">
    <div class="row g-4">
        <div class="col-md-4">
            <div class="card h-100 border-top border-4 border-warning">
                <div class="card-body text-center p-4">
                    <div class="bg-light rounded-circle p-3 d-inline-block mb-3">
                        <i class="fas fa-user-graduate fa-3x" style="color: var(--primary-color);"></i>
                    </div>
                    <h4 class="card-title fw-bold">Students</h4>
                    <p class="card-text text-muted">Access resources, announcements, and track your academic progress.</p>
                    <a href="{{ url_for('students') }}" class="btn btn-outline-primary rounded-pill px-4">View More</a>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 border-top border-4 border-warning">
                <div class="card-body text-center p-4">
                    <div class="bg-light rounded-circle p-3 d-inline-block mb-3">
                        <i class="fas fa-chalkboard-teacher fa-3x" style="color: var(--primary-color);"></i>
                    </div>
                    <h4 class="card-title fw-bold">Faculty</h4>
                    <p class="card-text text-muted">Manage courses, upload notes, and interact with students efficiently.</p>
                    <a href="{{ url_for('faculty') }}" class="btn btn-outline-primary rounded-pill px-4">Meet Faculty</a>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 border-top border-4 border-warning">
                <div class="card-body text-center p-4">
                    <div class="bg-light rounded-circle p-3 d-inline-block mb-3">
                        <i class="fas fa-trophy fa-3x" style="color: var(--primary-color);"></i>
                    </div>
                    <h4 class="card-title fw-bold">Achievements</h4>
                    <p class="card-text text-muted">Explore the latest awards, publications, and research breakthroughs.</p>
                    <a href="{{ url_for('achievements') }}" class="btn btn-outline-primary rounded-pill px-4">Highlights</a>
                </div>
            </div>
        </div>
    </div>
</div>

<section class="bg-light py-5">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-lg-6 mb-4 mb-lg-0">
                <img src="https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&q=80" alt="Tech" class="img-fluid rounded shadow">
            </div>
            <div class="col-lg-6">
                <h3 class="fw-bold mb-3" style="color: var(--primary-color);">Important Dates & Information</h3>
                <div class="accordion" id="infoAccordion">
                    <div class="accordion-item shadow-sm mb-2 border-0 rounded">
                        <h2 class="accordion-header">
                            <button class="accordion-button fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                                Semester Registration
                            </button>
                        </h2>
                        <div id="collapseOne" class="accordion-collapse collapse show" data-bs-parent="#infoAccordion">
                            <div class="accordion-body text-muted">
                                Registration for the upcoming semester begins next week. Make sure all dues are cleared to proceed with course selection.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item shadow-sm mb-2 border-0 rounded">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">
                                Exam Schedules
                            </button>
                        </h2>
                        <div id="collapseTwo" class="accordion-collapse collapse" data-bs-parent="#infoAccordion">
                            <div class="accordion-body text-muted">
                                Mid-term examinations are scheduled for next month. Detailed timetables will be published on the dashboard soon.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}""",

    'templates/students.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <h2 class="fw-bold" style="color: var(--primary-color);">Student Corner</h2>
    <p class="text-muted">Explore various clubs, activities, and resources dedicated back to our students.</p>
    <div class="row g-4 mt-4">
        <div class="col-md-6 col-lg-3">
            <div class="card h-100 shadow-sm border-0 rounded-4 p-4">
                <i class="fas fa-users fa-3x mb-3 text-info"></i>
                <h5 class="fw-bold">Student Clubs</h5>
                <p class="text-muted small">Join Coding, Robotics, and Debate clubs to explore your interests.</p>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="card h-100 shadow-sm border-0 rounded-4 p-4">
                <i class="fas fa-briefcase fa-3x mb-3 text-success"></i>
                <h5 class="fw-bold">Placements</h5>
                <p class="text-muted small">Get the latest updates on internship and placement drives.</p>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="card h-100 shadow-sm border-0 rounded-4 p-4">
                <i class="fas fa-book-open fa-3x mb-3 text-warning"></i>
                <h5 class="fw-bold">Central Library</h5>
                <p class="text-muted small">Search the digital archive of the central library online.</p>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="card h-100 shadow-sm border-0 rounded-4 p-4">
                <i class="fas fa-laptop-code fa-3x mb-3 text-danger"></i>
                <h5 class="fw-bold">Hackathons</h5>
                <p class="text-muted small">Upcoming departmental and inter-college hackathons.</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/faculty.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h2 class="fw-bold" style="color: var(--primary-color);">Our Esteemed Faculty</h2>
        <p class="text-muted">Meet the brilliant minds behind the world-class education.</p>
    </div>
    <div class="row g-4 justify-content-center">
        {% if faculties %}
            {% for f in faculties %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm border-0 rounded-4 text-center p-4">
                    <div class="mb-3">
                        <img src="https://ui-avatars.com/api/?name={{ f.name }}&background=random" class="rounded-circle" width="100">
                    </div>
                    <h5 class="fw-bold">{{ f.name }}</h5>
                    <p class="text-muted small mb-1">{{ f.email }}</p>
                    <p class="badge bg-secondary">Faculty Member</p>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center text-muted">
                <h4>No faculty members enlisted yet.</h4>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    'templates/achievements.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h2 class="fw-bold" style="color: var(--primary-color);">Department Achievements</h2>
        <p class="text-muted">Celebrating success and excellence.</p>
    </div>
    <div class="row justify-content-center">
        <div class="col-md-10">
            {% if achievements %}
                {% for a in achievements %}
                <div class="card border-0 shadow-sm rounded-4 mb-4">
                    <div class="card-body p-4 d-flex align-items-center">
                        <i class="fas fa-trophy fa-3x text-warning me-4"></i>
                        <div>
                            <h5 class="fw-bold mb-1">{{ a.title }}</h5>
                            <p class="text-muted mb-0">{{ a.description }}</p>
                            <small class="text-primary fw-bold">{{ a.date }}</small>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center text-muted">
                    <i class="fas fa-medal fa-4x mb-3 opacity-50"></i>
                    <h4>New achievements will be showcased here!</h4>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/news.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h2 class="fw-bold" style="color: var(--primary-color);">Latest News & Updates</h2>
    </div>
    <div class="row">
        {% if news %}
            {% for n in news %}
            <div class="col-md-6 mb-4">
                <div class="card h-100 shadow-sm border-0 rounded-4">
                    <div class="card-body p-4">
                        <span class="badge bg-primary mb-2">{{ n.category|default('General') }}</span>
                        <h4 class="fw-bold">{{ n.title }}</h4>
                        <p class="text-muted">{{ n.content }}</p>
                        <hr>
                        <small class="text-muted"><i class="far fa-calendar-alt me-2"></i>{{ n.date }}</small>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center text-muted">
                <i class="fas fa-newspaper fa-4x mb-3 opacity-50"></i>
                <h4>No news published recently.</h4>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",
    
    'templates/contact.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h2 class="fw-bold" style="color: var(--primary-color);">Contact Us</h2>
        <p class="text-muted">Get in touch with the department administration.</p>
    </div>
    <div class="row justify-content-center g-4">
        <div class="col-md-5">
            <div class="card shadow-sm border-0 rounded-4 h-100 bg-primary text-white p-5">
                <h4 class="fw-bold mb-4">Contact Information</h4>
                <div class="mb-4">
                    <h5><i class="fas fa-map-marker-alt me-3"></i> Address</h5>
                    <p class="ms-4 mb-0 opacity-75">Department of CSE<br>IITN Campus, Tech Road<br>City, State, 100001</p>
                </div>
                <div class="mb-4">
                    <h5><i class="fas fa-phone me-3"></i> Phone</h5>
                    <p class="ms-4 mb-0 opacity-75">+91 123 456 7890</p>
                </div>
                <div>
                    <h5><i class="fas fa-envelope me-3"></i> Email</h5>
                    <p class="ms-4 mb-0 opacity-75">info@cse.iitn.ac.in</p>
                </div>
            </div>
        </div>
        <div class="col-md-7">
            <div class="card shadow-sm border-0 rounded-4 h-100 p-5">
                <h4 class="fw-bold mb-4" style="color: var(--primary-color);">Send us a Message</h4>
                <form>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <input type="text" class="form-control" placeholder="Your Name" required>
                        </div>
                        <div class="col-md-6">
                            <input type="email" class="form-control" placeholder="Your Email" required>
                        </div>
                        <div class="col-12">
                            <input type="text" class="form-control" placeholder="Subject" required>
                        </div>
                        <div class="col-12">
                            <textarea class="form-control" rows="5" placeholder="Message" required></textarea>
                        </div>
                        <div class="col-12">
                            <button type="button" class="btn btn-primary rounded-pill px-5 fw-bold" onclick="alert('Message sent successfully!')">Submit</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",
    
    'templates/auth/login.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card shadow-lg border-0 rounded-4">
                <div class="card-header bg-white text-center py-4 border-0">
                    <h3 class="fw-bold mb-0" style="color: var(--primary-color);">Application Portal Login</h3>
                    <p class="text-muted mb-0 mt-2">Sign in to access your dashboard</p>
                </div>
                <div class="card-body p-4 p-md-5 pt-0">
                    <form method="POST" action="{{ url_for('login') }}">
                        <div class="form-floating mb-3">
                            <input type="email" class="form-control" id="email" name="email" placeholder="name@example.com" required>
                            <label for="email">Email address</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                            <label for="password">Password</label>
                        </div>
                        <div class="d-grid mb-3">
                            <button type="submit" class="btn btn-primary btn-lg rounded-pill fw-bold">Login</button>
                        </div>
                        <div class="text-center">
                            <p class="mb-0 text-muted">Don't have an account? <a href="{{ url_for('register') }}" style="color: var(--primary-color); font-weight: 600;">Register here</a></p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/auth/register.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-lg border-0 rounded-4">
                <div class="card-header bg-white text-center py-4 border-0">
                    <h3 class="fw-bold mb-0" style="color: var(--primary-color);">Create an Account</h3>
                    <p class="text-muted mb-0 mt-2">Join the department portal</p>
                </div>
                <div class="card-body p-4 p-md-5 pt-0">
                    <form method="POST" action="{{ url_for('register') }}">
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="name" name="name" placeholder="John Doe" required>
                            <label for="name">Full Name</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="email" class="form-control" id="email" name="email" placeholder="name@example.com" required>
                            <label for="email">Email address</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                            <label for="password">Password</label>
                        </div>
                        <div class="form-floating mb-4">
                            <select class="form-select" id="role" name="role" aria-label="Role select">
                                <option value="student" selected>Student</option>
                                <option value="faculty">Faculty</option>
                            </select>
                            <label for="role">Select Role</label>
                        </div>
                        <div class="alert alert-info py-2" style="font-size: 0.9rem;">
                            <i class="fas fa-info-circle me-1"></i> New accounts require admin approval (except first user).
                        </div>
                        <div class="d-grid mb-3 mt-4">
                            <button type="submit" class="btn btn-primary btn-lg rounded-pill fw-bold">Register</button>
                        </div>
                        <div class="text-center">
                            <p class="mb-0 text-muted">Already have an account? <a href="{{ url_for('login') }}" style="color: var(--primary-color); font-weight: 600;">Login here</a></p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/dashboard/admin.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold" style="color: var(--primary-color);"><i class="fas fa-shield-alt me-2"></i>Admin Dashboard</h2>
        <span class="badge bg-primary fs-6 py-2 px-3 rounded-pill">Admin Mode</span>
    </div>

    <div class="row mb-5">
        <div class="col-md-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-header border-0 bg-white pt-4 px-4 pb-0">
                    <h5 class="fw-bold mb-0">Pending Approvals</h5>
                </div>
                <div class="card-body">
                    {% if pending_users %}
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Requested Role</th>
                                    <th>Date</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for u in pending_users %}
                                <tr>
                                    <td class="fw-bold">{{ u.name }}</td>
                                    <td>{{ u.email }}</td>
                                    <td><span class="badge bg-secondary">{{ u.role|capitalize }}</span></td>
                                    <td>{{ u.created_at.strftime('%Y-%m-%d') if u.created_at else 'N/A' }}</td>
                                    <td>
                                        <a href="{{ url_for('approve_user', user_id=u._id) }}" class="btn btn-sm btn-success rounded-pill px-3"><i class="fas fa-check me-1"></i> Approve</a>
                                        <a href="{{ url_for('delete_user', user_id=u._id) }}" class="btn btn-sm btn-danger rounded-pill px-3" onclick="return confirm('Are you sure?')"><i class="fas fa-times me-1"></i> Reject</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <p class="text-muted text-center py-4 mb-0"><i class="fas fa-check-circle text-success fs-1 mb-3 d-block"></i> No pending approvals.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-header border-0 bg-white pt-4 px-4 pb-0">
                    <h5 class="fw-bold mb-0">All Users</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for u in users %}
                                <tr>
                                    <td class="fw-bold">{{ u.name }}</td>
                                    <td>{{ u.email }}</td>
                                    <td>
                                        {% if u.role == 'admin' %}
                                            <span class="badge bg-danger">Admin</span>
                                        {% elif u.role == 'faculty' %}
                                            <span class="badge bg-info text-dark">Faculty</span>
                                        {% else %}
                                            <span class="badge bg-primary">Student</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if u.approved %}
                                            <span class="text-success fw-bold"><i class="fas fa-check-circle"></i> Active</span>
                                        {% else %}
                                            <span class="text-warning fw-bold"><i class="fas fa-clock"></i> Pending</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if u.role != 'admin' %}
                                        <a href="{{ url_for('delete_user', user_id=u._id) }}" class="btn btn-sm btn-outline-danger rounded-pill" onclick="return confirm('Delete this user?')"><i class="fas fa-trash-alt"></i></a>
                                        {% else %}
                                        <button class="btn btn-sm btn-outline-secondary rounded-pill" disabled><i class="fas fa-lock"></i></button>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/dashboard/faculty.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold" style="color: var(--primary-color);"><i class="fas fa-chalkboard-teacher me-2"></i>Faculty Dashboard</h2>
        <span class="badge bg-info text-dark fs-6 py-2 px-3 rounded-pill">Faculty Mode</span>
    </div>

    <div class="row">
        <div class="col-lg-4 mb-4">
            <div class="card shadow-sm border-0 rounded-4 h-100">
                <div class="card-header bg-white border-bottom-0 pt-4 px-4 pb-0">
                    <h5 class="fw-bold"><i class="fas fa-cloud-upload-alt me-2 text-primary"></i>Upload Notes</h5>
                </div>
                <div class="card-body p-4">
                    <form action="{{ url_for('upload_note') }}" method="POST" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label class="form-label fw-medium">Note Title</label>
                            <input type="text" class="form-control" name="title" required placeholder="e.g. Chapter 1: Introduction">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Subject Code/Name</label>
                            <input type="text" class="form-control" name="subject" required placeholder="e.g. CS101">
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-medium">File (PDF/DOC)</label>
                            <input class="form-control" type="file" name="file" required accept=".pdf,.doc,.docx,.ppt,.pptx">
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary rounded-pill fw-bold"><i class="fas fa-upload me-2"></i>Upload Resource</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-lg-8 mb-4">
            <div class="card shadow-sm border-0 rounded-4 h-100">
                <div class="card-header bg-white border-bottom-0 pt-4 px-4 pb-0">
                    <h5 class="fw-bold"><i class="fas fa-folder-open me-2 text-warning"></i>My Uploaded Notes</h5>
                </div>
                <div class="card-body p-0">
                    {% if notes %}
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="ps-4">Title</th>
                                    <th>Subject</th>
                                    <th>Date</th>
                                    <th class="pe-4">File Name</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for note in notes %}
                                <tr>
                                    <td class="ps-4 fw-medium">{{ note.title }}</td>
                                    <td><span class="badge bg-light text-dark border">{{ note.subject }}</span></td>
                                    <td class="text-muted small">{{ note.date.strftime('%b %d, %Y') if note.date else 'N/A' }}</td>
                                    <td class="pe-4">
                                        <a href="{{ url_for('static', filename='uploads/' + note.filename) }}" class="text-decoration-none" target="_blank">
                                            <i class="fas fa-file-pdf text-danger me-1"></i> {{ note.filename }}
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-box-open fs-1 text-muted mb-3 opacity-50"></i>
                        <p class="text-muted mb-0">You haven't uploaded any notes yet.</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/dashboard/student.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold" style="color: var(--primary-color);"><i class="fas fa-user-graduate me-2"></i>Student Dashboard</h2>
        <span class="badge bg-success fs-6 py-2 px-3 rounded-pill">Student Mode</span>
    </div>

    <div class="row g-4 mb-5">
        <div class="col-md-4">
            <div class="card shadow-sm border-0 rounded-4 h-100 bg-primary text-white">
                <div class="card-body p-4 text-center">
                    <i class="fas fa-book-reader fa-3x mb-3 opacity-75"></i>
                    <h4 class="fw-bold">My Courses</h4>
                    <p class="mb-0 opacity-75">View enrolled subjects and syllabus.</p>
                    <button class="btn btn-light btn-sm rounded-pill mt-3 px-4 fw-bold">View</button>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 rounded-4 h-100 bg-warning text-dark">
                <div class="card-body p-4 text-center">
                    <i class="fas fa-file-alt fa-3x mb-3 opacity-75"></i>
                    <h4 class="fw-bold">Assignments</h4>
                    <p class="mb-0 opacity-75">Check pending tasks and deadlines.</p>
                    <button class="btn btn-dark btn-sm rounded-pill mt-3 px-4 fw-bold">Check</button>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 rounded-4 h-100 bg-info text-white">
                <div class="card-body p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3 opacity-75"></i>
                    <h4 class="fw-bold">Grades</h4>
                    <p class="mb-0 opacity-75">Access your academic performance summary.</p>
                    <button class="btn btn-light btn-sm rounded-pill mt-3 px-4 fw-bold text-info">Reports</button>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-header bg-white border-bottom-0 pt-4 px-4 pb-0">
                    <h5 class="fw-bold"><i class="fas fa-bell text-warning me-2"></i>Recent Notifications</h5>
                </div>
                <div class="card-body p-4">
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item px-0 py-3 d-flex align-items-center border-bottom">
                            <div class="bg-light rounded p-2 me-3"><i class="fas fa-calendar-alt text-primary"></i></div>
                            <div>
                                <h6 class="mb-1 fw-bold">Mid-Term Schedule Released</h6>
                                <small class="text-muted">Just now</small>
                            </div>
                        </li>
                        <li class="list-group-item px-0 py-3 d-flex align-items-center">
                            <div class="bg-light rounded p-2 me-3"><i class="fas fa-exclamation-circle text-danger"></i></div>
                            <div>
                                <h6 class="mb-1 fw-bold">Last date for fee payment is upcoming Friday.</h6>
                                <small class="text-muted">1 day ago</small>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/notes.html': """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h2 class="fw-bold" style="color: var(--primary-color);">Study Materials & Notes</h2>
        <p class="text-muted">Access resources uploaded by the faculty covering all subjects.</p>
    </div>

    <div class="row justify-content-center mb-5">
        <div class="col-md-8">
            <form action="{{ url_for('notes') }}" method="GET" class="d-flex shadow-sm rounded-pill bg-white p-2">
                <input type="text" name="q" class="form-control border-0 bg-transparent shadow-none px-3" placeholder="Search by topic, subject code..." value="{{ search_query }}">
                <button type="submit" class="btn btn-primary rounded-pill px-4 fw-bold">Search</button>
            </form>
        </div>
    </div>

    <div class="row g-4">
        {% if notes %}
            {% for note in notes %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm border-0 rounded-4 p-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-light text-primary border border-primary-subtle">{{ note.subject }}</span>
                            <small class="text-muted"><i class="far fa-clock me-1"></i>{{ note.date.strftime('%b %d, %Y') if note.date else '' }}</small>
                        </div>
                        <h5 class="card-title fw-bold mb-3">{{ note.title }}</h5>
                        <p class="card-text text-muted mb-4 small"><i class="fas fa-user-tie me-2"></i>Prof. {{ note.uploaded_by }}</p>
                        <a href="{{ url_for('static', filename='uploads/' + note.filename) }}" target="_blank" class="btn btn-outline-primary w-100 rounded-pill"><i class="fas fa-download me-2"></i>Download File</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-folder-open fa-4x text-muted mb-3 opacity-50"></i>
                <h4 class="text-muted">No notes found!</h4>
                <p class="text-muted">Try a different search query or check back later.</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}"""
}

for filepath, content in templates.items():
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("UI Setup Complete")
