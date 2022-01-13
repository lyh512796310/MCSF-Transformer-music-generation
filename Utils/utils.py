import os
import numpy as np
import pickle
import glob
from music21 import *
from Utils.Note_Self import *
from Utils.Chord_Self import *
from Utils.util_commen import *
import miditoolkit
from fractions import Fraction  # 插入模块
def get_notes(file_path):
    notes_time_all_all_midi = []
    for midi_file in glob.glob(file_path):
        print(midi_file+" : saving ……")
        piece = covert2C_key(midi_file)
        # 全音轨(左右手)
        notes_all = []
        if len(piece)==1:
            print(midi_file+" : error ……")
            continue
        for part in piece.parts:
            notes_single_track = []
            for element in part:
                if isinstance(element, note.Note):
                    note_self = Note_Self(element.pitch,element.offset,element.duration.quarterLength,element.volume.velocity)
                    notes_single_track.append(note_self)
                elif isinstance(element, note.Rest):
                    rest_self = Rest_Self(element.offset,element.duration.quarterLength)
                    notes_single_track.append(rest_self)
                elif isinstance(element, chord.Chord):
                    chord_number = Chord2number(element)
                    chord_self = Chord_Self(chord_number,element.offset,element.duration.quarterLength,element.volume.velocity)
                    notes_single_track.append(chord_self)
            notes_all.append(notes_single_track)
        notes_right = notes_all[0] # 右手
        notes_left = notes_all[1] # 左手
        # 时间刻度匹配
        notes_time_all_single_midi = []
        for left_index in notes_left:
            left_offset = left_index.offset
            right_offset = left_index.offset+left_index.quarterLength
            for right_index in notes_right:
                if ((type(left_index) == Rest_Self) and (type(right_index) != Rest_Self)): # 左手是Rest
                    if (left_offset <= right_index.offset and right_index.offset < right_offset):
                        right_time = str(right_index.pitch)+'_'+str(right_index.quarterLength)
                        left_time = 'Rest'
                        notes_time_all_single_midi.append([left_time,right_time])
                elif((type(left_index) == Rest_Self) and (type(right_index) == Rest_Self)):
                    right_time = 'Rest'
                    left_time = 'Rest'
                    notes_time_all_single_midi.append([left_time, right_time])
                elif((type(left_index) == Chord_Self) and (type(right_index) != Rest_Self)):
                    if (left_offset == right_index.offset):
                        right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                        left_time = str(left_index.pitch)+'_chord_star'
                        notes_time_all_single_midi.append([left_time,right_time])
                    elif(left_offset < right_index.offset and right_index.offset < right_offset):
                        right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                        # left_time = str(left_index.pitch) + '_chord_keep'
                        left_time = 'chord_keep'
                        notes_time_all_single_midi.append([left_time, right_time])
                elif((type(left_index) == Note_Self) and (type(right_index) != Rest_Self)):
                    if (left_offset == right_index.offset):
                        right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                        left_time = str(left_index.pitch) + '_' + str(left_index.quarterLength)
                        notes_time_all_single_midi.append([left_time,right_time])
                    elif(left_offset < right_index.offset and right_index.offset < right_offset):
                        right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                        left_time = str(left_index.pitch) + '_' + str(left_index.quarterLength)
                        notes_time_all_single_midi.append([left_time,right_time])
        # print(len(notes_right),len(notes_time_all_single_midi))
        notes_time_all_all_midi.append(notes_time_all_single_midi)
    current_dir = os.path.dirname(os.getcwd())  # 获取当前文件的上一级文件夹目录
    if 'data' not in get_from_path(current_dir):
        data_root = os.getcwd()  # 当前目录
        result_root = os.path.join(data_root, '..', 'data')
        os.makedirs(result_root)
    with open('../data/notes', 'wb') as filepath:  # 从路径中打开文件，将数据写入data/notes
        pickle.dump(notes_time_all_all_midi, filepath)  # 把notes写入到文件中
    # print(len(notes_time_all_all_midi))
    # print(notes_time_all_all_midi)
    evenet2word_word2evnet()
    return notes_time_all_all_midi  # 返回提取出来的notes列表
def evenet2word_word2evnet():
    e2w_w2e = []
    notes_all_files = pickle.load(open('../data/notes','rb'))
    lists = []
    dicts = {}
    for single_file in notes_all_files:
        for notes_time in single_file:
            str_ = str(notes_time[0])+":"+str(notes_time[1])
            lists.append(str_)
    list.sort(lists)
    new_list = list(dict.fromkeys(lists))
    for i in range(len(new_list)):
        dicts[new_list[i]] = i
    new_dicts = {v: k for k, v in dicts.items()}
    e2w_w2e.append(dicts)
    e2w_w2e.append(new_dicts)
    current_dir = os.path.dirname(os.getcwd())  # 获取当前文件的上一级文件夹目录
    if 'data' not in get_from_path(current_dir):
        data_root = os.getcwd()  # 当前目录
        result_root = os.path.join(data_root, '..', 'data')
        os.makedirs(result_root)
    with open('../data/event2word_word2event', 'wb') as filepath:  # 从路径中打开文件，将数据写入data/notes
        pickle.dump(e2w_w2e, filepath)  # 把notes写入到文件中
    return dicts,new_dicts
def covert2C_key(file_path):
    # load midi file using music21 library
    piece = converter.parse(file_path)
    # transpose all streams to C major. this process is to reduce the number of states
    # store the key of music before transposition.
    k = piece.analyze('key')
    # save the interval of C and current key
    if k.mode == 'minor':
        i = interval.Interval(k.parallel.tonic, pitch.Pitch('C'))
    else:
        i = interval.Interval(k.tonic, pitch.Pitch('C'))
    # transpose the music using stored interval
    piece = piece.transpose(i)
    # return transposed music
    return piece
def get_chords2C_key(file_path):
    chords = []
    for midi_file in glob.glob(file_path):
        print(midi_file)
        stream = covert2C_key(midi_file)
        parts = instrument.partitionByInstrument(stream)
        notes_to_parse = parts.parts[0].recurse()  # 递归 # 如果有乐器部分，取第一个乐器部分
        for element in notes_to_parse:  # notes本身不是字符串类型
            if isinstance(element, chord.Chord):
                chordnumer = Chord2number(element)#将和弦转化为number格式：45.21.78
                chords.append(chordnumer)  # 用.来分隔，把n按整数排序
    current_dir = os.path.dirname(os.getcwd()) #获取当前文件的上一级文件夹目录
    if 'data' not in get_from_path(current_dir):
        data_root = os.getcwd()# 当前目录
        result_root = os.path.join(data_root, '..', 'data')
        os.makedirs(result_root)
    with open('../chord2vec/chords','w') as f:
        for index in chords:
            f.write(str(index)+" ")
    with open('../data/chords_frequency', 'wb') as filepath:
        chords_all = chords
        fin_result = word_sort(chords_all,True)
        pickle.dump(fin_result,filepath)
    return chords,fin_result
# 切换乐器
def converter2another_instruments(file_path,instrument):
    s = converter.parse(file_path)
    for p in s.parts:
        p.insert(0, instrument.Violin())
    s.write('midi', 'new_output.mid')
def covert2another_key(file_path,key):
    keys = ['C','C#','D','D#','E','E#','F','G','G#','A','A#','B']
    piece = converter.parse(file_path)
    if key in keys:
        k = piece.analyze('key')
        if k.mode == 'minor':
            i = interval.Interval(k.parallel.tonic, pitch.Pitch(key))
        else:
            i = interval.Interval(k.tonic, pitch.Pitch(key))
        # transpose the music using stored interval
        piece = piece.transpose(i)
        # return transposed music
        print(k &" convert to " + key)
        return piece
    else:
        print(key &" is not the standard key,"
                    "plz input from"
                    "'C,C#,D,D#,E,E#,F,G,G#,A,A#,B' ")
        return piece
def get_promot2predict_Input(midi_file):
    piece = covert2C_key(midi_file)
    print(midi_file+' is promoting')
    notes_all = []
    if len(piece) == 1:
        return midi_file + " : error ……"
    for part in piece.parts:
        notes_single_track = []
        for element in part:
            if isinstance(element, note.Note):
                note_self = Note_Self(element.pitch, element.offset, element.duration.quarterLength,
                                      element.volume.velocity)
                notes_single_track.append(note_self)
            elif isinstance(element, note.Rest):
                rest_self = Rest_Self(element.offset, element.duration.quarterLength)
                notes_single_track.append(rest_self)
            elif isinstance(element, chord.Chord):
                chord_number = Chord2number(element)
                chord_self = Chord_Self(chord_number, element.offset, element.duration.quarterLength,
                                        element.volume.velocity)
                notes_single_track.append(chord_self)
        notes_all.append(notes_single_track)
    notes_right = notes_all[0]  # 右手
    notes_left = notes_all[1]  # 左手
    # 时间刻度匹配
    notes_time_all_single_midi = []
    for left_index in notes_left:
        left_offset = left_index.offset
        right_offset = left_index.offset + left_index.quarterLength
        for right_index in notes_right:
            if ((type(left_index) == Rest_Self) and (type(right_index) != Rest_Self)):  # 左手是Rest
                if (left_offset <= right_index.offset and right_index.offset < right_offset):
                    right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                    left_time = 'Rest'
                    notes_time_all_single_midi.append([left_time, right_time])
            elif ((type(left_index) == Rest_Self) and (type(right_index) == Rest_Self)):
                right_time = 'Rest'
                left_time = 'Rest'
                notes_time_all_single_midi.append([left_time, right_time])
            elif ((type(left_index) == Chord_Self) and (type(right_index) != Rest_Self)):
                if (left_offset == right_index.offset):
                    right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                    left_time = str(left_index.pitch) + '_chord_star'
                    notes_time_all_single_midi.append([left_time, right_time])
                elif (left_offset < right_index.offset and right_index.offset < right_offset):
                    right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                    # left_time = str(left_index.pitch) + '_chord_keep'
                    left_time = 'chord_keep'
                    notes_time_all_single_midi.append([left_time, right_time])
            elif ((type(left_index) == Note_Self) and (type(right_index) != Rest_Self)):
                if (left_offset == right_index.offset):
                    right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                    left_time = str(left_index.pitch) + '_' + str(left_index.quarterLength)
                    notes_time_all_single_midi.append([left_time, right_time])
                elif (left_offset < right_index.offset and right_index.offset < right_offset):
                    right_time = str(right_index.pitch) + '_' + str(right_index.quarterLength)
                    left_time = str(left_index.pitch) + '_' + str(left_index.quarterLength)
                    notes_time_all_single_midi.append([left_time, right_time])
    # e2w,w2e = pickle.load(open('../data/event2word_word2event', 'rb'))
    lists = []
    for notes_time in notes_time_all_single_midi:
        str_ = str(notes_time[0]) + ":" + str(notes_time[1])
        lists.append(str_)
    return lists
# original
def create_predict_melody(predict_notes,output_path):
    score = stream.Score()
    offset_right = 0
    offset_left = 0
    output_notes_right = stream.Stream()
    output_notes_left = stream.Stream()
    notes_right = []
    notes_left = []
    for i in predict_notes:
        note_left,note_right = i.split(":")
        notes_right.append(note_right)
        notes_left.append(note_left)
    divs = []
    quaterLength_div_sum = []
    for i in range(len(notes_left)):
        if '_chord_star' in notes_left[i]:
            divs.append(i)
    # chord quarterLength
    for i in range(len(divs)-1):
        quarterLength_sum = 0
        for index in range(divs[i],divs[i+1]):
            if 'Rest' in notes_right[index]:
                break
            pitch,quarterLength = notes_right[index].split("_")
            if "/" in quarterLength:
                import fractions
                f = fractions.Fraction(quarterLength)
                quarterLength_sum += f
            else:
                quarterLength_sum += float(quarterLength)
        notes_left[divs[i]] = notes_left[divs[i]] +":"+ str(quarterLength_sum)
    # last chords
    quarterLength_last_sum = 0
    for i in range(divs[-1],len(notes_right)):
        if 'Rest' in notes_right[i]:
            break
        pitch,quarterLength = notes_right[i].split("_")
        quarterLength_last_sum += float(quarterLength)
    notes_left[divs[-1]] = notes_left[divs[-1]] +":"+ str(quarterLength_last_sum)

    for index_final in range(len(predict_notes)):
        if (('Rest' in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            new_note = note.Rest()
            new_note.duration.quarterLength = 0.5
            new_note.offset = offset_right
            output_notes_left.append(new_note)
            output_notes_right.append(new_note)
            offset_right += 0.5
            offset_left += 0.5
        elif (('Rest' not in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            # 右手
            pitch,quarterLength = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            new_note_right.duration.quarterLength = float(quarterLength)
            new_note_right.offset = offset_right
            new_note_right.storedInstrument = instrument.Piano()
            offset_right += float(quarterLength)
            # 左手
            new_note_left = note.Rest()
            new_note_left.duration.quarterLength = float(quarterLength)
            new_note_left.offset = offset_left
            offset_left += float(quarterLength)

            output_notes_right.append(new_note_right)
            output_notes_left.append(new_note_left)
        elif(('chord_star') in (notes_left[index_final])):
            # 右手
            pitch, quarterLength_r = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            if "/" in quarterLength_r:
                import fractions
                f = fractions.Fraction(quarterLength_r)
                new_note_right.duration.quarterLength = f
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += f
            else:
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
            # 左手
            chord_,quarterLength_l = notes_left[index_final].split(":")
            note_in_chord_ = chord_.split("_")[0]
            note_in_chord = note_in_chord_.split(".")
            notes_c_l = []  # notes列表接收单音
            for current_note in note_in_chord:
                new_note_left = note.Note(int(current_note))  # 把当前音符化成整数，在对应midi_number转换成note
                new_note_left.storedInstrument = instrument.Piano()  # 乐器用钢琴
                notes_c_l.append(new_note_left)
            new_chord = chord.Chord(notes_c_l)  # 再把notes中的音化成新的和弦
            new_chord.duration.quarterLength = float(quarterLength_l)
            new_chord.offset = offset_left
            offset_left += float(quarterLength_l)

            output_notes_right.append(new_note_right)
            output_notes_left.append(new_chord)
        elif (('chord_keep') in (notes_left[index_final])):
            # 右手
            pitch, quarterLength_r = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)

            if "/" in quarterLength_r:
                import fractions
                f = fractions.Fraction(quarterLength_r)
                new_note_right.duration.quarterLength = f
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += f
            else:
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
            # 左手

            output_notes_right.append(new_note_right)

    part1 = stream.Part()
    part1.append(output_notes_right)
    part2 = stream.Part()
    part2.append(output_notes_left)
    # 创建音乐流(stream)
    score.insert(0, part1)  # 把上面的循环输出结果传到流
    score.insert(1, part2)  # 把上面的循环输出结果传到流

    # 写入midi文件
    score.write('midi', fp=output_path)
    return 1
# v1
def create_melody_chord_change(predict_notes,emotional_tendency,outputpath):
    score = stream.Score()
    offset_right = 0
    offset_left = 0
    output_notes_right = stream.Stream()
    output_notes_left = stream.Stream()
    notes_right = []
    notes_left = []
    for i in predict_notes:
        note_left,note_right = i.split(":")
        notes_right.append(note_right)
        notes_left.append(note_left)
    divs = []
    for i in range(len(notes_left)):
        if '_chord_star' in notes_left[i]:
            divs.append(i)
    # chord quarterLength
    for i in range(len(divs)-1):
        quarterLength_sum = 0
        for index in range(divs[i],divs[i+1]):
            if 'Rest' in notes_right[index]:
                break
            pitch,quarterLength = notes_right[index].split("_")
            quarterLength_sum += float(quarterLength)
        notes_left[divs[i]] = notes_left[divs[i]] +":"+ str(quarterLength_sum)
    # last chords
    quarterLength_last_sum = 0
    for i in range(divs[-1],len(notes_right)):
        if 'Rest' in notes_right[i]:
            break
        pitch,quarterLength = notes_right[i].split("_")
        quarterLength_last_sum += float(quarterLength)
    notes_left[divs[-1]] = notes_left[divs[-1]] +":"+ str(quarterLength_last_sum)
    # 重复和弦检测
    chords_change_flags = repeat_chord_detection(notes_left)
    for index_final in range(len(predict_notes)):
        if (('Rest' in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            new_note = note.Rest()
            new_note.duration.quarterLength = 0.5
            new_note.offset = offset_right
            output_notes_left.append(new_note)
            output_notes_right.append(new_note)
            offset_right += 0.5
            offset_left += 0.5
        elif (('Rest' not in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            # 右手
            pitch,quarterLength = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            new_note_right.duration.quarterLength = float(quarterLength)
            new_note_right.offset = offset_right
            new_note_right.storedInstrument = instrument.Piano()
            offset_right += float(quarterLength)
            # 左手
            new_note_left = note.Rest()
            new_note_left.duration.quarterLength = float(quarterLength)
            new_note_left.offset = offset_left
            offset_left += float(quarterLength)

            output_notes_right.append(new_note_right)
            output_notes_left.append(new_note_left)
        elif(('chord_star') in (notes_left[index_final])):
            flag = 0
            # 判断是否为需要更换的和弦
            for i in chords_change_flags:
                if (str(i) == str(index_final)):
                    flag = 1
            if (flag == 0):
                # 右手
                pitch, quarterLength_r = notes_right[index_final].split("_")
                new_note_right = note.Note(pitch)
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
                # 左手
                chord_,quarterLength_l = notes_left[index_final].split(":")
                note_in_chord_ = chord_.split("_")[0]
                note_in_chord = note_in_chord_.split(".")
                notes_c_l = []  # notes列表接收单音
                for current_note in note_in_chord:
                    new_note_left = note.Note(int(current_note))  # 把当前音符化成整数，在对应midi_number转换成note
                    new_note_left.storedInstrument = instrument.Piano()  # 乐器用钢琴
                    new_note_left.octave = 3  # 乐器用钢琴
                    notes_c_l.append(new_note_left)
                new_chord = chord.Chord(notes_c_l)  # 再把notes中的音化成新的和弦
                new_chord.duration.quarterLength = float(quarterLength_l)
                new_chord.offset = offset_left
                offset_left += float(quarterLength_l)

                output_notes_right.append(new_note_right)
                output_notes_left.append(new_chord)
            # 需要变更
            elif(flag == 1):
                # 右手
                pitch, quarterLength_r = notes_right[index_final].split("_")
                new_note_right = note.Note(pitch)
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
                # 左手和弦变换
                chord_, quarterLength_l = notes_left[index_final].split(":")
                note_in_chord_ = chord_.split("_")[0]
                # 变换
                note_in_chord_ = chord_change(note_in_chord_)
                note_in_chord = note_in_chord_.split(".")
                notes_c_l = []  # notes列表接收单音
                for current_note in note_in_chord:
                    new_note_left = note.Note(int(current_note))  # 把当前音符化成整数，在对应midi_number转换成note
                    new_note_left.storedInstrument = instrument.Piano()  # 乐器用钢琴
                    new_note_left.octave = 3  # 乐器用钢琴
                    notes_c_l.append(new_note_left)
                new_chord = chord.Chord(notes_c_l)  # 再把notes中的音化成新的和弦
                new_chord.duration.quarterLength = float(quarterLength_l)
                new_chord.offset = offset_left
                offset_left += float(quarterLength_l)

                output_notes_right.append(new_note_right)
                output_notes_left.append(new_chord)
                flag = 0
        elif (('chord_keep') in (notes_left[index_final])):
            # 右手
            pitch, quarterLength_r = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            new_note_right.duration.quarterLength = float(quarterLength_r)
            new_note_right.offset = offset_right
            new_note_right.storedInstrument = instrument.Piano()
            offset_right += float(quarterLength_r)
            # 左手
            output_notes_right.append(new_note_right)
    part1 = stream.Part()
    part1.append(output_notes_right)
    part2 = stream.Part()
    part2.append(output_notes_left)
    # 创建音乐流(stream)
    score.insert(0, part1)  # 把上面的循环输出结果传到流
    score.insert(1, part2)  # 把上面的循环输出结果传到流
    # 写入midi文件
    score.write('midi', fp="../result_midi/output_chord_change.mid")
    return 1
# v2
def create_melody_chord_change_promote(predict_notes,emotional_tendency,outputpath):
    score = stream.Score()
    offset_right = 0
    offset_left = 0
    output_notes_right = stream.Stream()
    output_notes_left = stream.Stream()
    notes_right = []
    notes_left = []
    for i in predict_notes:
        note_left,note_right = i.split(":")
        notes_right.append(note_right)
        notes_left.append(note_left)
    divs = []
    for i in range(len(notes_left)):
        if '_chord_star' in notes_left[i]:
            divs.append(i)
    # chord quarterLength
    for i in range(len(divs)-1):
        quarterLength_sum = 0
        for index in range(divs[i],divs[i+1]):
            if 'Rest' in notes_right[index]:
                break
            pitch,quarterLength = notes_right[index].split("_")
            quarterLength_sum += float(quarterLength)
        notes_left[divs[i]] = notes_left[divs[i]] +":"+ str(quarterLength_sum)
    # last chords
    quarterLength_last_sum = 0
    for i in range(divs[-1],len(notes_right)):
        if 'Rest' in notes_right[i]:
            break
        pitch,quarterLength = notes_right[i].split("_")
        quarterLength_last_sum += float(quarterLength)
    notes_left[divs[-1]] = notes_left[divs[-1]] +":"+ str(quarterLength_last_sum)
    # 重复和弦检测
    chords_change_flags = repeat_chord_detection(notes_left)
    for index_final in range(len(predict_notes)):
        if (('Rest' in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            new_note = note.Rest()
            new_note.duration.quarterLength = 0.5
            new_note.offset = offset_right
            output_notes_left.append(new_note)
            output_notes_right.append(new_note)
            offset_right += 0.5
            offset_left += 0.5
        elif (('Rest' not in (notes_right[index_final])) and ('Rest' in (notes_left[index_final]))):
            # 右手
            pitch,quarterLength = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            new_note_right.duration.quarterLength = float(quarterLength)
            new_note_right.offset = offset_right
            new_note_right.storedInstrument = instrument.Piano()
            offset_right += float(quarterLength)
            # 左手
            new_note_left = note.Rest()
            new_note_left.duration.quarterLength = float(quarterLength)
            new_note_left.offset = offset_left
            offset_left += float(quarterLength)

            output_notes_right.append(new_note_right)
            output_notes_left.append(new_note_left)
        elif(('chord_star') in (notes_left[index_final])):
            flag = 0
            # 判断是否为需要更换的和弦
            for i in chords_change_flags:
                if (str(i) == str(index_final)):
                    flag = 1
            if (flag == 0):
                # 右手
                pitch, quarterLength_r = notes_right[index_final].split("_")
                new_note_right = note.Note(pitch)
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
                # 左手
                chord_,quarterLength_l = notes_left[index_final].split(":")
                note_in_chord_ = chord_.split("_")[0]
                note_in_chord = note_in_chord_.split(".")
                notes_c_l = []  # notes列表接收单音
                for current_note in note_in_chord:
                    new_note_left = note.Note(int(current_note))  # 把当前音符化成整数，在对应midi_number转换成note
                    new_note_left.storedInstrument = instrument.Piano()  # 乐器用钢琴
                    new_note_left.octave = 3  # 乐器用钢琴
                    notes_c_l.append(new_note_left)
                new_chord = chord.Chord(notes_c_l)  # 再把notes中的音化成新的和弦
                new_chord.duration.quarterLength = float(quarterLength_l)
                new_chord.offset = offset_left
                offset_left += float(quarterLength_l)

                output_notes_right.append(new_note_right)
                output_notes_left.append(new_chord)
            # 需要变更
            elif(flag == 1):
                # 右手
                pitch, quarterLength_r = notes_right[index_final].split("_")
                new_note_right = note.Note(pitch)
                new_note_right.duration.quarterLength = float(quarterLength_r)
                new_note_right.offset = offset_right
                new_note_right.storedInstrument = instrument.Piano()
                offset_right += float(quarterLength_r)
                # 左手和弦变换
                chord_, quarterLength_l = notes_left[index_final].split(":")
                note_in_chord_ = chord_.split("_")[0]
                # 变换
                # 相关旋律配比
                pitchs = []
                pitchs_q_r = 0
                for i in range(100):
                    pitch, quarterLength_r = notes_right[index_final+i].split("_")
                    pitchs.append(pitch)
                    pitchs_q_r += float(quarterLength_r)
                    if pitchs_q_r == float(quarterLength_l):
                        break
                note_in_chord_ = chord_change(note_in_chord_,pitchs)
                note_in_chord = note_in_chord_.split(".")
                notes_c_l = []  # notes列表接收单音
                for current_note in note_in_chord:
                    new_note_left = note.Note(int(current_note))  # 把当前音符化成整数，在对应midi_number转换成note
                    new_note_left.storedInstrument = instrument.Piano()  # 乐器用钢琴
                    new_note_left.octave = 3  # 乐器用钢琴
                    notes_c_l.append(new_note_left)
                new_chord = chord.Chord(notes_c_l)  # 再把notes中的音化成新的和弦
                new_chord.duration.quarterLength = float(quarterLength_l)
                new_chord.offset = offset_left
                offset_left += float(quarterLength_l)

                output_notes_right.append(new_note_right)
                output_notes_left.append(new_chord)
                flag = 0
        elif (('chord_keep') in (notes_left[index_final])):
            # 右手
            pitch, quarterLength_r = notes_right[index_final].split("_")
            new_note_right = note.Note(pitch)
            new_note_right.duration.quarterLength = float(quarterLength_r)
            new_note_right.offset = offset_right
            new_note_right.storedInstrument = instrument.Piano()
            offset_right += float(quarterLength_r)
            # 左手

            output_notes_right.append(new_note_right)
    part1 = stream.Part()
    part1.append(output_notes_right)
    part2 = stream.Part()
    part2.append(output_notes_left)
    # 创建音乐流(stream)
    score.insert(0, part1)  # 把上面的循环输出结果传到流
    score.insert(1, part2)  # 把上面的循环输出结果传到流

    # 写入midi文件
    score.write('midi', fp=outputpath)
    return 1
if __name__ == '__main__':
    # get_notes('../data/*.mid')
    # get_promot2predict_Input('../data/hpps40.mid')
    # get_chords2C_key('../data/*.mid')
    # predict_notes = ['0.3.7_chord_star:E-4_0.5', 'chord_keep:F4_0.25', 'chord_keep:E-4_0.25', '10.2.5_chord_star:D4_0.5', 'chord_keep:E-4_0.25', 'chord_keep:D4_0.25', '8.0.3_chord_star:C4_0.5', 'chord_keep:D4_0.25', 'chord_keep:C4_0.25','7.10.2_chord_star:B-3_0.75', 'chord_keep:C4_0.25', '10.2.5_chord_star:D4_0.25', 'chord_keep:E-4_0.25', 'chord_keep:F4_0.5', '5.9.0_chord_star:G4_0.5', 'chord_keep:F4_0.5', '10.2.5_chord_star:B-4_1.5', 'chord_keep:F4_0.5', '0.3.7_chord_star:G4_0.5', 'chord_keep:C5_0.5', 'chord_keep:A4_0.5', '0.4.7_chord_star:G4_0.5', 'chord_keep:C5_0.5', 'chord_keep:B4_0.5', 'chord_keep:C5_0.5', 'chord_keep:B4_0.5', '0.4.7_chord_star:C5_0.5', 'chord_keep:D5_0.5', 'chord_keep:B4_0.5', 'chord_keep:A4_0.5', 'chord_keep:G4_0.5', '5.9.0_chord_star:F4_1.0', 'chord_keep:A4_0.5', 'chord_keep:B4_0.5', 'chord_keep:A4_0.5', '0.4.7_chord_star:G4_1.0', 'chord_keep:E5_1.0', 'chord_keep:G5_1.0', '2.5.9_chord_star:F5_1.0', 'chord_keep:F5_1.0', 'chord_keep:G5_0.5', 'chord_keep:E5_0.5', 'chord_keep:G5_0.5', '7.11.2_chord_star:F5_0.5', 'chord_keep:E5_0.5', '5.9.0_chord_star:F5_0.5', 'chord_keep:A4_0.5', 'chord_keep:B4_0.5', '0.4.7_chord_star:C5_1.0',
    #                  'Rest:Rest', 'Rest:C4_0.5', 'Rest:E4_0.5', 'Rest:E4_0.5', 'Rest:F4_0.5', '0.4.7_chord_star:E4_1.0', 'chord_keep:G4_0.5', 'chord_keep:F4_0.5', '0.4.7_chord_star:E4_1.0', 'chord_keep:G4_1.0', '0.4.7_chord_star:C4_1.0', 'chord_keep:D5_1.0', '0.4.7_chord_star:E5_0.5', 'chord_keep:C5_0.5', 'chord_keep:B4_0.5', 'chord_keep:C5_0.5', '11.2.5.7_chord_star:B4_0.5', 'chord_keep:A4_0.5', 'chord_keep:G4_0.5', 'chord_keep:A4_0.5', 'chord_keep:G4_1.0', 'chord_keep:E4_1.0', 'chord_keep:F4_1.0', 'chord_keep:D4_1.0', 'chord_keep:C4_1.0', '5.9.0_chord_star:F4_1.0', 'chord_keep:A4_0.75', 'chord_keep:F4_0.25', '0.4.7_chord_star:E4_1.0', 'chord_keep:G4_1.0', '0.4.7_chord_star:C4_1.0', 'chord_keep:E4_1.0', 'chord_keep:D4_1.0', 'chord_keep:E4_1.0', 'chord_keep:F4_1.0', '0.4.7_chord_star:G4_0.5', 'chord_keep:G4_1.0', 'chord_keep:G4_0.5', '5.9.0_chord_star:F4_1.0', 'chord_keep:D4_1.0', '0.4.7_chord_star:C4_2.0', '0.4.7_chord_star:C5_1.0', 'chord_keep:E5_1.0', '11.2.5.7_chord_star:D5_1.0', 'chord_keep:G4_1.0', 'chord_keep:G4_0.5', 'chord_keep:G4_0.5', 'chord_keep:G4_0.5', 'chord_keep:G4_1.0', '0.4.7_chord_star:C4_1.0', 'chord_keep:E4_1.0', 'chord_keep:F4_1.0', '0.4.7_chord_star:G4_0.5', 'chord_keep:G4_1.0', '0.4.7_chord_star:C4_1.0', 'chord_keep:D4_1.0', '0.4.7_chord_star:C4_3.0', 'chord_keep:G4_0.5', 'chord_keep:G4_1.0', '11.2.5.7_chord_star:G4_1.0', 'chord_keep:F4_1.0', '0.4.7_chord_star:G4_1.0', 'chord_keep:E4_1.0', 'chord_keep:C4_1.0', 'chord_keep:D4_1.0', 'chord_keep:C4_1.0', 'chord_keep:G3_1.0', 'chord_keep:C4_1.0', '5.9.0_chord_star:F4_1.0', 'chord_keep:D4_1.0',
    #                  '0.4.7_chord_star:C4_3.0']
    # create_melody_chord_change_promote(predict_notes,emotional_tendency =True)
    print()



