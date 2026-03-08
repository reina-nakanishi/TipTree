document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".search-form");
  const input = form.querySelector("input[name='q']");

  form.addEventListener("submit", function (e) {
    if (!input.value.trim()) {
      e.preventDefault(); 
    }
  });
});