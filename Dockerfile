FROM python:3.6-jessie

ENV noninteractive=true PYTHONUNBUFFERED=1

RUN apt-get update && \
	apt-get install -y apt-utils \
	apt-transport-https \
	locales \
	python3-dev \
	supervisor \
	nginx \
    netcat

WORKDIR /codenation/codenation

COPY ./requirements.txt /codenation/

RUN pip install --upgrade pip && \
    pip install -r ../requirements.txt

COPY . /codenation/

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    cp -r /codenation/config/nginx.conf /etc/nginx/sites-available/default && \
    cp -r /codenation/config/supervisor.conf /etc/supervisor/conf.d/

RUN chmod +x /codenation/entrypoint.sh

EXPOSE 6606
CMD ["/codenation/entrypoint.sh"]