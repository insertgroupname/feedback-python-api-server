FROM python:3.8-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./app.py" ]