import os
import tensorflow as tf
from core.yolov3 import YOLOv3, decode, compute_loss
import test as ts
import mAP.main as main_map
import matplotlib.pyplot as plt
import numpy as np
import pickle
import shutil
from mAP.sum_pr import sumpr
from mAP.main import get_map
from train import create_model
import tqdm

color_list=['#ffc0cb', '#c71585', '#ff00ff', '#4b0082', '#e6e6fa', '#00008b', '#708090', '#4682b4', '#5f9ea0', '#00ffff',
            '#008b8b', '#40e0e0', '#00ff7f', '#00ff00', '#adff2f', '#ffffe0', '#f0e68c', '#2e8b57', '#f5deb3', '#ffdead',
            '#faf0e6', '#fff5ee', '#e9967a', '#800000', '#dcdcdc', '#808080', '#000000', '#7cfc00', '#cd5c5c']


CurDir = os.path.join(os.getcwd())
MapPath = os.path.join(CurDir, 'plot', 'mAP', 'map.txt')
FigsDir = os.path.join(CurDir, 'plot', 'figs')
'''
if os.path.exists(FigsDir):
    shutil.rmtree(FigsDir)
os.mkdir(FigsDir)
'''

def plot_map():
    map_fig_path = os.path.join(FigsDir, 'map')
    with open(MapPath, 'rb') as map_f:
        map_list = pickle.load(map_f)
        #print(type(map_list))
        x_axis = list(range(len(map_list)))
        plt.figure(num='mAP–train steps curve')
        plt.title('mAP–train steps curve')
        plt.xlabel('Epochs')
        plt.ylabel('mAP')
        y = [x/10 for x in range(11)]
        plt.plot(x_axis, map_list, 'r-')
        plt.axis([0, 50, 0, 1])
        plt.yticks(y)
        plt.savefig(map_fig_path)

TrainLossPath = os.path.join(CurDir, 'plot', 'train_loss', 'train_loss.txt')

def plot_train_loss():
    train_loss_fig_path = os.path.join(FigsDir, 'train_loss')
    with open(TrainLossPath, 'rb') as train_map_f:
        train_loss_list = pickle.load(train_map_f)
        train_x_axis = list(range(len(train_loss_list)))
        plt.figure(num='Loss–train step curve')
        plt.title('Loss–train step curve')
        plt.xlabel('Training steps')
        plt.ylabel('Loss')
        plt.plot(train_x_axis, train_loss_list, 'b-')
        plt.savefig(train_loss_fig_path)

TestLossPath = os.path.join(CurDir, 'plot', 'test_loss', 'test_loss.txt')
def plot_test_loss():
    test_loss_fig_path = os.path.join(FigsDir, 'test_loss')
    with open(TestLossPath, 'rb') as test_map_f:
        test_loss_list = pickle.load(test_map_f)
        test_x_axis = list(range(len(test_loss_list)))
        plt.figure(num='Loss–train step curve')
        plt.title('Loss–train step curve')
        plt.xlabel('Testing epochs')
        plt.ylabel('Loss')
        plt.plot(test_x_axis, test_loss_list, 'r-')
        plt.savefig(test_loss_fig_path)


results_path = os.path.join(CurDir, 'mAp', 'results', 'results.txt')
def plot_pr():
    pr_fig_path = os.path.join(FigsDir, 'pr')
    with open(results_path, 'r') as results_f:
        results_data = results_f.readlines()
        indexes = []
        for i, line in enumerate(results_data):
            if line.find('#') > -1:
                indexes.append(i)
            if len(indexes) >= 2:
                break

    pr_data = results_data[1:indexes[1]-1]

    plt.figure(num='Precision–recall curve')
    plt.title('Precision–recall curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    color_index = 0
    for j, data in enumerate(pr_data):
        if data.find('=') > -1:
            class_line = data
            pre_line = pr_data[j+1]
            re_line = pr_data[j+2]

            class_name = (class_line.strip().split(' '))[2]


            pre_str = (pre_line.strip().replace(']', '').split('['))[1]
            pre_str_list = (pre_str.replace('\'', '').replace(' ', '')).split(',')
            pre_int_list = [float(x) for x in pre_str_list]

            re_str = (re_line.strip().replace(']', '').split('['))[1]
            re_str_list = (re_str.replace("'", '').replace(' ', '')).split(',')
            re_int_list = [float(x) for x in re_str_list]

            plt.plot(re_int_list, pre_int_list, color=color_list[color_index], label=class_name)
            color_index += 1

    plt.legend()
    plt.savefig(pr_fig_path)



'''搭建模型'''
'''
model = create_model()
weights_path = os.path.join(CurDir, 'model', "yolov3.weights")
model.load_weights(weights_path)
model.summary()
'''

def plot_class_precision():
    # 得到#号的行
    with open(results_path, 'r') as results_f:
        results_data = results_f.readlines()
        indexes = []
        for i, line in enumerate(results_data):
            if line.find('#') > -1:
                indexes.append(i)

    map_line = results_data[indexes[1] + 1]

    class_list = []
    for d in results_data:
        if d.find('tp') > -1:
            class_precision_list = []
            d_ = d.strip().replace(' ', '').replace('(', '#').replace(',', '#').replace(')', '').split('#')
            d_0 = d_[0].split(':')
            d_1 = d_[1].split(':')

            class_precision_list.append(d_0[0])
            class_precision_list.append(float(d_1[1]) / float(d_0[1]))
            class_list.append(class_precision_list)

    class_list.sort(key=lambda x: x[1], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    class_str_list = [x[0] for x in class_list]


    y_pos = np.arange(len(class_str_list))


    performance = [x[1] for x in class_list]

    rects = ax.barh(y_pos, performance, color='gold', align="center")

    ax.set_yticks(y_pos)  # 设置标度的位置

    ax.set_yticklabels(class_str_list)  # 设置纵坐标的每一个刻度的属性值

    ax.invert_yaxis()  # 反转标度值

    ax.set_xlabel('Precision', size=20)  # 设置横坐标的单位

    ax.set_title(map_line, size=20)  # 设定图片的标题


    # show the number in the top of the bar
    for rect, y, num in zip(rects, y_pos, performance):
        x = rect.get_width()
        plt.text(x + 0.005, y, "%.2f" % num)

    pmap_fig_path = os.path.join(FigsDir, 'pmap')
    plt.savefig(pmap_fig_path)


def get_acc_pre_rec(model, points=100):
    acc_list = []
    threshold_list = []
    precision_list = []
    recall_list = []
    for SCORE_THRESHOLD in tqdm.tqdm(range(1, points)):
        ts.test(model, SCORE_THRESHOLD / points)
        main_map.get_map()
        threshold_list.append(float(SCORE_THRESHOLD / points))
        # 得到#号的行
        with open(results_path, 'r') as results_f:
            results_data = results_f.readlines()
            indexes = []
            for i, line in enumerate(results_data):
                if line.find('#') > -1:
                    indexes.append(i)

        #统计gt的个数
        gt_obj_name_all = {}
        for i in range(len(results_data)):
            if i > indexes[2] and i < (indexes[3] - 1):
                d = results_data[i].strip().replace(' ', '').split(':')
                gt_obj_name_all[d[0]] = int(d[1])

            if i >= indexes[3]: break

        gt_num_list = list(gt_obj_name_all.values())
        gt_num = np.sum(gt_num_list)

        # print('测试集中的所有样本数据：', obj_name_all)
        # 读取fp，fp；计算R-P值
        predict_correct = 0
        predict_sum = 0
        for d in results_data:
            if d.find('tp') > -1:
                d_ = d.strip().replace(' ', '').replace('(', '#').replace(',', '#').replace(')', '').split('#')
                d_0 = d_[0].split(':')
                d_1 = d_[1].split(':')
                predict_sum += int(d_0[1])
                predict_correct += int(d_1[1])

        acc = float(predict_correct / gt_num)
        precision = float(predict_correct / predict_sum)
        recall = float(predict_correct / gt_num)
        acc_list.append(acc)
        precision_list.append(precision)
        recall_list.append(recall)

    return threshold_list, acc_list, precision_list, recall_list

def plot_acc(threshold_list, acc_list):
    acc_fig_path = os.path.join(FigsDir, 'acc')
    plt.figure(num='Accuracy–threshold curve')
    plt.title('Accuracy–threshold curve')
    plt.xlabel('Threshold')
    plt.ylabel('Accuracy')
    plt.axis([0, 1, 0, 1])
    plt.plot(threshold_list, acc_list, 'r-')
    plt.savefig(acc_fig_path)

def plot_precision(threshold_list, precision_list):
    pre_fig_path = os.path.join(FigsDir, 'precision')
    plt.figure(num='Precision–threshold curve')
    plt.title('Precision–threshold curve')
    plt.xlabel('Threshold')
    plt.ylabel('Precision')
    plt.axis([0, 1, 0, 1])
    plt.plot(threshold_list, precision_list, 'r-')
    plt.savefig(pre_fig_path)

def plot_recall(threshold_list, recall_list):
    pre_fig_path = os.path.join(FigsDir, 'recall')
    plt.figure(num='Recall–threshold curve')
    plt.title('Recall–threshold curve')
    plt.xlabel('Threshold')
    plt.ylabel('Recall')
    plt.axis([0, 1, 0, 1])
    plt.plot(threshold_list, recall_list, 'r-')
    plt.savefig(pre_fig_path)


if __name__ == '__main__':
    create = True
    if create:
        model = create_model()
        weights_path = os.path.join(CurDir, 'model', "yolov3.weights")
        model.load_weights(weights_path)
        model.summary()
        ts.test(model, 0.3, draw_boxes=False)

    print(get_map())
    plot_class_precision()
    '''
    plot_map()
    plot_train_loss()
    plot_test_loss()
    ts.test(model, 0.3, draw_boxes=True)
    print(get_map())
    plot_class_precision()
    sumpr()

    threshold_list, acc_list, precision_list, recall_list = get_acc_pre_rec(model, points=10)
    plot_acc(threshold_list, acc_list)
    plot_precision(threshold_list, precision_list)
    plot_recall(threshold_list, recall_list)
    '''



