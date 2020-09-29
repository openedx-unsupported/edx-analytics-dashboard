FROM ubuntu:xenial as openedx

RUN apt update && \
  apt-get install -y software-properties-common && \
  apt-add-repository -y ppa:deadsnakes/ppa && apt-get update && \
  apt-get install -y curl && \
  apt-get upgrade -qy && \
  apt install -y git-core language-pack-en build-essential python3.8-dev python3.8-distutils libmysqlclient-dev && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python3.8 get-pip.py && python3.8 -m pip install --upgrade pip setuptools && \
  rm -rf /var/lib/apt/lists/*

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

