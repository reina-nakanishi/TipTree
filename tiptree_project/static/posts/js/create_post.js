document.addEventListener("DOMContentLoaded", () => {
  const parentSelect = document.getElementById("parent-category");
  const childSelect = document.getElementById("child-category");

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

  const openConfirmBtn = document.getElementById("openConfirmBtn");
  const submitBtn = document.getElementById("submitBtn");
  const confirmArea = document.getElementById("confirmArea");
  const formGroups = document.querySelectorAll(".form-group");
  const backBtn = document.getElementById("backBtn");

  openConfirmBtn?.addEventListener("click", () => {
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

});