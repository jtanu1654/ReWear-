// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Global state
let currentUser = null;
let featuredItems = [];
let categories = [];
let currentSlide = 0;
let carouselStart = 0;
const CAROUSEL_VISIBLE_COUNT = 3;

// DOM Elements
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');
const featuredCarousel = document.getElementById('featuredCarousel');
const categoriesGrid = document.getElementById('categoriesGrid');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Initialize application
function initializeApp() {
    loadFeaturedItems();
    loadCategories();
    loadStats();
    checkAuthStatus();
}

// Setup event listeners
function setupEventListeners() {
    // Mobile navigation toggle
    if (navToggle) {
        navToggle.addEventListener('click', toggleMobileMenu);
    }

    // Form submissions
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                closeModal(modal.id);
            }
        });
    });
}

// Mobile menu toggle
function toggleMobileMenu() {
    navMenu.classList.toggle('active');
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function switchModal(fromModalId, toModalId) {
    closeModal(fromModalId);
    openModal(toModalId);
}

// Authentication functions
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    try {
        showLoading('loginForm');
        
        const response = await fetch(`${API_BASE_URL}/accounts/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData),
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data.user;
            if (data.token) {
                localStorage.setItem('authToken', data.token);
            }
            showMessage('Login successful!', 'success');
            closeModal('loginModal');
            updateUIForLoggedInUser();
        } else {
            showMessage(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        hideLoading('loginForm');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const registerData = {
        email: formData.get('email'),
        password: formData.get('password'),
        confirm_password: formData.get('confirm_password'),
        first_name: formData.get('name').split(' ')[0] || '',
        last_name: formData.get('name').split(' ').slice(1).join(' ') || ''
    };

    if (registerData.password !== registerData.confirm_password) {
        showMessage('Passwords do not match', 'error');
        return;
    }

    try {
        showLoading('registerForm');
        
        const response = await fetch(`${API_BASE_URL}/accounts/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData),
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data.user;
            showMessage('Registration successful!', 'success');
            closeModal('registerModal');
            updateUIForLoggedInUser();
        } else {
            // Collect all error messages into a single string
            let errorMsg = 'Registration failed';
            if (data) {
                if (typeof data === 'string') {
                    errorMsg = data;
                } else if (typeof data === 'object') {
                    errorMsg = Object.values(data).flat().join(' ');
                }
            }
            showMessage(errorMsg, 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        hideLoading('registerForm');
    }
}

async function logout() {
    try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_BASE_URL}/accounts/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (response.ok) {
            currentUser = null;
            localStorage.removeItem('authToken');
            updateUIForLoggedOutUser();
            showMessage('Logged out successfully', 'success');
        } else {
            showMessage('Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// API functions
async function loadFeaturedItems() {
    try {
        const response = await fetch(`${API_BASE_URL}/items/featured/`);
        const data = await response.json();
        if (response.ok) {
            featuredItems = data.results || data;
            renderFeaturedItems();
        }
    } catch (error) {
        console.error('Error loading featured items:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/items/categories/`);
        const data = await response.json();
        
        if (response.ok) {
            categories = data.results || data;
            renderCategories();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadStats() {
    try {
        // Simulate stats loading (in a real app, these would come from the API)
        const stats = {
            totalItems: 1250,
            totalSwaps: 456,
            totalUsers: 789,
            wasteReduced: 2340
        };

        updateStats(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Rendering functions
function renderFeaturedItems() {
    if (!featuredCarousel) return;
    const track = document.createElement('div');
    track.className = 'carousel-track';
    track.style.width = `${CAROUSEL_VISIBLE_COUNT * 320}px`;
    track.style.transition = 'none';

    let itemsToShow = [];
    for (let i = 0; i < CAROUSEL_VISIBLE_COUNT; i++) {
        const index = (carouselStart + i) % featuredItems.length;
        itemsToShow.push(featuredItems[index]);
    }

    track.innerHTML = itemsToShow.map(item => `
        <div class="item-card">
            <img src="${item.images[0]?.image || 'https://via.placeholder.com/300x250?text=No+Image'}" 
                 alt="${item.title}" class="item-image">
            <div class="item-content">
                <h3 class="item-title">${item.title}</h3>
                <p class="item-price">${item.points_value} points</p>
                <p class="item-owner">by ${item.owner.first_name} ${item.owner.last_name}</p>
                <div class="item-actions">
                    <button class="btn btn-primary btn-small" onclick="viewItem(${item.id})">
                        View Details
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="proposeSwap(${item.id})">
                        Propose Swap
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    featuredCarousel.innerHTML = '';
    featuredCarousel.appendChild(track);
}

setInterval(() => {
    if (featuredItems.length > CAROUSEL_VISIBLE_COUNT) {
        carouselStart = (carouselStart + 1) % featuredItems.length;
        renderFeaturedItems();
    }
}, 3000);

function renderCategories() {
    if (!categoriesGrid) return;

    const categoryIcons = {
        'Tops': 'fas fa-tshirt',
        'Bottoms': 'fas fa-socks',
        'Dresses': 'fas fa-female',
        'Outerwear': 'fas fa-umbrella',
        'Shoes': 'fas fa-shoe-prints',
        'Accessories': 'fas fa-gem'
    };

    categoriesGrid.innerHTML = categories.map(category => `
        <div class="category-card" onclick="browseCategory('${category.name}')">
            <div class="category-icon">
                <i class="${categoryIcons[category.name] || 'fas fa-tag'}"></i>
            </div>
            <h3 class="category-name">${category.name}</h3>
            <p class="category-count">${typeof category.item_count !== 'undefined' ? category.item_count : (category.items?.length || 0)} items</p>
        </div>
    `).join('');
}

function updateStats(stats) {
    document.getElementById('totalItems').textContent = stats.totalItems.toLocaleString();
    document.getElementById('totalSwaps').textContent = stats.totalSwaps.toLocaleString();
    document.getElementById('totalUsers').textContent = stats.totalUsers.toLocaleString();
    document.getElementById('wasteReduced').textContent = stats.wasteReduced.toLocaleString();
}

// UI update functions
function updateUIForLoggedInUser() {
    const navMenu = document.getElementById('nav-menu');
    if (navMenu) {
        navMenu.innerHTML = `
            <a href="index.html#home" class="nav-link">Home</a>
            <a href="index.html#browse" class="nav-link">Browse</a>
            <a href="user-dashboard.html" class="nav-link" id="dashboardLink">Dashboard</a>
            <button class="btn btn-primary" onclick="logout()">Logout</button>
        `;
        // Add click handler for dashboard link if you want SPA behavior (optional)
        const dashboardLink = document.getElementById('dashboardLink');
        if (dashboardLink) {
            dashboardLink.addEventListener('click', function(e) {
                // If you want to use SPA navigation, handle here
                // For now, let it navigate normally
            });
        }
    }
}

function updateUIForLoggedOutUser() {
    const navMenu = document.getElementById('nav-menu');
    if (navMenu) {
        navMenu.innerHTML = `
            <a href="#home" class="nav-link">Home</a>
            <a href="#browse" class="nav-link">Browse</a>
            <a href="#about" class="nav-link">About</a>
            <a href="#contact" class="nav-link">Contact</a>
            <button class="btn btn-primary" onclick="openModal('loginModal')">Login</button>
            <button class="btn btn-secondary" onclick="openModal('registerModal')">Sign Up</button>
        `;
    }
}

// Utility functions
function showMessage(message, type = 'success') {
    console.log('showMessage called:', message, type); // Debug log
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    console.log('Message div added:', messageDiv, 'Current DOM:', document.body.innerHTML);
    setTimeout(() => {
        messageDiv.remove();
        console.log('Message div removed');
    }, 5000);
}

function showLoading(formId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="spinner"></div> Loading...';
    }
}

function hideLoading(formId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
    }
}

async function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        try {
            const response = await fetch(`${API_BASE_URL}/accounts/profile/`, {
                headers: { 'Authorization': `Token ${token}` }
            });
            if (response.ok) {
                const user = await response.json();
                currentUser = user;
                updateUIForLoggedInUser();
            } else {
                // Token invalid or expired
                localStorage.removeItem('authToken');
                currentUser = null;
                updateUIForLoggedOutUser();
            }
        } catch {
            localStorage.removeItem('authToken');
            currentUser = null;
            updateUIForLoggedOutUser();
        }
    } else {
        currentUser = null;
        updateUIForLoggedOutUser();
    }
}

// Navigation functions
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// --- Carousel functions for featured items (DISABLED for grid layout) ---
// Remove updateCarousel, nextSlide, prevSlide, and setInterval for carousel

// Item interaction functions
function viewItem(itemId) {
    // Navigate to item detail page
    window.location.href = `product-detail.html?id=${itemId}`;
}

function proposeSwap(itemId) {
    if (!currentUser) {
        openModal('loginModal');
        return;
    }
    
    // Navigate to swap proposal page
    window.location.href = `propose-swap.html?item=${itemId}`;
}

function browseCategory(categoryName) {
    // Navigate to category browse page
    window.location.href = `browse.html?category=${encodeURIComponent(categoryName)}`;
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.step, .category-card, .item-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}); 

// Product Listings rendering
async function loadProductListings(query = "") {
    const grid = document.getElementById('productListingsGrid');
    if (!grid) return;
    grid.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    let url = `${API_BASE_URL}/items/`;
    if (query) {
        url = `${API_BASE_URL}/items/search/?q=${encodeURIComponent(query)}`;
    }
    try {
        const response = await fetch(url);
        const data = await response.json();
        const items = data.results || data;
        if (items.length === 0) {
            grid.innerHTML = '<div class="text-center">No items found.</div>';
            return;
        }
        grid.innerHTML = items.map(item => `
            <div class="product-card">
                <img src="${item.images?.[0]?.image || 'https://via.placeholder.com/300x180?text=No+Image'}" class="product-card-image" alt="${item.title}">
                <div class="product-card-content">
                    <div>
                        <div class="product-card-title">${item.title}</div>
                        <div class="product-card-points">${item.points_value} points</div>
                        <div class="product-card-owner">by ${item.owner?.first_name || ''} ${item.owner?.last_name || ''}</div>
                    </div>
                    <div class="product-card-actions">
                        <button class="btn btn-primary btn-small" onclick="viewItem(${item.id})">View</button>
                        <button class="btn btn-secondary btn-small" onclick="proposeSwap(${item.id})">Swap</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        grid.innerHTML = '<div class="text-center">Failed to load items.</div>';
    }
}

// Connect both search bars
window.searchItems = function(which = "main") {
    let query = "";
    if (which === "top") {
        query = document.getElementById('topSearchInput').value;
    } else {
        query = document.getElementById('searchInput').value;
    }
    loadProductListings(query);
};

// Initial load
window.addEventListener('DOMContentLoaded', function() {
    loadProductListings();
}); 