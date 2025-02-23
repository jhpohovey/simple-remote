import requests
import logging
import socket
import re
import argparse 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# https://developer.roku.com/docs/developer-program/dev-tools/external-control-api.md

class RokuRemote:
    def __init__(self, ip_address=None, port=8060):
        self.base_url = f"http://{ip_address}:{port}" if ip_address else None
        if ip_address:
            logger.info(f"Initialized RokuRemote with IP: {ip_address} and port: {port}")
        else:
            logger.info("Initialized RokuRemote without IP address")

    def send_command(self, command):
        if not self.base_url:
            logger.error("No IP address set for RokuRemote")
            return
        url = f"{self.base_url}/keypress/{command}"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                logger.info(f"Command '{command}' sent successfully.")
            else:
                logger.error(f"Failed to send command '{command}'. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to send command '{command}'. Exception: {e}")

    def power_on(self):
        logger.info("Power On command called")
        self.send_command("powerOn")

    def power_off(self):
        logger.info("Power Off command called")
        self.send_command("PowerOff")

    def keyup(self):
        logger.info("Key Up command called")
        self.send_command("keyup")

    def volume_up(self):
        logger.info("Volume Up command called")
        self.send_command("VolumeUp")

    def volume_down(self):
        logger.info("Volume Down command called")
        self.send_command("VolumeDown")

    def volume_mute(self):
        logger.info("Volume Mute command called")
        self.send_command("VolumeMute")

    def home(self):
        logger.info("Home command called")
        self.send_command("Home")

    def back(self):
        logger.info("Back command called")
        self.send_command("Back")

    def select(self):
        logger.info("Select command called")
        self.send_command("Select")

    def up(self):
        logger.info("Up command called")
        self.send_command("Up")

    def down(self):
        logger.info("Down command called")
        self.send_command("Down")

    def left(self):
        logger.info("Left command called")
        self.send_command("Left")

    def right(self):
        logger.info("Right command called")
        self.send_command("Right")

    def play(self):
        logger.info("Play command called")
        self.send_command("Play")

    def pause(self):
        logger.info("Pause command called")
        self.send_command("Pause")

    def rewind(self):
        logger.info("Rewind command called")
        self.send_command("Rev")

    def fast_forward(self):
        logger.info("Fast Forward command called")
        self.send_command("Fwd")

    def info(self):
        logger.info("Info command called")
        self.send_command("Info")

    def instant_replay(self):
        logger.info("Instant Replay command called")
        self.send_command("InstantReplay")

    def backspace(self):
        logger.info("Backspace command called")
        self.send_command("Backspace")

    def search(self):
        logger.info("Search command called")
        self.send_command("Search")

    def enter(self):
        logger.info("Enter command called")
        self.send_command("Enter")

    def find_remote(self):
        logger.info("Find Remote command called")
        self.send_command("FindRemote")

    def channel_up(self):
        logger.info("Channel Up command called")
        self.send_command("ChannelUp")

    def channel_down(self):
        logger.info("Channel Down command called")
        self.send_command("ChannelDown")

    def input_tuner(self):
        logger.info("Input Tuner command called")
        self.send_command("InputTuner")

    def input_hdmi1(self):
        logger.info("Input HDMI1 command called")
        self.send_command("InputHDMI1")

    def input_hdmi2(self):
        logger.info("Input HDMI2 command called")
        self.send_command("InputHDMI2")

    def input_hdmi3(self):
        logger.info("Input HDMI3 command called")
        self.send_command("InputHDMI3")

    def input_hdmi4(self):
        logger.info("Input HDMI4 command called")
        self.send_command("InputHDMI4")

    def input_av1(self):
        logger.info("Input AV1 command called")
        self.send_command("InputAV1")

    @staticmethod
    def discover_roku_tvs():
        logger.info("Discovering Roku TVs on the network...")
        ssdp_request = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "MAN: \"ssdp:discover\"\r\n"
            "MX: 1\r\n"
            "ST: roku:ecp\r\n"
            "\r\n"
        )
        ssdp_address = ("239.255.255.250", 1900)

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(5)

        try:
            sock.sendto(ssdp_request.encode(), ssdp_address)
        except OSError as e:
            logger.warning(f"Failed to send SSDP request. Exception: {e}")
            return []

        roku_tvs = []
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                if "roku:ecp" in data.decode():
                    ip_address = re.search(r"LOCATION: http://(.*):8060/", data.decode()).group(1)
                    roku_tvs.append(ip_address)
                    logger.info(f"Found Roku TV at IP: {ip_address}")
        except socket.timeout:
            logger.info("Discovery completed.")

        return roku_tvs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control a Roku TV using ECP-based commands.")
    parser.add_argument("--ip", type=str, help="IP address of the Roku TV")
    parser.add_argument("--port", type=int, default=8060, help="Port of the Roku TV (default: 8060)")
    parser.add_argument("--demo", action="store_true", help="Run example commands")
    parser.add_argument("--enable-logging", action="store_true", help="Enable logging")
    args = parser.parse_args()

    if args.enable_logging:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    if args.ip:
        remote = RokuRemote(args.ip, args.port)
        if args.demo:
            # Example commands
            remote.power_on()
            remote.power_off()
            remote.keyup()
            remote.volume_up()
            remote.volume_down()
            remote.volume_mute()
            remote.home()
            remote.back()
            remote.select()
            remote.up()
            remote.down()
            remote.left()
            remote.right()
            remote.play()
            remote.pause()
            remote.rewind()
            remote.fast_forward()
            remote.info()
            remote.instant_replay()
            remote.backspace()
            remote.search()
            remote.enter()
            remote.find_remote()
            remote.channel_up()
            remote.channel_down()
            remote.input_tuner()
            remote.input_hdmi1()
            remote.input_hdmi2()
            remote.input_hdmi3()
            remote.input_hdmi4()
            remote.input_av1()
    else:
        logger.error("No IP address provided. Use --ip to specify the IP address.")
