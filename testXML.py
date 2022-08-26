from Glare_detector import glareDetector
import os
from pathlib import Path
import cv2
import shutil

try:
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
    shutil.rmtree('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
except:
    pass
try:
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
    os.mkdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
except:
    pass


def testXML(single_blur, threshold, pixels, percent):
    directory = '/Users/exahealth/Documents/Glare Detector/Raw/Glare Images/'
    correctlyPositiveCounter = 0
    missedCounter = 0
    for image in os.listdir(directory):
        #print(falsePositiveCounter)
        image_path = directory + image
        xml_path = image_path.replace('Glare Images', 'Labels')
        xml_path = Path(xml_path).with_suffix('.xml')

        # try: 
        #     decision, percentOccupancy = glareDetector(image_path, xml_path, single_blur, threshold, pixels, percent)
        # except:
        #     print('error')
        #     continue

        decision, percentOccupancy = glareDetector(image_path, xml_path)

        print(decision)
        if decision == 'Too much glare':
            correctlyPositiveCounter += 1
            #img = cv2.imread(image_path)
            #os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
            #cv2.imwrite(str(percentOccupancy) + '.jpg', img)
        
        else:
            missedCounter += 1
            #img = cv2.imread(image_path)
            #os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Missed')
            #cv2.imwrite(str(percentOccupancy) + '.jpg', img)
        
        if missedCounter == 7:
            return
        
    errors = missedCounter/(missedCounter+falsePositiveCounter)
    return errors
