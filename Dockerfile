FROM python:3.13
WORKDIR /app
ENV FORCE_DATE=""
ENV DATA_URL=""
ENV BEHIND_REVERSE_PROXY=""
RUN groupadd -g 1000 python && \
    useradd -M --home-dir /app -u 1000 -g 1000 python && \
    chown python:python /app && \
    # Install locales
    apt-get update && \
    apt-get install -y locales && \
    sed -i '/nl_NL.UTF-8/s/^# //g' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    apt-get clean && \
    rm -rf /var/cache
USER python
COPY . /app
RUN pip3 install -r requirements.txt
CMD /app/.local/bin/gunicorn -w 6 -b :8000 'app:create_app()'
EXPOSE 8000
