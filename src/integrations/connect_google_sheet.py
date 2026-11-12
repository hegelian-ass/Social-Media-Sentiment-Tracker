import gspread

client = gspread.service_account(
    filename="../credentials/google_credentials.json"
)

spreadsheet = client.open("LOP_Sentiment_Tracker")

print("Successfully connected!")
print("Spreadsheet:", spreadsheet.title)


for worksheet in spreadsheet.worksheets():
    print("\nWorksheet:", worksheet.title)
    print("First 10 rows:")

    for row in worksheet.get("A1:Z10"):
        print(row)
        