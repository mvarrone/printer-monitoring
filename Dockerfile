FROM python:3.9.7-alpine

WORKDIR /usr/src

COPY requirements.txt ./

RUN apk add --no-cache bash \
    && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev \
    && /usr/local/bin/python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . .

CMD ["sh", "docker-entrypoint.sh"]
