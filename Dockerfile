FROM python:3.8-slim-buster

WORKDIR /usr/app

COPY requirements.txt ./
# COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -m spacy download en_core_web_lg
CMD [ "python", "./app.py" ]