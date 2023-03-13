FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update

# copy the requirements first and run pip install
# as it tends to change very little, it should
# be placed before copying backend folder
ADD ./requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /code
WORKDIR /code

ADD ./ /code/