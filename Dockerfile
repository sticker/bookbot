FROM python:3.7-slim
MAINTAINER kakincamp-team <isp-kakin-camp@list.nifty.co.jp>

# 日本時間対応
ENV TZ=Asia/Tokyo

RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq \
 && apt-get install -y \
      build-essential \
      xorg \
      libssl-dev \
      libxrender-dev \
      wget \
      unzip \
      gdebi \
      multiarch-support \
 && apt-get autoremove \
 && apt-get clean

RUN wget http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb && \
    dpkg -i libpng12-0_1.2.54-1ubuntu1.1_amd64.deb && \
    rm -f libpng12-0_1.2.54-1ubuntu1.1_amd64.deb

RUN wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb && \
    dpkg -i libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb && \
    rm -f libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb

RUN wget https://cloudfront.debian.net/debian-archive/debian/pool/main/libj/libjpeg8/libjpeg8_8d-1+deb7u1_amd64.deb && \
    dpkg -i libjpeg8_8d-1+deb7u1_amd64.deb && \
    rm -f libjpeg8_8d-1+deb7u1_amd64.deb

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
