FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m camoufox fetch

COPY . .

CMD ["python", "main.py"]