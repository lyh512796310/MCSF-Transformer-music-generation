import glob
from music21 import *
from chord2vec.chord2vec import *
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
def Chord2number(chord):
	# 转换后格式：45.21.78(midi_number)
	chord2number = '.'.join(str(n) for n in chord.normalOrder)
	return chord2number
def get_score_melody(file_path):
	files = 0
	Score = []
	for midi_file in glob.glob(file_path):
		notes = []
		note_beats = []
		score_single = []
		stream = covert2C_key(midi_file)
		parts = instrument.partitionByInstrument(stream)
		notes_to_parse = parts.parts[0].recurse()
		for element in notes_to_parse:
			if isinstance(element, note.Note):
				note_self = (str(element.pitch)+":"+str(element.duration.quarterLength))
				notes.append(note_self)
			elif isinstance(element, chord.Chord):
				break
		note_all = len(notes)
		for index in range(len(notes)):
			note_beat = notes[index].split(":")[1]
			note_beats.append(note_beat)
		note_beat_num = len(note_beats)
		note_beats_new = list(dict.fromkeys(note_beats))
		score_beat =  len(note_beats_new)/note_beat_num
		notes_no_repeat = list(dict.fromkeys(notes))
		score_note = len(notes_no_repeat)/note_all
		score_single.append(score_note)
		score_single.append(score_beat)
		# print(score_note,score_chord_final,score_beat)
		Score.append(score_single)
		files += 1
		if (files == 50):
			break
	# 平均
	score_note_all =  score_beat_all = 0
	for i in Score:
		score_note,score_beat = i[0],i[1]
		score_note_all+=score_note

		score_beat_all+=score_beat
	a = score_note_all/files
	c = score_beat_all/files
	print(a,c)
	return a,c
def get_score_both(file_path):
	files = 0
	Scores = []
	Score = []
	for midi_file in glob.glob(file_path):
		notes = []
		chords = []
		note_beats = []
		score_single = []
		stream = covert2C_key(midi_file)
		parts = instrument.partitionByInstrument(stream)
		notes_to_parse = parts.parts[0].recurse()
		for element in notes_to_parse:
			if isinstance(element, note.Note):
				note_self = (str(element.pitch)+":"+str(element.duration.quarterLength))
				notes.append(note_self)
			elif isinstance(element, chord.Chord):
				rest_self = (str(Chord2number(element))+":"+str(element.duration.quarterLength))
				chords.append(rest_self)
		note_all = len(notes)
		chord_all = len(chords)
		sum_chord_similar_scores = 0
		for index in range(len(chords)-1):
			chords_1 = chords[index].split(":")[0]
			chords_2 = chords[index+1].split(":")[0]
			list_t = ['0.4.7', '11.2.5.7', '5.9.0', '2.5.9', '7.11.2', '0.3.7', '9.0.4', '10.2.5', '6.9.0.2', '4.7.10.0', '4.7', '3.7.10', '8.0.3', '9.0.3.5', '1.4.7.9', '7.10.2', '5.8.0', '2.7', '7.0', '2.6.9', '9.0', '4.7.11', '2.5.8.10', '9.1.4', '11.2.6', '9.0.2.5', '8.11.2.4']
			if chords_1 or chords_2 not in list_t:
				f = 0.5
			else:
				f = predict_chord2chord(chords_1, chords_2)
			sum_chord_similar_scores += f
		for index in range(len(notes)):
			note_beat = notes[index].split(":")[1]
			note_beats.append(note_beat)
		note_beat_num = len(note_beats)
		note_beats_new = list(dict.fromkeys(note_beats))
		score_beat =  len(note_beats_new)/note_beat_num
		final_chord_similar_scores = sum_chord_similar_scores / chord_all
		notes_no_repeat = list(dict.fromkeys(notes))
		chords_no_repeat = list(dict.fromkeys(chords))
		score_note = len(notes_no_repeat)/note_all
		score_chord = len(chords_no_repeat)/chord_all
		score_chord_final = score_chord*0.7 + final_chord_similar_scores*0.3
		score_single.append(score_note)
		score_single.append(score_chord_final)
		score_single.append(score_beat)
		# print(score_note,score_chord_final,score_beat)
		Score.append(score_single)
		files += 1
		if (files == 50):
			break
	# 平均
	score_note_all = score_chord_final_all = score_beat_all = 0
	for i in Score:
		score_note,score_chord_final,score_beat = i[0],i[1],i[2]
		score_note_all+=score_note
		score_chord_final_all+=score_chord_final
		score_beat_all+=score_beat
	a = score_note_all/files
	b = score_chord_final_all/files
	c = score_beat_all/files
	print(a,b,c)
	return a,b,c
def get_score(file_path):
	files = 0
	Scores = []
	Score = []
	for midi_file in glob.glob(file_path):
		notes = []
		chords = []
		note_beats = []
		score_single = []
		stream = covert2C_key(midi_file)
		parts = instrument.partitionByInstrument(stream)
		notes_to_parse = parts.parts[0].recurse()
		for element in notes_to_parse:
			if isinstance(element, note.Note):
				note_self = (str(element.pitch)+":"+str(element.duration.quarterLength))
				notes.append(note_self)
			elif isinstance(element, chord.Chord):
				rest_self = (str(Chord2number(element))+":"+str(element.duration.quarterLength))
				chords.append(rest_self)
		note_all = len(notes)
		chord_all = len(chords)
		sum_chord_similar_scores = 0
		for index in range(len(chords)-1):
			chords_1 = chords[index].split(":")[0]
			chords_2 = chords[index+1].split(":")[0]
			sum_chord_similar_scores+=predict_chord2chord(chords_1, chords_2)
		for index in range(len(notes)):
			note_beat = notes[index].split(":")[1]
			note_beats.append(note_beat)
		note_beat_num = len(note_beats)
		note_beats_new = list(dict.fromkeys(note_beats))
		score_beat =  len(note_beats_new)/note_beat_num
		final_chord_similar_scores = sum_chord_similar_scores / chord_all
		notes_no_repeat = list(dict.fromkeys(notes))
		chords_no_repeat = list(dict.fromkeys(chords))
		score_note = len(notes_no_repeat)/note_all
		score_chord = len(chords_no_repeat)/chord_all
		score_chord_final = score_chord*0.7 + final_chord_similar_scores*0.3
		score_single.append(score_note)
		score_single.append(score_chord_final)
		score_single.append(score_beat)
		# print(score_note,score_chord_final,score_beat)
		Score.append(score_single)
		files += 1
		if (files == 50):
			break
	# 平均
	score_note_all = score_chord_final_all = score_beat_all = 0
	for i in Score:
		score_note,score_chord_final,score_beat = i[0],i[1],i[2]
		score_note_all+=score_note
		score_chord_final_all+=score_chord_final
		score_beat_all+=score_beat
	a = score_note_all/files
	b = score_chord_final_all/files
	c = score_beat_all/files
	print(a,b,c)
	return a,b,c
if __name__ == '__main__':
	# get_score('./data/*.mid')
	# get_score_melody('./data_test/baseline-melody.mid')
	get_score_both('./result_midi/*.mid')