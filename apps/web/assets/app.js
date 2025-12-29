console.log("[DEBUG] MINIMAL APP.JS LOADED - IF YOU SEE THIS, LOADING WORKS");
console.log("Time:", new Date().toISOString());

// Minimal init to remove skeleton if possible
document.addEventListener('DOMContentLoaded', () => {
  const title = document.getElementById('track-title');
  if (title) title.textContent = "Minimal Test Loaded";
});
