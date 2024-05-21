FROM python:3.8.10

WORKDIR /code

ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Start and enable SSH
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd \
    && chmod u+x startup.sh

RUN rm -f /etc/ssh/sshd_config
COPY sshd_config /etc/ssh/

EXPOSE 5000 2222

ENTRYPOINT [ "/code/startup.sh" ]
