FROM alpine:latest
WORKDIR /emqtt
COPY emqtt.py requirements.txt ./
RUN apk add --update py-pip
RUN apk add --no-cache python3 && pip install -r requirements.txt
EXPOSE 1025
CMD ["python3", "emqtt.py"]
