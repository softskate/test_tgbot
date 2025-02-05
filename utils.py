from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from config import WORKSHEET


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive']

class SheetsAPI:
    def __init__(self, cred_file) -> None:
        creds = Credentials.from_service_account_file(cred_file, scopes=SCOPES)
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open_by_key(WORKSHEET).worksheet('Заявки')
        self.last_data = self.get_rows()


    def get_rows(self):
        all_data = self.sheet.get_all_records()
        now = datetime.now()
        return {int(row['User_name пользователя']): row['Описание задачи'] for row in all_data}


    def update_data(self, chat_id, text):
        user_data = self.last_data.get(chat_id)
        if user_data:
            self.last_data[chat_id] += '\n\n' + text

        else:
            self.last_data[chat_id] = text

        row = list(self.last_data.keys()).index(chat_id) + 2
        self.sheet.update([[chat_id, self.last_data[chat_id]]], f'A{row}:B{row}')
