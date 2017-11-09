#!/usr/bin/env python3
import os
import asyncore
import logging
from smtpd import SMTPServer

from paho.mqtt import publish


defaults = {
    'SMTP_PORT': 1025,
    'MQTT_HOST': 'localhost',
    'MQTT_PORT': 1883,
    'MQTT_USERNAME': '',
    'MQTT_PASSWORD': '',
    'MQTT_TOPIC': 'emqtt',
    'MQTT_PAYLOAD': 'ON',
    'DEBUG': False
}
config = {
    setting: os.environ.get(setting, default)
    for setting, default in defaults.items()
}
level = logging.DEBUG if config['DEBUG'] == 'True' else logging.INFO

log = logging.getLogger()
log.setLevel(level)
ch = logging.StreamHandler()
fh = logging.FileHandler('emqtt.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(fh)


class EmailServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        log.debug('Mail from: {}\nContent (truncated): {}'.format(mailfrom, data[:250]))
        try:
            payload = config['MQTT_PAYLOAD']
            topic = '{}/{}'.format(config['MQTT_TOPIC'], mailfrom.replace('@', ''))
            log.debug('Publishing "%s" to %s', payload, topic)
            self.mqtt_publish(topic, payload)
        except Exception as e:
            log.exception('Failed publishing')
    
    def mqtt_publish(self, topic, payload):
        publish.single(
            topic,
            payload,
            hostname=config['MQTT_HOST'],
            port=config['MQTT_PORT'],
            auth={
                'username': config['MQTT_USERNAME'],
                'password': config['MQTT_PASSWORD']
            } if config['MQTT_USERNAME'] else None
        )


def run():
    foo = EmailServer(
        ('0.0.0.0', config['SMTP_PORT']),
        None # remoteaddr
    )
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    log.debug(', '.join([f'{k}={v}' for k, v in config.items()]))
    log.info('Running')
    run()
