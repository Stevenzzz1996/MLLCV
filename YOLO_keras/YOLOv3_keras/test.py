import cv2
import os
import shutil
import numpy as np
import tensorflow as tf
import core.utils as utils
from core.config import cfg
import timeit
import random


def test(model, SCORE_THRESHOLD,draw_boxes=False):

    INPUT_SIZE = 416
    CLASSES = utils.read_class_names(cfg.YOLO.CLASSES)

    # TODO cups:改动部分使用TODO标记
    predicted_dir_path = "./mAP/predicted"
    ground_truth_dir_path = "./mAP/ground-truth"
    if os.path.exists(predicted_dir_path):
        shutil.rmtree(predicted_dir_path)
    if os.path.exists(ground_truth_dir_path):
        shutil.rmtree(ground_truth_dir_path)
    if os.path.exists(cfg.TEST.DECTECTED_IMAGE_PATH):
        shutil.rmtree(cfg.TEST.DECTECTED_IMAGE_PATH)

    os.mkdir(cfg.TEST.DECTECTED_IMAGE_PATH)
    os.mkdir(predicted_dir_path)
    os.mkdir(ground_truth_dir_path)

    # import show_tools
    time_sum = 0
    with open(cfg.TEST.ANNOT_PATH, "r") as annotation_file:
        ori_list = annotation_file.readlines()
        '''
        ori_fifty_list = ori_list[-50:]
        other_list = ori_list[:-50]
        other_25_list = random.choices(other_list, k=25)
        annotation_file_list = ori_fifty_list + other_25_list
        '''
        test_sum = len(ori_list)
        print("test " + str(test_sum) + " pictures")
        j = "|"
        k = "="
        kong = " "
        for num, line in enumerate(ori_list):
            # show_tools.view_bar('image_enhancement', num, len(annotation_file.readlines()))
            annotation = line.strip().split()
            image_path = annotation[0]
            image_name = image_path.split("/")[-1]
            img_name = image_name.split(".")[0]

            bbox_data_gt = np.array(
                [list(map(int, box.split(","))) for box in annotation[1:]],dtype = np.int16
            )
            if len(bbox_data_gt) == 0:
                bboxes_gt = []
                classes_gt = []
            else:
                bboxes_gt, classes_gt = bbox_data_gt[:, :4], bbox_data_gt[:, 4]
            ground_truth_path = os.path.join(ground_truth_dir_path, img_name + ".txt")
            # TODO cups
            # print('=> ground truth of %s:' % image_name)
            num_bbox_gt = len(bboxes_gt)
            with open(ground_truth_path, "w") as f:
                for i in range(num_bbox_gt):
                    class_name = CLASSES[classes_gt[i]-1]
                    xmin, ymin, xmax, ymax = list(map(str, bboxes_gt[i]))
                    bbox_mess = " ".join([class_name, xmin, ymin, xmax, ymax]) + "\n"
                    f.write(bbox_mess)

            # TODO cups
            # print('=> predict result of %s:' % image_name)
            predict_result_path = os.path.join(predicted_dir_path, img_name + ".txt")
            # Predict Process
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_size = image.shape[:2]
            image_data = utils.image_preporcess(
                np.copy(image), [INPUT_SIZE, INPUT_SIZE]
            )

            image_data = image_data[np.newaxis, ...].astype(np.float32)


            predict_model = tf.keras.Model(inputs=model.get_layer('input_1').input,
                                           outputs=[model.get_layer('tf_op_layer_concat_4').output,
                                                    model.get_layer('tf_op_layer_concat_7').output,
                                                    model.get_layer('tf_op_layer_concat_10').output])
            start = timeit.default_timer()
            pred_bbox = predict_model(image_data)

            pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
            pred_bbox = tf.concat(pred_bbox, axis=0)
            bboxes = utils.postprocess_boxes(
                pred_bbox, image_size, INPUT_SIZE, SCORE_THRESHOLD
            )

            bboxes = utils.nms(bboxes, cfg.TEST.IOU_THRESHOLD, method="nms")


            end = timeit.default_timer()
            time_sum += end - start

            if cfg.TEST.DECTECTED_IMAGE_PATH is not None and draw_boxes == True:
                image = utils.draw_bbox(image, bboxes)
                cv2.imwrite(cfg.TEST.DECTECTED_IMAGE_PATH + image_name, image)

            with open(predict_result_path, "w") as f:
                for bbox in bboxes:

                    coor = np.array(bbox[:4], dtype=np.int32)
                    score = bbox[4]
                    class_ind = int(bbox[5])
                    class_name = CLASSES[class_ind]
                    score = "%.4f" % score
                    xmin, ymin, xmax, ymax = list(map(str, coor))
                    bbox_mess = (
                        " ".join([class_name, score, xmin, ymin, xmax, ymax]) + "\n"
                    )
                    f.write(bbox_mess)

            final_str = j + k*(int((num+1)/3)+1) + ">" + kong*(int((test_sum-1-num)/3)) + "| %d" % (int((num+1)/test_sum * 100)) + "%"
            print(final_str, end='\r')
    print("")
    print("average consume time:", time_sum/(num+1))
    print("test predit done")
