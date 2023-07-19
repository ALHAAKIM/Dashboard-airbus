# Dockerfile
# builds a docker image of a python app, that provides docker stats as prometheus metrics 
# on port 8080

FROM python:3
RUN apt-get update

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python3", "promStats.py", "run", "--host=0.0.0.0", "-p", "8080"]
