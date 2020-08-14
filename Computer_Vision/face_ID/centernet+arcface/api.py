import cv2
import numpy as np
from PIL import ImageFile, Image
from centerface import CenterFace


net = CenterFace()

def ensure_cv(im):
    if type(im) == str:
        im = cv2.imread(im)
    elif isinstance(im, ImageFile.ImageFile):
        im = np.array(im)[:, :, :3]
        im = im[:, :, ::-1]
    return im

def detect(im):
    global net
    im = ensure_cv(im)
    h, w = im.shape[0:2]
    dets, lms = net(im, h, w, threshold=0.35)
    res = []
    for (det, lm) in zip(dets, lms):
        det = list(map(lambda x: round(x, 2), det))
        lm = list(map(lambda x: round(x, 2), lm))
        res.append([det, lm])
    return res


def align(im, tsize=128, desiredLeftEye=0.35):
    im = ensure_cv(im)
    res = detect(im)
    crop = []
    for (det, lm) in res:
        left_eye = lm[2:4]
        right_eye = lm[0:2]
        # compute the angle between the eye centroids
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # compute X distance, because we want to align the face
        # make it Y1 = Y2
        desiredRightEye = 1.0 - desiredLeftEye
        dist = np.sqrt((dX ** 2) + (dY ** 2))
        desiredDist = desiredRightEye - desiredLeftEye
        desiredDist *= tsize
        scale = desiredDist / dist

        eyesCenter = (left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2
        M = cv2.getRotationMatrix2D(eyesCenter, angle, scale)
        tX = tsize * 0.5
        tY = tsize * desiredLeftEye
        M[0, 2] += (tX - eyesCenter[0])
        M[1, 2] += (tY - eyesCenter[1])

        (w, h) = (tsize, tsize)
        output = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_CUBIC)
        crop.append(output)
    return crop,res