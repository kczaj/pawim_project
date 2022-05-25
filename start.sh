#!/bin/bash

secret="LOGIN_JWT_SECRET="
value=$(openssl rand -base64 32)
touch .env
echo "${secret}${value}" > .env
secret="SECRET_KEY="
value=$(openssl rand -base64 32)
echo "${secret}${value}" >> .env

docker-compose up $1