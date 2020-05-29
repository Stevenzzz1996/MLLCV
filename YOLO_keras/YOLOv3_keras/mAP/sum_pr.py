import os
import pickle
import glob
import shutil
import matplotlib.pyplot as plt

def voc_ap(rec, prec):
  """
  --- Official matlab code VOC2012---
  mrec=[0 ; rec ; 1];
  mpre=[0 ; prec ; 0];
  for i=numel(mpre)-1:-1:1
      mpre(i)=max(mpre(i),mpre(i+1));
  end
  i=find(mrec(2:end)~=mrec(1:end-1))+1;
  ap=sum((mrec(i)-mrec(i-1)).*mpre(i));
  """
  rec.insert(0, 0.0)  # insert 0.0 at begining of list
  rec.append(1.0)  # insert 1.0 at end of list
  mrec = rec[:]
  prec.insert(0, 0.0)  # insert 0.0 at begining of list
  prec.append(0.0)  # insert 0.0 at end of list
  mpre = prec[:]
  """
   This part makes the precision monotonically decreasing
    (goes from the end to the beginning)
    matlab:  for i=numel(mpre)-1:-1:1
                mpre(i)=max(mpre(i),mpre(i+1));
  """
  # matlab indexes start in 1 but python in 0, so I have to do:
  #   range(start=(len(mpre) - 2), end=0, step=-1)
  # also the python function range excludes the end, resulting in:
  #   range(start=(len(mpre) - 2), end=-1, step=-1)
  for i in range(len(mpre) - 2, -1, -1):
    mpre[i] = max(mpre[i], mpre[i + 1])
  """
   This part creates a list of indexes where the recall changes
    matlab:  i=find(mrec(2:end)~=mrec(1:end-1))+1;
  """
  i_list = []
  for i in range(1, len(mrec)):
    if mrec[i] != mrec[i - 1]:
      i_list.append(i)  # if it was matlab would be i + 1
  """
   The Average Precision (AP) is the area under the curve
    (numerical integration)
    matlab: ap=sum((mrec(i)-mrec(i-1)).*mpre(i));
  """
  ap = 0.0
  for i in i_list:
    ap += ((mrec[i] - mrec[i - 1]) * mpre[i])
  return ap, mrec, mpre

def sumpr():
    CurDir = os.path.join(os.getcwd(), 'mAP')
    GtDir = os.path.join(CurDir, 'ground-truth')
    PrDir = os.path.join(CurDir, 'predicted')
    TempDir = os.path.join(CurDir, 'temp')
    if os.path.exists(TempDir): shutil.rmtree(TempDir)
    os.mkdir(TempDir)


    gt_file_list = glob.glob(GtDir + '/*.txt')
    gt_num = 0
    for gt_file in gt_file_list:
        save_gt_data_list = []
        file_name = gt_file.split('\\')[-1]
        gt_temp_file_path = os.path.join(TempDir, file_name)
        with open(gt_file, 'r') as gt_f:
            for gt_data in gt_f:
                gt_num += 1
                gt_data_list = gt_data.strip().split(' ')
                temp_gt_data = {}
                temp_gt_data['class'] = gt_data_list[0]
                temp_gt_data['bbox'] = gt_data_list[1] + ' ' + gt_data_list[2] + ' ' + gt_data_list[3] + ' ' \
                                       + gt_data_list[4]
                temp_gt_data['used'] = False
                save_gt_data_list.append(temp_gt_data)

        with open(gt_temp_file_path, 'wb') as temp_f:
            pickle.dump(save_gt_data_list, temp_f)

    pre_file_list = glob.glob(PrDir+'/*.txt')
    predict_file = os.path.join(TempDir, 'predict.txt')
    with open(predict_file, 'wb') as pr_f:
        predict_data_list = []
        for pre_file in pre_file_list:
            pre_file_name = pre_file.split('\\')[-1]
            with open(pre_file, 'r') as prr_f:
                for pre_line in prr_f:
                    pred_data_list = pre_line.strip().split()
                    pre_data = {}
                    pre_data['class'] = pred_data_list[0]
                    pre_data['score'] = pred_data_list[1]
                    pre_data['bbox'] = pred_data_list[2] + ' ' + pred_data_list[3] + ' ' + pred_data_list[4] + ' ' \
                                       + pred_data_list[5]
                    pre_data['file'] = pre_file_name
                    predict_data_list.append(pre_data)

        predict_data_list.sort(key=lambda x:float(x['score']), reverse=True)
        pickle.dump(predict_data_list, pr_f)


    with open(predict_file, 'rb') as predict_f:
      predictions_data = pickle.load(predict_f)
      nd = len(predictions_data)
      tp = [0] * nd # creates an array of zeros of size nd
      fp = [0] * nd
      for idx, prediction in enumerate(predictions_data):
        file_id = prediction["file"]
        cur_class = prediction['class']

        # assign prediction to ground truth object if any
        #   open ground-truth with that file_id
        gt_file = TempDir + "/" + file_id
        ground_truth_data = pickle.load(open(gt_file, 'rb'))
        ovmax = -1
        gt_match = -1
        # load prediction bounding-box
        bb = [ float(x) for x in prediction["bbox"].split() ]
        for obj in ground_truth_data:
          # look for a class_name match
          if obj["class"] == cur_class:
            bbgt = [ float(x) for x in obj["bbox"].split() ]
            bi = [max(bb[0],bbgt[0]), max(bb[1],bbgt[1]), min(bb[2],bbgt[2]), min(bb[3],bbgt[3])]
            iw = bi[2] - bi[0] + 1
            ih = bi[3] - bi[1] + 1
            if iw > 0 and ih > 0:
              # compute overlap (IoU) = area of intersection / area of union
              ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                      + 1) * (bbgt[3] - bbgt[1] + 1) - iw * ih
              ov = iw * ih / ua
              if ov > ovmax:
                ovmax = ov
                gt_match = obj

        # assign prediction as true positive/don't care/false positive

        # set minimum overlap
        min_overlap = 0.3
        if ovmax >= min_overlap:
          if not bool(gt_match["used"]):
            # true positive
            tp[idx] = 1
            gt_match["used"] = True
            # update the ".json" file
            with open(gt_file, 'wb') as f:
                pickle.dump(ground_truth_data, f)
          else:
            # false positive (multiple detection)
            fp[idx] = 1
        else:
          # false positive
          fp[idx] = 1

    # compute precision/recall
      cumsum = 0
      for idx, val in enumerate(fp):
        fp[idx] += cumsum
        cumsum += val

      cumsum = 0
      for idx, val in enumerate(tp):
        tp[idx] += cumsum
        cumsum += val

      rec = tp[:]
      for idx, val in enumerate(tp):
        rec[idx] = float(tp[idx]) / gt_num
      #print(rec)
      prec = tp[:]
      for idx, val in enumerate(tp):
        prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
      #print(prec)

      ap, mrec, mprec = voc_ap(rec, prec)

      FigsDir = os.path.join(os.getcwd(), 'plot/figs')
      pr_fig_path = os.path.join(FigsDir, 'pr')
      plt.figure(num='Precision–recall curve')
      plt.title('Precision–recall curve')
      plt.xlabel('Recall')
      plt.ylabel('Precision')
      plt.plot(mrec, mprec, 'r-')
      plt.savefig(pr_fig_path)




