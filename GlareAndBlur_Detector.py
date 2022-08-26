import numpy as np
import cv2
import parse_files
from skimage import measure



def getResultWellBB(xml_path):
    strip_poly, line_centers, blood_well_center, x = parse_files.parse_xml(xml_path, 0)
    #Construct resultwell bounding box
    strip_poly = np.array(strip_poly)
    xmin = strip_poly.min(axis=0)[0]
    xmax =strip_poly.max(axis=0)[0]
    ymin =strip_poly.min(axis=0)[1]
    ymax = strip_poly.max(axis=0)[1]

    return xmin, xmax, ymin, ymax


def getResultwellBBJSON(labels, imageName):
    strip_poly = labels[imageName]['resultwell']['polygon']
    strip_poly = np.array(strip_poly)
    xmin = strip_poly.min(axis=0)[0]
    xmax =strip_poly.max(axis=0)[0]
    ymin =strip_poly.min(axis=0)[1]
    ymax = strip_poly.max(axis=0)[1]

    return int(xmin), int(xmax), int(ymin), int(ymax)

def glareDetectorJSON(labels, image_path, imageName):
    xmin, xmax, ymin, ymax = getResultwellBBJSON(labels, imageName)
    mask, fm = getGlareSpotsAndBlur(image_path, xmin, xmax, ymin, ymax)
    decision, percentOccupancy, fm = glareAndBlurDecision(mask, xmin, xmax, ymin, ymax, fm)
    
    return decision, percentOccupancy, fm

def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()

def getGlareSpotsAndBlur(image_path, xmin, xmax, ymin, ymax):
    image = cv2.imread(image_path)
    #image = cv2.resize(image, (2000,2000))
    xminN = xmin - (xmax-xmin)*2
    xmaxN = xmax + (xmax-xmin)*2
    yminN = ymin - (ymax-ymin)*2
    ymaxN = ymax + (ymax-ymin)*2
    if yminN < 0:
        yminN = 0
    if xminN <0:
        xminN = 0
    croppedimage = image[yminN:ymaxN, xminN:xmaxN]
    gray = cv2.cvtColor( croppedimage, cv2.COLOR_BGR2GRAY )
    blurred = cv2.GaussianBlur( gray, (11, 11), 0 )

    # threshold the image to reveal light regions in the
    # blurred image
    thresh = cv2.threshold( blurred, 200, 255, cv2.THRESH_BINARY )[1]

    # perform a series of erosions and dilations to remove
    # any small blobs of noise from the thresholded image
    thresh = cv2.erode( thresh, None, iterations=2 )
    thresh = cv2.dilate( thresh, None, iterations=4 )

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label( thresh, connectivity=2, background=0 )
    mask = np.zeros( thresh.shape, dtype="uint8" )
    # loop over the unique components
    for label in np.unique( labels ):
        # if this is the background label, ignore it
        if label == 0:
            continue
        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros( thresh.shape, dtype="uint8" )
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero( labelMask )
        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 300:
            mask = cv2.add( mask, labelMask )

    #cv2.imshow( "Image", image )
    #cv2.waitKey( 0 )

    #masked = cv2.bitwise_and(image, image, mask=mask)
    #cv2.imshow("Mask Applied to Image", masked)
    #cv2.waitKey(0)

    #fm = variance_of_laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY ))
    xminB = xmin - (xmax-xmin)*5
    xmaxB = xmax + (xmax-xmin)*5
    yminB = ymin - (ymax-ymin)*5
    ymaxB = ymax + (ymax-ymin)*5
    if yminB < 0:
        yminB = 0
    if xminB <0:
        xminB = 0
    imageB = image[yminB:ymaxB, xminB:xmaxB]
    fm = variance_of_laplacian(cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY ))

    return mask, fm

def glareAndBlurDecision(mask, xmin, xmax, ymin, ymax, fm):
    #Count number of pixels of mask in the resultwell bounding box region
    #Crop mask to resultwell area
    maskShape = mask.shape
    maskxmin = 0 + 2*(xmax-xmin)
    maskxmax = maskShape[1] - 2*(xmax-xmin)
    maskymin = 0 + 2*(ymax-ymin)
    maskymax = maskShape[0] - 2*(ymax-ymin)
    croppedMask = mask[maskymin:maskymax, maskxmin:maskxmax]
    #cv2.imshow('cropped mask', croppedMask)
    #cv2.waitKey(0)
    #Calculate area of resultwell bounding box
    area = (ymax-ymin)*(xmax-xmin)
    #Calculate % occupancy of resultwell by glare pixels
    numberOfGlarePixels = cv2.countNonZero(croppedMask)
    percentOccupancy = (numberOfGlarePixels/area)*100
    #If %occupancy exceeds threshold then say 'Too much glare on strip'
    if percentOccupancy > 15 and fm < 70:
        return 'Too much glare and blurry', percentOccupancy, fm
    elif percentOccupancy < 15 and fm < 70:
        return 'No glare and blurry', percentOccupancy, fm
    elif percentOccupancy > 15 and fm > 70:
        return 'Too much glare and not blurry', percentOccupancy, fm
    else:
        return 'Image fine', percentOccupancy, fm



def glareAndBlurDetector(image_path, xml_path):
    xmin, xmax, ymin, ymax = getResultWellBB(xml_path)
    mask, fm = getGlareSpotsAndBlur(image_path, xmin, xmax, ymin, ymax)
    decision, percentOccupancy, fm = glareAndBlurDecision(mask, xmin, xmax, ymin, ymax, fm)

    return decision, percentOccupancy, fm

