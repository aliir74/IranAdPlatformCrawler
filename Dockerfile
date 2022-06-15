FROM selenium/standalone-chrome:latest
USER root
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /opt
RUN apt-get update && apt-get install -y python3 python3-pip firefox
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src /opt/
