FROM docker.ocf.berkeley.edu/theocf/debian:stretch

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libpam-krb5 \
        nginx \
        python3 \
        python3-pip \
        python3-setuptools \
        runit \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY services/nginx/nginx.conf /etc/nginx
COPY discourse_pam /etc/pam.d/discourse

RUN mkdir -p /opt/discourse_sso

COPY requirements.txt /opt/discourse_sso/requirements.txt
RUN pip3 install -r /opt/discourse_sso/requirements.txt

RUN chown nobody:nogroup /opt/discourse_sso
WORKDIR /opt/discourse_sso
USER nobody

RUN echo "ocfstaff\nopstaff" > /opt/discourse_sso/allowed-groups

COPY --chown=nobody:nogroup app.py /opt/discourse_sso
COPY --chown=nobody:nogroup services /opt/discourse_sso/services

CMD ["runsvdir", "/opt/discourse_sso/services"]
