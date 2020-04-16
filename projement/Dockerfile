FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY README.md /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY projement /code/
