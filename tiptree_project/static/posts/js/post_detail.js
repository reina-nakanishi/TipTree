document.addEventListener("DOMContentLoaded", () => {

  const text = document.getElementById("post-text");
  const btn = document.getElementById("toggle-btn");

  if (text && btn) {  // ← これ追加！！

    if (text.scrollHeight <= text.clientHeight) {
      btn.style.display = "none";
    }

    btn.addEventListener("click", () => {
      text.classList.toggle("collapsed");

      if (text.classList.contains("collapsed")) {
        btn.textContent = "もっと見る";
      } else {
        btn.textContent = "閉じる";
      }
    });

  }

  document.addEventListener("input", function (e) {
    if (e.target.classList.contains("auto-resize")) {
      e.target.style.height = "auto";
      e.target.style.height = e.target.scrollHeight + "px";
    }
  });

  document.addEventListener("click", (e) => {
    console.log("clicked:", e.target);

    const btn = e.target.closest(".reply-btn");
    if (!btn) return;


    const container =
      btn.closest(".comment-content") ||
      btn.closest(".supplement-content");


    if (!container) return;

    const form =
      container.querySelector(".comment-reply-form") ||
      container.querySelector(".supplement-reply-form");

    if (!form) return;

    form.classList.toggle("is-open");

  });

  document.querySelectorAll(".toggle-replies").forEach(button => {

    button.addEventListener("click", () => {

      const item = button.closest(".comment-item, .supplement-item");
      const replies = item.querySelector(".comment-replies, .supplement-replies");
      const count = button.dataset.count;

      if (replies.style.display === "block") {

        replies.style.display = "none";
        button.textContent = `${count}件の返信を表示 ▼`;

      } else {

        replies.style.display = "block";
        button.textContent = `返信を非表示 ▲`;

      }

    });

  });

  // 対象のフォームクラスを全部まとめる
  document.addEventListener("submit", (e) => {

    const form = e.target;

    // 対象フォームだけ処理
    if (!form.matches(".supplement-form, .supplement-reply-form, .comment-form, .comment-reply-form")) {
      return;
    }

    e.preventDefault();

    // 🔥 送信中チェック（ここが最重要）
    if (form.dataset.submitting === "true") {
      return;
    }

    form.dataset.submitting = "true";

    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "送信中...";
    }

    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      },
    })
    .then(response => response.json())
    .then(data => {

      console.log(data);

      if (data.success) {
        form.reset();

        let container;

        if (form.classList.contains("supplement-form")) {
          container = document.querySelector(".supplement-list");

        } else if (form.classList.contains("comment-form")) {
          container = document.querySelector(".comment-list");

        } else if (form.classList.contains("supplement-reply-form")) {
          container = form.closest(".supplement-content")
                          .querySelector(".supplement-replies");

        } else if (form.classList.contains("comment-reply-form")) {
          container = form.closest(".comment-content")
                          .querySelector(".comment-replies");
        }

        if (container && data.html) {
          container.insertAdjacentHTML("afterbegin", data.html);
          container.style.display = "block";
        }

      } else {
        alert(data.error || "送信に失敗しました");
      }

    })
    .catch(() => alert("通信エラーです"))
    .finally(() => {
      form.dataset.submitting = "false";

      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "送信";
      }
    });

  });

});