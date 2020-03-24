# train_model.py
# Encode and train the model

import sys
import gpt_2_simple as gpt2
import pandas as pd
from os import path

if len(sys.argv) < 3:
    print('You must enter the corpus file and model name as parameters, e.g.: bot.py comment_data.txt 355M')
    sys.exit(1)    

file_name = sys.argv[1]
model_name = sys.argv[2]

sess = gpt2.start_tf_sess()

# Check if file exists
if not path.isfile(file_name):
    print("File does not exist. Please use a text corpus for training.")
    sys.exit(1)    

# Encode data if not already encoded
if file_name[-4:] != ".npz":
    old_file_name = file_name
    file_name = file_name[:-4] + ".npz"
    print("Encoding data...")
    try:
        gpt2.encode_dataset(old_file_name, out_path=file_name, model_name=model_name)
    except:
        print("Failed to encode data. Please check that your file is a text corpus that can be encoded.")
        sys.exit(1)    

gpt2.finetune(sess, file_name, model_name=model_name, multi_gpu=False, overwrite=True)

