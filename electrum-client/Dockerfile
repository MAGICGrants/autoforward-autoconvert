FROM python:3.12-alpine

ARG VERSION
ARG CHECKSUM_SHA512

ENV ELECTRUM_VERSION $VERSION
ENV ELECTRUM_USER electrum
ENV ELECTRUM_HOME /home/$ELECTRUM_USER
ENV ELECTRUM_NETWORK mainnet

RUN adduser -D $ELECTRUM_USER

RUN mkdir -p /data ${ELECTRUM_HOME} && \
	ln -sf /data ${ELECTRUM_HOME}/.electrum && \
	chown ${ELECTRUM_USER} ${ELECTRUM_HOME}/.electrum /data

# IMPORTANT: always verify gpg signature before changing a hash here!
ENV ELECTRUM_CHECKSUM_SHA512 $CHECKSUM_SHA512

RUN apk --no-cache add --virtual build-dependencies gcc musl-dev libsecp256k1 libsecp256k1-dev libressl-dev
RUN wget https://download.electrum.org/${ELECTRUM_VERSION}/Electrum-${ELECTRUM_VERSION}.tar.gz
RUN [ "${ELECTRUM_CHECKSUM_SHA512}  Electrum-${ELECTRUM_VERSION}.tar.gz" = "$(sha512sum Electrum-${ELECTRUM_VERSION}.tar.gz)" ]
RUN echo -e "**************************\n SHA 512 Checksum OK\n**************************"
RUN pip3 install cryptography Electrum-${ELECTRUM_VERSION}.tar.gz
RUN rm -f Electrum-${ELECTRUM_VERSION}.tar.gz

RUN mkdir -p /data \
	    ${ELECTRUM_HOME}/.electrum/wallets/ \
	    ${ELECTRUM_HOME}/.electrum/testnet/wallets/ \
	    ${ELECTRUM_HOME}/.electrum/regtest/wallets/ \
	    ${ELECTRUM_HOME}/.electrum/simnet/wallets/ && \
    ln -sf ${ELECTRUM_HOME}/.electrum/ /data && \
	chown -R ${ELECTRUM_USER} ${ELECTRUM_HOME}/.electrum /data

USER $ELECTRUM_USER
WORKDIR $ELECTRUM_HOME
VOLUME /data
EXPOSE 7000

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
