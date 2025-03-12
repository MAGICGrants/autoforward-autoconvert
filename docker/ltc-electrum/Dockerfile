FROM ubuntu:latest

ARG VERSION
ARG CHECKSUM_SHA512

RUN apt update && \
    apt install -y wget libfuse2 fuse3

ENV ELECTRUM_VERSION=$VERSION
ENV ELECTRUM_USER=electrum
ENV ELECTRUM_HOME=/home/$ELECTRUM_USER
ENV ELECTRUM_CHECKSUM_SHA512 $CHECKSUM_SHA512

RUN useradd -m $ELECTRUM_USER
USER $ELECTRUM_USER
WORKDIR $ELECTRUM_HOME

RUN wget https://github.com/ltcmweb/electrum-ltc/releases/download/${ELECTRUM_VERSION}/electrum-ltc-${ELECTRUM_VERSION}-x86_64.AppImage -O electrum-ltc.appimage
RUN [ "${ELECTRUM_CHECKSUM_SHA512}  electrum-ltc.appimage" = "$(sha512sum electrum-ltc.appimage)" ]
RUN echo -e "**************************\n SHA 512 Checksum OK\n**************************"
COPY --chown=$ELECTRUM_USER:$ELECTRUM_USER ./docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x ./electrum-ltc.appimage ./docker-entrypoint.sh
RUN ./electrum-ltc.appimage --appimage-extract
RUN rm ./electrum-ltc.appimage

EXPOSE 7000
ENTRYPOINT [ "./docker-entrypoint.sh" ]