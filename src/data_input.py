def get_dataset() -> list:
    """
        获取数据集
        @:return [train_texts,train_labels,test_texts,test_labels]
    """
    filenames = ['train_contents.txt', 'train_labels.txt', 'test_contents.txt', 'test_labels.txt']
    return [open(get_path() + file, encoding='utf-8').read().split('\n') for file in filenames]


def get_path() -> str:
    """
    :return: 数据集存放相对路径
    """
    return '../data/'
