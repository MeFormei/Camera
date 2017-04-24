# USAGE
# python object_movement.py --video object_tracking_example.mp4
# python object_movement.py

# import the necessary packages
from collections import deque
from threading import Timer 
import numpy as np
import argparse
import imutils
import cv2
import pyautogui
import paho.mqtt.client as mqtt
import json
from PyQt4 import QtGui # to get display resolution

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
ap.add_argument("-q","--mqtt", nargs='?',
	help="enable mqtt with given ip")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
GREEN_LOWER = (29, 86, 6)
GREEN_UPPER = (64, 255, 255)

# get display resolution
app = QtGui.QApplication([])
SCREEN_RESOLUTION = app.desktop().screenGeometry()
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_RESOLUTION.width(), SCREEN_RESOLUTION.height()
FRAME_WIDTH, FRAME_HEIGHT = 352, 240
MOUSE_THRESHOLD = 20
WIDTH_FACTOR = np.abs(SCREEN_WIDTH / FRAME_WIDTH)
HEIGHT_FACTOR = np.abs(SCREEN_HEIGHT / FRAME_HEIGHT)

# Limits
EAST_LIMIT = 0.9 * FRAME_WIDTH
WEST_LIMIT = 0.1 * FRAME_WIDTH
NORTH_LIMIT = 0.1 * FRAME_HEIGHT
SOUTH_LIMIT = 0.7 * FRAME_HEIGHT
TIMER_LIMIT = 1.0

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
last_mouse_pos = (0, 0)
counter = 0
(dX, dY) = (0, 0)
direction = ""

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(0)
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
	camera.set(cv2.CAP_PROP_FPS,15)

# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

mqtt_enabled = args.get("mqtt",False)
direction_sent = False

# Connects to mqtt broker
if mqtt_enabled:
	client = mqtt.Client()
	client.connect(MQTT_HOST)
	client.loop_start()

def mqtt_publish(topic, payload):
	if mqtt_enabled:
		client.publish(topic, payload)
	else:
		print(topic + ' - ' + payload)

def reset_direction():
	global direction_sent
	direction_sent = False

def send_direction(direction):
	global direction_sent
	direction_sent = True
	mqtt_publish('direction',direction)
	t = Timer(TIMER_LIMIT, reset_direction)
	t.start()

# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=FRAME_WIDTH, height=FRAME_HEIGHT)
	# mirror image horizontally
	frame = cv2.flip(frame, 1)
	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			# cv2.circle(frame, (int(x), int(y)), int(radius),
			# 	(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), 1)
			pts.appendleft(center)

		center_x = center[0]
		center_y = center[1]

		if not direction_sent:
			if center_x > EAST_LIMIT:
				send_direction('EAST');
			elif center_x < WEST_LIMIT:
				send_direction('WEST')
			elif center_y < NORTH_LIMIT:
				send_direction('NORTH')
			elif center_y > SOUTH_LIMIT:
				send_direction('SOUTH')
			else:
				print('limit=%d x=%d y=%d' % (SOUTH_LIMIT,center_x,center_y))

	# loop over the set of tracked points
	for i in np.arange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# check to see if enough points have been accumulated in
		# the buffer
		if counter >= 10 and i == 1 and len(pts) >= 10 and pts[-10] is not None:
			# compute the difference between the x and y
			# coordinates and re-initialize the direction
			# text variables
			dX = pts[-10][0] - pts[i][0]
			dY = pts[-10][1] - pts[i][1]
			(dirX, dirY) = ("", "")

			center_x = pts[i][0]
			center_y = pts[i][1]

			mouse_dX = np.abs(last_mouse_pos[0] - center_x)
			mouse_dY = np.abs(last_mouse_pos[1] - center_y)

			if mouse_dX > MOUSE_THRESHOLD or mouse_dY > MOUSE_THRESHOLD:
				last_mouse_pos = (center_x, center_y)

				abs_center_x = np.round(center_x * WIDTH_FACTOR)
				abs_center_y = np.round(center_y * HEIGHT_FACTOR)
				# pyautogui.moveTo(abs_center_x, abs_center_y, duration=0)
				position_json = json.dumps({'x': abs_center_x, 'y': abs_center_y})
				
				# mqtt_publish('position', position_json)

			# ensure there is significant movement in the
			# x-direction
			if np.abs(dX) > 50:
				dirX = "East" if np.sign(dX) == 1 else "West"

			# ensure there is significant movement in the
			# y-direction
			if np.abs(dY) > 50:
				dirY = "North" if np.sign(dY) == 1 else "South"

			# handle when both directions are non-empty
			if dirX != "" and dirY != "":
				direction = "{}-{}".format(dirY, dirX)

			# otherwise, only one direction is non-empty
			else:
				direction = dirX if dirX != "" else dirY

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		# thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		# cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# show the movement deltas and the direction of movement on
	# the frame
	cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 3)
	cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)

	# show the frame to our screen and increment the frame counter
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	counter += 1

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
