FROM bitnami/python

RUN apt-get update ; apt-get -y install netcat default-mysql-client && pip3 install PyJWT tornado cryptography mysql-connector tornadoadfsoauth2
WORKDIR /web/
ADD web /web
ADD schema.sql /web/
ADD wait-for /web/
