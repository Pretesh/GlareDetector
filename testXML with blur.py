from GlareAndBlur_Detector import glareAndBlurDetector
import os
from pathlib import Path
import cv2
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

directory = '/Users/exahealth/Documents/Glare Detector/Raw/Glare Images/'

falsePositiveCounter = 0
for image in os.listdir(directory):
    print(falsePositiveCounter)
    image_path = directory + image
    xml_path = image_path.replace('Glare Images', 'Labels')
    xml_path = Path(xml_path).with_suffix('.xml')

    try: 
        decision, percentOccupancy, fm = glareAndBlurDetector(image_path, xml_path)
    except:
        print('error')
        continue

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

