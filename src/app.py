# TikTok認証用のアプリを作成する
# tiktok_displayAPI.pyでデータ取得-記録までの処理を実装する
# app.pyでFlaskを使用したアプリを構築する

from flask import Flask, render_template, url_for, request, redirect
import random
import requests
import gspread
from google.oauth2.service_account import Credentials


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


# まずは、login-kit実装用のルートを構築する
app_id = '7263966704714696709'
client_key = 'awe3jub5pxkrgw42'
client_secret = '68b7811c85635b26da2648cdc2c6e060'

app = Flask(__name__)


@app.route('/')
def index():
    SERVER_ENDPOINT_OAUTH = url_for('request_to_tiktok_oauth')
    return render_template('start_page.html', SERVER_ENDPOINT_OAUTH=SERVER_ENDPOINT_OAUTH)


@app.route('/oauth')
def request_to_tiktok_oauth():
    base_url = 'https://www.tiktok.com/v2/auth/authorize/'
    csrfState = str(random.randint(0, 1000000))
    redirect_url = url_for('get_access_key', _external=True)  # Use _external=True to get the absolute URL
    params = {
        'client_key': client_key,
        'scope': 'user.info.basic',
        'response_type': 'code',
        'redirect_uri': redirect_url,
        'state': csrfState
    }
    SERVER_ENDPOINT_KEY = base_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])

    # リクエストヘッダーに指定された情報を使用
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }

    print('Redirecting to TikTok OAuth...')
    return redirect(SERVER_ENDPOINT_KEY)


@app.route('/callback')
def get_access_key():
    # callbackURLのパラメータからアクセスキーを取得
    try:
        code = request.args.get('code')
        return redirect(url_for('get_access_token', code=code))
    except:
        return 'code is not found...'


@app.route('/get-access/<code>')
def get_access_token(code):
    # アクセストークンを取得するためにpostする
    # resから取得したアクセストークンを保存する
    base_url = 'https://www.tiktok.com/v2/auth/authorize/'
    redirect_url = url_for('get_access_key', _external=True)  # Use _external=True to get the absolute URL
    params = {
        'client_key': client_key,
        'scope': 'user.info.basic',
        'response_type': 'code',
        'code': code,
        'redirect_uri': redirect_url,
    }
    tokens = []
    res = requests.post(base_url, params=params)
    access_token = res['access_token']
    open_id = res['open_id']
    refresh_token = res['refresh_token']
    print(access_token)
    print(open_id)
    print(refresh_token)
    tokens.append([access_token, refresh_token, open_id])
    wb.values_append('access-token', {'valueInputOption': 'USER_ENTERED'}, {'values': tokens})
    return "get access token successfully!"


if __name__ == '__main__':
    print('start apps')
    app.run(debug=True)
