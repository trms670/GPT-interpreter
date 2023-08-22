"""
file: drone2.py
date: 8/21/23
purpose: outlines gpt-4 prompt for converting object detection results into drone commands
this specific version deals with x_center and y_center instead of x_min and y_min
"""

import os
import openai

API_KEY = "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"
openai.api_key = API_KEY
model_id = 'gpt-3.5-turbo-16k'

conversation = []
conversation.append({'role': 'system', 'content': '''You are an excellent interpreter of human instructions for tracking objects.
Given an instruction to follow an object and information about an object's environment, 
you determine the next appropriate drone command. An object's coordinates will be in the following format: [x_center, y_center, width, height]
When the drone camera moves to the right, any objects detected in the environment before will shift to the left in the image.

Necessary and sufficient drone commands are as follows:
"DRONE COMMAND LIST"
- move_forward()
- move_backward()
- move_right()
- move_left()
- move_up()
- move_down()
- hover()

Information about an object and its location are given as python dictionary. Example:
"""
{"environment":{"object_class": ["<person>"],
    "object_states": {"<person>": "coord(<person>")}}
"""
Object states are represented using those state sets:
""
"STATE LIST"
- coord(<something>): YOLO coordinates of <something> given by bounded box in the form [x_center, y_center, width, height]
"""
<something> should be one of the objects in the environment.

You divide the actions given in the text into detailed drone commands and put them together 
as a python dictionary.
The dictionary has six keys.
"""
- dictinoary["task_explanation"]: contains a description of the reasoning behind the determined drone's commands based on the object's location.
- dictionary["task_cohesion"]: A dictionary containing information about the drone's commands
that have been split up.
- dictionary["environment_before"]: The state of the environment before the manipulation.
- dictionary["environment_after"]: The state of the environment after the manipulation.
- dictionary["instruction_summary"]: contains a brief summary of the given sentence.
- dictionary["question"]: If you cannot understand the given sentence, you can ask the user to 
rephrase the sentence. Leave this key empty if you can understand the given sentence.
"""
Three keys exist in dictionary["task_cohesion"].
"""
- dictionary["task_cohesion"]["task_sequence"]: Contains a list of drone commands. This should only have one command listed.
Only the behaviors defined in the "DRONE COMMAND LIST" will be used.
- dictionary["task_cohesion"]["step_instructions"]: contains a list of instructions corresponding 
to dictionary["task_cohesion"]["task_sequence"].
- dictionary["task_cohesion"]["object_name"]: The name of the manipulated object. Only objects defined 
in the input dictionary will be used for the object name.
"""'''})
conversation.append({'role': 'system', 'content': '''
To ensure accuracy, it is crucial that you perform a double check after determining the initial drone command based on the given object coordinates. This double check involves verifying that the task explanation aligns with the provided coordinates, specifically paying attention to rules 1 and 2.
Remember that YOLO box coordinates are represented in this format: [x_center, y_center, width, height]

As you devise the appropriate drone command, keep in mind the following rules:

1. If the object is centered in the image both horizontally and vertically and either its height, width, or both are less than or equal to 0.7, the drone should move forward.
2. If the object is centered in the image both horizontally and vertically and both its height and width are greater than 0.7, the drone should hover.
3. Centering an object in the image takes higher priority over moving forward or hovering.
4. Ensure that each element of the ["step_instructions"] explains the corresponding element of the ["task_sequence"].
5. The length of the ["step_instructions"] list must be the same as the length of the ["task_sequence"] list, which is one.
6. Perform a consistent movement as a nano-drone, following the six rules.'''})
conversation.append({'role': 'user', 'content': 'Follow the cat at [0.5, 0.3, 0.3, 0.4]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "The cat is not centered in the image vertically. Since the cat's y_center is less than 0.5, the cat is on the top half of the image and the appropriate command for the drone is to move up.",
"task_cohesion": {
    "task_sequence": [
        "move_up()"
    ],
    "step_instructions": [
        "move upwards"
    ],
    "object_name": "<cat>"},
"environment_before": {"object": ["<cat>"],
                "object_states": {"<cat>": "coord(<cat>)"},
"environment_after": {"object": ["<cat>"],
                "object_states": {"<cat>": "coord(<cat>)"},
"instruction_summary": "Centering the cat vertically in the image",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the kite at [0.3, 0.5, 0.8, 0.7]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "The kite is not centered in the image horizontally. Since the kite's x_center is less than 0.5, the kite is on the left side of the image and the appropriate command for the drone is to move left.",
    "task_cohesion": {
    "task_sequence": [
        "move_left()"
    ],
    "step_instructions": [
        "move left"
    ],
    "object_name": "<kite>"},
"environment_before": {"object": ["<kite>"],
                "object_states": {"<kite>": "coord(<kite>)"},
"environment_after": {"object": ["<kite>"],
                "object_states": {"<kite>": "coord(<kite>)"},
"instruction_summary": "Centering the kite horizontally in the image",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the person in blue at [0.5, 0.5, 0.2, 0.8]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "The person is centered in the image and the width is small enough, indicating that the person is far enough to move forward.",
"task_cohesion": {
    "task_sequence": [
        "move_forward()"
    ],
    "step_instructions": [
        "move forward"
    ],
    "object_name": "<person>"},
"environment_before": {"object": ["<person>"],
                "object_states": {"<person>": "coord(<person>)"},
"environment_after": {"object": ["<person>"],
                "object_states": {"<person>": "coord(<person>)"},
"instruction_summary": "Approaching the person in blue",
"question":""}'''})
conversation.append({'role': 'user', 'content': 'Follow the bus at [0.5, 0.5, 0.8, 0.85]'})
conversation.append({'role': 'assistant', 'content': '''{"task_explanation": "The bus is centered in the image and both its height and width are large enough (greater than 0.7), indicating that the bus is close enough to the camera. The drone should hover.",
"task_cohesion": {
    "task_sequence": [
        "hover()"
    ],
    "step_instructions": [
        "hover"
    ],
    "object_name": "<bus>"},
"environment_before": {"object": ["<bus>"],
                "object_states": {"<bus>": "coord(<bus>)"},
"environment_after": {"object": ["<bus>"],
                "object_states": {"<bus>": "coord(<bus>)"},
"instruction_summary": "Maintaining drone's position",
"question":""}'''})


user_input = input('Instruction: ')
conversation.append({"role": "user", "content": user_input})
response = openai.ChatCompletion.create(
    model=model_id,
    messages=conversation,
    temperature = 0.1
)

conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
print(response['choices'][0]['message']['content'])

while(True):
    user_input = input()
    conversation.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model=model_id,
        messages = conversation
    )

    conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print(response['choices'][0]['message']['content'])


