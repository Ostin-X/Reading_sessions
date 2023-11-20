FROM python:3.11-slim

# env variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWEITEBYTECODE 1

# setting work directory
WORKDIR /code

# Copy the project's dependency files
COPY pyproject.toml poetry.lock /code/

# Install Poetry and project dependencies
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

RUN mkdir -p /code/static && if [ ! -d /code/media ]; then mkdir /code/media; fi

COPY src /code


