import numpy as np
import cv2
import matplotlib.pyplot as plt

# 160 derece kamera parametreleri


def undistort(img_path):

    DIM=(640, 480)
    K=np.array([[313.6350493564022, 0.0, 320.71730392592855], [0.0, 312.0775867365282, 229.1132293785942], [0.0, 0.0, 1.0]])
    D=np.array([[-0.07412526103660831], [0.12135574435333629], [-0.0968640232098603], [0.0019216678167765422]])
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    

    return undistorted_img
