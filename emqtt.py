#!/usr/bin/env python3
import os
import time
import email
from email.policy import default
import asyncio
import logging
from datetime import datetime

from aiosmtpd.controller import Controller
from paho.mqtt import publish


defaults = {
    'SMTP_PORT': 1025,
    'MQTT_HOST': 'localhost',
    'MQTT_PORT': 1883,
    'MQTT_USERNAME': '',
    'MQTT_PASSWORD': '',
    'MQTT_TOPIC': 'emqtt',
    'MQTT_PAYLOAD': 'ON',
    'MQTT_RESET_TIME': '300',
    'MQTT_RESET_PAYLOAD': 'OFF',
    'SAVE_ATTACHMENTS': 'True',
    'SAVE_ATTACHMENTS_DURING_RESET_TIME': 'False',
    'DEBUG': 'False'
}
config = {
    setting: os.environ.get(setting, default)
    for setting, default in defaults.items()
}
# Boolify
for key, value in config.items():
    if value == 'True':
        config[key] = True
    elif value == 'False':
        config[key] = False

level = logging.DEBUG if config['DEBUG'] else logging.INFO

log = logging.getLogger('emqtt')
log.setLevel(level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Log to console
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)


class EMQTTHandler:
    def __init__(self, loop):
        self.loop = loop
        self.reset_time = int(config['MQTT_RESET_TIME'])
        self.handles = {}

    async def handle_DATA(self, server, session, envelope):
        log.debug('Message from %s', envelope.mail_from)
        msg = email.message_from_bytes(envelope.original_content, policy=default)
        log.debug(
            'Message data (truncated): %s',
            envelope.content.decode('utf8', errors='replace')[:250]
        )
        topic = '{}/{}'.format(config['MQTT_TOPIC'], envelope.mail_from.replace('@', ''))
        self.mqtt_publish(topic, config['MQTT_PAYLOAD'])

        # Save attached files if configured to do so.
        if config['SAVE_ATTACHMENTS'] and (
                # Don't save them during reset time unless configured to do so.
                topic not in self.handles
                or config['SAVE_ATTACHMENTS_DURING_RESET_TIME']):
            for att in msg.iter_attachments():
                # Just save images
                if not att.get_content_type().startswith('image'):
                    continue
                filename = att.get_filename()
                image_data = att.get_content()
                file_path = os.path.join('attachments', filename)
                log.info('Saving attached file %s to %s', filename, file_path)
                with open(file_path, 'wb') as f:
                    f.write(image_data)

        # Cancel any current scheduled resets of this topic
        if topic in self.handles:
            self.handles.pop(topic).cancel()

        if self.reset_time:
            # Schedule a reset of this topic
            self.handles[topic] = self.loop.call_later(
                self.reset_time,
                self.mqtt_publish,
                topic,
                config['MQTT_RESET_PAYLOAD']
            )
        return '250 Message accepted for delivery'

    def mqtt_publish(self, topic, payload):
        log.info('Publishing "%s" to %s', payload, topic)
        try:
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
        except Exception as e:
            log.exception('Failed publishing')


if __name__ == '__main__':
    log.debug(', '.join([f'{k}={v}' for k, v in config.items()]))

    # If there's a dir called log - set up a filehandler
    if os.path.exists('log'):
        log.info('Setting up a filehandler')
        fh = logging.FileHandler('log/emqtt.log')
        fh.setFormatter(formatter)
        log.addHandler(fh)

    loop = asyncio.get_event_loop()

    c = Controller(EMQTTHandler(loop), loop, '0.0.0.0', config['SMTP_PORT'])
    c.start()
    log.info('Running')
    try:
        while True:
            time.sleep(1)
    except:
        c.stop()
        raise
