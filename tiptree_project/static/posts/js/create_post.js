document.addEventListener("DOMContentLoaded", () => {
  const parentSelect = document.getElementById("parent-category");
  const childSelect = document.getElementById("child-category");

  parentSelect.addEventListener("change", () => {
    const parentId = parentSelect.value;

    // 親カテゴリ未選択なら子カテゴリをリセット
    if (!parentId) {
      childSelect.innerHTML =
        '<option value="">サブカテゴリを選択</option>';
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
          '<option value="">サブカテゴリを選択</option>';

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
});