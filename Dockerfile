FROM python:3.9-buster

ADD ./src/chickenrun/ /app

WORKDIR /app



RUN pip install --no-cache-dir  -r requirements.txt

CMD [ "python", "./chickenrun.py" ]
