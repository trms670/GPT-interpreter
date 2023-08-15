import cv2
import numpy as np

import time
import sys
import os
import random

CONFIDENCE = 0.5
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5

# the neural network configuration
config_path = "darknet/cfg/yolov3.cfg"
# the YOLO net weights file
weights_path = "darknet/yolov3.weights"
# weights_path = "weights/yolov3-tiny.weights"
global_boxes = []

closest_box_coords = [0, 0, 0, 0]
closest_box_wh = [0, 0, 0, 0]


def box_image(image_name, follow="person"):
  global closest_box_coords
  global closest_box_wh
  # loading all the class labels (objects)
  labels = open("darknet/data/coco.names").read().strip().split("\n")
  # generating colors for each object for later plotting
  colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
  net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
  path_name = image_name
  image = cv2.imread(path_name)
  file_name = os.path.basename(path_name)
  filename, ext = file_name.split(".")
  h, w = image.shape[:2]
  ih, iw = image.shape[:2]
  # create 4D blob
  blob = cv2.dnn.blobFromImage(image,
                               1 / 255.0, (416, 416),
                               swapRB=True,
                               crop=False)
  # print("image.shape:", image.shape)
  # print("blob.shape:", blob.shape)

  # sets the blob as the input of the network
  net.setInput(blob)
  # get all the layer names
  ln = net.getLayerNames()
  try:
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
  except IndexError:
    # in case getUnconnectedOutLayers() returns 1D array when CUDA isn't available
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
  # feed forward (inference) and get the network output
  # measure how much it took in seconds
  start = time.perf_counter()
  layer_outputs = net.forward(ln)
  time_took = time.perf_counter() - start
  # print(f"Time took: {time_took:.2f}s")
  person_index = labels.index(follow)

  font_scale = 1
  thickness = 1
  boxes, tylerboxes, confidences, class_ids = [], [], [], []
  # loop over each of the layer outputs
  for output in layer_outputs:
    # loop over each of the object detections
    for detection in output:
      # extract the class id (label) and confidence (as a probability) of
      # the current object detection
      scores = detection[5:]
      class_id = np.argmax(scores)
      confidence = scores[class_id]
      # discard out weak predictions by ensuring the detected
      # probability is greater than the minimum probability
      # if confidence > CONFIDENCE and class_id == person_index:
      if confidence > CONFIDENCE:
        # scale the bounding box coordinates back relative to the
        # size of the image, keeping in mind that YOLO actually
        # returns the center (x, y)-coordinates of the bounding
        # box followed by the boxes' width and height
        box = detection[:4] * np.array([w, h, w, h])
        (centerX, centerY, width, height) = box.astype("int")
        # use the center (x, y)-coordinates to derive the top and
        # and left corner of the bounding box
        x = int(centerX - (width / 2))
        y = int(centerY - (height / 2))
        # update our list of bounding box coordinates, confidences,
        # and class IDs
        boxes.append([x, y, int(width), int(height)])
        tylerboxes.append([round(x/iw, 2), round(y/ih, 2), round(width/iw, 2), round(height/ih, 2)])
        confidences.append(float(confidence))
        class_ids.append(class_id)

  # loop over the indexes we are keeping
  # print(boxes)
  # print(class_ids)
  # perform the non maximum suppression given
  if any(boxes):
    indices = cv2.dnn.NMSBoxes(boxes, confidences, SCORE_THRESHOLD,
                               IOU_THRESHOLD)
    # of all the boxes, randomly select one box
    if any(indices): i = random.choice(indices)
    else: i = 0  # if no boxes are detected, then select the first box
    # extract the bounding box coordinates
    if (closest_box_coords == None and i != 0):
      # print("Here!")
      x, y = boxes[i][0], boxes[i][1]
      w, h = boxes[i][2], boxes[i][3]
      closest_box_coords = [x, y]
      closest_box_wh = [w, h]
      closest_box_coords = find_closest_box(boxes, closest_box_coords[0],
                                            closest_box_coords[1], class_ids,
                                            boxes.index(boxes[i]))
    elif (i == 0):
      # print("Never")
      closest_box_coords = find_closest_box(boxes, closest_box_coords[0],
                                            closest_box_coords[1], class_ids,
                                            class_ids[i] if class_ids else 0)
      # closest_box_coords, closest_box_wh = closest_box[:2], closest_box[2:] if closest_box else ([0,0], [0,0])
      x, y = closest_box_coords[0], closest_box_coords[1]
      w, h = closest_box_coords[2], closest_box_coords[3]
      # print(x, " " ,y)

    if (class_ids == []):
      class_ids = [0]
      confidences = [0]

      # draw a bounding box rectangle and label on the image

      # loop over the boxes (indices)
    for i in indices.flatten():
      # extract the bounding box coordinates
      x, y = boxes[i][0], boxes[i][1]
      w, h = boxes[i][2], boxes[i][3]
      # draw a bounding box rectangle and label on the image
      color = [int(c) for c in colors[class_ids[i]]]
      cv2.rectangle(image, (x, y), (x + w, y + h),
                    color=color,
                    thickness=thickness)
      text = f"{labels[class_ids[i]]}: {confidences[i]:.2f}"
      # calculate text width & height to draw the transparent boxes as background of the text
      (text_width, text_height) = cv2.getTextSize(text,
                                                  cv2.FONT_HERSHEY_SIMPLEX,
                                                  fontScale=font_scale,
                                                  thickness=thickness)[0]
      text_offset_x = x
      text_offset_y = max(
          0, y - 5)  # Ensure that the text always falls within the image
      box_coords = ((text_offset_x, text_offset_y),
                    (text_offset_x + text_width + 2,
                     text_offset_y - text_height))
      overlay = image.copy()
      cv2.rectangle(overlay,
                    box_coords[0],
                    box_coords[1],
                    color=color,
                    thickness=cv2.FILLED)
      # add opacity (transparency to the box)
      image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
      # now put the text (label: confidence %)
      cv2.putText(image,
                  text, (x, y - 5 if y - 5 > 0 else 15),
                  cv2.FONT_HERSHEY_SIMPLEX,
                  fontScale=font_scale,
                  color=(0, 0, 0),
                  thickness=thickness)

  # new_image_path = f"temp.jpg"
  # print(boxes)
  #print the class label for each box

  boxes_and_labels = []
  for i in indices.flatten():
    boxes_and_labels.append([tylerboxes[i], labels[class_ids[i]]])
  # cv2.imwrite(new_image_path, image)
  return boxes_and_labels


# Function to find box closest to a certain coordinate (x, y)
def find_closest_box(boxes, x, y, all_class_id, current_class_id=0):
  # only consider boxes with the same class id
  same_class_boxes = [
      box for box, class_id in zip(boxes, all_class_id)
      if class_id == current_class_id
  ]
  # calculate the distance between the center of the box and the coordinate (x, y)
  distances = [((box[0] + box[2] / 2) - x)**2 + ((box[1] + box[3] / 2) - y)**2
               for box in same_class_boxes]
  # return the box with the smallest distance if there are boxes of the same class
  if distances:
    return same_class_boxes[np.argmin(distances)]
  else:
    # if no boxes of the same class are found, return a random box
    return random.choice(boxes) if boxes else None


#print([f"{box}" for box in box_image("giraffe.jpg")])