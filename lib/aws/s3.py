from lib import get_logger
from logging import DEBUG
from boto3 import Session
import os


class S3(object):
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "798228459898")
    S3_BUCKET_PDF = f"bookbot-pdf-{AWS_ACCOUNT_ID}"

    def __init__(self):
        self.logger = get_logger(__name__)
        region_name = os.getenv('AWS_REGION', 'ap-northeast-1')
        # 環境変数 AWS_REGION が設定されていない場合は処理しない
        if region_name != '':
            session = Session(region_name=region_name)
            self.resource = session.resource('s3')

    def upload(self, bucket_name: str, path_local: str, path_s3: str):
        s3 = self.resource
        self.logger.log(DEBUG, "upload: path_s3=" + path_s3 + " path_local=" + path_local)
        s3.Bucket(bucket_name).upload_file(path_local, path_s3)

    def upload_to_pdf(self, path_local: str, process_yyyy=None):
        self.upload(bucket_name=self.S3_BUCKET_PDF,
                    path_local=path_local,
                    path_s3=process_yyyy + "/" + os.path.basename(path_local))
