import argparse
import json
from threading import Timer

import cv2
import imutils
import numpy as np
import paho.mqtt.client as mqtt

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--mqtt", nargs='?', default='', help="enable mqtt with given ip")
ap.add_argument("-i", "--showimage", action='store_true', help="enable image show")
args = ap.parse_args()

# define the lower and upper boundaries of the "green" ball in the HSV color space
GREEN_LOWER = (29, 86, 6)
GREEN_UPPER = (64, 255, 255)

FRAME_WIDTH, FRAME_HEIGHT = 352, 240
POSITION_THRESHOLD = 5

# Limits
EAST_LIMIT = 0.9 * FRAME_WIDTH
WEST_LIMIT = 0.1 * FRAME_WIDTH
NORTH_LIMIT = 0.1 * FRAME_HEIGHT
SOUTH_LIMIT = 0.7 * FRAME_HEIGHT
TIMER_LIMIT = 1.0

# initialize the last position, direction string and position and direction flags
last_position = (0, 0)
lost_position = False
direction_str = ""
direction_sent = False

camera = cv2.VideoCapture(0)
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
# camera.set(cv2.CAP_PROP_FPS,15)

mqtt_enabled = True if args.mqtt else False

# Connects to mqtt broker
if mqtt_enabled:
    print('MQTT enabled')
    mqtt_host = args.mqtt
    mqtt_port = 1883
    print('Connecting to {} on port {}.'.format(mqtt_host, mqtt_port))
    client = mqtt.Client()
    client.connect(mqtt_host, mqtt_port)
    client.loop_start()
    print('Connected!')


def mqtt_publish(topic, payload):
    if mqtt_enabled:
        client.publish(topic, payload)
        print('(MQTT) {} - {}'.format(topic, payload))
    else:
        print(topic + ' - ' + payload)


def reset_direction():
    global direction_str
    global direction_sent
    direction_str = ""
    direction_sent = False


def send_direction(direction):
    global direction_sent
    direction_sent = True
    mqtt_publish('direction', direction)
    t = Timer(TIMER_LIMIT, reset_direction)
    t.start()


def send_position(position):
    if position:
        x, y = position
        position_payload = json.dumps({'x': x, 'y': y})
    else:
        position_payload = 'none'

    mqtt_publish('position', position_payload)


# keep looping
try:
    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()

        # resize the frame, blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        # mirror image horizontally
        frame = cv2.flip(frame, 1)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current (x, y) center of the ball
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(contours) > 0:
            lost_position = False

            # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(contours, key=cv2.contourArea)
            ((circle_x, circle_y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame, then update the list of tracked points
                cv2.circle(frame, (int(circle_x), int(circle_y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), 1)

            center_x, center_y = center

            if not direction_sent:
                if center_x > EAST_LIMIT:
                    direction_str = 'EAST'
                    send_direction(direction_str)
                elif center_x < WEST_LIMIT:
                    direction_str = 'WEST'
                    send_direction(direction_str)
                elif center_y < NORTH_LIMIT:
                    direction_str = 'NORTH'
                    send_direction(direction_str)
                elif center_y > SOUTH_LIMIT:
                    direction_str = 'SOUTH'
                    send_direction(direction_str)
                else:
                    direction_str = ''

            position_dX = np.abs(last_position[0] - center_x)
            position_dY = np.abs(last_position[1] - center_y)

            if position_dX > POSITION_THRESHOLD or position_dY > POSITION_THRESHOLD:
                last_position = (center_x, center_y)
                send_position(last_position)

        else:
            if not lost_position:
                send_position(None)
                lost_position = True

        if args.showimage:
            # show the movement deltas and the direction of movement on the frame
            cv2.putText(frame, direction_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 3)
            cv2.putText(frame, "x: {}, y: {}".format(last_position[0], last_position[1]), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            # show the frame to our screen
            cv2.imshow("Frame", frame)

            # if the 'q' key is pressed, stop the loop
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                if mqtt_enabled:
                    client.disconnect()
                break

except KeyboardInterrupt:
    if mqtt_enabled:
        client.disconnect()

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
