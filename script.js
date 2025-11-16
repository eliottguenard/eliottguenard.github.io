// ========================================
// NAVIGATION ACTIVE AU SCROLL
// ========================================
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

function activateNavOnScroll() {
    const scrollY = window.pageYOffset;
    
    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}

window.addEventListener('scroll', activateNavOnScroll);

// ========================================
// FILTRAGE DES PROJETS PAR ANNÉE
// ========================================
const filterBtns = document.querySelectorAll('.filter-btn');
const projectGrids = document.querySelectorAll('.projects-grid');

filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const year = this.getAttribute('data-year');
        
        // Mise à jour des boutons actifs
        filterBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Affichage des projets correspondants
        projectGrids.forEach(grid => {
            const gridYear = grid.getAttribute('data-year');
            
            if (year === 'all') {
                grid.style.display = 'grid';
            } else if (gridYear === year) {
                grid.style.display = 'grid';
            } else {
                grid.style.display = 'none';
            }
        });
    });
});

// Initialisation : afficher les projets de 1ère année au chargement
document.addEventListener('DOMContentLoaded', () => {
    projectGrids.forEach(grid => {
        const gridYear = grid.getAttribute('data-year');
        if (gridYear === '1') {
            grid.style.display = 'grid';
        } else {
            grid.style.display = 'none';
        }
    });
});

// ========================================
// BOUTON SCROLL TO TOP
// ========================================
const scrollTopBtn = document.getElementById('scrollTop');

function toggleScrollTopButton() {
    if (window.pageYOffset > 300) {
        scrollTopBtn.classList.add('visible');
    } else {
        scrollTopBtn.classList.remove('visible');
    }
}

window.addEventListener('scroll', toggleScrollTopButton);

scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// ========================================
// SMOOTH SCROLLING POUR TOUS LES LIENS
// ========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            const headerHeight = document.querySelector('.header').offsetHeight;
            const targetPosition = targetElement.offsetTop - headerHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ========================================
// ANIMATIONS AU SCROLL (INTERSECTION OBSERVER)
// ========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observer les éléments à animer
document.querySelectorAll('.project-card, .detail-card, .contact-card, .timeline-item').forEach(el => {
    observer.observe(el);
});

// ========================================
// MENU MOBILE (RESPONSIVE)
// ========================================
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileMenuToggle.querySelector('i').classList.toggle('fa-bars');
        mobileMenuToggle.querySelector('i').classList.toggle('fa-times');
    });
    
    // Fermer le menu mobile au clic sur un lien
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                mobileMenuToggle.querySelector('i').classList.remove('fa-times');
                mobileMenuToggle.querySelector('i').classList.add('fa-bars');
            }
        });
    });
}

// ========================================
// PERFORMANCE : DEBOUNCE POUR LE SCROLL
// ========================================
function debounce(func, wait = 10) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Applique le debounce aux événements de scroll
window.addEventListener('scroll', debounce(() => {
    activateNavOnScroll();
    toggleScrollTopButton();
}, 10));

// ========================================
// CONSOLE MESSAGE PROFESSIONNEL
// ========================================
console.log('%c👋 Bienvenue sur mon portfolio !', 'font-size: 20px; color: #34D399; font-weight: bold;');
console.log('%cSi vous êtes ici, c\'est que vous êtes curieux ! N\'hésitez pas à me contacter.', 'font-size: 14px; color: #3B82F6;');
console.log('%c📧 eliott.guenard@gmail.com', 'font-size: 12px; color: #9CA3AF;');
