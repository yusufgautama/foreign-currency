FROM python:3.6
LABEL maintainer "Yusuf Pradana <yusufgtm@gmail.com>"
RUN apt-get update

WORKDIR /home/foreign_currency
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn psycopg2

COPY app app
COPY migrations migrations
COPY manage.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_ENV="docker"
EXPOSE 5000
ENTRYPOINT ["sh", "/home/foreign_currency/boot.sh"]