from easydict import EasyDict as edict


__C                           = edict()
# Consumers can get config by: from config import cfg

cfg                           = __C

# YOLO options
__C.YOLO                      = edict()

# Set the class name
__C.YOLO.CLASSES              = "C:/Users/24991/Desktop/YOLO_keras/YOLO_keras/YOLOv3_keras/data/classes/circuit.names"
__C.YOLO.ANCHORS              = "C:/Users/24991/Desktop/YOLO_keras/YOLO_keras/YOLOv3_keras/data/anchors/circuit_anchors.txt"
__C.YOLO.STRIDES              = [8, 16, 32]
__C.YOLO.ANCHOR_PER_SCALE     = 3
__C.YOLO.IOU_LOSS_THRESH      = 0.5
__C.YOLO.TrainContinueFlag    = False

# Train options
__C.TRAIN                     = edict()


__C.TRAIN.ANNOT_PATH          = "C:/Users/24991/Desktop/YOLO_keras/YOLO_keras/YOLOv3_keras/data/datasets/new_data.txt"
__C.TRAIN.ANNOT_SUM           = 125
__C.TRAIN.BATCH_SIZE          = 4
# __C.TRAIN.INPUT_SIZE            = [320, 352, 384, 416, 448, 480, 512, 544, 576, 608]
__C.TRAIN.INPUT_SIZE          = [416]
__C.TRAIN.DATA_AUG            = True
__C.TRAIN.LR_INIT             = 1e-4
__C.TRAIN.LR_END              = 1e-6
__C.TRAIN.WARMUP_EPOCHS       = 10
__C.TRAIN.SUM_STEPS           = 70000
__C.TRAIN.EPOCHS              = __C.TRAIN.SUM_STEPS // (__C.TRAIN.ANNOT_SUM // __C.TRAIN.BATCH_SIZE) - __C.TRAIN.WARMUP_EPOCHS



# TEST options
__C.TEST                      = edict()

__C.TEST.ANNOT_PATH           = "C:/Users/24991/Desktop/YOLO_keras/YOLO_keras/YOLOv3_keras/data/datasets/new_data.txt"
__C.TEST.BATCH_SIZE           = 4
__C.TEST.INPUT_SIZE           = [416]
__C.TEST.DATA_AUG             = False
__C.TEST.DECTECTED_IMAGE_PATH = "./data/detection"
__C.TEST.SCORE_THRESHOLD      = 0.3
__C.TEST.IOU_THRESHOLD        = 0.45


