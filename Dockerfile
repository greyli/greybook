FROM python:3.12-slim

RUN groupadd -r greybook && useradd -r -g greybook greybook

WORKDIR /home/greybook
RUN apt-get update
RUN apt-get install -y gcc g++

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY greybook greybook
COPY migrations migrations
COPY logs logs
COPY uploads uploads
COPY app.py .

ENV FLASK_APP app
ENV FLASK_CONFIG production

RUN chown -R greybook:greybook .
USER greybook

EXPOSE 5000
RUN venv/bin/flask db upgrade
ENTRYPOINT ["venv/bin/gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
