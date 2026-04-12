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

    // temp / current 両方消す
    document.querySelectorAll(".temp-thumbnail, .current-thumbnail")
      .forEach(el => el.remove());

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

    // temp / current 両方消す
    document.querySelectorAll(".temp-video, .current-video")
      .forEach(el => el.remove());

    const url = URL.createObjectURL(file);
    videoPreview.src = url;
    videoPreview.style.display = "block";
    videoPreview.setAttribute("controls", "controls");
  });

});