import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
from lib import get_logger, app_home


class Pdf:
    def __init__(self):
        self.logger = get_logger(__name__)

    def make_approved_html(self, item: dict) -> str:
        item['entry_date'] = "%s/%s/%s %s:%s:%s" % (item['entry_time'][0:4],
                                            item['entry_time'][4:6],
                                            item['entry_time'][6:8],
                                            item['entry_time'][8:10],
                                            item['entry_time'][10:12],
                                            item['entry_time'][12:14])
        book_type = item.get('book_type', '本')
        if book_type != '本':
            item['book_type'] = f'({book_type})'
        else:
            item['book_type'] = ''
        self.logger.debug(item)

        tpl_path = os.path.join(app_home, "resource", "tpl")
        tpl_name = "approved.tpl.htm"
        env = Environment(loader=FileSystemLoader(tpl_path, encoding="utf8"))
        tpl = env.get_template(tpl_name)
        html = tpl.render(item, app_home=app_home)
        return html

    def make_approved_pdf(self, item: dict, save_path: str):

        html = self.make_approved_html(item)

        # PDFファイルを保存
        try:
            pdfkit.from_string(html, save_path)
        except:
            import traceback
            traceback.print_exc()
            return False

        return save_path


