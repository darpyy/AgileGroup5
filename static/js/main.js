// Main JS for event handlers

// Automatic Slideshow for images
let slideIndex = 0;
showSlides();

function showSlides() {
    let i;
    let slides = document.getElementsByClassName("slides");
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) {
        slideIndex = 1
    }
    slides[slideIndex-1].style.display = "block";
    setTimeout(showSlides, 5000); // 2 sec changes
}

function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth' 
  });
}

function signIn(){

  
}

// --- Dark Mode Logic ---

// Select the button and the root element
const themeBtn = document.getElementById('theme-toggle');
const htmlEl = document.documentElement;

// Check for a saved theme in the browser's memory
const currentTheme = localStorage.getItem('theme');

// If the user previously chose dark, apply it immediately
if (currentTheme === 'dark') {
    htmlEl.classList.add('dark-mode');
}

// Handle the click event
if (themeBtn) {
    themeBtn.addEventListener('click', () => {
        // Toggle the class
        htmlEl.classList.toggle('dark-mode');
        
        // Check if we are now in dark mode
        let theme = 'light';
        if (htmlEl.classList.contains('dark-mode')) {
            theme = 'dark';
        }
        
        // Save the choice so it persists across your 10 pages
        localStorage.setItem('theme', theme);
    });
}