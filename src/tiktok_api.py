import requests
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta

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
wb = gc.open_by_key('1iBCRimWCHJ_HtA8z9gD03mP1CccbTTLZDLfEvysV06g') # access_token sheet id
sh = wb.get_worksheet(0)


def main():
    access_tokens = get_access_token()
    print(access_tokens)
    append_data = []
    for access_token in access_tokens:
        print('access_token: ', access_token)
        user_data = get_user_data(access_token)
        post_data = get_post_data(access_token)
        print('start merge data')
        merged_data = merge_data(user_data, post_data)
        if not merged_data:
            continue
        # merged_dataは2次元配列になっている。
        append_data.extend(merged_data)
        print('next account')
    handle_spread_sheet(append_data)
    print('更新完了しました！')


# spread sheet からアクセストークンをリストで取得する処理
def get_access_token():
    access_tokens = sh.col_values(1)
    del access_tokens[0]
    return access_tokens


def get_post_data(access_token):
    base_url = 'https://open.tiktokapis.com/v2/video/list/'

    headers = {
        'Authorization': 'Bearer ' + access_token,  #ここにアクセストークンを指定
        'Content-Type': 'application/json'
    }

    params = {
        'fields': 'id,title,share_url,create_time,like_count,comment_count,share_count,view_count,cover_image_url'
    }

    data = {
        'max_count': 15
    }
    try:
        res = requests.post(base_url, headers=headers, params=params, json=data)
    except Exception as e:
        # 通信エラーなどの例外が発生した場合
        print(f"An error occurred: {str(e)}")

    # レスポンスの処理
    post_data = []
    if res.status_code == 200:
        response_data = res.json()
        print('---get post-data!!!---')
        # print(response_data)
        if 'data' in response_data:
            videos = response_data['data']['videos']
            for video in videos:
                video_id = video['id']
                title = video['title']
                share_url = video['share_url']
                created_time = video['create_time']
                like_count = video['like_count']
                comment_count = video['comment_count']
                share_count = video['share_count']
                view_count = video['view_count']
                cover_image_url = video['cover_image_url']
                created_time_jst, time_delta = process_past_time(created_time)
                data = [video_id, title, share_url, created_time_jst, like_count, comment_count, share_count, view_count, cover_image_url,time_delta]
                post_data.append(data)
    else:
        print('Request failed with status code:', res.status_code)
    # post_dataは二次元配列になっている
    return post_data


def get_user_data(access_token):
    base_url = 'https://open.tiktokapis.com/v2/user/info/'

    headers = {
        'Authorization': 'Bearer ' + access_token,  # ここにアクセストークンを指定
    }

    params = {
        'fields' : 'open_id,display_name,avatar_url_100'
    }

    res = requests.get(base_url, headers=headers, params=params)
    user_data = []
    if res.status_code == 200:
        response_data = res.json()
        # print('---get user-data---')
        # print(response_data)
        if 'data' in response_data:
            user = response_data['data']['user']
            open_id = user['open_id']
            account_name = user['display_name']
            icon_url = user['avatar_url_100']
            user_data.extend([open_id, account_name, icon_url])
    # user_dataは1次元配列になっている
    return user_data


def merge_data(user_data, post_data):
    # user_dataは1次元配列で渡され、post_dataは2次元配列で渡される
    # なので、post_dataの各値に対してuser_dataとtodayをマージする必要がある
    # なのでpost_dataの配列数分繰り返し処理を行う必要がある
    jst_timezone = timezone(timedelta(hours=9))
    today = str(datetime.now(jst_timezone))
    merged_data = []
    base_merged_data = [today]
    base_merged_data.extend(user_data)
    # print('user_data: ', user_data)
    # print('post_data: ', post_data)
    if len(post_data) == 0:
        return False
    else:
        for one_post_data in post_data:
            one_merged_data = base_merged_data + one_post_data
            print(base_merged_data)
            print(one_merged_data)
            merged_data.append(one_merged_data)
        return merged_data

def process_past_time(utc_unix_epoch):
    import math
    # 提供されたUTC Unix epoch (秒単位)
    # UTC Unix epochをdatetimeオブジェクトに変換
    utc_datetime = datetime.utcfromtimestamp(utc_unix_epoch)
    # 日本標準時 (JST) への変換
    jst_timezone = timezone(timedelta(hours=9))  # UTC+9:00 (日本標準時)
    jst_datetime = utc_datetime.astimezone(jst_timezone)
    # 今日の日付と時刻を取得
    today = datetime.now(jst_timezone)
    # 今日の日時と提供されたUnix epochの日時の差を計算
    time_difference = today - jst_datetime
    # 差を時間に変換
    # 差を日と時間に変換
    hours_difference = time_difference.total_seconds() / 3600
    hours_difference_round = round(hours_difference)
    # print("今日の日時:", today)
    # print("提供されたUnix epochの日時 (JST):", str(jst_datetime))
    # print("今日の日時との差:", hours_difference_round, '時間')
    return str(jst_datetime), hours_difference_round


# spreadsheetへのデータ追加
def handle_spread_sheet(append_data):
    wb_db = gc.open_by_key('1VwJux4jbXUlc6Mjgs0ky-U6SduD2whyKB_gOsD9FAdM')
    sheet_name = 'data-base'
    wb_db.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': append_data})
    print('データ追加完了！')


if __name__ == '__main__':
    print('start apps')
    main()
