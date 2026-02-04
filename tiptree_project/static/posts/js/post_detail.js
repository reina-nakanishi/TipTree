document.addEventListener("DOMContentLoaded", () => {

  const modal = document.getElementById("delete-modal");
  const form = document.getElementById("delete-form");
  const text = modal.querySelector(".modal-text");
  const subText = modal.querySelector(".modal-subtext");
  const closeBtn = modal.querySelector(".close-btn");

  document.querySelectorAll(".open-delete-modal").forEach(btn => {
    btn.addEventListener("click", () => {
      openDeleteModal(btn);
    });
  });

  closeBtn.addEventListener("click", closeDeleteModal);

  function openDeleteModal(btn) {
    // 削除先URL
    form.action = btn.dataset.url;

    // メイン文言
    text.textContent =
      btn.dataset.text || "本当に削除しますか？";

    // 補足内容（本文）
    if (btn.dataset.content) {
      subText.textContent = btn.dataset.content;
      subText.style.display = "block";
    } else {
      subText.textContent = "";
      subText.style.display = "none";
    }

    modal.classList.remove("hidden");
  }

  function closeDeleteModal() {
    modal.classList.add("hidden");
    form.action = ""; // 念のためリセット
  }

});


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

    const container = btn.closest(".supplement-content, .comment-content");
    if (!container) return;

    const form = container.querySelector(
      ".supplement-reply-form, .comment-reply-form"
    );
    if (!form) return;

    form.classList.toggle("is-open");
  });
});

document.querySelectorAll(".reply-btn").forEach(btn => {
  btn.addEventListener("click", () => {

    console.log("返信ボタン押された");

    const container = btn.closest(".comment-content");
    console.log("container:", container);

    const form = container?.querySelector(".comment-reply-form");
    console.log("form:", form);
  });
});