import gspread
from google.oauth2.service_account import Credentials
import time

def test_spreadsheet():
    # スプレッドシートの連携処理を別で書いておく。
    secret_credentials_json_oath = './my-project-42400-tiktok-api-b96b06c2fc39.json'
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(
        secret_credentials_json_oath,
        scopes=scopes
    )

    gc = gspread.authorize(credentials)
    wb = gc.open_by_key('1iBCRimWCHJ_HtA8z9gD03mP1CccbTTLZDLfEvysV06g')
    sh = wb.get_worksheet(0)

    tokens = []
    access_token = 'aaaaaaaaaaaaaaaaaa'
    open_id = 'bbbbbbbbbbbbbbb'
    refresh_token = 'ccccccccccccccc'
    tokens.append([access_token, refresh_token, open_id])
    wb.values_append('access-token', {'valueInputOption': 'USER_ENTERED'}, {'values': tokens})
    print("get access token successfully!")

    time.sleep(1)

    refresh_tokens = sh.col_values(2)
    print(refresh_tokens)
    cell_values = []
    for refresh_token in refresh_tokens:
        if refresh_token == 'refresh token':
            print('skip because this is column name')
            continue

        cell_value = []
        result = ['wwwwww', 'uiuiuiuiuiu']
        print(refresh_token)
        new_access_token = result[0]
        new_refresh_token = result[1]
        cell_value.append(new_access_token)
        cell_value.append(new_refresh_token)
        cell_values.append(cell_value)
    print(cell_values)
    row_count = len(cell_values)
    sh.update(f'A2:B{row_count+1}', cell_values)  # シートの access_token & refresh_token を更新する
    print('更新完了！')



if __name__ == '__main__':
    print('start test_spreadsheet')
    test_spreadsheet()

