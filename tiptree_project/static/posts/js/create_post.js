document.addEventListener("DOMContentLoaded", () => {
  const parentSelect = document.getElementById("parent-category");
  const childSelect = document.getElementById("child-category");

  const openConfirmBtn = document.getElementById("openConfirmBtn");
  const submitBtn = document.getElementById("submitBtn");
  const confirmArea = document.getElementById("confirmArea");
  const formGroups = document.querySelectorAll(".form-group");
  const backBtn = document.getElementById("backBtn");

  parentSelect?.addEventListener("change", () => {
    const parentId = parentSelect.value;

    // 親カテゴリ未選択なら子カテゴリをリセット
    if (!parentId) {
      childSelect.innerHTML =
        '<option value="">---------</option>';
      return;
    }

    // Ajax（fetch）でDjangoにリクエスト
    fetch(`/posts/load_child_categories/?parent_id=${parentId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error("通信に失敗しました");
        }
        return response.json(); // JSON → JSオブジェクト
      })
      .then(data => {
        // 子カテゴリを初期化
        childSelect.innerHTML =
          '<option value="">---------</option>';

        // JSONデータを元にoptionを追加
        data.forEach(category => {
          const option = document.createElement("option");
          option.value = category.id;
          option.textContent = category.name;
          childSelect.appendChild(option);
        });
      })
      .catch(error => {
        console.error("エラー:", error);
      });
  });



  // ===== サムネ =====
  const thumbnailInput = document.getElementById("thumbnailInput");
  const thumbnailPreview = document.getElementById("thumbnailPreview");

  thumbnailInput?.addEventListener("change", () => {
    const file = thumbnailInput.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    thumbnailPreview.src = url;
    thumbnailPreview.style.display = "block";
  });


  // ===== 動画 =====
  const videoInput = document.getElementById("videoInput");
  const videoPreview = document.getElementById("videoPreview");

  videoInput?.addEventListener("change", () => {
    const file = videoInput.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    videoPreview.src = url;
    videoPreview.style.display = "block";
    videoPreview.setAttribute("controls", "controls");
  });

  function validateRequiredFields() {
    // タイトル
    const titleInput = document.getElementById("id_title");
    titleInput.setCustomValidity("");

    if (!titleInput.value.trim()) {
      titleInput.setCustomValidity("タイトルを入力してください。");
    } else if (titleInput.value.length > 100) {
      titleInput.setCustomValidity("タイトルは100字以内で書いてください。");
    }

    // カテゴリ（親カテゴリ）
    const parentCategoryInput =
      document.getElementById("parent-category");
    parentCategoryInput.setCustomValidity("");

    if (!parentCategoryInput.value) {
      parentCategoryInput.setCustomValidity(
        "カテゴリを選択してください。"
      );
    }

    // サムネイル画像
    const thumbnailInput =
      document.getElementById("thumbnailInput");
    thumbnailInput.setCustomValidity(
      thumbnailInput.validationMessage &&
      thumbnailInput.validity.customError
        ? thumbnailInput.validationMessage
        : ""
    );

    if (!thumbnailInput.files.length) {
      thumbnailInput.setCustomValidity(
        "サムネイル画像を選択してください。"
      );
    }

    // 動画
    const videoInput =
      document.getElementById("videoInput");

    // すでに validateVideo() で customError が設定されている場合は残す
    if (!videoInput.validity.customError) {
      videoInput.setCustomValidity("");
    }

    if (!videoInput.files.length &&
        !videoInput.validity.customError) {
      videoInput.setCustomValidity(
        "動画ファイルを選択してください。"
      );
    }

    // 本文
    const contentInput =
      document.getElementById("id_content");
    contentInput.setCustomValidity("");

    if (!contentInput.value.trim()) {
      contentInput.setCustomValidity(
        "本文を入力してください。"
      );
    }
  }

  function validateThumbnail() {
    if (!thumbnailInput) return;

    const file = thumbnailInput.files[0];
    if (!file) return; // required は reportValidity() が判定
    
    // 前回のエラーをリセット
    thumbnailInput.setCustomValidity("");

    const validExtensions = [".jpg", ".jpeg", ".png"];
    const fileName = file.name.toLowerCase();

    const isValid = validExtensions.some(ext =>
      fileName.endsWith(ext)
    );

    if (!isValid) {
      thumbnailInput.setCustomValidity(
        "対応している画像形式はJPEGとPNGです。"
      );
    }
  }

  function validateVideo() {
    if (!videoInput) return;

    const file = videoInput.files[0];
    if (!file) return; // required は reportValidity() が判定

    // 前回のエラーをリセット
    videoInput.setCustomValidity("");

    // 拡張子チェック
    const validExtensions = [".mp4", ".mov"];
    const fileName = file.name.toLowerCase();

    const isValidExtension = validExtensions.some(ext =>
      fileName.endsWith(ext)
    );

    if (!isValidExtension) {
      videoInput.setCustomValidity(
        "MP4またはMOV形式の動画をアップしてください。"
      );
      return;
    }

    // MIMEタイプチェック（任意だが追加）
    if (!file.type.startsWith("video/")) {
      videoInput.setCustomValidity(
        "動画ファイルを選択してください。"
      );
      return;
    }

    // ファイルサイズチェック（30MB）
    const maxSize = 30 * 1024 * 1024;

    if (file.size > maxSize) {
      videoInput.setCustomValidity(
        "動画は30MB以内にしてください。"
      );
    }
  }

  function validateForm() {
    validateRequiredFields();
    validateThumbnail();
    validateVideo();
  }


  function showFieldErrors() {
    // すべてのエラー表示を初期化
    document.querySelectorAll(".js-error-message").forEach(el => {
      el.textContent = "";
      el.style.display = "none";
    });

    // エラーのある項目を取得
    const invalidFields = form.querySelectorAll(":invalid");

    if (invalidFields.length === 0) {
      return true;
    }

    invalidFields.forEach(field => {
      const inputArea = field.closest(".input-area");
      const errorBox = inputArea.querySelector(".js-error-message");

      if (errorBox) {
        errorBox.textContent = field.validationMessage;
        errorBox.style.display = "block";
      }
    });

    // 最初のエラー項目へフォーカス
    invalidFields[0].focus();

    return false;
  }


  openConfirmBtn?.addEventListener("click", () => {

    validateForm();

    form.checkValidity();

    if (!showFieldErrors()) {
      return;
    }

    const titleInput = document.querySelector("[name='title']");
    const parentCategoryInput = document.querySelector("[name='parent_category']");
    const categoryInput = document.querySelector("[name='category']");
    const contentInput = document.querySelector("[name='content']");
    const descriptionInput = document.querySelector("[name='description']");

    const confirmTitle = document.getElementById("confirmTitle");
    const confirmParentCategory = document.getElementById("confirmParentCategory");
    const confirmCategory = document.getElementById("confirmCategory");
    const confirmContent = document.getElementById("confirmContent");
    const confirmDescription = document.getElementById("confirmDescription");
    const confirmThumbnail = document.getElementById("confirmThumbnail");
    const confirmVideo = document.getElementById("confirmVideo");


    // テキスト反映
    confirmTitle.textContent = titleInput.value;

    confirmParentCategory.textContent =
      parentCategoryInput.selectedOptions[0]?.text || "";

    confirmCategory.textContent =
      categoryInput.value
        ? categoryInput.selectedOptions[0].text
        : "未選択";

    confirmContent.textContent = contentInput.value;
    confirmDescription.textContent = descriptionInput.value;


    // サムネ反映
    if (thumbnailPreview.src) {
      confirmThumbnail.src = thumbnailPreview.src;
      confirmThumbnail.style.display = "block";
    } else {
      confirmThumbnail.style.display = "none";
    }


    // 動画反映
    if (videoPreview.src) {
      confirmVideo.src = videoPreview.src;
      confirmVideo.style.display = "block";
    } else {
      confirmVideo.style.display = "none";
    }


    // 入力フォーム非表示
    formGroups.forEach(group => {
      group.style.display = "none";
    });

    openConfirmBtn.style.display = "none";
    confirmArea.style.display = "block";
    submitBtn.style.display = "inline-block";
  });

  backBtn?.addEventListener("click", () => {
    formGroups.forEach(group => {
      group.style.display = "";
    });

    confirmArea.style.display = "none";
    submitBtn.style.display = "none";
    openConfirmBtn.style.display = "";
  });

  const form = document.querySelector(".create-post-form");

  console.log("form:", form);
  console.log("submitBtn:", submitBtn);

  form.addEventListener("submit", () => {
    submitBtn.disabled = true;
    submitBtn.textContent = "投稿中...";
  });

});