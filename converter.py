from __future__ import division 
import sys
import scipy.io as sio
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np 
import os, glob 
import datetime

debug = False
running_from_path = os.getcwd()

# Based on https://stackoverflow.com/a/20679579
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

# Based on https://stackoverflow.com/a/20679579
def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

# https://arcpy.wordpress.com/2012/04/20/146/
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def writeAnnotationFiles(set_name, root_path, write_image_boxes = False, save_images_with_boxes = False, show_image = False):
    firstFile = True
    
    processMax = 100000
    processed = 0

    images_dir = root_path + "/images/"
    annotation_dir = root_path + "/annotations/"
    new_annotations = root_path + "/new_annotations/"
    new_images = root_path + "/new_images/"

    if not os.path.exists(new_annotations):
        os.makedirs(new_annotations)

    if save_images_with_boxes and not os.path.exists(new_images):
        os.makedirs(new_images)

    # Change directory to annotations to retreive only file names
    os.chdir(annotation_dir)
    matlab_annotations = glob.glob("*.mat")

    os.chdir(running_from_path)

    set_info_file = open(set_name + ".txt","w")

    for file in matlab_annotations:
        firstBox = True
        if(processed >= processMax):
            break

        filename = file.split(".")[0]
        
        if(debug):
            print(file)

        with Image.open(images_dir + filename + ".jpg") as pil_image:
            content = sio.loadmat(annotation_dir + file, matlab_compatible  = False)

            boxes = content["boxes"]

            if(write_image_boxes or save_images_with_boxes):
                draw = ImageDraw.Draw(pil_image)

            # image_width = 360
            # image_height = 480
            width, height = pil_image.size

            hs = open(new_annotations + filename + ".txt","w")

            for box in boxes.T:
                a = box[0][0][0][0]
                b = box[0][0][0][1]
                c = box[0][0][0][2]
                d = box[0][0][0][3]

                aXY = (a[0][1], a[0][0])
                bXY = (b[0][1], b[0][0])
                cXY = (c[0][1], c[0][0])
                dXY = (d[0][1], d[0][0])

                if(write_image_boxes or save_images_with_boxes):
                    draw.line([aXY, bXY], fill=(255,0,0,255))
                    draw.line([bXY, cXY], fill=(255,0,0,255))
                    draw.line([cXY, dXY], fill=(255,0,0,255))
                    draw.line([dXY, aXY], fill=(255,0,0,255))

                line1 = line(aXY, cXY)
                line2 = line(bXY, dXY)

                maxX = max(aXY[0], bXY[0], cXY[0], dXY[0])
                minX = min(aXY[0], bXY[0], cXY[0], dXY[0])
                maxY = max(aXY[1], bXY[1], cXY[1], dXY[1])
                minY = min(aXY[1], bXY[1], cXY[1], dXY[1])

                # (<absolute_x> / <image_width>)
                absX = (maxX - minX) / width

                #(<absolute_y> / <image_height>)
                absY = (maxY - minY) / height

                intersect_x, intersect_y = intersection(line1, line2)

                abs_intersect_x = intersect_x / width
                abs_intersect_y = intersect_y / height
                
                if(debug):
                    print("0 %f %f %f %f" %(abs_intersect_x, abs_intersect_y, absX, absY))
                
                if(not firstBox):
                    hs.write("\n")

                hs.write("0 %f %f %f %f" %(abs_intersect_x, abs_intersect_y, absX, absY)),

                if(firstBox):
                    firstBox = False

            hs.close() 

            if(save_images_with_boxes):
                rgb_img = pil_image.convert("RGB")
                rgb_img.save(new_images + filename + ".jpg")
                rgb_img.close()

            if(show_image and processMax < 10):
                pil_image.show()

            pil_image.close()
            processed = processed + 1
            
            if(not firstFile):
                set_info_file.write("\n")    

            set_info_file.write("data/obj/%s/%s.jpg" %(set_name, filename))

            if(firstFile):
                firstFile = False

    set_info_file.close()

start_time = datetime.datetime.now()

if(len(sys.argv) > 1):
    training_config = {
        "test": "hand_dataset/test_dataset/test_data",
        "train": "hand_dataset/training_dataset/training_data",
        "validation": "hand_dataset/validation_dataset/validation_data"
    }

    for index in range(1, len(sys.argv)):
        if sys.argv[index] not in training_config:
            print("Not a valid config value, either use no arguments or on of the following: "),
            for key, _ in training_config.items():
                print(key),
        else:
            writeAnnotationFiles(sys.argv[index], training_config[sys.argv[index]])
else:
    print("else")
    writeAnnotationFiles("test", "hand_dataset/test_dataset/test_data")
    writeAnnotationFiles("train", "hand_dataset/training_dataset/training_data")
    writeAnnotationFiles("validation", "hand_dataset/validation_dataset/validation_data")

end_time = datetime.datetime.now()
seconds_elapsed = (end_time - start_time).total_seconds()
print("It took {} to execute this".format(hms_string(seconds_elapsed)))

