import os

def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        print(root)  # 当前目录路径
        print(dirs)  # 当前路径下所有子目录
        print(files)  # 当前路径下所有非目录子文件
# 返回上一级目录
def get_last_path():
    return os.path.dirname(os.getcwd())
# 获取当前目录下的所有文件夹及文件名
def get_from_path(file_dir):
    return os.listdir(file_dir)

# 判断上一级是否存在file_name文件夹 如果没有就创建文件夹file_name
def mkdir_parrents_path(file_name):
    current_dir = os.path.dirname(os.getcwd())  # 获取当前文件的上一级文件夹目录
    if str(file_name) not in get_from_path(current_dir):
        data_root = os.getcwd()  # 当前目录
        result_root = os.path.join(data_root, '..', str(file_name))
        os.makedirs(result_root)
    print(str(file_name)+ " is already exist")
# 词频排序
def word_sort(seqence, reverse_choose):
    rc = reverse_choose
    # dict:chord:chords_frequency
    result = {}
    for index in seqence:
        if index in result:
            result[index] = result[index] + 1  # 该字符第N次在字典里
        else:
            result[index] = 1  # 该字符第一次在字典里
    # 按照次数从大到小排序
    fin_result = list(zip(result.values(), result.keys()))
    fin_result.sort(reverse=rc, key=lambda x: x[0])
    return fin_result
    print(fin_result)