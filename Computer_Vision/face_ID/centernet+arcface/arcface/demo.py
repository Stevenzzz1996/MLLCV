import cv2
import pcn
import arcface
import numpy as np
from random import choices
from imutils import paths


directory = 'examples'
images = list(paths.list_files(directory))


def random_select():
    global images
    imgs = choices(images, k=2)
    return imgs

def crop_face(img):
    # NOTE: demo purpose: only the first face will be cropped!
    winlist = pcn.detect(img)
    crops = pcn.crop(img, winlist, 128) # input of net is 1x128x128
    face = crops[0]
    return face


if __name__ == '__main__':
    img1, img2 = random_select()

    img1 = cv2.imread(img1)
    img2 = cv2.imread(img2)

    face1 = crop_face(img1)
    face2 = crop_face(img2)

    fe1 = arcface.featurize(face1)
    fe2 = arcface.featurize(face2)

    similar = arcface.compare(fe1, fe2)

    canvas = np.hstack((face1, face2))
    # bottom = np.full((20, 256, 3), (0, 0, 0))
    same = 'Yes' if similar > arcface.threshold else 'No'
    comments = f'Similarity: {similar:.3f}  Same Person?: {same}'
    # cv2.putText(bottom, comments, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
    print(comments)

    # canvas = np.vstack((canvas, bottom)) 
    canvas = canvas.astype(np.uint8)
    cv2.imshow("ArcFace Demo", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()