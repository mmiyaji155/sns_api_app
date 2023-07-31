import requests
import json
import os
import gspread


def main():
    post_data = get_post_data()
    handle_spread_sheet(post_data)
    print('更新完了しました！')


def get_post_data():
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


# spreadsheetへのデータ貼り付け
def handle_spread_sheet(post_data):
    wb = gspread.service_account(filename='Google_cloud key_my-project-58552-python-40b21b969066.json')
    ws = wb.open_by_url('***spread sheet url***') #urlを入力
    old_data = ws.get_all_values()
    new_data = old_data.extend(post_data)
    ws.update_cells(new_data)

# 現在のデータを取得する
# 新しいデータを追加する（using extend method）
# 追加後のすべてのデータを貼り付ける