fetch("cw_jobs.json")
  .then(response => response.json())
  .then(data => {
    let tbody = document.querySelector("#jobsTable tbody");
    data.forEach(job => {
      let row = "<tr>";
      row += `<td>${job.title}</td>`;
      row += `<td>${job.category}</td>`;
      row += `<td>${job.price}</td>`;
      row += `<td>${job.client}</td>`;
      row += `<td><a href="${job.url}" target="_blank">リンク</a></td>`;
      
      // ⬇⬇⬇ 追加：全文（description）を隠しカラムに入れる
      row += `<td style="display:none;">${job.description || ""}</td>`;

      row += "</tr>";
      tbody.innerHTML += row;
    });

    // DataTables 初期化（description を検索対象に含める）
    $('#jobsTable').DataTable({
      columnDefs: [
        { targets: [5], visible: false } // 6列目（description）を非表示
      ]
    });
  });
