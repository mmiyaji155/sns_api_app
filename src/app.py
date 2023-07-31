# TikTok認証用のアプリを作成する
# tiktok_displayAPI.pyでデータ取得-記録までの処理を実装する
# app.pyでFlaskを使用したアプリを構築する

from flask import Flask, render_template, url_for, request, redirect
import random
import requests


# まずは、login-kit実装用のルートを構築する
app_id = '7234296212580845574'
client_key = 'awrf3sfxux1til3h'
client_secret = '033a282cd4bc77bab397c21ae1b52c85'

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
    code = request.args.get('code')
    return redirect(url_for('get_access_token', code=code))


@app.route('/get-access/<code>')
def get_access_token(code):
    # アクセストークンを取得するためにpostする
    # resから取得したアクセストークンを保存する
    base_url = 'https://www.tiktok.com/v2/auth/authorize/'
    redirect_url = url_for('get_access_key', _external=True)  # Use _external=True to get the absolute URL
    header = {}
    params = {
        'client_key': client_key,
        'scope': 'user.info.basic',
        'response_type': 'code',
        'code': code,
        'redirect_uri': redirect_url,
    }
    res = requests.post(base_url, headers=header, params=params)
    access_token = res['access_token']
    open_id = res['open_id']
    refresh_token = res['refresh_token']
    print(access_token)
    print(open_id)
    print(refresh_token)
    return "get access token successfully!"


if __name__ == '__main__':
    print('start apps')
    app.run(debug=True)
