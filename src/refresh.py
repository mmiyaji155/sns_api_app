
# アクセストークンのリフレッシュの処理を記述
# githubで定期実行する
# アカウントごとのアクセストークンをシート上で管理する

import requests
import gspread
from google.oauth2.service_account import Credentials


def refresh_access_token(client_key, client_secret, refresh_token):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    payload = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response_json = response.json()

        if "access_token" in response_json:
            return response_json
        else:
            print("アクセストークンのリフレッシュエラー:")
            print(response_json)
            return None

    except requests.exceptions.RequestException as e:
        print("アクセストークンのリフレッシュエラー:", e)
        return None


# 使用例
client_key = "YOUR_CLIENT_KEY"
client_secret = "YOUR_CLIENT_SECRET"
refresh_token = "USER_REFRESH_TOKEN"


# スプレッドシートの連携処理を別で書いておく。
secret_credentials_json_oath = './src/my-project-42400-tiktok-api-b96b06c2fc39.json'
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


def main():
    refresh_tokens = sh.col_values(2)
    print(refresh_tokens)
    cell_values = []
    for refresh_token in refresh_tokens:
        if refresh_token == 'refresh token':
            print('skip because this is column name')
            continue

        result = refresh_access_token(client_key, client_secret, refresh_token)
        cell_value = []
        if result:
            new_access_token = result["access_token"]
            new_refresh_token = result["refresh_token"]
            print("新しいアクセストークン:", result["access_token"])
            print("有効期限:", result["expires_in"], "秒")
            print("リフレッシュトークン:", result["refresh_token"])
            print("リフレッシュトークンの有効期限:", result["refresh_expires_in"], "秒")
            print("スコープ:", result["scope"])
            cell_value.append(new_access_token)
            cell_value.append(new_refresh_token)
            cell_values.append(cell_value)
        else:
            continue
    #   spread sheet を更新する
    row_count = len(cell_values)
    sh.update(f'B2:C{row_count+1}', cell_values)  # シートの access_token & refresh_token を更新する
    print('更新完了！')
