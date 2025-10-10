document.addEventListener('DOMContentLoaded', () => {
    // Animation douce pour le défilement des ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Gestion du formulaire d'inscription
    const signupForm = document.querySelector('.signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = signupForm.querySelector('input[type="email"]').value;
            // Ici, vous pourrez ajouter la logique pour envoyer l'email à votre backend
            alert('Merci de votre intérêt ! Nous vous contacterons bientôt.');
            signupForm.reset();
        });
    }

    // Animation d'apparition au scroll
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe les cartes de fonctionnalités pour l'animation
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Ajouter la classe visible quand l'élément entre dans le viewport
    document.addEventListener('scroll', () => {
        document.querySelectorAll('.feature-card.visible').forEach(card => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        });
    });
});
