FROM python:3

ADD ./src/chickenrun/ /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "./chickenrun.py" ]
