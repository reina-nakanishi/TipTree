document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".search-form");
  const input = form.querySelector("input[name='q']");

  form.addEventListener("submit", function (e) {
    if (!input.value.trim()) {
      e.preventDefault(); 
    }
  });
});


document.addEventListener("DOMContentLoaded", () => {

  const messages = {
    post: "この投稿を削除しますか？",
    comment: "このコメントを削除しますか？",
    supplement:"この補足を削除しますか？",
    comment_reply:"この返信を削除しますか？",
    supplement_reply:"この返信を削除しますか？",
    logout:"ログアウトしますか？",
    auth:"この操作にはログインが必要です"
  };

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-type]");
    if (!el) return;

    const url = el.dataset.url;
    const title = el.dataset.title;
    const type = el.dataset.type;

    e.preventDefault();

    const message = `${messages[type]}\n${title || ""}`;

    openModal({
      message: message,
      url: url,
      type: type
    });
  });

});

function openModal({ message, url, type }) {
  const modal = document.getElementById("common-modal");
  const messageArea = document.getElementById("modal-message");
  const form = document.getElementById("modal-form");
  const actionsArea = document.getElementById("modal-actions");

  // メッセージ表示
  messageArea.innerText = message;

  // フォームを渡すurlを指定
  form.action = url;

  // ボタン初期化
  actionsArea.innerHTML = "";

  // 削除ボタン
  const buttonTexts = {
    logout: "ログアウト",
    auth:"ログイン"
  };

  const deleteBtn = document.createElement("button");

  deleteBtn.innerText = buttonTexts[type] || "削除";

  if (type === "auth") {
    deleteBtn.className = "primary";
    deleteBtn.type = "button";

    deleteBtn.addEventListener("click", () => {
      window.location.href = url;
    });

  } else {
    deleteBtn.className = "danger";
    deleteBtn.type = "submit";
  }

  actionsArea.appendChild(deleteBtn);

  modal.classList.remove("hidden");
}

function closeModal() {
  document.getElementById("common-modal").classList.add("hidden");
}