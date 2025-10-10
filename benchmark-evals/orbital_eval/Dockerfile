FROM python:3.9-slim
WORKDIR /workspace
# Install git and Python dependencies
RUN apt-get update && apt-get install -y git && pip install pytest gitpython
COPY . /workspace