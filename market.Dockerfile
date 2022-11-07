# syntax=docker/dockerfile:1

FROM python:3.10-slim

# set up the venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install the required modules
COPY pip_reqs.txt .
RUN pip3 install -r pip_reqs.txt

# install the app
WORKDIR /app
COPY ./demo_config.py .
COPY ./item.py .
COPY ./market.py .

CMD [ "python3", "-u", "-m", "market" ]
