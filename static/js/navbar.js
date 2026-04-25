function initNavbar() {
  const btn = document.getElementById("profileBtn");
  const dropdown = document.getElementById("profileDropdown");

  if (btn && dropdown) {
    btn.addEventListener("click", () => {
      dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add("hidden");
      }
    });
  }
}

// Run after components are injected
document.addEventListener("DOMContentLoaded", () => {
  includeComponents().then(() => {
    initNavbar();
  });
});
