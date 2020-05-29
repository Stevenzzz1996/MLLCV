from core.dataset import Dataset
import tensorflow as tf
import core.utils as utils
from core.config import cfg
import tqdm
import cv2


draw_dataset = Dataset('train')
data_product = draw_dataset.loda_data()
for i in tqdm.tqdm(range(10)):
    get = next(data_product)
    get = get[0]
    label = get[1]
    print(label[].shape)
    assert 0
    pred_bbox = list([label[0], label[1], label[2]])
    image_size = get[2]
    image = get[3]
    pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
    pred_bbox = tf.concat(pred_bbox, axis=0)
    bboxes = utils.postprocess_boxes(
                    pred_bbox, image_size, 416, 0.3
                )

    bboxes = utils.nms(bboxes, cfg.TEST.IOU_THRESHOLD, method="nms")
    image = utils.draw_bbox(image, bboxes)
    cv2.imwrite(str(i)+'.jpg', image)