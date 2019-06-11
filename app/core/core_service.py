import threading
import json
import time
import paho.mqtt.client as mqtt

from ph_sensor import PHSensor


class CoreService(object):
    _comm_client = None
    _comm_delay = 0
    _thread_comms = None
    _thread_lock = None
    _ph = None

    _status_channel_name = '/sensors/ph'
    _system_channel_name = '/system'

    _is_debug = False


    def __init__(self):
        self._ph = PHSensor()
        self._ph._set_i2c_address(99)

    def start(self):
        self._comm_client = mqtt.Client(
            client_id="service_atlasph",
            clean_session=True
        )

        self._comm_client.on_message = self._on_message
        self._comm_client.on_connect = self._on_connect
        self._comm_client.on_publish = self._on_publish
        self._comm_client.on_subscribe = self._on_subscribe

        self._thread_lock = threading.RLock()

        self._thread_comms = threading.Thread(target=self._start_thread_comms)
        self._thread_comms.setDaemon(True)
        self._thread_comms.start()

        while True:
            time.sleep(1)
            ph = self._ph._query('R')

            self.output('{"sender": "service_atlasph", "message": "%s"}' % ph)

    def _on_connect(self, client, userdata, flags, rc):
        self.output('{"sender": "service_atlasph", "message": "Connected to GrandCentral."}')

    def _on_message(self, client, userdata, msg):
        msg_struct = None

        try:
            msg_struct = json.loads(msg.payload)

        except:
            pass

    def _on_publish(self, mosq, obj, mid):
        pass

    def _on_subscribe(self, mosq, obj, mid, granted_qos):
        msg = {
            'sender': 'service_atlasph',
            'message': 'Successfully subscribed to GrandCentral /system channel.'
        }

        self.output(str(msg), )

    def _on_log(self, mosq, obj, level, string):
        pass

    def _connect_to_comms(self):
        comms_server = 'localhost'
        comms_port = 1883

        if self._is_debug:
            print('Connecting to comms system @ %s:%s' % (comms_server, comms_port))

        try:
            self._comm_client.connect(
                comms_server,
                comms_port,
                60
            )

        except Exception, e:
            if self._is_debug:
                print('Could not connect to local GranCentral. Retry in one second.')

            time.sleep(1)
            self._connect_to_comms()

    def _start_thread_comms(self):
        if self._is_debug:
            print('Comms thread started.')

        self._thread_lock.acquire()

        try:
            self._connect_to_comms()

        finally:
            self._thread_lock.release()

        if self._is_debug:
            print('Connected to comms server.')

        while True:
            self._thread_lock.acquire()

            try:
                if self._comm_delay > 2000:
                    self._comm_client.loop()
                    self._comm_delay = 0

                else:
                    self._comm_delay += 1

            finally:
                self._thread_lock.release()

    def output(self, msg, channel=_status_channel_name):
        if self._comm_client:
            self._comm_client.publish(channel, msg)

        if self._is_debug:
            print(msg)
