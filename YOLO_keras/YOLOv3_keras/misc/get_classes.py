import os
import glob
import xml.etree.cElementTree as ET
from tqdm import tqdm

CurDir = os.getcwd()
RootDir = os.path.dirname(CurDir)
DataDir = os.path.join(RootDir, 'data')
VocDir = os.path.join(DataDir, 'VOCdevkit')
Vocdevkit_trainDir = os.path.join(VocDir, 'VOCdevkit_test')
Vocdevkit_train_anno_Dir = os.path.join(Vocdevkit_trainDir, 'Annotation')

ClassDir = os.path.join(DataDir, 'classes')
if not os.path.exists(ClassDir):
    os.mkdir(ClassDir)

ClassPath = os.path.join(ClassDir, 'circuit.names')
lis_class_names = []
lis_train_xml_path = glob.glob(Vocdevkit_train_anno_Dir + '/*.xml')
with open(ClassPath, 'w') as class_file:
    for xml_path in tqdm(lis_train_xml_path):
        tree = ET.parse(xml_path)

        for obj in tree.findall('object'):
            name = obj.find('name').text
            if "\"" in name:
                name = name.replace('\"', "")
            name = (name.split())[0] + '\n'
            if name not in lis_class_names:
                lis_class_names.append(name)
    class_file.writelines(lis_class_names)

print(len(lis_class_names))