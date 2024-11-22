# Этот скрипт создан для аутентификация,
# подключение к Google Sheets API,
# запись данных в таблицу,
# вывод результата.
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Если модифицируете права доступа, удалите файл token.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def authenticate_and_get_service():
    '''Аутентификация и получение сервиса для работы с Google Sheets API'''
    creds = None
    # Проверка наличия файла token.json с сохранёнными токенами
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Если токен устарел или отсутствует, запускаем процесс аутентификации
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем токен для будущих запусков
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)

def write_to_sheet(VALUES, RANGE, SHEET_ID):
    '''Запись данных в таблицу'''
    try:
        service = authenticate_and_get_service()
        sheet = service.spreadsheets()

        # Подготовка данных для записи
        body = {
            'values': VALUES
        }

        # Запись данных в указанный диапазон
        result = sheet.values().update(
            spreadsheetId=SHEET_ID, range=RANGE,
            valueInputOption='RAW', body=body
        ).execute()

        print(f'{result.get('updatedCells')} ячеек обновлено. Row added:{RANGE}')

    except HttpError as err:
        print(err)

def read_from_sheet(SHEET_ID, RANGE):
    '''Чтение данных из таблицы'''
    service = authenticate_and_get_service()
    sheet = service.spreadsheets()

    # Чтение данных из указанного диапазона
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            if len(row) > 2:
                print(row)
                yield row

def read_row_from_sheet(SHEET_ID, RANGE):
    '''Чтение данных из таблицы'''
    service = authenticate_and_get_service()
    sheet = service.spreadsheets()

    # Чтение данных из указанного диапазона
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    values = result.get('values', [])

    if not values:
        return ''
    return values