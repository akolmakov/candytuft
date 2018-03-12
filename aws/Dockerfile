FROM ubuntu:17.10

# apt-transport-https ca-certificates gnupg

RUN apt-get update -qqy \
    && apt-get -qqy install wget unzip git python3-pip \
    && pip3 install --upgrade pip

ARG CHROME_VERSION="google-chrome-stable"
RUN wget -qO - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qqy \
    && apt-get -qqy install $CHROME_VERSION \
    && rm /etc/apt/sources.list.d/google-chrome.list \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

ARG CHROME_DRIVER_VERSION="2.36"
RUN wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && rm -rf /usr/bin/chromedriver \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/bin \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod 755 /usr/bin/chromedriver

ARG CANDYTUFT_WHEEL="candytuft-0.1-py2.py3-none-any.whl"
ADD ${CANDYTUFT_WHEEL} /tmp

RUN pip3 install --ignore-installed /tmp/${CANDYTUFT_WHEEL}

EXPOSE 8080

RUN mkdir /var/log/candytuft

CMD candytuft --chrome-path "/usr/bin/google-chrome" --chrome-driver-path "/usr/bin/chromedriver" --log-file-path "/var/log/candytuft/candytuft.log"