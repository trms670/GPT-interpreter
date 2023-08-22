"""
file: gptplot.py
date: 8/21/23
purpose: outlines gpt-4 prompt and defines function for centering an object in the image given x_center and z_center
"""

import os
import openai
import json

API_KEY = "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"
openai.api_key = API_KEY
model_id = 'gpt-3.5-turbo-16k'

conversation = []
conversation.append({'role': 'system', 'content': '''You are an excellent interpreter of human instructions for tracking objects.
Given an instruction to follow an object and information about an object's location, 
you determine the next appropriate drone command. An object's coordinates will be in the following format: [x_center, z_center]
When the drone camera moves to the right, any objects detected in the environment before will shift to the left in the image.

Necessary and sufficient drone commands are as follows:
"DRONE COMMAND LIST"
- hover()
- move_right()
- move_left()
- move_up()
- move_down()

You divide the actions given in the text into detailed drone commands and put them together 
as a python dictionary.
The dictionary has six keys.
"""
- dictinoary["task_explanation"]: contains a description of the reasoning behind the determined drone's commands based on the object's location.
- dictionary["task_cohesion"]: A dictionary containing information about the drone's commands
that have been split up.
- dictionary["instruction_summary"]: contains a brief summary of the given sentence.
- dictionary["question"]: If you cannot understand the given sentence, you can ask the user to rephrase the sentence. Leave this key empty if you can understand the given sentence.
"""
Three keys exist in dictionary["task_cohesion"].
"""
- dictionary["task_cohesion"]["task_sequence"]: Contains a list of drone commands. This should only have one command listed.
Only the behaviors defined in the "DRONE COMMAND LIST" will be used.
- dictionary["task_cohesion"]["step_instructions"]: contains a list of instructions corresponding 
to dictionary["task_cohesion"]["task_sequence"].
- dictionary["task_cohesion"]["object_name"]: The name of the manipulated object. Only objects defined 
in the input will be used for the object name.
"""'''})
conversation.append({"role": "system", "content":
'''To ensure accuracy, it is crucial that you perform a double check procedure after determining the initial drone command based on the given object coordinates. This double check involves verifying that the task explanation aligns with the provided coordinates, specifically paying attention to rules 1 and 2.
Remember that YOLO box coordinates are represented in this format: [x_center, z_center]

As you devise the appropriate drone command, keep in mind the following rules:

1. If the object is centered in the image both horizontally and vertically, meaning both the x_center and z_center are greater than 0.4 and less than 0.6, the drone should move forward.
2. You should not move left or right if the x_center is greater than 0.4 and less than 0.6.
3. Centering an object in the image takes higher priority over or hovering.
4. Ensure that each element of the ["step_instructions"] explains the corresponding element of the ["task_sequence"].
5. The length of the ["step_instructions"] list must be the same as the length of the ["task_sequence"] list, which is one.
6. Perform a consistent movement as a nano-drone, following the six rules.'''})
conversation.append({'role': 'system', 'content': '''
I will give you some examples of the input and the output you will generate. Please provide the output in JSON format.
Example 1:
"""
- Input:
"Instruction: Follow the cat at [0.58, 0.3]"
- Output:
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
Example 2:
"""
- Input:
"Instruction: Follow the kite at [0.7, 0.45]"
- Output:
```
{"task_explanation": "Since the kite's x_center is greater than 0.6, the kite is on the right side of the image and the appropriate command for the drone is to move right.",
    "task_cohesion": {
    "task_sequence": [
        "move_right()"
    ],
    "step_instructions": [
        "move right"
    ],
    "object_name": "<kite>"},
"instruction_summary": "Centering the kite horizontally in the image",
"question":""}
```
Example 3:
"""
- Input:
"Instruction: Follow the person in blue at [0.45, 0.56]"
- Output:
```
{"task_explanation": "The person is centered in the image since both x_center and z_center are greater than 0.4 and less than 0.6, indicating that drone should hover.",
"task_cohesion": {
    "task_sequence": [
        "hover()"
    ],
    "step_instructions": [
        "hover"
    ],
    "object_name": "<person>"},
"instruction_summary": "Maintaining drone's position",
"question":""}
```
Example 4:
"""
- Input:
"Instruction: Follow the gun at [0.42, 0.61]"
- Output:
```
{"task_explanation": "Since the gun's z_center is greater than 0.6, the gun is on the bottom half of the image and the appropriate command for the drone is to move diwn.",
"task_cohesion": {
    "task_sequence": [
        "move_down()"
    ],
    "step_instructions": [
        "move downwards"
    ],
    "object_name": "<gun>"},
"instruction_summary": "Centering the gun vertically in the image",
"question":""}
```
'''})

"""
parameters: a double representing x_center of object, a double representing y_center of object
returns: a string detailing the next drone command
purpose: given an object and its coordinates, the function inputs an instruction to follow the object
to the gpt prompt and returns the next appropriate drone command
"""
def get_command(x_center, z_center, object_name):
    user_input = 'Instruction: Follow the ' + object_name + ' at [' + str(x_center) + ', ' + str(z_center) + ']'
    print(user_input)
    conversation.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0.1
    )
    conversation.pop()
    json_string = response['choices'][0]['message']['content']
    #conversation.append({"role": "assistant", "content": json_string})
    #print(json_string)
    json_object = json.loads(json_string)
    return json_object['task_cohesion']['task_sequence'][0]

"""while(True):
    user_input = input()
    conversation.append({"role": "user", "content":user_input})
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        temperature = 0.1
    )
    conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print(response['choices'][0]['message']['content'])"""