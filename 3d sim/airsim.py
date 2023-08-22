"""
file: airsim.py
date: 8/21/23
purpose: outlines gpt-3.5 prompt to output code for converting object detection results into drone commands
"""

import os
import openai
import json

API_KEY = "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"
openai.api_key = API_KEY
model_id = 'gpt-3.5-turbo-16k'

conversation = []
conversation.append({'role': 'system', 'content': '''Imagine you are helping me interact with the AirSim simulator. We are controlling an embodied agent. At any given point of time, you have the following abilities. You are also required to output code for some of the requests.
Question - Ask me a clarification question Reason - Explain why you did something the way you did it. Code - Output a code command that achieves the desired goal.

The scene consists of several objects. We have access to the following functions, please use only these functions as much as possible:

Perception:

get_image() : Renders an image from the front facing camera of the agent 
detect_objects(img): Runs an object detection model on an image img, and returns two variables - obj_list, which is a list of the names of objects detected in the scene. obj_locs, a list of bounding box coordinates in the image for each object.

Action:

forward(): Move forward by 0.1 meters. 
turn_left(): Turn left by 90 degrees. 
turn_right(): Turn right by 90 degrees.
move_left(): Move left by 0.1 meters.
move_right(): Move right by 0.1 meters.
move_up(): Move up by 0.1 meters.
move_down(): Move down by 0.1 meters.

You are not to use any other hypothetical functions. You can use functions from Python libraries such as math, numpy etc. Are you ready?'''})
conversation.append({'role': 'assistant', 'content': '''Yes, I'm ready to help you interact with the AirSim simulator. How can I assist you?'''})

conversation.append({'role': 'user', 'content': '''I need you to help me find an object. Objects might be scattered around the scene, so if you don't find it right away, a good strategy is to turn around a few times to see if it becomes visible.
Give me code to explore and find the bottle. Assume the object detection model has already been loaded. Please use the functions I listed above.'''})
response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0
)
conversation.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})
print(response['choices'][0]['message']['content'])

conversation.append({'role': 'user', 'content': '''Great! Now let's say we did find the bottle. Now I want to move towards it until the bottle is centered in the image. 
The only information we have is the location of the bottle bounding box in the image. Note that instead of x_max and y_max, the bounding box includes width and height. Assume the bounding box coordinates are already normalized and the image width and height are 1.0. 
Also, opt for movement adjustments over turning. We can set the threshold to be 0.1. Can you give me code to make this happen?'''})
response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0
)
conversation.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})
print(response['choices'][0]['message']['content'])

"""
Potential follow-ups to prompt:
* Great! Can you combine both pieces of code and give me one script, which will explore to find the object of interest and then also move the agent towards it?
* Can you modify this function so it is valid for any type of object that I specify, not just a bottle? Also keep the code as compact as possible.
* Can you modify this function so that the agent will move closer to the object once it is centered in the image?
* Can you base distance off the average between the width and height of the bounding box and have it be greater than 0.7?
* Awesome! Let's add an action called hover() in which the agent will maintain its current position. Can you modify this function so that if the target object is at a close enough distance, the agent will hover instead of moving forward?
* Excellent! I want you to modularize this code a bit. Why don't you try coming up with a few functions and use them?
* Great! Now let's say the bottle is centered in the image. Now I want to get closer to the bottle until the width and height of the bottle bounding box are large enough. Can you give me code to make this happen?
"""

while(True):
    user_input = input()
    conversation.append({"role": "user", "content":user_input})
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0
    )
    conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print(response['choices'][0]['message']['content'])
