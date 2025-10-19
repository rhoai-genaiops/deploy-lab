// RDU Website JavaScript
(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        
        // Smooth scrolling for anchor links
        function initSmoothScrolling() {
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
        }
        
        // Header scroll effects
        function initHeaderEffects() {
            const header = document.querySelector('.header');
            
            window.addEventListener('scroll', function() {
                if (window.scrollY > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            });
        }
        
        // Animation on scroll
        function initScrollAnimations() {
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
            
            const animateElements = document.querySelectorAll('.program-card, .stat-item, .feature, .admission-card');
            animateElements.forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        }
        
        // Stats counter animation
        function initStatsCounters() {
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
        }
        
        // Program filtering system
        function initProgramFiltering() {
            const buttons = document.querySelectorAll('.tab-button');
            const cards = document.querySelectorAll('.program-card');
            
            if (buttons.length === 0 || cards.length === 0) return;
            
            buttons.forEach((btn) => {
                btn.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    const selectedCategory = this.getAttribute('data-category');
                    
                    // Update button states
                    buttons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Filter cards
                    let visible = 0;
                    cards.forEach(card => {
                        const cardCategory = card.getAttribute('data-category');
                        const shouldShow = selectedCategory === 'all' || cardCategory === selectedCategory;
                        
                        if (shouldShow) {
                            card.classList.remove('hidden');
                            card.style.display = 'block';
                            visible++;
                            
                            // Animate in
                            card.style.opacity = '0';
                            card.style.transform = 'translateY(20px)';
                            
                            setTimeout(() => {
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                            }, visible * 50);
                            
                        } else {
                            card.classList.add('hidden');
                            card.style.display = 'none';
                        }
                    });
                });
            });
            
            // Card hover effects
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    if (!this.classList.contains('hidden')) {
                        this.style.transform = 'translateY(-8px) scale(1.02)';
                    }
                });
                
                card.addEventListener('mouseleave', function() {
                    if (!this.classList.contains('hidden')) {
                        this.style.transform = 'translateY(0) scale(1)';
                    }
                });
            });
        }
        
        // Mobile menu
        function initMobileMenu() {
            const navMenu = document.querySelector('.nav-menu');
            const navContainer = document.querySelector('.nav-container');
            
            if (!navMenu || !navContainer) return;
            
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
            
            navContainer.appendChild(hamburger);
            
            hamburger.addEventListener('click', () => {
                if (navMenu.style.display === 'flex') {
                    navMenu.style.display = 'none';
                } else {
                    navMenu.style.display = 'flex';
                }
            });
            
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
        }
        
        // Copy contact info
        function initContactCopy() {
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
                            }).catch(() => {
                                // Silent fail for copy functionality
                            });
                        }
                    });
                }
            });
        }
        
        // Initialize all features
        initSmoothScrolling();
        initHeaderEffects();
        initScrollAnimations();
        initStatsCounters();
        initProgramFiltering();
        initMobileMenu();
        initContactCopy();
    });
    
})();