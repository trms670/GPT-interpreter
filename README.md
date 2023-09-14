# About this project
Under the direction of Guojun Chen and Professor Lin Zhong, I collaborated with Freeman Irabaruta and designed a GPT interpreter for drone commands based on YOLO coordinates. Recently, gun violence and school shootings have reached an all-time high, affecting countless lives of innocent individuals and their loved ones. Hiring an entire security team is costly to many public schools and first responders take several crucial minutes to arrive on the scene after a threat has been called. Our project aims to provide a cost-effective, user-friendly drone surveillance system that will follow and distract any suspicious activity detected before the appropriate authorities arrive. My contribution to this goal involved converting object detection results received from the surveillance model into appropriate drone commands.

# 2D sim
The main task for the drone will be to follow an object. Before the drone moves closer to the object, we want to center the object in the image first. This section details files that can run a simulation using a 3D Python plot library to visualize and test the output of the gpt prompt design.

## gptplot.py
This file consists of a *gpt-3.5-turbo* prompt that will center an object in the image. The only input the prompt will receive is an instruction to follow a specific object at its coordinates in the following format: [*x_center*, *z_center*].

Here is a general prompt template that will be consistent for all versions you will see of this GPT interpreter:
- Declaration of system's role and its background/setup.
- list of available drone commands (ex. `move_right()`)
- dictionary output format w/ descriptions of its keys
- double-check mechanism
- an outline of rules the dictionary must follow
- example inputs/outputs

This is an example of what an input/output would look like for this specific prompt.

Input: 
`Instruction: Follow the cat at [0.58, 0.3]`

Output:
```
{"task_explanation": "Since the cat's z_center is less than 0.4, the cat is on the top half of the image and the appropriate command for the drone is to move up.",
"task_cohesion": {
    "task_sequence": [
        "move_up()"
    ],
    "step_instructions": [
        "move upwards"
    ],
    "object_name": "<cat>"},
"instruction_summary": "Centering the cat vertically in the image",
"question":""}
```

Lastly, `gptplot.py` contains the *get_command* function which will be used in `plot.py`.

## plot.py
### Requirements
This file requires the installation of [matplotlib](https://matplotlib.org/stable/index.html), which is a library that can create interactive visuals in Python. This library is used to run the simulator using the prompt detailed in `gptplot.py`.
### Contents
Using a 3D coordinate system, the file initializes initial drone and object locations as well as the height and width of the object. Using matplotlib, the program plots a 3D graph of the drone and the object with its bounding box.

Here is an example of this 3D graph:

<img width="701" alt="Screen Shot 2023-07-17 at 10 15 24 AM" src="https://github.com/trms670/GPT-interpreter/assets/107161660/f06b9c26-cd3c-4ca7-ae36-3187dc2652a8">

The blue triangle represents the object and the red circle represents the drone. 

Based on these locations, the program calculates the relative object x and z coordinates and plots these on a 2D graph to show if the object is centered in the image.

Here is an example of this 2D graph:

<img width="699" alt="Screen Shot 2023-07-17 at 10 15 36 AM" src="https://github.com/trms670/GPT-interpreter/assets/107161660/ff5ba18a-6ad3-4f43-a0cf-f7dbb8de2418">

The blue triangle represents the object with the bounding box around it. The yellow region in the center represents the area where the object is considered centered in the image.

These relative coordinates are then passed through the `get_command` function defined in `gptplot.py`, which will output the next appropriate drone movement. The drone will move accordingly and the whole process is repeated until the prompt outputs the `hover()` command, meaning the object is now centered in the image.

## drone2.py
This file is a version of the `drone3.py` file using *x_center* and *y_center* that will be discussed later on this page.

# 3D sim
## drone3.py
A similar prompt to the one defined in `gptplot.py` and uses *gpt-4* instead of *gpt-3.5-turbo*. The coordinates are represented by the YOLO coordinate system explained [here](https://albumentations.ai/docs/getting_started/bounding_boxes_augmentation/). Instead of *x_center* and *y_center* the prompt uses *x_min* and *y_min*. Additionally, the prompt includes the `move_forward()` command which will be outputted if the object is centered in the image.

This is an example of what an input/output would look like for this specific prompt.

Input: 
`Instruction: Follow the person in blue at [0.20, 0.21, 0.50, 0.56]`

Output:
```
{"task_explanation": "Since the person's x_center (0.45) is greater than 0.40 and less than 0.60, the person is centered horizontally in the image. Since the y_center (0.49) is greater than 0.40 and less than 0.60, the person is also centered vertically in the image. Both the person's width and height are not greater than 0.60 so the person is at a far enough distance to move forward.",
"task_cohesion": {
    "task_sequence": [
        "move_forward()"
    ],
    "object_name": "<person>"},
"instruction_summary": "Approaching the person in blue",
"question":""}
```

This file contains the *get_command* function which will be used in `follow_drone.py`

## object_detection.py
This file was written by my colleague Freeman. It contains the *box_image* function which will be used in `follow_drone.py`. The function takes in an image and runs YOLO (You Only Look Once), an object detection algorithm, on the image and outputs all bounding box coordinates for each object in the image. In order to run this function, you need to install [Darknet](https://pjreddie.com/darknet/install/#cuda).

## follow_drone.py
### Requirements
Microsoft released a simulator for drones called *AirSim* that is built on Unreal Engine designed for AI experimentation. In order to run this program, you need to build AirSim on your computer. Here is how to build AirSim on [macOS](https://microsoft.github.io/AirSim/build_macos/).

Please note that Microsoft AirSim uses the *NED coordinate system* (+X is North, +Y is East, +Z is Down).
### Contents
This file runs the Microsoft simulator using the output from the prompt defined in `drone3.py` and the bounding box coordinates retrieved from `object_detection.py`. The program gets the current drone location, takes a picture using the drone camera, and passes the image to the *box_image* function from `object_detection.py`. The program then filters through all bounding boxes until it finds the coordinates of the specific object it is looking for, and then passes those coordinates into the *gpt-4* interpreter from `drone3.py`. Once it gets the next appropriate drone command, the drone will move accordingly. This process repeats until the drone is close enough to the object.

## airsim.py
This file is a test file that outlines a *gpt-3.5* prompt to see if *gpt-3.5* is able to output its own correct code for converting object detection results into drone commands. Results were inconclusive.

# crazyflie
The specific model of the drone we used was the Crazyflie 2.1 due to its light and compact size. The following files are used to control the drone directly using the Crazyflie Python API.

## connect_log_param.py
This file connects the local computer to the crazyflie using the crazyflie PA.

## motion_flying.py
Once the crazyflie is connected, this file commands the drone to take off, hover, rise, hover, and land back down safely. Modifications may be made.

## commander.py
From the Crazyflie API, this file details functions for drone movement. More functions will be added to mimic the definitions of the functions used in the gpt interpreter.

# Next Steps
## Update prompts
The current *gpt-4* prompt is fairly accurate but falters in some specific cases. More alterations will be made to remedy these issues. Another consideration is how I want the prompt to calculate distance. Right now, I am basing it on the width and height being above or below a specific threshold.
## Test Crazyflie
After I define specific functions for drone movement, I will be able to move on to testing the gpt interpreter on the crazyflie drone using a similar program to `follow_drone.py`.
