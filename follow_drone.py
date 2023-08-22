"""
file: follow_drone.py
date: 8/21/23
purpose: using microsoft AirSim, run simulation following an object using gpt interpreter
"""

import setup_path
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2
from object_detection import box_image
from drone3 import get_command

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# establish variables to keep track of drone's location
x_loc = 0
y_loc = 0
z_loc = 0
step_size = 3
object_name = "orange"
filename = "test"

state = client.getMultirotorState()
s = pprint.pformat(state)
print("state: %s" % s)

"""imu_data = client.getImuData()
s = pprint.pformat(imu_data)
print("imu_data: %s" % s)

barometer_data = client.getBarometerData()
s = pprint.pformat(barometer_data)
print("barometer_data: %s" % s)

magnetometer_data = client.getMagnetometerData()
s = pprint.pformat(magnetometer_data)
print("magnetometer_data: %s" % s)

gps_data = client.getGpsData()
s = pprint.pformat(gps_data)
print("gps_data: %s" % s)"""

# takeoff drone
airsim.wait_key('Press any key to takeoff')
print("Taking off...")
client.armDisarm(True)
client.takeoffAsync().join()

state = client.getMultirotorState()
print("state: %s" % pprint.pformat(state))

# move drone so object is in drone's field of vision
airsim.wait_key('Press any key to move vehicle')
client.moveToPositionAsync(x_loc + 10, y_loc + 30, z_loc, 2).join()
client.hoverAsync().join()

while(True):
    # user can stop loop at any time
    if (input("stop? ") == "yes"):
        break

    # update drone's current location
    x_loc = client.simGetVehiclePose().position.x_val
    y_loc = client.simGetVehiclePose().position.y_val
    z_loc = client.simGetVehiclePose().position.z_val

    # get image from drone and save to a png file
    airsim.wait_key('Press any key to take picture')

    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
    response = responses[0]
    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8) 
    img_rgb = img1d.reshape(response.height, response.width, 3)
    airsim.write_png(os.path.normpath(filename + '.png'), img_rgb)
    
    command = None
    # run object detection on image
    for box in box_image("test.png"):
        # get bounding box coordinates for specific object user wishes to follow
        if box[1] == 'orange':
            print(box[0])
            # send box coordinates and object name to gpt interpretor and get result
            command = get_command(box[0], object_name)
            print(command)
            break
    # based on result move drone accordingly using NED coordinate system
    if command is None:
        continue
    if (command == "hover()"):
        break
    elif (command == "move_up()"):
        client.moveToPositionAsync(x_loc, y_loc, z_loc - step_size, 2).join()
    elif (command == "move_down()"):
        client.moveToPositionAsync(x_loc, y_loc, z_loc + step_size, 2).join()
    elif (command == "move_right()"):
        client.moveToPositionAsync(x_loc, y_loc + step_size, z_loc, 2).join()
    elif (command == "move_left()"):
        client.moveToPositionAsync(x_loc, y_loc - step_size, z_loc, 2).join()
    elif (command == "move_forward()"):
        client.moveToPositionAsync(x_loc + step_size, y_loc, z_loc, 2).join()
    
    client.hoverAsync().join()

# print current state of drone
state = client.getMultirotorState()
print("state: %s" % pprint.pformat(state))

# reset drone
airsim.wait_key('Press any key to reset to original state')

client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)
