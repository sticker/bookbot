from lib import get_logger
from logging import DEBUG, INFO, WARNING
from boto3 import Session
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from time import sleep
import os


class Dynamodb(object):
    CAPACITY_EXCEPTIONS = (
        "ValidationException",
    )

    RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                        'ThrottlingException')
    RETRY_COUNT = 10

    def __init__(self):
        self.logger = get_logger(__name__)
        region_name = os.getenv('AWS_REGION', 'ap-northeast-1')
        # 環境変数 AWS_REGION が設定されていない場合は処理しない
        if region_name != '':
            session = Session(region_name=region_name)
            self.resource = session.resource('dynamodb')

    def insert(self, target, item):
        table = self.resource.Table(target)
        self.request_within_capacity(table, "put_item(Item=self.emptystr_to_none(param))", item)

    def remove(self, target, key):
        table = self.resource.Table(target)
        table.delete_item(Key=key)

    def truncate(self, target):
        self.logger.log(INFO, "%s のレコードをすべて削除します" % target)
        table = self.resource.Table(target)
        # データ全件取得
        delete_items = []
        parameters = {}
        ExclusiveStartKey = None
        while True:
            if ExclusiveStartKey is None:
                response = self.request_within_capacity(table, "scan()")
            else:
                response = self.request_within_capacity(table, "scan(ExclusiveStartKey=param)", ExclusiveStartKey)

            delete_items.extend(response["Items"])

            if ("LastEvaluatedKey" in response) is True:
                ExclusiveStartKey = response["LastEvaluatedKey"]
            else:
                break

        # キー抽出
        key_names = [x["AttributeName"] for x in table.key_schema]
        delete_keys = [{k: v for k, v in x.items() if k in key_names} for x in delete_items]

        # データ削除
        # with table.batch_writer() as batch:
        #     for key in delete_keys:
        #         batch.delete_item(Key=key)
        for key in delete_keys:
            self.logger.log(DEBUG, '%s を削除します' % key)
            self.request_within_capacity(table, "delete_item(Key=param)", key)

        self.logger.log(INFO, "%s のレコードをすべて削除しました" % target)
        return 0

    def find(self, target):
        table = self.resource.Table(target)
        convert_items = []
        ExclusiveStartKey = None
        while True:
            if ExclusiveStartKey is None:
                response = self.request_within_capacity(table, "scan()")
            else:
                response = self.request_within_capacity(table, "scan(ExclusiveStartKey=param)", ExclusiveStartKey)

            items = response["Items"]
            for item in items:
                convert_items.append(self.none_to_emptystr(item))
            if ("LastEvaluatedKey" in response) is True:
                ExclusiveStartKey = response["LastEvaluatedKey"]
            else:
                break

        return convert_items

    def query(self, tablename, key, value, sortkey=None, sortvalue=None, indexname=None, scan_index_forward=True):
        """
        PKey、SKeyを指定してDynamoDBからデータを取得する
        :param tablename:
        :param key:
        :param value:
        :param sortkey:
        :param sortvalue:
        :param indexname:
        :param scan_index_forward:
        :return:
        """
        table = self.resource.Table(tablename)

        if sortkey and sortvalue:
            kce = Key(key).eq(value) & Key(sortkey).eq(sortvalue)
        elif not sortkey and not sortvalue:
            kce = Key(key).eq(value)

        indexname_param = ""
        if indexname is not None:
            indexname_param = f", IndexName='{indexname}'"

        convert_items = []
        ExclusiveStartKey = None
        while True:
            if ExclusiveStartKey is None:
                method_str = f"query(KeyConditionExpression=param, ScanIndexForward={scan_index_forward}{indexname_param})"
                response = self.request_within_capacity(table, method_str, kce)
            else:
                method_str = f"query(KeyConditionExpression=param, ScanIndexForward={scan_index_forward}{indexname_param}, ExclusiveStartKey={ExclusiveStartKey})"
                response = self.request_within_capacity(table, method_str, kce)

            items = response["Items"]
            for item in items:
                convert_items.append(self.none_to_emptystr(item))
            if ("LastEvaluatedKey" in response) is True:
                ExclusiveStartKey = response["LastEvaluatedKey"]
            else:
                break

        return convert_items

    def emptystr_to_none(self, item):
        '''
        Boto3では空文字をDynamoDBに登録できないため、空文字をNoneに変換する
        see. https://qiita.com/t-fuku/items/0ad85c245f62883a4d11

        :param item:
        :return:
        '''
        for k, v in item.items():
            if isinstance(v, dict):
                self.emptystr_to_none(v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    list_elem = v[i]

                    if isinstance(list_elem, str):
                        if list_elem == '':
                            v[i] = None
                    elif isinstance(list_elem, list) or isinstance(list_elem, dict):
                        self.emptystr_to_none(list_elem)
            elif isinstance(v, str):
                if v == '':
                    item[k] = None

        return item

    def none_to_emptystr(self, item):
        '''
        Boto3では空文字をDynamoDBに登録できないため、空文字をNoneに変換して登録している
        DynamoDBからデータを取得するときは、Noneを空文字に戻す
        see. https://qiita.com/t-fuku/items/0ad85c245f62883a4d11

        :param item:
        :return:
        '''
        for k, v in item.items():
            if isinstance(v, dict):
                self.none_to_emptystr(v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    list_elem = v[i]

                    if list_elem is None:
                        v[i] = ''
                    elif isinstance(list_elem, list) or isinstance(list_elem, dict):
                        self.none_to_emptystr(list_elem)
            elif v is None:
                item[k] = ''

        return item

    def request_within_capacity(self, table, method_str, param=None):
        '''
        Tableオブジェクトのメソッド実行時にスループットキャパシティを超えたらリトライする
        スループットキャパシティが1000未満の場合は100ずつ増加させてリトライする
        スループットキャパシティが1000以上の場合はスリープしてリトライする
        :param table: Tableオブジェクト
        :param method_str: 実行したいメソッドの文字列（evalで実行される）
        :param param: method_str内で記述された "param" 部分に渡すオブジェクト
        :return: メソッド実行時のresponse
        '''
        retries = 0
        for i in range(self.RETRY_COUNT):
            try:
                response = eval("table.%s" % method_str)
                return response
            except ClientError as err:
                if err.response['Error']['Code'] not in self.RETRY_EXCEPTIONS:
                    raise
                else:
                    self.logger.log(INFO, 'DynamoDBのキャパシティを超えたためsleepしてリトライします retries=%d' % retries)
                    sleep(2 ** retries)
                    retries += 1

        return None