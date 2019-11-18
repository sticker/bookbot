import os


# botアカウントのトークンを指定
API_TOKEN = os.getenv('API_TOKEN')

# このbot宛のメッセージで、どの応答にも当てはまらない場合の応答文字列
DEFAULT_REPLY = "意味がわかりませんよ！helpでコマンドを確認してください！"

# プラグインスクリプトを置いてあるサブディレクトリ名のリスト
PLUGINS = ['plugins']

# 年間上限金額
MAX_AMOUNT = os.getenv("MAX_AMOUNT", 10000)

# 公式チャンネルID
DEFAULT_CHANNEL_ID = os.getenv('DEFAULT_CHANNEL_ID', 'CC6DENSDV')

# 感想登録リマインダの通知時間
IMPRESSION_REMINDER_TIME = "11:00"
