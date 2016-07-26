import logging
import time

import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


def on_connect(client, userdata, rc):
    logger.info("Connected with status {}".format(rc))
    client.subscribe("#")


def on_disconnect(client, userdata, rc):
    server = userdata["server"]
    logger.info("Disconnected")
    if not server.stop:
        j = 3
        for i in range(j):
            logger.info("Trying to reconnect")
            try:
                client.reconnect()
                logger.info("Reconnected")
                break
            except Exception as e:
                if i < j:
                    logger.warn(e)
                    time.sleep(1)
                    continue
                else:
                    raise


def on_message(client, userdata, message):
    logger.debug("Received message from topic {}".format(message.topic))
    channel = userdata["channel"]
    channel.send("mqtt.sub", {
        "topic": message.topic,
        "payload": message.payload,
        "qos": message.qos,
        "host": userdata["host"],
        "port": userdata["port"],
    })


class Server(object):
    def __init__(self, channel, host, port):
        self.channel = channel
        self.host = host
        self.port = port
        self.client = mqtt.Client(userdata={
            "server": self,
            "channel": self.channel,
            "host": self.host,
            "port": self.port,
        })
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message

    def run(self):
        self.stop = False
        self.client.connect(self.host, self.port)
        logger.info("Starting loop")
        while not self.stop:
            self.client.loop()
            logger.debug("Restarting loop")

        self.client.disconnect()
