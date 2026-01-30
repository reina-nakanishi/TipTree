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

document.addEventListener("input", function (e) {
  if (e.target.classList.contains("auto-resize")) {
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  }
});

document.querySelectorAll(".reply-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const container = btn.closest(".supplement-content");
    const form = container.querySelector(".supplement-reply-form");
    const textarea = form.querySelector("textarea");

    form.classList.toggle("is-open");

    if (form.classList.contains("is-open") && textarea) {
      textarea.style.height = "auto";   // ← これ！
      textarea.value = "";              // ← 念のため
      textarea.focus();
    }
  });
});