from Glare_detector import glareDetectorJSON
import os
import json
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

def testJSON (single_blur, threshold, pixels, percent):
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
    normalCounter = 0
    #imageNumber = 1
    for image in os.listdir(directory):
        #print(falsePositiveCounter)
        #print(imageNumber)
        image_path = directory + image

        # try: 
        #     decision, percentOccupancy = glareDetectorJSON(labels, image_path, image, single_blur, threshold, pixels, percent)
        # except:
        #     print('error')
        #     continue

        decision, percentOccupancy = glareDetectorJSON(labels, image_path, image, single_blur, threshold, pixels, percent)

        print(decision)
        if decision == 'Too much glare':
            falsePositiveCounter += 1
            #img = cv2.imread(image_path)
            #os.chdir('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/Glare')
            #cv2.imwrite(str(percentOccupancy) + '.jpg', img)
        else:
            normalCounter += 1

        #imageNumber += 1

        if falsePositiveCounter == 30:
            return

        errors = falsePositiveCounter/(falsePositiveCounter+normalCounter)
        return errors
