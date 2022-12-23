FROM python:3.10

RUN mkdir /data

WORKDIR /data

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY server.py .

CMD ["python", "server.py"]