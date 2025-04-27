import gspread
from google.oauth2.service_account import Credentials

scropes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scropes)
client = gspread.authorize(creds)

sheet_id = "1JjBzplMaAfL3zXF_aRkAa1OuCS-W07RriC7itBNguNQ"
sheet = client.open_by_key(sheet_id)

sheet.worksheet('Sheet1').append_row(['2025-04-21 17:00:00-06:00', '17', '70'])
# value_list = sheet.sheet1.row_values(1)
# print(value_list)

# sheets = sheet.worksheets()

# gc = gspread.service_account(filename='credentials.json')

