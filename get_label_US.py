import numpy as np
import glob
import os

path_txt = "./data/us/"
path_label = "./data/us/label/"
if not os.path.exists(path_label):
    os.makedirs(path_label)
label_files = glob.glob(path_txt + "*.mfl")
label_class = path_txt.split('/')[-2]
file_id = 0
with open(path_label + label_class, 'wb') as label_filename:
    for label_file in label_files:
        label_data = open(label_file, 'r')
        flag_kw = 0
        flag_frame = 0
        label_info_temp = np.empty((0, 4))

        label_name = label_file.split('/')[-1][8:-4][0:6]
        for line_ in label_data:
            line_temp = line_
            line_ = line_.split()
            line_ = np.asarray(line_)

            if line_temp[1:5] == 'data':
                file_id += 1
                filename_ = line_temp
                filename_ = filename_.split('/')[-1:][0]
                filename_ = filename_[:-6]
                filename_ = filename_ + '_' + str(file_id)
                print("filename: ", filename_)

            if len(line_) == 5:
                word = line_[-1]
                if 'u' == word or 's' == word:
                    start_frame = np.int(line_[0])
                    keyword = word
                    print("keyword: ", word)
                    print("start frame: ", start_frame)
                    flag_kw = 1
                    line_prev = line_
                    if word == 'u':
                        prev_word = word
                        start_frame_prev = start_frame
                    word_now = word
                    continue

            if flag_kw:
                line_now = line_
                if len(line_now) == 4:
                    line_prev2 = line_prev
                    line_prev = line_now
                else:
                    line_now = line_prev2
                    end_frame = np.int(round(np.float(line_now[1])))
                    if word_now == 's' and prev_word == 'u':
                        start_frame = start_frame_prev
                        kword = 'us'
                        prev_word = 'X'
                        print("end frame: ", end_frame)
                    elif word_now == 's' and prev_word != 'u':
                        kword = 's'
                        prev_word = 'X'
                        print("end frame: ", end_frame)
                    else:
                        kword = 'u'
                        prev_word = 'X'
                        print("end frame: ", end_frame)

                    print(np.array([filename_, kword, start_frame, end_frame]).reshape(1, 4).shape)
                    label_info_temp = np.concatenate((label_info_temp,
                                                      np.array([filename_, kword, start_frame, end_frame]).reshape(1, 4)),
                                                     axis=0)

                    flag_kw = 0

            if len(line_) == 1 and 'data' not in line_temp:
                file_end = file_prev
                print("total frame: ", file_end[1])
                frame_length = file_end[1].astype(np.float)
                frame_length = int(round(frame_length))
                flag_frame = 1

            else:
                file_prev = line_

            if flag_frame:
                num_kw, _ = np.shape(label_info_temp)
                label_info = np.concatenate((label_info_temp, np.tile(frame_length, (num_kw, 1))), axis=1)
                np.savetxt(label_filename, label_info, delimiter=',', fmt='%s')
                flag_frame = 0
                label_info_temp = np.empty((0, 4))