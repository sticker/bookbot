FROM ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/bookbot-platform:latest
MAINTAINER kakincamp-team <isp-kakin-camp@list.nifty.co.jp>

# ソースを配置
USER root
RUN mkdir -p /service/bookbot
COPY . /service/bookbot
WORKDIR /service/bookbot

# Python依存ライブラリをインストール
RUN pipenv install

## botを起動する
ENTRYPOINT ["pipenv", "run"]

# CMDでデフォルト引数を指定
CMD ["start"]
