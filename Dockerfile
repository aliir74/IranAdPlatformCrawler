FROM selenium/standalone-chrome:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /opt
RUN sudo apt-get update && sudo apt-get install -y python3 python3-pip
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src /opt/
