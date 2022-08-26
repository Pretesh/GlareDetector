import numpy as np
import cv2
import parse_files
from skimage import measure


def getGlareSpots(image_path, xmin, xmax, ymin, ymax, single_blur, threshold, pixels):
    image = cv2.imread(image_path)
    #image = cv2.resize(image, (2000,2000))
    # xminN = xmin - (xmax-xmin)*2
    # xmaxN = xmax + (xmax-xmin)*2
    # yminN = ymin - (ymax-ymin)*2
    # ymaxN = ymax + (ymax-ymin)*2
    # if yminN < 0:
    #     yminN = 0
    # if xminN <0:
    #     xminN = 0
    image = image[ymin:ymax, xmin:xmax]
    gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
    blurred = cv2.GaussianBlur( gray, (single_blur, single_blur), 0 )

    # threshold the image to reveal light regions in the
    # blurred image
    thresh = cv2.threshold( blurred, threshold, 255, cv2.THRESH_BINARY )[1]

    # perform a series of erosions and dilations to remove
    # any small blobs of noise from the thresholded image
    thresh = cv2.erode( thresh, None, iterations=2 )
    thresh = cv2.dilate( thresh, None, iterations=4 )


    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label( thresh, connectivity=2, background=0 )

    mask = np.zeros( labels.shape, dtype="uint8" )
    # loop over the unique components



    for label in np.unique( labels ):
        # if this is the background label, ignore it
        if label == 0:
            continue
        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros( labels.shape, dtype="uint8" )
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero( labelMask )
        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > pixels:
            mask = cv2.add( mask, labelMask )

    # cv2.imshow( "Image", image )
    # cv2.waitKey( 0 )

    # cv2.imshow( "mask", mask )
    # cv2.waitKey( 0 )

    # masked = cv2.bitwise_and(image, image, mask=mask)
    # cv2.imshow("Mask Applied to Image", masked)
    # cv2.waitKey(0)

    return mask

def getResultWellBB(xml_path):
    strip_poly, line_centers, blood_well_center, x = parse_files.parse_xml(xml_path, 0)
    #Construct resultwell bounding box
    strip_poly = np.array(strip_poly)
    xmin = strip_poly.min(axis=0)[0]
    xmax =strip_poly.max(axis=0)[0]
    ymin =strip_poly.min(axis=0)[1]
    ymax = strip_poly.max(axis=0)[1]

    return xmin, xmax, ymin, ymax

def glareDecision(mask, xmin, xmax, ymin, ymax, percent):
    #Count number of pixels of mask in the resultwell bounding box region
    # #Crop mask to resultwell area
    # maskShape = mask.shape
    # maskxmin = 0 + 2*(xmax-xmin)
    # maskxmax = maskShape[1] - 2*(xmax-xmin)
    # maskymin = 0 + 2*(ymax-ymin)
    # maskymax = maskShape[0] - 2*(ymax-ymin)
    # croppedMask = mask[maskymin:maskymax, maskxmin:maskxmax]
    # cv2.imshow('cropped mask', croppedMask)
    # cv2.waitKey(0)
    #Calculate area of resultwell bounding box
    area = (ymax-ymin)*(xmax-xmin)
    #Calculate % occupancy of resultwell by glare pixels
    numberOfGlarePixels = cv2.countNonZero(mask)
    percentOccupancy = (numberOfGlarePixels/area)*100
    #If %occupancy exceeds threshold then say 'Too much glare on strip'
    if percentOccupancy > percent:
        return 'Too much glare', percentOccupancy
    else:
        return 'No glare', percentOccupancy

def glareDetector(image_path, xml_path, single_blur, threshold, pixels, percent):
    xmin, xmax, ymin, ymax = getResultWellBB(xml_path)
    mask = getGlareSpots(image_path, xmin, xmax, ymin, ymax, single_blur, threshold, pixels,)
    decision, percentOccupancy = glareDecision(mask, xmin, xmax, ymin, ymax, percent)

    return decision, percentOccupancy

def getResultwellBBJSON(labels, imageName):
    strip_poly = labels[imageName]['resultwell']['polygon']
    strip_poly = np.array(strip_poly)
    xmin = strip_poly.min(axis=0)[0]
    xmax =strip_poly.max(axis=0)[0]
    ymin =strip_poly.min(axis=0)[1]
    ymax = strip_poly.max(axis=0)[1]

    return int(xmin), int(xmax), int(ymin), int(ymax)

def glareDetectorJSON(labels, image_path, imageName, single_blur, threshold, pixels, percent):
    xmin, xmax, ymin, ymax = getResultwellBBJSON(labels, imageName)
    mask = getGlareSpots(image_path, xmin, xmax, ymin, ymax, single_blur, threshold, pixels)
    decision, percentOccupancy = glareDecision(mask, xmin, xmax, ymin, ymax, percent)
    
    return decision, percentOccupancy

#image = '/Users/exahealth/Documents/Glare Detector/Raw/Rare/AbbottBinaxNOW-ADR-Abbott Validation Study-A301TZG-Station7-Flow Hood-1651174364361.jpeg'
#xml = '/Users/exahealth/Documents/Glare Detector/Raw/Labels/AbbottBinaxNOW-ADR-Abbott Validation Study-A301TZG-Station7-Flow Hood-1651174364361.xml'
#decision, percentOccupancy = glareDetector(image, xml)

#print(decision)
#print(percentOccupancy)