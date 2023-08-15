import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from gptplot import get_command
import mpl_toolkits.mplot3d.art3d as art3d

plt.style.use('_mpl-gallery')

object_name = "cat"
step_size = 2

#drone and object coordinates
droneloc = {
    'x': 2,
    'y': 0,
    'z': 3
}

objloc = {
    'x': -5,
    'y': 1,
    'z': 7
}

#camera dimensions
cam_x_length = 20
cam_z_length = 15

obj_width = 2
obj_height = 2

obj_rel_width = obj_width
obj_rel_height = obj_height

while(True):
    #relative coordinates
    obj_rel_x = ((objloc['x'] - droneloc['x']) + (cam_x_length / 2)) / cam_x_length
    obj_rel_z = ((cam_z_length / 2) - (objloc['z'] - droneloc['z'])) / cam_z_length

    if (obj_rel_x < 0 or obj_rel_z < 0 or obj_rel_x > 1 or obj_rel_z > 1 or objloc['y'] <= droneloc['y']):
        print("Object out of view")
        break

    # Plot 3D
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=[7, 6], layout='constrained')

    rec = Rectangle((objloc['x'] - (obj_width / 2), objloc['z'] - (obj_height / 2)), obj_width, obj_height, edgecolor = 'blue', fill = False)
    ax.add_patch(rec)
    art3d.pathpatch_2d_to_3d(rec, z=objloc['y'], zdir="y")

    ax.scatter(droneloc['x'], droneloc['y'], droneloc['z'], c='r', marker='o', label='Drone')
    ax.scatter(objloc['x'], objloc['y'], objloc['z'], c='b', marker='^', label='Object')

    ax.set_title("Drone and Object 3D Positions")
    ax.set(xlabel= "X", ylabel = "Y", zlabel = "Z",
        xlim = [-10, 10], ylim = [-10, 10], zlim = [-10, 10])

    plt.show(block=False)
    if(input("end? ") == "yes"):
        break
    plt.close()

    #Plot 2D
    fig, ax = plt.subplots(figsize=[7,6], layout='constrained')

    #centered relative area
    ax.add_patch(Rectangle((0.4, 0.4), 0.2, 0.2,
    facecolor = 'yellow'))
    if (objloc['y'] - droneloc['y'] != 0):
        obj_rel_width = (obj_width / ((objloc['y'] - droneloc['y']) ** 2)) / cam_x_length
        obj_rel_height = (obj_height / ((objloc['y'] - droneloc['y']) ** 2)) / cam_z_length
    relrec = Rectangle((obj_rel_x - (obj_rel_width / 2), obj_rel_z - (obj_rel_height / 2)), obj_rel_width, obj_rel_height, edgecolor = 'blue', fill = False)
    ax.add_patch(relrec)

    ax.scatter(obj_rel_x, obj_rel_z, c='b', marker='^', label='Object')
    ax.set(xlim = (0,1), ylim = (0,1),
    xticks=np.arange(0, 1, step=0.1), yticks=np.arange(0, 1, step=0.1), 
    xlabel = 'X', ylabel = 'Z')
    ax.set_title("Object's YOLO Position")
    ax.invert_yaxis()

    plt.show(block=False)
    if(input("end? ") == "yes"):
        break
    plt.close()

    #get gpt results
    #print(obj_rel_x)
    #print(obj_rel_z)
    command = get_command(round(obj_rel_x, 3), round(obj_rel_z, 3), object_name)
    print(command)
    #move drone according to gpt output
    if (command == "hover()"):
        break
    elif (command == "move_up()"):
        droneloc['z'] += step_size
    elif (command == "move_down()"):
        droneloc['z'] -= step_size
    elif (command == "move_right()"):
        droneloc['x'] += step_size
    elif (command == "move_left()"):
        droneloc['x'] -= step_size

    print(droneloc)