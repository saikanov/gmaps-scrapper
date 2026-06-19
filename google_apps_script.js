// Web App endpoint untuk export lead ke Google Sheet.
// Mendukung: 1 campaign = 1 sheet (tab), auto-header, dan batch insert.
//
// Payload yang diterima (JSON):
// {
//   "sheetName": "(UAE) Lead Database",   // opsional -> bikin tab kalau belum ada
//   "rows": [                              // batch; atau kirim field langsung (single)
//     {
//       "date": "...", "companyName": "...", "pic": "...", "position": "...",
//       "phone": "...", "email": "...", "country": "...", "city": "...",
//       "address": "...", "accountExecutive": "...", "noted": "..."
//     }
//   ]
// }

var HEADERS = [
  "No", "Tanggal", "Nama Perusahaan", "PIC", "Jabatan",
  "No Handphone", "Email", "Negara", "Kota", "Alamat",
  "Account Executive", "Noted"
];

function doPost(e) {
  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (error) {
    return jsonOut({ status: "error", message: "Invalid JSON" });
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1 campaign = 1 sheet (tab). Bikin baru kalau belum ada.
  // Kalau sheetName kosong -> fallback ke active sheet (back-compat).
  var sheet;
  if (data.sheetName) {
    sheet = ss.getSheetByName(data.sheetName) || ss.insertSheet(data.sheetName);
  } else {
    sheet = ss.getActiveSheet();
  }

  // Tulis header kalau sheet masih kosong.
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight("bold");
    sheet.setFrozenRows(1);
  }

  // Terima batch (rows) atau single object (back-compat).
  var leads = Array.isArray(data.rows) ? data.rows : [data];
  if (leads.length === 0) {
    return jsonOut({ status: "success", inserted: 0, sheet: sheet.getName() });
  }

  var startRow = Math.max(sheet.getLastRow() + 1, 2);
  var baseNo = startRow - 1;

  var values = leads.map(function (lead, i) {
    return [
      baseNo + i,
      lead.date || "",
      lead.companyName || "",
      lead.pic || "",
      lead.position || "",
      "'" + (lead.phone || ""),   // paksa text biar gak jadi notasi ilmiah / formula
      lead.email || "",
      lead.country || "",
      lead.city || "",
      lead.address || "",
      lead.accountExecutive || "",
      lead.noted || ""
    ];
  });

  // Satu kali tulis (batch) — jauh lebih cepat & aman dari quota daripada per baris.
  sheet.getRange(startRow, 1, values.length, HEADERS.length).setValues(values);

  return jsonOut({ status: "success", inserted: values.length, sheet: sheet.getName() });
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
