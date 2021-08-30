FROM ubuntu:focal as openedx

RUN apt update && apt-get upgrade -qy
RUN apt install -y git-core language-pack-en python3.8 python3-pip python3.8-distutils libmysqlclient-dev && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  pip install --upgrade pip setuptools && \
  rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/venv
RUN python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV ANALYTICS_DASHBOARD_CFG /edx/etc/insights.yml

WORKDIR /edx/app/analytics_dashboard
COPY requirements /edx/app/analytics_dashboard/requirements
RUN python3.8 -m pip install -r requirements/production.txt

EXPOSE 8110
CMD gunicorn -b 127.0.0.1:8110 --workers 2 --timeout=300 analytics_dashboard.wsgi:application

RUN useradd -m --shell /bin/false app
USER app
COPY . /edx/app/analytics_dashboard

FROM openedx as edx.org
RUN python3.8 -m pip install newrelic
CMD newrelic-admin run-program gunicorn -b 127.0.0.1:8110 --workers 2 --timeout=300 analytics_dashboard.wsgi:application

