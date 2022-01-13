import os
from chord2vec.chord2vec import *
from music21 import note,chord
import random
class Chord_Self(object):
    def __init__(self, pitch, offset, quarterLength, velocity=90):
        self.pitch = pitch
        self.offset = offset
        self.quarterLength = quarterLength
        self.velocity = velocity

    def __repr__(self):
        return 'Chord(pitch={}, offset={}, quarterLength={}, velocity={})'.format(
            self.pitch, self.offset, self.quarterLength, self.velocity)
def Chord2number(chord):
    # 转换后格式：45.21.78(midi_number)
    chord2number = '.'.join(str(n) for n in chord.normalOrder)
    return chord2number
pitch_match_number = {'C':0,'C#':1,'D-':1,'D':2,
                      'D#':3,'E-':3,'E':4,'F':5,
                      'F#':6,'G-':6,'G':7,'G#':8,
                      'A-':8,'A':9,'A#':10,'B-':10,
                      'B':11}
class myChords():
    # Some Chords:
    chord_root = {'root0':'0',
                  'root1':'1',
                  'root2':'2'}

    chord_second_maj = {'maj0-2':'0.2',
                        'maj0-4':'0.4',
                        'maj0-5':'0.5',
                        'maj0-7':'0.7',
                        'maj0-9':'0.9',

                        'maj1-4': '1.4',
                        'maj1-6': '1.6',

                        'maj2-7': '2.7',
                        'maj2-9': '2.9',}

    chord_second_min = {'min0-1':'0.1',
                        'min0-3':'0.3',
                        'min0-6':'0.6',
                        'min0-8':'0.8',
                        'min0-11':'0.11',

                        'min1-3':'1.3',
                        'min1-5':'1.5',

                        'min2-6':'2.6',
                        'min2-8':'2.8'}

    chord_third_maj = {'maj0-2-7':'0.2.7',
                       'maj0-2-8':'0.2.9',
                       'maj0-4-7':'0.4.7',
                       'maj0-4-9':'0.4.9',
                       'maj0-5-7':'0.5.7',
                       'maj0-5-9':'0.5.9'}

    chord_third_min = {'min0-1-6':'0.1.6',
                       'min0-1-8':'0.1.8',
                       'min0-3-6':'0.3.6',
                       'min0-3-7':'0.3.7',
                       'min0-3-8':'0.3.8',
                       'min0-6-9':'0.6.9'
    }

def chord_change(chord_change, pitchs, emotional_tendency=True):  # 默认为高兴的音乐
    # 候选
    seq = []
    for i in pitchs:
        seq.append(pitch_match_number[i[:-1]])
    # chords_related = predict_related_chords(chord_change)
    flag = 0
    len_pi = len(pitchs)
    if len_pi>=4:
        flag = 1 # 4 or 5 or 6
    else:
        flag = 0 # 1 or 2 or 3
    if emotional_tendency:
        chord_number = chord_change.split('.')
        chord_head = chord_number[0]
        new_chord_numbers = []
        new_note_numbers = []
        for i in chord_number:
            if int(i) >= int(chord_head):
                new_chord_number = int(i) - int(chord_head)
                new_chord_numbers.append(new_chord_number)
            elif int(i) < int(chord_head):
                new_chord_number = int(i) + 12 - int(chord_head)
                new_chord_numbers.append(new_chord_number)
        if flag == 0:
            for i in seq:
                if int(i) >= int(chord_head):
                    new_note_number = int(i) - int(chord_head)
                    new_note_numbers.append(new_note_number)
                elif int(i) < int(chord_head):
                    new_note_number = int(i) + 12 - int(chord_head)
                    new_note_numbers.append(new_note_number)
            if len_pi == 1:
                # a = random.sample(myChords.chord_root.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
                # chord_restore = int(myChords.chord_root[a[0]]) + int(chord_head)
                return chord_change
            elif len_pi == 2:
                if 0 in new_note_numbers:
                    final_chord = ''
                    if 3 in new_note_numbers:
                        final_chord = myChords.chord_second_maj['maj0-5']
                    elif 4 in new_note_numbers:
                        final_chord = myChords.chord_second_maj['maj0-4']
                    elif 7 in new_chord_numbers:
                        final_chord = myChords.chord_second_maj['maj0-7']
                    else:
                        a = myChords.chord_second_maj['maj0-5']
                        b = myChords.chord_second_maj['maj0-7']
                        c = myChords.chord_second_maj['maj0-9']
                        sss = []
                        sss.append(a)
                        sss.append(b)
                        sss.append(c)
                        final_chord = random.choice(sss)

                    final_chord_n = final_chord.split(".")
                    for j in range(len(final_chord_n)):
                        final_chord_n[j] = int(final_chord_n[j])+ int(chord_head)
                        if final_chord_n[j] >= 12:
                            final_chord_n[j] -= 12
                    for k in range(len(final_chord_n)):
                        final_chord_n[k] = str(final_chord_n[k])
                    new_final_chord = '.'.join(final_chord_n)
                    return new_final_chord
                else:
                    return chord_change
            elif len_pi == 3:
                return chord_change
        elif flag == 1:
            if chord_change == '0.4.7':
                b = ''
                for c in myChords.chord_third_maj.keys():
                    a = random.sample(myChords.chord_third_maj.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
                    b = myChords.chord_third_maj[a[0]]
                return b
            elif chord_change == '5.9.0':
                listb = ['5.9','5.0','9.0','5.7.0','5.9.0']
                final_chord = random.choice(listb)
                return final_chord
            else:
                # pitch 4 5 6 7 8
                return chord_change
    else:# 失落的音乐
        chord_number = chord_change.split('.')
        chord_head = chord_number[0]
        new_chord_numbers = []
        new_note_numbers = []
        for i in chord_number:
            if int(i) >= int(chord_head):
                new_chord_number = int(i) - int(chord_head)
                new_chord_numbers.append(new_chord_number)
            elif int(i) < int(chord_head):
                new_chord_number = int(i) + 12 - int(chord_head)
                new_chord_numbers.append(new_chord_number)
        if flag == 0:
            for i in seq:
                if int(i) >= int(chord_head):
                    new_note_number = int(i) - int(chord_head)
                    new_note_numbers.append(new_note_number)
                elif int(i) < int(chord_head):
                    new_note_number = int(i) + 12 - int(chord_head)
                    new_note_numbers.append(new_note_number)
            if len_pi == 1:
                # a = random.sample(myChords.chord_root.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
                # chord_restore = int(myChords.chord_root[a[0]]) + int(chord_head)
                return chord_change
            elif len_pi == 2:
                if 0 in new_note_numbers:
                    final_chord = ''
                    if 3 in new_note_numbers:
                        final_chord = myChords.chord_second_min['min0-3']
                    elif 4 or 5 or 6 in new_note_numbers:
                        final_chord = myChords.chord_second_min['min0-6']
                    elif 7 or 8 in new_chord_numbers:
                        final_chord = myChords.chord_second_min['min0-8']
                    else:
                        a = myChords.chord_second_min['min0-3']
                        b = myChords.chord_second_min['min0-6']
                        c = myChords.chord_second_min['min0-8']
                        d = myChords.chord_second_min['min0-11']
                        sss = []
                        sss.append(a)
                        sss.append(b)
                        sss.append(c)
                        sss.append(d)
                        final_chord = random.choice(sss)

                    final_chord_n = final_chord.split(".")
                    for j in range(len(final_chord_n)):
                        final_chord_n[j] = int(final_chord_n[j]) + int(chord_head)
                        if final_chord_n[j] >= 12:
                            final_chord_n[j] -= 12
                    for k in range(len(final_chord_n)):
                        final_chord_n[k] = str(final_chord_n[k])
                    new_final_chord = '.'.join(final_chord_n)
                    return new_final_chord
                else:
                    return chord_change
            elif len_pi == 3:

                return chord_change
        elif flag == 1:
            if chord_change == '0.4.7':
                b = ''
                for c in myChords.chord_third_maj.keys():
                    a = random.sample(myChords.chord_third_min.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
                    b = myChords.chord_third_maj[a[0]]
                return b
            elif chord_change == '5.9.0':
                listb = ['5.8', '5.0', '8.0', '5.8.0']
                final_chord = random.choice(listb)
                return final_chord
            else:
                # pitch 4 5 6 7 8
                return chord_change
def repeat_chord_detection(chords):
    chords_new = []
    for i in chords:
        chords_new.append(i)
    chord_divs = []
    for i in range(len(chords_new)):
        if '_chord_star' in chords_new[i]:
            chords_new[i],_ = chords_new[i].split(":")
            chords_new[i] = (chords_new[i].split("_"))[0]
            chords_new[i] = chords_new[i]+":"+str(i)
        else:
            chords_new[i] = None
    chords_new = list(filter(None, chords_new))
    # 将连续3次不变化的和弦进行变换
    list_eazy = ['0.4.7','11.2.5.7','5.9.0']
    for i in range(len(chords_new)-2):
        if(chords_new[i].split(":")[0] == chords_new[i+1].split(":")[0] and chords_new[i+1].split(":")[0] == chords_new[i+2].split(":")[0]):
            chord_divs.append(int(chords_new[i+1].split(":")[1]))
        for i2 in list_eazy:
            if (i2 == chords_new[i].split(":")[0]):
                chord_divs.append(int(chords_new[i].split(":")[1]))
    chord_divs = list(dict.fromkeys(chord_divs))
    chord_divs.sort()
    print(chord_divs)
    return chord_divs

if __name__ == '__main__':
    # print(chord_change('0.4.7'))
    print()
