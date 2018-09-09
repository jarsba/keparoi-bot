FROM python:3.6-alpine

COPY requirements.txt /

RUN apk --no-cache --update-cache add python3-dev gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev g++ libxslt-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY /app /app
WORKDIR /app

CMD [ "python", "main.py" ]
