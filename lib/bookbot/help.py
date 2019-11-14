from lib import get_logger


class Help:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.botname = "bookbot"

    def default(self, message):
        botname = self.botname

        usages = list()
        usages.append(f"`@{botname} list` : 直近20件の登録情報をリスト表示する")
        usages.append(f"`@{botname} list [検索文字]` : 過去全件から *題名* ・ *氏名* ・ *Slack名* で検索（複数指定でAND検索）")
        usages.append(f"`@{botname} desc [登録番号]` : 指定した番号の登録情報を感想付きで表示する  alias: `describe` `display` `detail` `詳細`")
        usages.append(f"`@{botname} total` : 自分の今年度の立替金合計を表示する alias: `合計`")
        usages.append(f"`@{botname} total all [年度(YYYY)]` : 指定年度（省略すると今年度）のすべての立替金合計を表示する alias: `合計 全て`")
        usages.append(f"`@{botname} rm [登録番号]` : 指定した番号の登録情報を削除する alias: `del` `delete` `削除`")

        message.send("\n".join(usages))
