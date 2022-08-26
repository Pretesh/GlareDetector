from GlareAndBlur_Detector import glareDetectorJSON
import os
from pathlib import Path
import cv2
import json
import numpy as np
import shutil

try:
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/GlareAndBlur')
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Blur')
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
except:
    pass
try:
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/GlareAndBlur')
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Blur')
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
except:
    pass

validationSets = ['/Users/exahealth/Documents/Glare Detector/Raw/Validation/BankedSampleClean/', 
                '/Users/exahealth/Documents/Glare Detector/Raw/Validation/Mar4/',
                 '/Users/exahealth/Documents/Glare Detector/Raw/Validation/May11/']
JSONs = ['/Users/exahealth/Documents/Glare Detector/Raw/validationLabels/Banked_sample_resultwell_corners.json', 
        '/Users/exahealth/Documents/Glare Detector/Raw/validationLabels/Mar4_resultwell_corners.json', 
        '/Users/exahealth/Documents/Glare Detector/Raw/validationLabels/May11_resultwell_corners.json']

directory = validationSets[1]
jsonDirectory = JSONs[1]

f = open(jsonDirectory)
labels = json.load(f)
f.close()

falsePositiveCounter = 0
imageNumber = 1
for image in os.listdir(directory):
    print(falsePositiveCounter)
    print(imageNumber)
    image_path = directory + image
    imageName = str(image)

    try: 
        decision, percentOccupancy, fm = glareDetectorJSON(labels, image_path, imageName)
    except:
        print('error')
        continue

    #decision, percentOccupancy, fm = glareDetectorJSON(labels, image_path, imageName)

    print(decision)
    if decision == 'Too much glare and blurry':
        falsePositiveCounter += 1
        img = cv2.imread(image_path)
        os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/GlareAndBlur')
        cv2.imwrite(str(round(percentOccupancy, 1)) + '_' + str(round(fm, 1)) + '.jpg', img)
        print('1')
    elif decision == 'No glare and blurry':
        falsePositiveCounter += 1
        img = cv2.imread(image_path)
        os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Blur')
        cv2.imwrite(str(round(percentOccupancy, 1)) + '_' + str(round(fm, 1)) + '.jpg', img)
        print('2')
    elif decision == 'Too much glare and not blurry':
        falsePositiveCounter += 1
        img = cv2.imread(image_path)
        os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
        cv2.imwrite(str(round(percentOccupancy, 1)) + '_' + str(round(fm, 1)) + '.jpg', img)
        print('3')
    else:
        img = cv2.imread(image_path)
        os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
        cv2.imwrite(str(round(percentOccupancy, 1)) + '_' + str(round(fm, 1)) + '.jpg', img)
        print('4')

    imageNumber += 1
