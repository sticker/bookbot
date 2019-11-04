FROM python:3.7-slim
MAINTAINER kakincamp-team <isp-kakin-camp@list.nifty.co.jp>

# 日本時間対応
ENV TZ=Asia/Tokyo

RUN apt-get update -qq \
 && apt-get install -y \
      build-essential \
      xorg \
      libssl-dev \
      libxrender-dev \
      wget \
      unzip \
      gdebi \
      libpng-dev \
      libjpeg-dev \
      libssl-dev \
 && apt-get autoremove \
 && apt-get clean
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.2.1/wkhtmltox-0.12.2.1_linux-wheezy-amd64.deb && \
    dpkg -i wkhtmltox-0.12.2.1_linux-wheezy-amd64.deb && \
    rm -f wkhtmltox-0.12.2.1_linux-wheezy-amd64.deb

# 日本語フォントとして Noto Fonts をインストールする。
RUN wget https://noto-website.storage.googleapis.com/pkgs/Noto-unhinted.zip \
 && unzip -d NotoSansJapanese Noto-unhinted.zip \
 && mkdir -p /usr/share/fonts/opentype \
 && mv -fv ./NotoSansJapanese /usr/share/fonts/opentype/NotoSansJapanese \
 && rm -rfv Noto-unhinted.zip \
 && fc-cache -fv

# pipenvをインストール
RUN pip install pipenv

# ソースを配置
USER root
RUN mkdir -p /service/bookbot
COPY . /service/bookbot
WORKDIR /service/bookbot

# Python依存ライブラリをインストール
RUN pipenv install

## bashを起動する
ENTRYPOINT ["pipenv", "run"]

# CMDでデフォルト引数を指定
CMD ["start"]
