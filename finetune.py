from model import MusicTransformer
from glob import glob
from Utils.utils import *
from data.read_and_view import *
import os

def main():
    # declare model
    model = MusicTransformer(
        checkpoint='LYH-checkpoint',
        is_training=True)
    # prepare data
    notes = view_pkl('./data/notes')
     # you need to revise it
    training_data = model.prepare_data(notes_all_files = notes)
    output_checkpoint_folder = 'LYH-checkpoint-output' # your decision
    if not os.path.exists(output_checkpoint_folder):
        os.mkdir(output_checkpoint_folder)
    # finetune
    model.finetune(
        training_data=training_data,
        output_checkpoint_folder=output_checkpoint_folder)
    model.close()

if __name__ == '__main__':
    main()
