"""Example script for using the Emulated Roku api."""

if __name__ == "__main__":
    import socket
    import asyncio
    import logging
    import emulated_roku
    import paho.mqtt.publish as publish
    import os
    
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    # servers = []
    servers = {}

    desired_servers = ['MediaRoom', 'LivingRoom', 'MasterBedroom', 'Office', 'Deck']

    DEFAULT_HOST_IP = "10.9.8.43"
    DEFAULT_LISTEN_PORTS = 6230
    MQTT_HOST = "10.9.8.184"
    MQTT_PORT = 1883
    
    DEFAULT_UPNP_BIND_MULTICAST = True

    class MQTTRokuCommandHandler(emulated_roku.RokuCommandHandler):
        """Emulated Roku command handler."""
        def publish(self, event, usn, message):
            topic = 'roku/'+event
            publish.single(topic, message, hostname = MQTT_HOST, port = int(MQTT_PORT))

        def on_keydown(self, roku_usn, key):
            # self.publish('keydown', roku_usn, key)
            self.publish('keypress', roku_usn, key)

        # def on_keyup(self, roku_usn, key):
        #     self.publish('keyup', roku_usn, key)

        def on_keypress(self, roku_usn, key):
            print(roku_usn)
            self.publish('keypress', roku_usn, key)

        def launch(self, roku_usn, app_id):
            self.publish('app', roku_usn, app_id)



    @asyncio.coroutine
    def init(loop):
        handler = MQTTRokuCommandHandler()
        ip_adjustment = 0
        ip = DEFAULT_HOST_IP.split('.')
        for server in desired_servers:
            discovery_endpoint, roku_api_endpoint = emulated_roku.make_roku_api(
                loop=loop,
                handler=handler,
                host_ip=DEFAULT_HOST_IP,
                listen_port=DEFAULT_LISTEN_PORTS,
                advertise_ip=ip[0] + '.' + ip[1] + '.' + ip[2] + '.' + ip[3] + ip_adjustment,
                advertise_port=DEFAULT_LISTEN_PORTS,
                bind_multicast=DEFAULT_UPNP_BIND_MULTICAST,
                name=server)  # !Change Host IP!

            discovery_transport, _ = yield from discovery_endpoint
            api_server = yield from roku_api_endpoint

            servers[server + "_discovery"] = discovery_transport
            servers[server + "_api"] = api_server

            ip_adjustment = ip_adjustment + 1

    loop.run_until_complete(init(loop))

    loop.run_forever()