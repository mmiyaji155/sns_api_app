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
app_id = '7321858940730443782'
client_key = 'awp9eb2ocfla7v3y'
client_secret = 'MPAbLk31CMW5xWSaVGqashblc0lo5NOg'

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
        'response_type': 'code',
        'scope': 'user.info.basic,video.list',
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
    print('start get_access_kye')
    try:
        code = request.args.get('code')
        print('success!!')
        print(code)
        return redirect(url_for('get_access_token', code=code))
    except:
        print('code is not found...')
        return 'code is not found...'


@app.route('/get-access/<code>', methods=['POST'])
def get_access_token(code):
    # アクセストークンを取得するためにpostする
    # resから取得したアクセストークンを保存する
    print('start get_access_token')
    print('===code===')
    print(code)
    base_url = 'https://www.tiktok.com/v2/oauth/token/'
    redirect_url = url_for('get_access_key', _external=True)  # Use _external=True to get the absolute URL
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    params = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_url
    }
    print(params)
    tokens = []
    try:
        response = requests.post(base_url, headers=headers, params=params)
        print('=== Response Status Code ===')
        print(response.status_code)
        print('=== Response Content ===')
        print(response.text)
        print('===response===')
        print(response)
        res = response.json()
        print('===res===')
        print(res)
    except Exception as e:
        # 通信エラーなどの例外が発生した場合
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

    if 'access_token' in res:
        access_token = res['access_token']
        open_id = res['open_id']
        refresh_token = res['refresh_token']
        print(access_token)
        print(open_id)
        print(refresh_token)
        tokens.append([access_token, refresh_token, open_id])
        wb.values_append('access-token', {'valueInputOption': 'USER_ENTERED'}, {'values': tokens})
        print("get access token successfully!")
        return "get access token successfully!"
    else:
        error_description = res.get('error_description', 'Unknown error')
        print(f"Error: {error_description}")
        return f"Error: {error_description}", 500  # 500 Internal Server Errorを返す


if __name__ == '__main__':
    print('start apps')
    app.run(debug=True)
