# import tqdm
# with open('C:/Users/24991/Desktop/YOLOV3/data/dataset/train.txt','r+') as f:
#     data = f.readlines()
#     for i in range(len(data)):
#         datai = data[i].split(' ')
#         # print(datai)
#         # 如果存在0就写入
#         persondata = []
#         len(persondata)
#         for t in range(1,len(datai)): #一行中的数据,只选取person部分
#             # if datai[t].split(',')[4] == 0:
#             #     #persondata = str(datai[t])
#             #     #persondata = []
#             #     print(datai[t])
#                 # persondata.append(datai[t])
#             #print(persondata)
#             data_person_per = datai[t].split(',')
#             # print(datai[t],data_person_per[4])
#             if int(data_person_per[4]) == 0:
#                 persondata.append(datai[t])
#         #print(len(persondata))
#
#         if int(len(persondata))>0:
#             #print(len(persondata))
#             anchor = ''
#             for i in range(len(persondata)):
#                 strdata = str(persondata[i]) +' '
#                 if strdata != ' ':
#                     anchor+= strdata
#             all = str(datai[0] +' '+anchor)
#             if  all.strip():
#                 with open('new_data.txt', 'a') as file_handle:  # .txt可以不自己新建,代码会自动新建
#                     file_handle.write(all)  # 写入
#                     file_handle.write('\n')


# def delblankline(infile, outfile):
#     infopen = open(infile, 'r', encoding="utf-8")
#     outfopen = open(outfile, 'w', encoding="utf-8")
#
#     lines = infopen.readlines()
#     for line in lines:
#         line = line.strip()
#         if len(line) != 0:
#             outfopen.writelines(line)
#             outfopen.write('\n')
#     infopen.close()
#     outfopen.close()
#
#
# delblankline("train2.txt", "train3.txt")


# infopen = open('C:/Users/24991/Desktop/YOLOV3/data/dataset/train1.txt', 'r', encoding="utf-8")
# outfopen = open('C:/Users/24991/Desktop/YOLOV3/data/dataset/train2.txt', 'w', encoding="utf-8")
# lines = infopen.readlines()
# for line in lines:
#     line = line.split(' ')
#     anchor_data = line[1:]
#     # print(anchor_data)
#     anchor_data_line = str()
#     for i in range(len(anchor_data)):
#         anchor_classfication = anchor_data[i].split(',')[4]
#         anchor_information = anchor_data[i].split(',')[0:4]
#         xmin = anchor_information[0]
#         ymin = anchor_information[1]
#         xmax = anchor_information[2]
#         ymax = anchor_information[3]
#         classes = 1
#         anchor_base = ' ' + ','.join(map(str,[xmin,ymin,xmax,ymax,classes]))
#         anchor_data_line+=anchor_base
#     all_data= str(line[0])+str(anchor_data_line)
#     outfopen.writelines(all_data)
#     outfopen.write('\n')



infopen = open('C:/Users/24991/Desktop/YOLOV3/data/dataset/train2.txt', 'r', encoding="utf-8")
outfopen = open('C:/Users/24991/Desktop/YOLOV3/data/dataset/train4.txt', 'w', encoding="utf-8")
lines = infopen.readlines()
for line in lines:
    line = line.split(' ')
    server_path = '/media/psdz/data3/pub_data/data/urun_tandong_video/data/COCO/images/train2017/'
    path_line = line[0].split('/')
    #print(path_line[5])
    anchor_data = line[1:]
    last_path  = server_path+str(path_line[5])
    # print(anchor_data)
    anchor_data_line = str()
    for i in range(len(anchor_data)):
        anchor_classfication = anchor_data[i].split(',')[4]
        anchor_information = anchor_data[i].split(',')[0:4]
        xmin = anchor_information[0]
        ymin = anchor_information[1]
        xmax = anchor_information[2]
        ymax = anchor_information[3]
        classes = 0
        anchor_base = ' ' + ','.join(map(str,[xmin,ymin,xmax,ymax,classes]))
        anchor_data_line+=anchor_base
    all_data= str(last_path)+str(anchor_data_line)
    print(all_data)
    outfopen.writelines(all_data)
    outfopen.write('\n')


