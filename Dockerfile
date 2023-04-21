FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# copy the requirements first and run pip install
# as it tends to change very little, it should
# be placed before copying backend folder
COPY ./requirements.txt /code

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/

CMD ["python", "main.py"]
