FROM ubuntu:24.04

ARG GET_COMMIT_HASH
ENV GET_COMMIT_HASH=$GET_COMMIT_HASH

WORKDIR /app

RUN apt-get update
RUN apt-get install -y ffmpeg python3 python3-pip
COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt
COPY src .

CMD ["python3", "main.py"]
