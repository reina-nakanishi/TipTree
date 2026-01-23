function openDeleteModal() {
    document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
  document.getElementById('delete-modal').classList.add('hidden');
}

document.addEventListener("DOMContentLoaded", () => {
  const text = document.getElementById("post-text");
  const btn = document.getElementById("toggle-btn");

  if (text.scrollHeight <= text.clientHeight) {
    btn.style.display = "none";
    return;
  }

  btn.addEventListener("click", () => {
    text.classList.toggle("collapsed");

    if (text.classList.contains("collapsed")) {
      btn.textContent = "もっと見る";
    } else {
      btn.textContent = "閉じる";
    }
  });
});