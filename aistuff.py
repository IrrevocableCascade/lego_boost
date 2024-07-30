import time
import random
from time import sleep
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import EncodedMotor, TiltSensor, Current, Voltage, COLORS, COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_BLUE

# Constants declaration
COLOR_GREEN = 1
COLOR_RED = 3
DETECTION_DISTANCE = 10
SAFE_DISTANCE = 6
ANGULAR_SPEED = 1
ROTATION_DEGREE = 120  # Decrease size of turns for better navigation

def get_options():
    import argparse
    arg_parser = argparse.ArgumentParser(
        description='Demonstrate move-hub communications',
    )
    arg_parser.add_argument(
        '-c', '--connection',
        default='auto://',
        help='''Specify connection URL to use, `protocol://mac?param=X` with protocol in:
    "gatt","pygatt","gattlib","gattool", "bluepy","bluegiga"'''
    )
    arg_parser.add_argument(
        '-d', '--demo',
        default='all',
        help="Run a particular demo, default all"
    )
    return arg_parser


def connection_from_url(url):
    import pylgbst
    if url == 'auto://':
        return None
    try:
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        from urlparse import urlparse, parse_qs
    parsed = urlparse(url)
    name = 'get_connection_%s' % parsed.scheme
    factory = getattr(pylgbst, name, None)
    if not factory:
        msg = "Unrecognised URL scheme/protocol, expect a get_connection_<protocol> in pylgbst: %s"
        raise ValueError(msg % parsed.protocol)
    params = {}
    if parsed.netloc.strip():
        params['hub_mac'] = parsed.netloc
    for key, value in parse_qs(parsed.query).items():
        if len(value) == 1:
            params[key] = value[0]
        else:
            params[key] = value
    return factory(
        **params
    )


def move_forward():
    hub.motor_AB.timed(1, 1, 1)

def rotate():
    turn_degrees = random.randint(-ROTATION_DEGREE, ROTATION_DEGREE)
    if turn_degrees < 0:
        hub.motor_AB.angled(abs(turn_degrees), -ANGULAR_SPEED, ANGULAR_SPEED)
    else:
        hub.motor_AB.angled(turn_degrees, ANGULAR_SPEED, -ANGULAR_SPEED)


def control_robot():
    while True:
        distance = hub.vision_sensor.distance
        # if sensor value is -1, it is not getting any reading
        if distance == -1:
            time.sleep(0.1)
            continue

        if distance < SAFE_DISTANCE:
            hub.led.set_color(COLOR_RED)
            rotate()
        else:
            hub.led.set_color(COLOR_GREEN)
            move_forward()

        time.sleep(0.1)

# Call the function to start the robot

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(relativeCreated)d\t%(levelname)s\t%(name)s\t%(message)s')
    parser = get_options()
    options = parser.parse_args()
    parameters = {}
    try:
        connection = connection_from_url(options.connection)  # get_connection_bleak(hub_name=MoveHub.DEFAULT_NAME)
        parameters['connection'] = connection
    except ValueError as err:
        parser.error(err.args[0])

    hub = MoveHub(**parameters)

    try:
        control_robot()
    finally:
        hub.disconnect()