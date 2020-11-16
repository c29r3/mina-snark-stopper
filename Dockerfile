FROM python:3.7-slim


RUN apt-get update \
    && apt-get install -y wget git \
    && rm -rf /var/lib/apt/lists/* \
    && rm /bin/sh \
    && ln -s /bin/bash /bin/sh \
    && groupadd -r user \
    && useradd --create-home --no-log-init -r -g user user \
    && mkdir /mina \
    && chown user:user /mina \
    && apt-get clean \
    && apt-get autoclean

    
WORKDIR /mina
USER user

RUN echo "Clone sources from repository..." \
    && git clone https://github.com/c29r3/mina-snark-stopper.git \
    && mv -f mina-snark-stopper/* . \
    && rm -rf mina-snark-stopper \
    && python3 -m venv venv \
    && source ./venv/bin/activate \
    && pip3 install -r requirements.txt --no-cache-dir

ENTRYPOINT ["/mina/venv/bin/python3", "snark-stopper.py"]
