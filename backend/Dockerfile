FROM python:3.11-bullseye
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt
# COPY the app code, which now includes the 'googleadk' and 'google' folders
COPY ./app /usr/src/app/app
COPY seed.py .