FROM lambci/lambda:build-python3.7

LABEL Name=fx_service Version=0.0.1
LABEL maintainer="<samatkins@outlook.com>"

RUN mkdir /opt/app
WORKDIR /opt/app
COPY . /opt/app

ARG PIP_REQUIREMENTS=src/requirements.txt
RUN python3 -m pip install -r ${PIP_REQUIREMENTS}

EXPOSE 3002
ENV PYTHONPATH=$PYTHONPATH:/opt/app/
