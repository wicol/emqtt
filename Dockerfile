FROM alpine:latest
WORKDIR /emqtt
COPY emqtt.py requirements.txt ./
RUN apk add --no-cache python3 && pip3 install -r requirements.txt
EXPOSE 1025
CMD ["python3", "emqtt.py"]
