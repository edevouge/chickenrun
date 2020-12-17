#!/bin/bash

set -o errexit
set -o nounset

# variables
duration=7300
subj="/C=FR/ST=France/L=Rennes/O=None/CN=Mosquitto"
key_size=2048

# create dir
mkdir -p ca client server

# generate ca, server and clients certs using openssl
openssl genrsa -out ./ca/ca.key ${key_size}
openssl req -new -x509 -days ${duration} -key ./ca/ca.key -out ./ca/ca.crt -subj ${subj}
openssl genrsa -out ./server/server.key ${key_size}
openssl req -new -out ./server/server.csr -key ./server/server.key -subj ${subj}
openssl x509 -req -in ./server/server.csr -CA ./ca/ca.crt -CAkey ./ca/ca.key -CAcreateserial -out ./server/server.crt -days ${duration}
openssl genrsa -out ./client/client.key ${key_size}
openssl req -new -out ./client/client.csr -key ./client/client.key  -subj ${subj}
openssl x509 -req -in ./client/client.csr -CA ./ca/ca.crt -CAkey ./ca/ca.key -CAcreateserial -out ./client/client.crt -days ${duration}
