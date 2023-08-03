import requests
import json
import os
import gspread
from google.oauth2.service_account import Credentials

# スプレッドシートの連携処理を別で書いておく。
secret_credentials_json_oath = './client_secret_534494746627-5ufnbaj92irssf58t39emk47pgo24aee.apps.googleusercontent.com.json'
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
    access_tokens = get_access_token()
    print(access_tokens)
    for access_token in access_tokens:
        post_data = get_post_data(access_token)
        handle_spread_sheet(post_data)
        print('next account')
    print('更新完了しました！')


# spread sheet からアクセストークンをリストで取得する処理
def get_access_token():
    access_tokens = sh.col_values(2)
    del access_tokens[0]
    return access_tokens


def get_post_data(access_token):
    base_url = 'https://open.tiktokapis.com/v2/video/list/'

    headers = {
        'Authorization': f'Bearer ' + os.environ('access_token'),  #ここにアクセストークンを指定
        'Content-Type': 'application/json'
    }

    params = {
        'fields': ['id', 'title', 'share_url', 'created_time', 'like_count', 'comment_count', 'share_count', 'view_count']
    }

    data = {
        'max_token': 100
    }

    res = requests.get(base_url, headers=headers, params=params, data=json.dumps(data))

    # レスポンスの処理
    post_data = []
    if res.status_code == 200:
        response_data = res.json()
        if 'data' in response_data:
            videos = response_data['data']['videos']
            for video in videos:
                video_id = video['id']
                title = video['title']
                share_url = video['share_url']
                created_time = video['created_time']
                like_count = video['like_count']
                comment_count = video['comment_count']
                share_count = video['share_count']
                view_count = video['view_count']
                data = [video_id, title, share_url, created_time, like_count, comment_count, share_count, view_count]
                post_data.append(data)

    else:
        print('Request failed with status code:', res.status_code)

    return post_data


# spreadsheetへのデータ追加
def handle_spread_sheet(post_data):
    sheet_name = 'data-base'
    wb.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': post_data})
    print('データ追加完了！')


if __name__ == '__main__':
    print('start apps')
    main()
