# emqtt

Receive emails and publish to MQTT. Super simple stuff. Topic will be `<configurable_prefix>/<sender_email.replace('@', '')>`.

I needed this to make my D-Link camera's motion sensor functionality useful.
Available actions on the camera are to send an email or upload an image to an FTP..
This script makes it easier to integrate into automation systems.

It's based on aiosmtpd and paho-mqtt.

I made a docker image because like any hipster dev I like docker. At least it's based on alpine so there's that.

Protip: `docker exec emqtt find attachments -type f -ctime +20 -delete`

## Run it

1. Create venv and activate it. Or don't.

1. `pip install -r requirements.txt`.

1. Give it some env vars. These are the defaults so omit whatever looks good.
   * SMTP_PORT=1025
   * MQTT_HOST=localhost
   * MQTT_PORT=1883
   * MQTT_USERNAME=""
   * MQTT_PASSWORD=""
   * MQTT_TOPIC=emqtt
   * MQTT_PAYLOAD=ON
   * MQTT_RESET_TIME=300
   * MQTT_RESET_PAYLOAD=OFF
   * SAVE_ATTACHMENTS=True
   * SAVE_ATTACHMENTS_DURING_RESET_TIME=False
   * DEBUG=False

1. Go.
```
$ python emqtt.py
2017-11-08 22:36:27,658 - root - INFO - Running
```

## Run it in docker

```
$ docker build -t emqtt .
$ docker run -d \
    --name emqtt \
    --net host \
    --restart always \
    -e "MQTT_USERNAME=mqtt" \
    -e "MQTT_PASSWORD=mqtt" \
    -e "DEBUG=True" \
    -v /etc/localtime:/etc/localtime:ro \
    -v $PWD/log:/emqtt/log \
    -v $PWD/attachments:/emqtt/attachments \
    emqtt
```

