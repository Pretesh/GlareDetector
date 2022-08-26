import os
import sys
import cv2
import glob
import numpy as np
import pickle
from lxml import etree

EXPECTED_OBJECT_NAMES = ['SwabAttachment', 'BinaxName', 'PinkBar', 'TopLogo', 'TestLine',
    'Inner TestKit', 'Inner Testkit', "Test", 'ResultWell', 'Resultwell', 'Result Well', 'ResultWell_box', 'C- Control Line', 'Control Line', 'C - Control',  'C-Control', 'Control', 'Test Line', 'T - Test Line', 'Blood_box', 'TestKit', 'X - Occluded', 'OverExpose', 'UnderExpose','InnerTestKit', 'Landmark']

def get_unique_child(node, target_tag):
    my_children = [c for c in node.getchildren() if c.tag == target_tag]
    assert(len(my_children) == 1)
    return my_children[0]

def get_name(my_obj):
    return get_unique_child(my_obj, 'name').text

def process_poly(poly_obj):
    num_children = len(poly_obj.getchildren())
    assert(num_children % 2 == 0)
    num_pts = num_children // 2
    pts = []
    for i in range(1, num_pts + 1):
        pt = []
        pt.append(int(get_unique_child(poly_obj, 'x%d'%(i)).text))
        pt.append(int(get_unique_child(poly_obj, 'y%d'%(i)).text))
        pts.append(pt)

    return pts

def process_bbox(bbox_obj):
    bbox = []
    bbox.append(int(get_unique_child(bbox_obj, 'xmin').text))
    bbox.append(int(get_unique_child(bbox_obj, 'ymin').text))
    bbox.append(int(get_unique_child(bbox_obj, 'xmax').text))
    bbox.append(int(get_unique_child(bbox_obj, 'ymax').text))
    return bbox

def process_pts(pts_obj):
    point = [] 
    point.append(int(get_unique_child(pts_obj, 'x1').text))
    point.append(int(get_unique_child(pts_obj, 'y1').text))
    return [point]


        


#returns bbox_poly (list of points), line_centers (dictionary with point values), blood_well_center (point), and is_valid (Boolean)
def parse_xml(xml_filename, require_blood_well_center):
    with open(xml_filename, 'rb') as f:
        my_tree = etree.parse(f)

    root = my_tree.getroot()
    my_objs  = [c for c in root.getchildren() if c.tag == 'object']
    strip_poly = None # Test Strip corners 
    line_centers = {} # T-Line and C-Line centers 
    blood_well_center = None # Blood box corners 
    for my_obj in my_objs:
        my_name = get_name(my_obj).strip()
        print(my_name)
        if my_name.strip() in ['ResultWell', 'Resultwell', 'Result Well']:
            if strip_poly is not None:
                # can't have duplicates here 
                return None, None, None, False
            if any([c.tag == 'polygon' for c in my_obj.getchildren()]):
                strip_poly = process_poly(get_unique_child(my_obj, 'polygon'))
            else:
                strip_poly = None 
        elif my_name in ['C - Control', 'T - Test Line', 'Control', 'Test Line', 'C-Control', 'Test', 'C- Control Line', 'Control Line', 'Test Line']:
            if my_name in line_centers:
                # can't have duplicates 
                return None, None, None, False


            if any([c.tag == 'polygon' for c in my_obj.getchildren()]):
                line_pts = 1.0 * np.array(process_poly(get_unique_child(my_obj, 'polygon')))
                line_center = np.mean(line_pts, axis=0)
            elif any([c.tag == 'bndbox' for c in my_obj.getchildren()]):
                bb = process_bbox(get_unique_child(my_obj, 'bndbox'))
                line_center = np.array([0.5 * bb[0] + 0.5 * bb[2], 0.5 * bb[1] + 0.5 * bb[3]])
            elif any([c.tag == 'point' for c in my_obj.getchildren()]):
                pts = process_pts(get_unique_child(my_obj, 'point'))
                line_center = np.mean(pts, axis=0)
            else:
                # not supported type for line 
                line_center = None 
            line_centers[my_name] = line_center
        elif my_name in ['Blood_box', 'Landmark']:
            if blood_well_center is not None:
                # can't have duplicates here 
                return None, None, None, False
            if any([c.tag == 'bndbox' for c in my_obj.getchildren()]):
                blood_well_bbox = process_bbox(get_unique_child(my_obj, 'bndbox'))
                blood_well_center = [0.5 * blood_well_bbox[0] + 0.5 * blood_well_bbox[2], 0.5 * blood_well_bbox[1] + 0.5 * blood_well_bbox[3]]
            elif any([c.tag == 'polygon' for c in my_obj.getchildren()]):
                bbox_points = 1.0 * np.array(process_poly(get_unique_child(my_obj, 'polygon')))
                blood_well_center = np.mean(bbox_points, axis=0)
            else:
                blood_well_center = None 
    
        elif my_name in ['OverExpose', 'UnderExpose']:
            return None, None, None, False
        else:
            if my_name not in EXPECTED_OBJECT_NAMES:
                print(my_name)
                print(xml_filename)

            assert(my_name in EXPECTED_OBJECT_NAMES)
    print([strip_poly, line_centers, blood_well_center])
    if strip_poly is None or (blood_well_center is None and require_blood_well_center):
        return None, None, None, False
    else:
        return strip_poly, line_centers, blood_well_center, True

#returns angle, center, bbox
#angle will be the amount that we need to rotate the image to make the strip upright
#center will be the center point to rotate around
#bbox will be (xmin,ymin,xmax,ymax) and will tell you how to crop out the strip once you've rotated the image
#it'll just be based on center and width and height from cv2.minAreaRect()
#use blood_well_center to check if it's upside-down after rotation
def poly_to_rotrect(bbox_poly, blood_well_center):
    #this means that we take a rectangle centered at (cx, cy) with width=w and height=h, and rotate it angle degrees clockwise to get the min-area-rect around bbox_poly
    ((cx, cy), (w, h), angle) = cv2.minAreaRect(np.array(bbox_poly))

    if blood_well_center is None: #make a "fake" blood_well_center that's directly below the strip, i.e. assume that the testkit was upright to begin with
        blood_well_center = [cx, cy + 69]

    #if width is more than height then just swap 'em and add 90 degrees to angle, and you'll get an equivalent result
    if w > h:
        temp = w
        w = h
        h = temp
        angle += 90.0

    #we're gonna rotate the image opposite to angle, but cv2.getRotationMatrix2D() does counterclockwise, so we can just use angle as-is
    #but first we need to check that we're not putting it upside-down
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rot_blood_well_center = np.squeeze(cv2.transform(np.array([[blood_well_center]]), M))
    if rot_blood_well_center[1] < cy:
        angle += 180.0

    bbox = np.around([cx - 0.5 * w, cy - 0.5 * h, cx + 0.5 * w, cy + 0.5 * h]).astype('int64')
    return angle, (cx, cy), bbox

def parse_data(image_dir, xml_dir, rot_image_dir, info_dict_filename, require_blood_well_center, png_keys):
    if not os.path.exists(rot_image_dir):
        os.makedirs(rot_image_dir)

    require_blood_well_center = int(require_blood_well_center)
    png_keys = int(png_keys)

    #info_dict will be keyed by image basename WITHOUT extension
    #value will be dictionary with keys "bbox", and "line_ys"
    #"bbox" will be an upright bbox (xmin,ymin,xmax,ymax) in the space of the rotated whole image
    #"line_ys" will be dictionary mapping to line y-coordinates in the space of the rotated whole image
    #keys of that dictionary will be "C - Control" and "T - Test Line"
    #no strip-contraction or dividing in half. that comes later.
    info_dict = {}

    images = sorted(glob.glob(os.path.join(image_dir, '*.*')))
    for image in images:
        k = os.path.splitext(os.path.basename(image))[0]
        k_info = k
        if png_keys:
            k_info = k_info + '.png'

        xml_filename = os.path.join(xml_dir, k + '.xml')
        if not os.path.exists(xml_filename):
            print('!')
            continue

        bbox_poly, line_centers, blood_well_center, is_valid = parse_xml(xml_filename, require_blood_well_center)
        if not is_valid:
            print('?')
            continue

        angle, center, bbox = poly_to_rotrect(bbox_poly, blood_well_center)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        numI = cv2.imread(image)
        numIrot = cv2.warpAffine(numI, M, (numI.shape[1], numI.shape[0]))
        cv2.imwrite(os.path.join(rot_image_dir, k + '.png'), numIrot)
        line_ys = {}
        for kk in sorted(line_centers.keys()):
            line_ys[kk] = np.squeeze(cv2.transform(np.array([[line_centers[kk]]]), M))[1]

        info_dict[k_info] = {'bbox' : bbox, 'line_ys' : line_ys}

    with open(info_dict_filename, 'wb') as f:
        pickle.dump(info_dict, f)

def usage():
    print('Usage: python parse_data.py <image_dir> <xml_dir> <rot_image_dir> <info_dict_filename> <require_blood_well_center> <strip_well_extension>')

if __name__ == '__main__':
    parse_data(*(sys.argv[1:]))