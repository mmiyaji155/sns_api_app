import time

import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import time

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
wb = gc.open_by_key('1VwJux4jbXUlc6Mjgs0ky-U6SduD2whyKB_gOsD9FAdM')
sh = wb.worksheet('data-base')


def discord_main():
    send_log = []
    result_df = process_data_max_view_count()
    for index, row in result_df.iterrows():
        account_name = row['account_name']
        icon_url = row['icon_url']
        view_count = row['view_count']
        open_id = row['open_id']
        embeds = gen_embed_post(row)
        bot = {'name' : account_name, 'icon_url' : icon_url, 'open_id' : open_id}
        post_flag, url, comment = handle_bot(bot, view_count)
        if post_flag:
            send_post(url, bot, embeds, comment, send_log)
            print('send!!')
        else: print('unsent!!')
        time.sleep(15)
    wb.values_append('send-log', {'valueInputOption': 'USER_ENTERED'}, {'values': send_log})
    # print('hello')


def handle_bot(bot, view_count):
    """
    botからアカウント名を取得し、投稿チャンネルのwebhook URLを特定する。
    アカウントとwebhookの一覧はシート上に作成しておき、この関数内で取得してくる。
    view_countを用いて、投稿対象かどうかをBoolでreturnする。
    trueの場合、view_countを用いて、メッセージを選択する。
    :param bot:
    :param view_count:
    :return:
    """
    post_flag = False
    sh_account_list = wb.worksheet('account-data')
    sh_log = wb.worksheet('send-log')
    df = pd.DataFrame(sh_account_list.get_values()[1:], columns=sh_account_list.get_values()[0])
    df_log = pd.DataFrame(sh_log.get_values()[1:], columns=sh_log.get_values()[0])
    # print(df_log)
    open_id = bot['open_id']
    url = df['webhook_url'].loc[df['open_id'] == open_id]
    if url.empty:
        print("URL is empty")
        url = 'https://discord.com/api/webhooks/1198140921229889566/YCarCSSNs0ZdkFpFBAvMH1aJZxQzqWffYEZdnpnMyQI3BhMmUM7KRnqftKUVLPz24ty1'
    else:
        print("URL is not empty:", url)
        url = url.item()
    df_log['view_count'] = df_log['view_count'].astype(np.int64)
    df_log = df_log.sort_values('view_count', ascending=False)
    # print(type(df_log))
    # print(df_log)

    df_log_uni = df_log.drop_duplicates(subset='open_id')
    # print(df_log_uni)

    previous_view_count = df_log_uni['view_count'].loc[df_log['open_id'] == open_id]
    print(previous_view_count)

    if previous_view_count.empty:
        previous_view_count = 0
    else:
        previous_view_count = previous_view_count.item()

    comment = '@everyone\n'

    # print(type(view_count))
    print(previous_view_count)
    if view_count >= 1000000:
        if previous_view_count < 1000000:
            comment += '100万再生突破🥂🚀'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''

    elif 1000000 > view_count >= 500000:
        if previous_view_count < 500000:
            comment += '50万再生突破🤩'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''

    elif 500000 > view_count >= 200000:
        if previous_view_count < 200000:
            comment += '20万再生突破🥳'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''

    elif 200000 > view_count >= 100000:
        if previous_view_count < 100000:
            comment += '10万再生突破🎊'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''

    elif 100000 > view_count >= 50000:
        if previous_view_count < 50000:
            comment += '5万再生突破👏'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''

    elif 50000 > view_count >= 10000:
        if previous_view_count < 10000:
            comment += '1万再生突破😁'
            post_flag = True
        else:
            print('通知対象外')
            comment = ''
    else:
        print('通知対象外')
        comment = ''

    # print('post_flag= ', post_flag)
    # print('url= ', url)
    # print('comment= ', comment)
    return post_flag, url, comment


def process_data_max_view_count():
    """
    投稿データのデータベースから、ヴィデオ後とにグループ化し、再生数の多い順に抽出する
    このデータを元に通知のハンドリングを行う
    :return:
    """
    df = pd.DataFrame(sh.get_values()[1:], columns=sh.get_values()[0])
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['create_time'] = pd.to_datetime(df['create_time'])
    df['time_delta'] = df['time_delta'].astype(np.int64)
    df['like_count'] = df['like_count'].astype(np.int64)
    df['comment_count'] = df['comment_count'].astype(np.int64)
    df['share_count'] = df['share_count'].astype(np.int64)
    df['view_count'] = df['view_count'].astype(np.int64)
    # print(df.dtypes)
    result_df = df.loc[df.groupby('video_id')['view_count'].idxmax().sort_values()]
    # print(result_df.loc[:, ['video_id', 'view_count']])
    # print('======')
    result_df = result_df.loc[result_df['view_count'] >= 10000]
    # print(result_df.loc[:, ['video_id', 'view_count']])
    return result_df


def gen_embed_post(series):
    title = series['title']
    share_url = series['share_url']
    thumbnail_url = series['cover_image_url']
    like_count = series['like_count']
    view_count = series['view_count']
    comment_count = series['comment_count']
    share_count = series['share_count']
    created_date = series['create_time'].strftime('%Y-%m-%d %H:%M:%S')
    pasta_time = series['time_delta']

    embed = {"embeds": [
        {
            "title": title,
            "url": share_url,
            "color": 2547914,
            "thumbnail": {
                "url": thumbnail_url
            },
            "fields": [
                {
                    "name": "再生数",
                    "value": view_count,
                    "inline": True,
                },
                {
                    "name": "いいね数",
                    "value": like_count,
                    "inline": True,
                },
                {
                    "name": "投稿日時",
                    "value": created_date,
                    "inline": True,
                },
                {
                    "name": "シェア数",
                    "value": share_count,
                    "inline": True,
                },
                {
                    "name": "コメント数",
                    "value": comment_count,
                    "inline": True,
                },
                {
                    "name": "経過日数",
                    "value": str(round(int(pasta_time)/24)),
                    "inline": True,
                },
            ],
        }
    ]}

    test = {"embeds": [
        {
            "title": "投稿のタイトルを指定--------------------",
            "url": "https://www.tiktok.com/@yukkurina__/video/7325786204018904328",
            "color": 2547914,
            # "thumbnail": {
            #     "url": "サムネ画像のURL"
            # },
            "fields": [
                {
                    "name": "再生数",
                    "value": "test",
                    "inline": True,
                },
                {
                    "name": "いいね数",
                    "value": "テスト",
                    "inline": True,
                },
                {
                    "name": "コメント数",
                    "value": "テスト",
                    "inline": True,
                },
                {
                    "name": "シェア数",
                    "value": "テスト",
                    "inline": True,
                },
            ],
        }
    ]}

    print('gen!')
    print('===embed===')
    print(embed)
    return embed['embeds']


def send_post(url, bot, embeds, content, array):
    webhook_url = url

    main_content = {
        'username': bot['name'],
        'avatar_url': bot['icon_url'],
        'content': content,
        'embeds': embeds
    }
    headers = {'Content-Type': 'application/json'}
    # print('====main_content====')
    # print(main_content)
    # print('-----')
    response = requests.post(webhook_url, json=main_content, headers=headers)
    print(response)
    view_count = embeds[0]['fields'][0]['value']
    account_name = bot['name']
    open_id = bot['open_id']
    array.append([open_id, account_name, view_count])
    # print('===array===')
    # print(array)



if __name__ == '__main__':

    discord_main()

