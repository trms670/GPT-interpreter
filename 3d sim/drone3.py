"""
file: drone3.py
date: 8/21/23
purpose: outlines gpt-4 prompt and defines function that converts object coordinates to drone commands
"""

import os
import openai
import json

API_KEY = "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"
openai.api_key = API_KEY
model_id = 'gpt-4'

conversation = []
conversation.append({'role': 'system', 'content': '''You are an excellent interpretor of human instructions for tracking objects. We are controlling an embodied agent.
Given an instruction to follow an object and information about an object's environment, 
you determine the next appropriate drone command. The only information we have is the location of the object bounding box in the image.
An object's coordinates will be in the following format: [x_min, y_min, width, height]. 

Necessary and sufficient drone commands are as follows:
"DRONE COMMAND LIST"
- move_right()
- move_left()
- move_up()
- move_down()
- move_forward()
- hover()

You divide the actions given in the text into detailed drone commands and put them together 
as a python dictionary.
The dictionary has four keys.
"""
- dictinoary["task_explanation"]: contains a description of the reasoning behind the determined drone's commands based on the object's location.
- dictionary["task_cohesion"]: A dictionary containing information about the drone's commands that have been split up.
- dictionary["instruction_summary"]: contains a brief summary of the given sentence.
- dictionary["question"]: If you cannot understand the given sentence, you can ask the user to 
rephrase the sentence. Leave this key empty if you can understand the given sentence.
"""
Two keys exist in dictionary["task_cohesion"].
"""
- dictionary["task_cohesion"]["task_sequence"]: Contains a list of drone commands. This should only have one command listed.
Only the behaviors defined in the "DRONE COMMAND LIST" will be used.
- dictionary["task_cohesion"]["object_name"]: The name of the manipulated object. Only objects defined 
in the input dictionary will be used for the object name.
"""'''})
conversation.append({'role': 'system', 'content': '''
To ensure accuracy, it is crucial that you perform a double check after determining the initial drone command based on the given object coordinates. This double check involves verifying that the task explanation aligns with the provided coordinates.
Remember that YOLO box coordinates are represented in this format: [x_min, y_min, width, height]. Note that instead of x_max and y_max, the bounding box includes width and height.

As you devise the drone command, keep in mind the following:

1. Assume the bounding box coordinates are already normalized and the image width and height are equal to 1.
2. We can set the threshold for centrality to be 0.1. This means the x_center and y_center must be greater than 0.40 and less than 0.60 for the object to be centered horizontally and vertically, respectively.
3. If the object is centered in the image, the agent will move closer to the object unless either the height or width are greater than 0.60. In this case, the agent will hover.
4. Every object in an instruction should be treated as a different object from previous instructions.
5. The length of the ["task_sequence"] list is always one.
6. Perform a consistent movement as a nano-drone, following the six rules.'''})
conversation.append({'role': 'user', 'content': 'Follow the cat at [0.25, 0.30, 0.40, 0.10]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "Since the cat's y_center (0.35) is less than 0.40, the kite is not centered vertically in the image. The cat is on the top half of the image and the appropriate command for the drone is to move up.",
"task_cohesion": {
    "task_sequence": [
        "move_up()"
    ],
    "object_name": "<cat>"},
"instruction_summary": "Centering the cat vertically in the image",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the kite at [0.29, 0.10, 0.20, 0.70]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "Since the kite's x_center (0.39) is less than 0.40, the kite is not centered horizontally in the image. The kite is on the left side of the image and the appropriate command for the drone is to move left.",
"task_cohesion": {
    "task_sequence": [
        "move_left()"
    ],
    "object_name": "<kite>"},
"instruction_summary": "Centering the kite horizontally in the image",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the person in blue at [0.20, 0.21, 0.50, 0.56]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "Since the person's x_center (0.45) is greater than 0.40 and less than 0.60, the person is centered horizontally in the image. Since the y_center (0.49) is greater than 0.40 and less than 0.60, the person is also centered vertically in the image. Both the person's width and height are not greater than 0.60 so the person is at a far enough distance to move forward.",
"task_cohesion": {
    "task_sequence": [
        "move_forward()"
    ],
    "object_name": "<person>"},
"instruction_summary": "Approaching the person in blue",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the bus at [0.19, 0.15, 0.80, 0.55]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "Since the person's x_center (0.59) is greater than 0.40 and less than 0.60, the person is centered horizontally in the image. Since the ball's y_center (0.425) is greater than 0.40 and less than 0.60, the person is also centered vertically in the image. The bus's width is greater than 0.60 so the bus is at a close enough distance to hover.",
"task_cohesion": {
    "task_sequence": [
        "hover()"
    ],
    "object_name": "<bus>"},
"instruction_summary": "Maintaining drone's position",
"question":""}'''})

"""
parameters: a double array containing bounding box coordinates, a string listing the object name
returns: a string detailing the next drone command
purpose: given an object and its coordinates, the function inputs an instruction to follow the object
to the gpt prompt and returns the next appropriate drone command
"""
def get_command(box, object_name):
    user_input = "Instruction: Follow the " + object_name + "at " + str(box) 
    conversation.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0
    )
    conversation.pop()

    # parse response to json format
    json_string = response['choices'][0]['message']['content']
    #conversation.append({"role": "assistant", "content": json_string})
    json_object = json.loads(json_string)
    return json_object['task_cohesion']['task_sequence'][0]
