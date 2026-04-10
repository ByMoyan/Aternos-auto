FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y xvfb

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["xvfb-run", "--auto-servernum", "python", "main.py"]