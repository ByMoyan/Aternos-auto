FROM python:3.11-slim-bookworm

WORKDIR /app

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

RUN apt-get update && apt-get install -y \
    wget bzip2 libgtk-3-0 libdbus-glib-1-2 libxt6 \
    libxrender1 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 \
    libcairo-gobject2 libgdk-pixbuf2.0-0 libxss1 libgbm1 \
    libnss3 libnspr4 xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m camoufox fetch

COPY . .

CMD ["python", "main.py"]