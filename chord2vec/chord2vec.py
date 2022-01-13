# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")
from gensim.models import word2vec
import logging
import pickle
import csv
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
from pandas import *

def train_and_save(file_path):
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)  # 输出日志信息
	sentences = word2vec.Text8Corpus(file_path)  # 将语料保存在sentence中
	model = word2vec.Word2Vec(sentences, sg=1, size=300,  window=5,  min_count=1,  negative=3, sample=0.001, hs=1, workers=4)  # 生成词向量空间模型
	model.save('../chord2vec/chord_predict_chord2vec.model')  # 保存模型
def train_and_increase_save(increase_chords_list):
	# 增量训练
	model = word2vec.Word2Vec.load('chord2vec/chord_predict_chord2vec.model')
	more_sentences = increase_chords_list
	model.build_vocab(more_sentences, update=True)
	model.train(more_sentences, total_examples=model.corpus_count, epochs=model.iter)
	model.save('chord_predict_chord2vec.model')
def predict_chord2chord(chord1,chord2):
	# 加载模型
	model = word2vec.Word2Vec.load('chord2vec/chord_predict_chord2vec.model')
	# 计算两个词的相似度/相关程度
	chord1_ = chord1
	chord2_ = chord2
	result = model.similarity(chord1_, chord2_)
	print(result)
	return result
def predict_chords_similarity():
	list = list_pre()
	lens = len(list)
	# 加载模型
	model = word2vec.Word2Vec.load('chord2vec/chord_predict_chord2vec.model')
	i,j = 0,0
	probability_xy = [[0]*lens]*lens
	for i in range(lens):# i行 j列
		for j in range(lens):
			result = model.similarity(list[i],list[j])
			result2 = round(result, 4) # Keep 3 decimals
			probability_xy[i][j] = result2 # 第i行 第j列
	with open('predict_chords_similarity.csv','w',newline='') as datacsv:
		csvwriter = csv.writer(datacsv,dialect=('excel'))
		list.insert(0,' ')
		for i in range(lens+1):
			if(i == 0):
				continue
			else:
				list[i] = "[ "+list[i]+" ]"
		csvwriter.writerow(list)
def plot_table(row, col, vals):
	from matplotlib import pyplot as plt
	import numpy as np
	R, C = len(row), len(col)
	idx = Index(row)
	df = DataFrame(np.random.randn(R, C), index=idx, columns=col)

	# 根据行数列数设置表格大小
	figC, figR = 2 * C, R
	fig = plt.figure(figsize=(figC, figR))

	# 设置fig并去掉边框
	ax = fig.add_subplot(111, frameon=True, xticks=[], yticks=[])
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['bottom'].set_visible(False)
	ax.spines['left'].set_visible(False)

	the_table = plt.table(cellText=vals, rowLabels=df.index, colLabels=df.columns, colWidths=[0.04] * vals.shape[1],
						  rowLoc='center', loc='center', cellLoc='center')
	the_table.set_fontsize(20)

	# 伸缩表格大小常数
	the_table.scale(figR / R * 2, figC / C * 1.5)
	plt.show()
def predict_related_chords(chord):
	# 计算某个词的相关词列表
	chord_ = chord
	# 加载模型
	model = word2vec.Word2Vec.load('/chord_predict_chord2vec.model')
	chords_related = model.most_similar(chord_, topn=10)  # 10个最相关的
	# for item in chords_related:
	# 	print(item[0], item[1])
	return chords_related
def find_unimportant_chord(list_chords):
	# 寻找不合群的词
	print("寻找不和谐的和弦")
	model = word2vec.Word2Vec.load('chord2vec/chord_predict_chord2vec.model')
	result4 = model.doesnt_match(list_chords.split())
	print("不和谐和弦：", result4)
	print("\n================================")
def list_pre():
	# ['0.4.7', '11.2.5.7', '5.9.0', '2.5.9', '7.11.2', '0.3.7', '9.0.4', '10.2.5', '6.9.0.2', '4.7.10.0', '4.7', '3.7.10', '8.0.3', '9.0.3.5', '1.4.7.9', '7.10.2', '5.8.0', '2.7', '7.0', '2.6.9', '9.0', '4.7.11', '2.5.8.10', '9.1.4', '11.2.6', '9.0.2.5', '8.11.2.4']
	list = []
	model = pickle.load(open("../data/chords_frequency",'rb'))
	for index in model:
		list.append(index[1])
	return list

if __name__ == '__main__':
	# train_and_save('chords')
	# predict_chords_similarity()
	# predict_related_chords('11.2.5.7')
	# predict_related_chords('0.4.7')
	# predict_related_chords('0.3.7')
	# find_unimportant_chord()
	predict_chord2chord('0.4.7', '0.4.7')
	print()
