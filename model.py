import tensorflow as tf
import numpy as np
import miditoolkit
import modules
import pickle
import time
from Utils.utils import *
from Utils.util_commen import *
tf.compat.v1.disable_eager_execution()
class MusicTransformer(object):
    ########################################
    # initialize
    ########################################
    def __init__(self, checkpoint, is_training=False):
        # load dictionary
        print("init ...")
        self.dictionary_path = './data/event2word_word2event'
        self.event2word, self.word2event = pickle.load(open(self.dictionary_path, 'rb'))
        # model settings
        self.x_len = 512
        self.mem_len = 512
        self.n_layer = 12
        self.d_embed = 512
        self.d_model = 512
        self.dropout = 0.1
        self.n_head = 8
        self.d_head = self.d_model // self.n_head
        self.d_ff = 2048
        self.n_token = len(self.event2word)
        self.learning_rate = 0.0002
        # load model
        self.is_training = is_training
        if self.is_training:
            self.batch_size = 4
        else:
            self.batch_size = 1
        # self.checkpoint_path = '{}/model'.format(checkpoint)
        self.checkpoint_path = '{}/model.ckpt'.format(checkpoint)
        self.load_model()
    ########################################
    # load model
    ########################################
    def load_model(self):
        # placeholders
        print("load model ...")
        self.x = tf.compat.v1.placeholder(tf.int32, shape=[self.batch_size, None])
        self.y = tf.compat.v1.placeholder(tf.int32, shape=[self.batch_size, None])
        self.mems_i = [tf.compat.v1.placeholder(tf.float32, [self.mem_len, self.batch_size, self.d_model]) for _ in range(self.n_layer)]
        # model
        self.global_step = tf.compat.v1.train.get_or_create_global_step()
        initializer = tf.compat.v1.initializers.random_normal(stddev=0.02, seed=None)
        proj_initializer = tf.compat.v1.initializers.random_normal(stddev=0.01, seed=None)
        with tf.compat.v1.variable_scope(tf.compat.v1.get_variable_scope()):
            xx = tf.transpose(self.x, [1, 0])
            yy = tf.transpose(self.y, [1, 0])
            loss, self.logits, self.new_mem = modules.transformer(
                dec_inp=xx,
                target=yy,
                mems=self.mems_i,
                n_token=self.n_token,
                n_layer=self.n_layer,
                d_model=self.d_model,
                d_embed=self.d_embed,
                n_head=self.n_head,
                d_head=self.d_head,
                d_inner=self.d_ff,
                dropout=self.dropout,
                dropatt=self.dropout,
                initializer=initializer,
                proj_initializer=proj_initializer,
                is_training=self.is_training,
                mem_len=self.mem_len,
                cutoffs=[],
                div_val=-1,
                tie_projs=[],
                same_length=False,
                clamp_len=-1,
                input_perms=None,
                target_perms=None,
                head_target=None,
                untie_r=False,
                proj_same_dim=True)
        self.avg_loss = tf.reduce_mean(loss)
        # vars
        all_vars = tf.compat.v1.trainable_variables()
        grads = tf.gradients(self.avg_loss, all_vars)
        grads_and_vars = list(zip(grads, all_vars))
        all_trainable_vars = tf.reduce_sum([tf.reduce_prod(v.shape) for v in tf.compat.v1.trainable_variables()])
        # optimizer
        decay_lr = tf.compat.v1.train.cosine_decay(
            self.learning_rate,
            global_step=self.global_step,
            decay_steps=400000,
            alpha=0.004)
        optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=decay_lr)
        self.train_op = optimizer.apply_gradients(grads_and_vars, self.global_step)
        # saver
        self.saver = tf.compat.v1.train.Saver()
        config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
        config.gpu_options.allow_growth = True
        self.sess = tf.compat.v1.Session(config=config)
        sess = tf.compat.v1.Session()
        sess.run(tf.compat.v1.global_variables_initializer())
        # self.saver.save(sess, "LYH-checkpoint/model.ckpt")
        self.saver.restore(self.sess, self.checkpoint_path)
    ########################################
    # temperature sampling
    ########################################
    def temperature_sampling(self, logits, temperature, topk):
        probs = np.exp(logits / temperature) / np.sum(np.exp(logits / temperature))
        if topk == 1:
            prediction = np.argmax(probs)
        else:
            sorted_index = np.argsort(probs)[::-1]
            candi_index = sorted_index[:topk]
            candi_probs = [probs[i] for i in candi_index]
            # normalize probs
            candi_probs /= sum(candi_probs)
            # choose by predicted probs
            prediction = np.random.choice(candi_index, size=1, p=candi_probs)[0]
        return prediction
    ########################################
    # prepare data
    ########################################
    def prepare_data(self, notes_all_files):
        # event to word
        all_words = []
        for single_file in notes_all_files:
            words = []
            for notes_time in single_file:
                str_ = str(notes_time[0]) + ":" + str(notes_time[1])
                words.append(self.event2word[str_])
            all_words.append(words)
        self.group_size = 5
        segments = []
        words_ = []
        for words in all_words:
            for i in words:
                words_.append(i)
        pairs = []
        for i in range(0, len(words_) - self.x_len - 1, self.x_len):
            x = words_[i:i + self.x_len]
            y = words_[i + 1:i + self.x_len + 1]
            pairs.append([x, y])
        pairs = np.array(pairs)
        # abandon the last
        for i in np.arange(0, len(pairs) - self.group_size, self.group_size * 2):
            data = pairs[i:i + self.group_size]
            if len(data) == self.group_size:
                segments.append(data)
        segments = np.array(segments)
        return segments
    ########################################
    # finetune
    ########################################
    def finetune(self, training_data, output_checkpoint_folder):
        print("finetune ...")
        # shuffle
        index = np.arange(len(training_data))
        np.random.shuffle(index)
        training_data = training_data[index]
        num_batches = len(training_data) // self.batch_size
        st = time.time()
        for e in range(200):
            total_loss = []
            for i in range(num_batches):
                segments = training_data[self.batch_size*i:self.batch_size*(i+1)]
                batch_m = [np.zeros((self.mem_len, self.batch_size, self.d_model), dtype=np.float32) for _ in range(self.n_layer)]
                for j in range(self.group_size):
                    batch_x = segments[:, j, 0, :]
                    batch_y = segments[:, j, 1, :]
                    # prepare feed dict
                    feed_dict = {self.x: batch_x, self.y: batch_y}
                    for m, m_np in zip(self.mems_i, batch_m):
                        feed_dict[m] = m_np
                    # run
                    _, gs_, loss_, new_mem_ = self.sess.run([self.train_op, self.global_step, self.avg_loss, self.new_mem], feed_dict=feed_dict)
                    # _, gs_, loss_, new_mem_ = sess.run(self.new_mem, feed_dict=feed_dict)
                    batch_m = new_mem_
                    total_loss.append(loss_)
                    print('>>> Epoch: {}, Step: {}, Loss: {:.5f}, Time: {:.2f}'.format(e, gs_, loss_, time.time()-st))
            self.saver.save(self.sess, '{}/model-{:03d}-{:.3f}'.format(output_checkpoint_folder, e, np.mean(total_loss)))
            # stop
            if np.mean(total_loss) <= 0.1:
                break
    ########################################
    # close
    ########################################
    def close(self):
        self.sess.close()
    ########################################
    # generate
    ########################################
    def generate(self, n_target_bar, temperature, topk, emotion,output_path, prompt=None):
        # if prompt, load it. Or, random start
        print("generate ...")
        if prompt:
            # 将旋律段作为初始生成部分

            C_KEY_PROMPT_NOTES = get_promot2predict_Input(prompt)
            word = []
            words = []
            # 截取前20音符作为初步
            for i in range(20):
                word.append(self.event2word[C_KEY_PROMPT_NOTES[i]])
            words.append(word)
        else:
            # 随机 未完成
           return
        # initialize mem
        batch_m = [np.zeros((self.mem_len, self.batch_size, self.d_model), dtype=np.float32) for _ in range(self.n_layer)]
        # generate
        original_length = len(words[0]) # 提示段音符长度
        initial_flag = 1
        current_generated_bar = 0 # 生成长度

        while current_generated_bar < n_target_bar:
            # input
            if initial_flag:
                # 生成
                temp_x = np.zeros((self.batch_size, original_length))
                for b in range(self.batch_size):
                    for z, t in enumerate(words[b]):
                        temp_x[b][z] = t
                initial_flag = 0
            else:
                temp_x = np.zeros((self.batch_size, 1))
                for b in range(self.batch_size):
                    temp_x[b][0] = words[b][-1]
            # prepare feed dict
            feed_dict = {self.x: temp_x}
            for m, m_np in zip(self.mems_i, batch_m):
                feed_dict[m] = m_np
            # model (prediction)
            _logits, _new_mem = self.sess.run([self.logits, self.new_mem], feed_dict=feed_dict)
            # sampling
            _logit = _logits[-1, 0]
            word = self.temperature_sampling(
                logits=_logit,
                temperature=temperature,
                topk=topk)
            words[0].append(word)
            # if bar event (only work for batch_size=1)
            current_generated_bar += 1
            # re-new mem
            batch_m = _new_mem
        # word_final = words[0][original_length:]
        word_final = words[0]
        predict = []
        for i in word_final:
            predict.append(self.word2event[i])
        print(predict)
        create_melody_chord_change_promote(predict,emotion,output_path)
        # write
