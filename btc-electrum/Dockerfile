FROM python:3.12-alpine

ARG VERSION
ARG CHECKSUM_SHA512

ENV BTC_ELECTRUM_VERSION=$VERSION
ENV BTC_ELECTRUM_USER=btc-electrum
ENV BTC_ELECTRUM_HOME=/home/$BTC_ELECTRUM_USER
ENV BTC_ELECTRUM_NETWORK=mainnet

RUN adduser -D $BTC_ELECTRUM_USER

RUN mkdir -p /data ${BTC_ELECTRUM_HOME} && \
	ln -sf /data ${BTC_ELECTRUM_HOME}/.electrum && \
	chown ${BTC_ELECTRUM_USER} ${BTC_ELECTRUM_HOME}/.electrum /data

# IMPORTANT: always verify gpg signature before changing a hash here!
ENV BTC_ELECTRUM_CHECKSUM_SHA512 $CHECKSUM_SHA512

RUN apk --no-cache add --virtual build-dependencies gcc musl-dev libsecp256k1 libsecp256k1-dev libressl-dev
RUN wget https://download.electrum.org/${BTC_ELECTRUM_VERSION}/Electrum-${BTC_ELECTRUM_VERSION}.tar.gz
RUN [ "${BTC_ELECTRUM_CHECKSUM_SHA512}  Electrum-${BTC_ELECTRUM_VERSION}.tar.gz" = "$(sha512sum Electrum-${BTC_ELECTRUM_VERSION}.tar.gz)" ]
RUN echo -e "**************************\n SHA 512 Checksum OK\n**************************"
RUN pip3 install cryptography Electrum-${BTC_ELECTRUM_VERSION}.tar.gz
RUN rm -f Electrum-${BTC_ELECTRUM_VERSION}.tar.gz

RUN mkdir -p /data \
	    ${BTC_ELECTRUM_HOME}/.electrum/wallets/ \
	    ${BTC_ELECTRUM_HOME}/.electrum/testnet/wallets/ \
	    ${BTC_ELECTRUM_HOME}/.electrum/regtest/wallets/ \
	    ${BTC_ELECTRUM_HOME}/.electrum/simnet/wallets/ && \
    ln -sf ${BTC_ELECTRUM_HOME}/.electrum/ /data && \
	chown -R ${BTC_ELECTRUM_USER} ${BTC_ELECTRUM_HOME}/.electrum /data

USER $BTC_ELECTRUM_USER
WORKDIR $BTC_ELECTRUM_HOME
VOLUME /data
EXPOSE 7000

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
