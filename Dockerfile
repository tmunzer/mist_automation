FROM python:3.12.0a3-slim

LABEL maintainer="tmunzer@juniper.net"
LABEL one.stag.mist_automation.version="2.0.0"
LABEL one.stag.mist_automation.release-date="2022-05-20"

RUN pip install --upgrade pip
RUN pip install --no-cache-dir flask requests

COPY ./src /app/
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 51361
CMD ["python","-u","/app/main.py"]
