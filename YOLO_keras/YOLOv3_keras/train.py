import os
import numpy as np
import tensorflow as tf
from core.dataset import Dataset
from core.yolov3 import YOLOv3, decode, compute_loss
from core.config import cfg
from callbacks import AutoLr, MAP, SelfModelCheckPoint
import shutil
import pickle



def yolo_loss(args):

    pred_result = args[:6]
    target = args[6]

    giou_loss = conf_loss = prob_loss = 0
    for i in range(3):
        conv, pred = pred_result[i * 2], pred_result[i * 2 + 1]
        target1, target2 = target[i * 2], target[i * 2 + 1]
        loss_items = compute_loss(pred, conv, target1, target2, i)
        giou_loss += loss_items[0]
        conf_loss += loss_items[1]
        prob_loss += loss_items[2]

    total_loss = (giou_loss + conf_loss + prob_loss)/3
    #print('')
    #print('giou_loss:{}, conf_loss:{}, prob_loss:{}'.format(giou_loss, conf_loss, prob_loss))
    total_loss = tf.convert_to_tensor([total_loss])
    return total_loss

def create_model(anchor_per_scale=3, num_classes=1, max_bbox_per_scale=150):
    input_tensor = tf.keras.layers.Input([416, 416, 3])
    conv_tensors = YOLOv3(input_tensor)

    output_tensors = []
    for i, conv_tensor in enumerate(conv_tensors):
        pred_tensor = decode(conv_tensor, i)
        output_tensors.append(conv_tensor)
        output_tensors.append(pred_tensor)

    model_body = tf.keras.Model(input_tensor, output_tensors)

    train_output_sizes = 416 // np.array(cfg.YOLO.STRIDES)
    batch_label_sbbox = tf.keras.layers.Input((train_output_sizes[0], train_output_sizes[0],
                                               anchor_per_scale, 5 + num_classes), dtype=np.float32)
    batch_label_mbbox = tf.keras.layers.Input((train_output_sizes[1], train_output_sizes[1],
                                               anchor_per_scale, 5 + num_classes), dtype=np.float32)
    batch_label_lbbox = tf.keras.layers.Input((train_output_sizes[2], train_output_sizes[2],
                                               anchor_per_scale, 5 + num_classes), dtype=np.float32)

    batch_sbboxes = tf.keras.layers.Input((max_bbox_per_scale, 4), dtype=np.float32)
    batch_mbboxes = tf.keras.layers.Input((max_bbox_per_scale, 4), dtype=np.float32)
    batch_lbboxes = tf.keras.layers.Input((max_bbox_per_scale, 4), dtype=np.float32)

    target = [batch_label_sbbox, batch_sbboxes, batch_label_mbbox, batch_mbboxes,
              batch_label_lbbox, batch_lbboxes]

    model_loss = tf.keras.layers.Lambda(yolo_loss, output_shape=(1,), name='yolo_loss')([*model_body.output, target])

    new_model = tf.keras.Model([model_body.input, *target], model_loss)


    return new_model

if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    trainset = Dataset('train')
    testset = Dataset('test')
    train_steps = len(trainset)
    val_steps = len(testset)

    #model_name = 'YOLOv3_245-{}'.format(int(time.time()))

    warmup_steps = cfg.TRAIN.WARMUP_EPOCHS * train_steps            #2 epoches
    train_epochs = cfg.TRAIN.WARMUP_EPOCHS + cfg.TRAIN.EPOCHS

    total_steps = train_epochs * train_steps                     #30 epoche

    CurDir = os.getcwd()
    model_dir = os.path.join(CurDir, 'model')
    if not cfg.YOLO.TrainContinueFlag:
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        os.mkdir(model_dir)


    model_path = os.path.join(model_dir, 'yolov3.weights')

    model = create_model()
    if os.path.exists(os.path.join(model_dir, 'checkpoint')):
        model.load_weights(model_path)
        print('loaded!')
    model.summary()

    model.compile(optimizer=tf.keras.optimizers.Adam(lr=cfg.TRAIN.LR_INIT), loss={'yolo_loss': lambda y_true, y_pred: y_pred})

    auto_lr = AutoLr(warmup_steps)
    mAP = MAP()
    checkpoint = SelfModelCheckPoint(model_path, 10000)

    callbacks = [auto_lr, checkpoint, mAP]

    if not cfg.YOLO.TrainContinueFlag:
        model.fit(trainset.loda_data(), epochs=train_epochs, steps_per_epoch=train_steps,
                            validation_data=testset.loda_data(), validation_steps=val_steps,
                            callbacks=callbacks)
    else:
        test_loss_save_dir = './plot/test_loss'
        test_loss_save_path = test_loss_save_dir + '/test_loss.txt'
        if os.path.exists(test_loss_save_path):
            with open(test_loss_save_path, 'rb') as test_loss_f:
                test_loss_list = pickle.load(test_loss_f)
                current_epochs = len(test_loss_list)

            model.fit(trainset.loda_data(), epochs=(train_epochs),
                                initial_epoch=current_epochs, steps_per_epoch=train_steps,
                                validation_data=testset.loda_data(), validation_steps=val_steps,
                                callbacks=callbacks)
        else:
            model.fit(trainset.loda_data(), epochs=train_epochs, steps_per_epoch=train_steps,
                                validation_data=testset.loda_data(), validation_steps=val_steps,
                                callbacks=callbacks)



