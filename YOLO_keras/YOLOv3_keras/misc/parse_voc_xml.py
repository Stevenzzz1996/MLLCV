# coding: utf-8

import xml.etree.ElementTree as ET
from tqdm import tqdm
import os

CurDir = os.getcwd()
RootDir = os.path.dirname(CurDir)
DataDir = os.path.join(RootDir, 'data')
VocDir = os.path.join(DataDir, 'VOCdevkit')
VOCdevkit_train_Dir = os.path.join(VocDir, 'VOCdevkit_train')
VOCdevkit_test_Dir = os.path.join(VocDir, 'VOCdevkit_test')

class_names_path = '../data/classes/circuit.names'
DatasetDir = '../data/dataset'

train_txt_path = DatasetDir + '/train.txt'
test_txt_path = DatasetDir + '/test.txt'

names_dict = {}

with open(class_names_path, 'r') as f:
    cnt = 0
    for line in f:
        line = line.strip()
        names_dict[line] = cnt
        cnt += 1


def parse_xml(img_path, path):
    tree = ET.parse(path)
    objects = [img_path]

    for obj in tree.findall('object'):
        name = ((obj.find('name').text).split())[0]
        if "\"" in name:
            name = name[1:]
        bbox = obj.find('bndbox')
        xmin = bbox.find('xmin').text
        ymin = bbox.find('ymin').text
        xmax = bbox.find('xmax').text
        ymax = bbox.find('ymax').text

        if int(xmin) > int(xmax):
            xmin, xmax = xmax, xmin

        if int(ymin) > int(ymax):
            ymin, ymax = ymax, ymin

        name = str(names_dict[name])
        box = ','.join([xmin, ymin, xmax, ymax, name])
        objects.append(box)
    if len(objects) > 1:
        return objects
    else:
        return None

def gen_txt(VOC_dir,txt_path):
    anno_dir = VOC_dir + '/Annotation'
    img_dir = VOC_dir + '/JPEGImages'
    lis_img = os.listdir(img_dir)
    copy_lis_img = lis_img.copy()
    for i, img in enumerate(copy_lis_img):
        lis_img[i] = img.strip().split('.')[0]

    with open(txt_path, 'w') as txt_file:
        for name in tqdm(lis_img):
            anno_path = anno_dir + '/' + name + '.xml'
            img_path = img_dir + '/' + name + '.jpg'
            objects = parse_xml(img_path, anno_path)
            objects_line = ' '.join(objects) + '\n'
            txt_file.write(objects_line)



train_cnt = 0
def parse_w_h_xml(img_path, path):
    global train_cnt
    tree = ET.parse(path)
    img_w = tree.findtext("./size/width")
    img_h = tree.findtext("./size/height")

    objects = [img_path, img_w, img_h]

    for obj in tree.findall('object'):
        name = ((obj.find('name').text).split())[0]
        if "\"" in name:
            name = name[1:]
        bbox = obj.find('bndbox')
        xmin = bbox.find('xmin').text
        ymin = bbox.find('ymin').text
        xmax = bbox.find('xmax').text
        ymax = bbox.find('ymax').text

        if int(xmin) > int(xmax):
            xmin, xmax = xmax, xmin

        if int(ymin) > int(ymax):
            ymin, ymax = ymax, ymin

        name = str(names_dict[name])
        box = ' '.join([name, xmin, ymin, xmax, ymax])
        objects.append(box)
    objects.insert(0, str(train_cnt))
    train_cnt += 1

    if len(objects) > 1:
        return objects
    else:
        return None

def gen_w_h_txt(VOC_dir,txt_path):
    anno_dir = VOC_dir + '/Annotation'
    img_dir = VOC_dir + '/JPEGImages'
    lis_img = os.listdir(img_dir)
    copy_lis_img = lis_img.copy()
    for i, img in enumerate(copy_lis_img):
        lis_img[i] = img[:-4]

    txt_file = open(txt_path, 'w')

    for name in tqdm(lis_img):
        anno_path = anno_dir + '/' + name + '.xml'
        img_path = img_dir + '/' + name + '.jpg'
        objects = parse_w_h_xml(img_path, anno_path)
        objects_line = ' '.join(objects) + '\n'
        txt_file.write(objects_line)

    txt_file.close()


gen_txt(VOCdevkit_train_Dir, train_txt_path)
gen_txt(VOCdevkit_test_Dir, test_txt_path)
gen_w_h_txt(VOCdevkit_train_Dir, DatasetDir + '/train_box.txt')
