function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch(error) {
    return ContentService.createTextOutput("Error parsing JSON");
  }

  // Find the next empty row
  var nextRow = sheet.getLastRow() + 1;
  if(nextRow < 2) nextRow = 2; // Fallback so we don't overwrite headers

  // Assign values based on columns in spreadsheet (1-indexed)
  // 1: No
  // 2: Tanggal/bulan/tahun
  // 3: Nama Perusahaan
  // 4: PIC
  // 5: Jabatan
  // 6: No Handphone
  // 7: Email
  // 8: Negara
  // 9: Kota
  // 10: Alamat
  // 11: Account Executive
  // 12: Noted

  sheet.getRange(nextRow, 1).setValue(nextRow - 1);
  sheet.getRange(nextRow, 2).setValue(data.date || ""); 
  sheet.getRange(nextRow, 3).setValue(data.companyName || ""); 
  sheet.getRange(nextRow, 4).setValue(data.pic || ""); 
  sheet.getRange(nextRow, 5).setValue(data.position || ""); 
  // Append single quote for phone number string formatting to avoid sci-notation or formula eval
  sheet.getRange(nextRow, 6).setValue("'" + (data.phone || "")); 
  sheet.getRange(nextRow, 7).setValue(data.email || ""); 
  sheet.getRange(nextRow, 8).setValue(data.country || ""); 
  sheet.getRange(nextRow, 9).setValue(data.city || ""); 
  sheet.getRange(nextRow, 10).setValue(data.address || ""); 
  sheet.getRange(nextRow, 11).setValue(data.accountExecutive || ""); 
  sheet.getRange(nextRow, 12).setValue(data.noted || ""); 

  var result = {"status": "success"};
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}
