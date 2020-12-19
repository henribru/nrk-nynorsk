FROM python:3.8-slim

WORKDIR /opt/app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install gcc -y && rm -rf /var/lib/apt/lists/*

RUN groupadd -r nrk_nynorsk && useradd --no-log-init --create-home --system --gid nrk_nynorsk nrk_nynorsk
USER nrk_nynorsk
ENV PATH=/home/nrk_nynorsk/.local/bin:$PATH

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev && rm -rf ~/.cache/pypoetry/cache/ ~/.cache/pypoetry/artifacts/

COPY . .

EXPOSE 8000

HEALTHCHECK CMD ["curl", "-f", "http://localhost:8000"]

ENTRYPOINT [ "./docker-entrypoint.sh" ]
