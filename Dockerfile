FROM python:3.9

WORKDIR /app
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY src .
ENTRYPOINT ["python3", "app.py"]