FROM python:3

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app

RUN apt update && apt install -y nodejs

ENTRYPOINT ["node", "app.js"]