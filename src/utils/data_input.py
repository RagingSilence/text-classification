import os


def get_dataset() -> list:
    """
        获取数据集
        @:return [train_texts, train_labels, test_texts, test_labels]
    """
    filenames = ['train_contents.txt', 'train_labels.txt', 'test_contents.txt', 'test_labels.txt']
    path = get_path()  # 使用修改后的 get_path 函数
    return [open(os.path.join(path, file), encoding='utf-8').read().split('\n') for file in filenames]


def get_path() -> str:
    """
    :return: 数据集存放的绝对路径
    """
    # 获取当前文件的  绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)
    # 返回相对于当前文件所在目录的上一级目录中的 data 文件夹的路径
    return os.path.join(current_dir, '..', '..', 'data')
