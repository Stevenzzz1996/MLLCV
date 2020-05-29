import tensorflow as tf
from core.config import cfg
from test import test
import mAP.main as main_map
import os
import pickle
import shutil

class AutoLr(tf.keras.callbacks.Callback):
    def __init__(self, warmup_steps=100):
        super().__init__()
        self.is_continue = cfg.YOLO.TrainContinueFlag
        self.global_steps = 0
        self.warmup_steps = warmup_steps
        self.train_loss_list = []
        self.test_loss_list = []
        self.train_loss_save_dir = './plot/train_loss'
        self.test_loss_save_dir = './plot/test_loss'
        self.train_loss_save_path = self.train_loss_save_dir + '/train_loss.txt'
        self.test_loss_save_path = self.test_loss_save_dir + '/test_loss.txt'

    def on_train_begin(self,batch,logs={}):
        if self.is_continue:
            if os.path.exists(self.train_loss_save_path):
                with open(self.train_loss_save_path, 'rb') as train_loss_f:
                    self.train_loss_list = list(pickle.load(train_loss_f))
                    surplus = len(self.train_loss_list) % (cfg.TRAIN.ANNOT_SUM // cfg.TRAIN.BATCH_SIZE)
                    self.train_loss_list = self.train_loss_list[:-surplus]
                    self.global_steps = len(self.train_loss_list)

            if os.path.exists(self.test_loss_save_path):
                with open(self.test_loss_save_path, 'rb') as test_loss_f:
                    self.test_loss_list = pickle.load(test_loss_f)

            if not os.path.exists(self.train_loss_save_dir):
                os.mkdir(self.train_loss_save_dir)
            if not os.path.exists(self.test_loss_save_dir):
                os.mkdir(self.test_loss_save_dir)
        else:
            if os.path.exists(self.train_loss_save_dir):
                shutil.rmtree(self.train_loss_save_dir)
            if os.path.exists(self.test_loss_save_dir):
                shutil.rmtree(self.test_loss_save_dir)

            os.mkdir(self.train_loss_save_dir)
            os.mkdir(self.test_loss_save_dir)

    def on_batch_begin(self, batch, logs={}):
        self.global_steps += 1
        if self.global_steps < self.warmup_steps:
            lr = self.global_steps / self.warmup_steps * cfg.TRAIN.LR_INIT
        else:
            lr = cfg.TRAIN.LR_INIT - self.global_steps * (cfg.TRAIN.LR_INIT - cfg.TRAIN.LR_END) / (cfg.TRAIN.SUM_STEPS)

        tf.keras.backend.set_value(self.model.optimizer.lr, lr)

    def on_batch_end(self, batch, logs={}):
        self.train_loss_list.append(logs.get('loss'))
        with open(self.train_loss_save_path, 'wb') as train_loss_f:
            pickle.dump(self.train_loss_list, train_loss_f)

    def on_epoch_end(self, epoch, logs={}):
        self.test_loss_list.append(logs.get('val_loss'))
        with open(self.test_loss_save_path, 'wb') as test_loss_f:
            pickle.dump(self.test_loss_list, test_loss_f)

    def on_epoch_begin(self, epoch, logs={}):
        print('learning_rate:', (tf.keras.backend.get_value(self.model.optimizer.lr)))

class MAP(tf.keras.callbacks.Callback):
    def __init__(self):
        super().__init__()
        self.is_continue = cfg.YOLO.TrainContinueFlag
        self.mAP_list = []
        self.map_list_save_dir = './plot/mAP'
        self.map_list_save_path = self.map_list_save_dir + '/map.txt'
        self.count_epochs = 0

    def on_train_begin(self, epoch, logs={}):
        if self.is_continue:
            if os.path.exists(self.map_list_save_path):
                with open(self.map_list_save_path, 'rb') as mAP_f:
                    self.mAP_list = pickle.load(mAP_f)
            if not os.path.exists(self.map_list_save_dir):
                os.mkdir(self.map_list_save_dir)
        else:
            if os.path.exists(self.map_list_save_dir):
                shutil.rmtree(self.map_list_save_dir)
            os.mkdir(self.map_list_save_dir)

    def on_epoch_end(self, epoch, logs={}):
        self.count_epochs += 1
        if self.count_epochs % 1 == 0:
            test(self.model, 0.3, draw_boxes=False)
            mAp = main_map.get_map()
            print(mAp)
            self.mAP_list.append(mAp)
            with open(self.map_list_save_path, 'wb') as map_f:
                pickle.dump(self.mAP_list, map_f)




class SelfModelCheckPoint(tf.keras.callbacks.Callback):
    def __init__(self, save_path, vl_baseline=5):
        super().__init__()
        self.save_path = save_path
        self.vl_baseline = vl_baseline
        self.is_continue = cfg.YOLO.TrainContinueFlag
        self.test_loss_list = []
        self.test_loss_save_dir = './plot/test_loss'
        self.test_loss_save_path = self.test_loss_save_dir + '/test_loss.txt'

    def on_train_epoch(self):
        if(self.is_continue):
            if os.path.exists(self.test_loss_save_path):
                with open(self.test_loss_save_path, 'rb') as test_loss_f:
                    self.test_loss_list = pickle.load(test_loss_f)
                    self.vl_baseline = self.test_loss_list[-1]

    def on_epoch_end(self, batch, logs={}):
        print("")
        if self.vl_baseline > logs.get('val_loss'):
            print('val_loss  improve from ', self.vl_baseline, ' to ', logs.get('val_loss'))
            self.vl_baseline = logs.get('val_loss')
            self.model.save_weights(self.save_path)
        else:
            print('val_loss did not improve from ', self.vl_baseline)


