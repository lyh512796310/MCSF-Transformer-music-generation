from model import MusicTransformer
import os
import glob
os.environ['CUDA_VISIBLE_DEVICES'] = '0'


def main():
	# declare model
	model = MusicTransformer(
		checkpoint='LYH-checkpoint',
		is_training=False)
	# generate from scratch
	# model.generate(
	# 	n_target_bar=16,
	# 	temperature=1.2,
	# 	topk=5,
	# 	output_path='result/from_scratch3.midi',
	# 	prompt=None)

	# generate continuation
	i = 0
	for midi_file in glob.glob('data_midi/*.mid'):
		midi_file_namglobe = midi_file.split("\\")[1]
		i+=1
		try:
			model.generate(
				n_target_bar=50,
				temperature=1.8,
				topk=5,
				emotion=True,
				output_path='result_midi/'+str(midi_file_name),
				prompt=midi_file)
			if (i >= 50):
				return
		except:
			continue
	model.close()
if __name__ == '__main__':
	main()
