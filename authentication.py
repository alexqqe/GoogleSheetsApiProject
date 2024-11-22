import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Указываем необходимые права доступа
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def authenticate_and_save_token():
    try:
        creds = None
        # Проверка наличия файла token.json с сохранёнными токенами
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # Если файл отсутствует или токен недействителен, инициируем процесс аутентификации
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Сохраняем токен в файл token.json для последующего использования
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    authenticate_and_save_token()