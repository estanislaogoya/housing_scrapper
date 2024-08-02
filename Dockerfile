# syntax=docker/dockerfile:1

FROM python:3.10.5-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /app

# Create a wrapper script
RUN echo "python -u main.py" > wrapper.sh
RUN chmod +x wrapper.sh

# CMD specifies the command to run on container startup
CMD ["sh", "./wrapper.sh"]