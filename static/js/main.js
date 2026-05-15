// Main JS for event handlers


// Automatic Slideshow for images
let slideIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
    showSlides();
});

function showSlides() {
  var i;
  var x = document.getElementsByClassName("slides");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";  
  }
  slideIndex++;
  if (slideIndex > x.length) {slideIndex = 1}    
  x[slideIndex-1].style.display = "block";  
  setTimeout(showSlides, 3000);
}

function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth' 
  });
}
