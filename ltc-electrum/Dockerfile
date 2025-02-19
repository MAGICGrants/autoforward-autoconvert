FROM python:3.12-alpine

ARG VERSION
ARG CHECKSUM_SHA512

ENV LTC_ELECTRUM_VERSION=$VERSION
ENV LTC_ELECTRUM_USER=ltc-electrum
ENV LTC_ELECTRUM_HOME=/home/$LTC_ELECTRUM_USER
ENV LTC_ELECTRUM_NETWORK=mainnet

RUN adduser -D $LTC_ELECTRUM_USER

RUN mkdir -p /data ${LTC_ELECTRUM_HOME} && \
	ln -sf /data ${LTC_ELECTRUM_HOME}/.electrum && \
	chown ${LTC_ELECTRUM_USER} ${LTC_ELECTRUM_HOME}/.electrum /data

# IMPORTANT: always verify gpg signature before changing a hash here!
ENV LTC_ELECTRUM_CHECKSUM_SHA512 $CHECKSUM_SHA512

RUN apk --no-cache add --virtual build-dependencies gcc musl-dev libsecp256k1 libsecp256k1-dev libressl-dev
RUN wget https://download.electrum.org/${LTC_ELECTRUM_VERSION}/Electrum-${LTC_ELECTRUM_VERSION}.tar.gz
RUN [ "${LTC_ELECTRUM_CHECKSUM_SHA512}  Electrum-${LTC_ELECTRUM_VERSION}.tar.gz" = "$(sha512sum Electrum-${LTC_ELECTRUM_VERSION}.tar.gz)" ]
RUN echo -e "**************************\n SHA 512 Checksum OK\n**************************"
RUN pip3 install cryptography Electrum-${LTC_ELECTRUM_VERSION}.tar.gz
RUN rm -f Electrum-${LTC_ELECTRUM_VERSION}.tar.gz

RUN mkdir -p /data \
	    ${LTC_ELECTRUM_HOME}/.electrum/wallets/ \
	    ${LTC_ELECTRUM_HOME}/.electrum/testnet/wallets/ \
	    ${LTC_ELECTRUM_HOME}/.electrum/regtest/wallets/ \
	    ${LTC_ELECTRUM_HOME}/.electrum/simnet/wallets/ && \
    ln -sf ${LTC_ELECTRUM_HOME}/.electrum/ /data && \
	chown -R ${LTC_ELECTRUM_USER} ${LTC_ELECTRUM_HOME}/.electrum /data

USER $LTC_ELECTRUM_USER
WORKDIR $LTC_ELECTRUM_HOME
VOLUME /data
EXPOSE 7001

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
