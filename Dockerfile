FROM python:3.8-slim

WORKDIR /opt/app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install curl gcc -y

RUN groupadd -r nrk_nynorsk && useradd --no-log-init -m -r -g nrk_nynorsk nrk_nynorsk
USER nrk_nynorsk

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
ENV PATH=/home/nrk_nynorsk/.poetry/bin:$PATH
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY . .

EXPOSE 8000

HEALTHCHECK CMD ["curl", "-f", "http://localhost:8000"]

ENTRYPOINT [ "./docker-entrypoint.sh" ]
