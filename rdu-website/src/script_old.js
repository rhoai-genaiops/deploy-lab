// RDU Website - All JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Setting up all features');
    
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    
    for (const link of links) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    // Header background change on scroll
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.program-card, .stat-item, .feature, .admission-card');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Mobile menu toggle
    const createMobileMenu = () => {
        const navMenu = document.querySelector('.nav-menu');
        const navContainer = document.querySelector('.nav-container');
        
        if (!navMenu || !navContainer) return;
        
        // Create hamburger button
        const hamburger = document.createElement('button');
        hamburger.className = 'hamburger';
        hamburger.innerHTML = '☰';
        hamburger.style.cssText = `
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        `;
        
        // Add hamburger to nav
        navContainer.appendChild(hamburger);
        
        // Toggle menu on hamburger click
        hamburger.addEventListener('click', () => {
            if (navMenu.style.display === 'flex') {
                navMenu.style.display = 'none';
            } else {
                navMenu.style.display = 'flex';
            }
        });
        
        // Show hamburger on mobile
        const updateMobileMenu = () => {
            if (window.innerWidth <= 768) {
                hamburger.style.display = 'block';
                navMenu.style.display = 'none';
            } else {
                hamburger.style.display = 'none';
                navMenu.style.display = 'flex';
            }
        };
        
        window.addEventListener('resize', updateMobileMenu);
        updateMobileMenu();
    };
    
    createMobileMenu();
    
    // Add loading animation for images
    const placeholderImages = document.querySelectorAll('.placeholder-image');
    placeholderImages.forEach(img => {
        img.style.transition = 'all 0.3s ease';
        img.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.05)';
        });
        img.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
        });
    });
    
    // Dynamic stats counter animation
    const animateCounters = () => {
        const counters = document.querySelectorAll('.stat-item h3');
        
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            const duration = 2000;
            const start = performance.now();
            
            const animate = (currentTime) => {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                if (counter.textContent.includes('%')) {
                    counter.textContent = Math.floor(progress * target) + '%';
                } else {
                    counter.textContent = Math.floor(progress * target);
                }
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            
            // Start animation when element is in view
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        requestAnimationFrame(animate);
                        counterObserver.unobserve(entry.target);
                    }
                });
            });
            
            counterObserver.observe(counter.closest('.stat-item'));
        });
    };
    
    animateCounters();
    
    // ===============================
    // PROGRAM CATEGORY FILTERING
    // ===============================
    
    const tabButtons = document.querySelectorAll('.tab-button');
    const programCards = document.querySelectorAll('.program-card');
    
    console.log('Filtering setup - Found', tabButtons.length, 'tab buttons');
    console.log('Filtering setup - Found', programCards.length, 'program cards');

    if (tabButtons.length > 0 && programCards.length > 0) {
        
        // Set up click handlers for each tab button
        tabButtons.forEach((button, index) => {
            console.log('Setting up button', index, 'with category:', button.getAttribute('data-category'));
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const category = this.getAttribute('data-category');
                console.log('Button clicked - Category:', category);
                
                // Update active tab styling
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter program cards
                let visibleCount = 0;
                programCards.forEach(card => {
                    const cardCategory = card.getAttribute('data-category');
                    
                    if (category === 'all' || cardCategory === category) {
                        // Show card
                        card.classList.remove('hidden');
                        card.style.display = 'block';
                        visibleCount++;
                        
                        // Animate in
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(30px)';
                        
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, 100 + (visibleCount * 50)); // Stagger animations
                        
                    } else {
                        // Hide card
                        card.classList.add('hidden');
                        card.style.display = 'none';
                    }
                });
                
                console.log('Filtered - Visible cards:', visibleCount);
            });
        });
        
        // Set up hover effects for program cards
        programCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                if (!this.classList.contains('hidden')) {
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                if (!this.classList.contains('hidden')) {
                    this.style.transform = 'translateY(0) scale(1)';
                }
            });
        });
        
    } else {
        console.error('Tab buttons or program cards not found!');
    }
    
    // ===============================
    // CONTACT INFO COPY FUNCTIONALITY
    // ===============================
    
    const contactInfo = document.querySelectorAll('footer p');
    contactInfo.forEach(info => {
        if (info.textContent.includes('@') || info.textContent.includes('(')) {
            info.style.cursor = 'pointer';
            info.title = 'Click to copy';
            
            info.addEventListener('click', function() {
                const text = this.textContent.replace(/[📍📞✉️]/g, '').trim();
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        const originalText = this.textContent;
                        this.textContent = 'Copied!';
                        setTimeout(() => {
                            this.textContent = originalText;
                        }, 1000);
                    }).catch(err => {
                        console.log('Copy failed:', err);
                    });
                }
            });
        }
    });
    
    console.log('All features initialized successfully');
});