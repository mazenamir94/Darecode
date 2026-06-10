FROM python:3.11-slim

# System deps + compilers for running generated code
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget build-essential default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# TypeScript + Express (so generated Node web servers can `require('express')`)
RUN npm install -g ts-node typescript express
ENV NODE_PATH=/usr/lib/node_modules

# Python deps
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Workspace for generated code
RUN mkdir -p /workspace sessions

ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color

ENTRYPOINT ["python", "main.py"]
