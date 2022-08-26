from testJSON import testJSON
from testXML import testXML
import shutil
import os
import numpy as np
import csv

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

try:
    os.remove('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/accuracy.csv')
except:
    pass

single_blur = [11]
threshold = [i for i in range (150, 240)]
pixels = [i for i in np.arange(10, 500, 10)]
percent = [i for i in np.arange(0.5, 70, 0.5)]

def model(single_blur, threshold, pixels, percent):
    clean_error = testJSON(single_blur, threshold, pixels, percent)
    if clean_error == 0.0:
        return
    glare_error = testXML(single_blur, threshold, pixels, percent)
    try:
        accuracy = 1-(glare_error+clean_error)
    except:
        return
    return glare_error, clean_error, accuracy

data = []

for a in single_blur:
    for b in threshold:
        for c in pixels:
            for d in percent:
                try:
                    glare_error, clean_error, accuracy = model(a, b, c, d)
                except:
                    continue
                data.append([a, b, c, d, glare_error, clean_error, accuracy])


print(data)
header = ['single blur', 'threshold', 'pixels', 'percent', 'glare error', 'clean error', 'accuracy']

with open('/Users/exahealth/Documents/Glare Detector/Raw/Positive images/accuracy.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

