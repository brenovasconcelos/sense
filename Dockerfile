FROM tiangolo/uwsgi-nginx-flask:python3.8
COPY ./app /app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -f /requirements.txt