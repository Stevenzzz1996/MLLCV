import os

import cv2
import torch
import numpy as np

from .models import resnet_face18

threshold = 0.4
device = 'cuda' if torch.cuda.is_available() else 'cpu'
'''
1.模型调用
2.余弦距离
3.阈值设定
'''
def load_model():
    cwd = os.path.dirname(__file__)
    net = resnet_face18(use_se=False)
    net = torch.nn.DataParallel(net)
    weights = torch.load(os.path.join(cwd, 'resnet18_110.pth'), map_location=device)
    net.load_state_dict(weights)
    net = net.to(device)
    net.eval()
    return net

net = load_model()

def load_image(image):
    if type(image) == str:
        image = cv2.imread(image)
    image = cv2.resize(image, (128, 128))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = np.dstack((image, np.fliplr(image)))
    image = image.transpose((2, 0, 1))
    image = image[:, np.newaxis, :, :]
    image = image.astype(np.float32, copy=False)
    image -= 127.5
    image /= 127.5
    return image


def cosin_metric(x1, x2):
    return np.dot(x1, x2) / (np.linalg.norm(x1) * np.linalg.norm(x2))


def featurize(image):
    """transform an image into vector-representation format

    Args:
        image: numpy-format image or str

    Returns:
        a 1024-dimension embedding of input face
    """
    image = load_image(image)
    image = torch.from_numpy(image).to(device)
    with torch.no_grad():
        feature = net(image)
    feature = feature.numpy() if device == 'cpu' else feature.cpu().numpy()
    fe1 = feature[::2]
    fe2 = feature[1::2]
    feature = np.hstack([fe1, fe2]).squeeze()
    return feature


def compare(f1, f2):
    """compare two faces or two features
    Args:
        f1: face feature vector 1
        f2: face feature vector 2
    Returns:
        face distance
    """
    return cosin_metric(f1, f2)
