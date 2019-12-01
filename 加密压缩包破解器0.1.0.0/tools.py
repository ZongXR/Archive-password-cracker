# %% 导入包
from zipfile import ZipFile
from multiprocessing import Pool
from itertools import product
from queue import Queue, Empty


# %% 定义一个函数，解压zip
def extract_zip(file_name: str, output_path=None, password=None) -> (bool, str):
    """
    定义一个函数，解压zip\n
    :param file_name: str 文件路径字符串
    :param output_path: str 解压后文件路径字符串，默认为当前路径
    :param password: str 密码字符串，默认无密码
    :return: (bool, str) 如果没有密码返回(True, "")；如果解压成功返回(True, password)；如果解压失败返回(False, "")
    """
    result = False, ""
    try:
        file = ZipFile(file_name)
        pwd = None if password is None else bytes(password, "utf8")
        file.extractall(path=output_path, members=None, pwd=pwd)
        result = (True, "") if password is None else (True, password)
    except FileNotFoundError:
        result = False, "FileNotFoundError"
    except RuntimeError:
        result = False, "BadPasswordError"
    finally:
        return result


# %% 定义一个函数遍历字典
def traverse_dict(passwords: [str], file_name: str, output_path=None, process_num=None):
    """
    定义一个函数遍历字典\n
    :param passwords: [str] 密码组成的迭代器
    :param file_name: str 压缩文件路径字符串
    :param output_path: str 解压后文件路径字符串，默认为当前路径
    :param process_num: int 进程池中的进程数，默认为核心数
    :return: Optional[str] 如果找到了密码，返回密码；如果密码为空，返回""；如果没找到密码，返回None
    """
    # 先判断是何种压缩类型，再根据对应的类型进行解压
    assert file_name.lower().endswith(".zip") or file_name.lower().endswith(".rar"), "不支持的文件类型"
    if file_name.lower().endswith(".zip"):
        extract_function = extract_zip
    elif file_name.lower().endswith(".rar"):
        pass
    # 先试试空密码能不能解压
    flag, result = extract_function(file_name, output_path, None)
    # 如果空密码能解压，直接返回""
    if flag:
        return result
    # 如果空密码解压失败，并且返回FileNotFoundError，直接抛出一个FileNotFoundError
    elif result == "FileNotFoundError":
        raise FileNotFoundError
    # 如果空密码不能解压，创建多进程
    pool = Pool(processes=process_num)
    que = Queue()
    # 将所有password装入进程池
    for password in passwords:
        if password.strip() == "":
            continue
        que.put(pool.apply_async(extract_function, args=(file_name, output_path, password.strip())))
    # 依次从进程池中取结果
    while True:
        try:
            flag, result = que.get(block=False).get()
            if flag:
                break
        except Empty:
            break
    # 结束进程池
    pool.terminate()
    pool.join()
    # 如果找到了正确的密码，返回结果
    if flag:
        return result
    # 如果没找到正确的密码，返回空
    else:
        return None


# %% 定义一个函数生成txt字典
def write_dict(path: str, digits1: int, digits2: int, num: bool, lower_letters: bool, upper_letters: bool, symbols: bool, process_num=None) -> bool:
    """
    定义一个函数，生成密码字典\n
    :param path: str 生成密码字典的保存路径
    :param digits1: int 密码至少多少位
    :param digits2: int 密码最多多少位
    :param num: bool 密码是否包含数字
    :param lower_letters: bool 密码是否包含小写字母
    :param upper_letters: bool 密码是否包含大写字母
    :param symbols: bool 密码是否包含特殊符号
    :param process_num: int 进程池中的进程数
    :return: bool 生成成功返回True, 生成失败返回False
    """
    # 对每个digit，扔到进程池中
    result = False
    try:
        with open(path, "w") as f:
            pass
        passwords_generated = generate_all_passwords((num, lower_letters, upper_letters, symbols), (digits1, digits2))
        pool = Pool(processes=process_num)
        passwords = []
        for password in passwords_generated:
            passwords.append(password)
            if len(passwords) == 16 * 1024:
                pool.apply(write_line, args=(path, passwords))
                passwords.clear()
        pool.apply(write_line, args=(path, passwords))
        pool.close()
        pool.join()
        result = True
    finally:
        return result


# %% 定义一个函数，手动引发Error
def multiprocessing_error(x) -> None:
    """
    定义一个函数，用于在非阻塞进程池中向主进程发送Error\n
    :return: None
    """
    print(x)
    raise Exception


# %% 根据指定位数，生成一个密码字典
def generate_dict(passwords: [str], path: str) -> None:
    """
    将密码列表写入文件\n
    :param passwords: [str] 密码列表
    :param path: str 文件路径字符串
    :return: None
    """
    with open(path, "w") as f:
        f.write("\n".join(passwords))


# %% 根据指定位数，生成一个[str]
def generate_lst(digit: int, seed: str) -> [str]:
    """
    根据指定选项，生成一个密码列表\n
    :param digit: int 密码位数
    :param seed: str 密码字典中都包含哪些字符
    :return: [str] 密码列表
    """
    return [password for password in generate_passwords(seed, digit)]


# %% 生成密码文件的函数
def generate_txt(digit: int, seed: str, path: str) -> None:
    """
    该函数用于根据指定位数和种子，写密码文件\n
    :param digit: int 密码位数
    :param seed: str 密码种子字符串
    :param path: str 文件路径字符串
    :return: None
    """
    passwords = generate_passwords(seed, digit)
    with open(path, "w") as f:
        for password in passwords:
            f.write(password + "\n")


# %% 写入一行文件
def write_line(path: str, passwords: [str]) -> None:
    """
    写入文件的一行
    :param path: str 文件路径字符串
    :param passwords: str 密码字符串列表
    :return: None
    """
    if len(passwords) == 0:
        return None
    with open(path, "a") as f:
        f.write("\n".join(passwords) + "\n")


# %% 定义一个函数读取字典
def read_dict(path: str) -> [str]:
    """
    定义一个函数读取密码列表\n
    :param path: str 密码文件路径字符串
    :return: [str] 密码列表
    """
    result = []
    try:
        with open(path) as f:
            result = f.read().splitlines(False)
    finally:
        return result


# %% 定义一个函数，根据booleans, digits输出一个迭代器
def generate_all_passwords(booleans: (bool, ), digits: (int, int)) -> [str]:
    """
    根据密码选项信息，生成密码迭代器\n
    :param booleans: (bool, ) 四个复选框是否被选中
    :param digits: (int, int) 位数范围
    :return: 密码迭代器
    """
    seed = generate_seed(booleans)
    repeats = range(min(*digits), max(*digits) + 1)
    # 生成器的总长度是 len(seed) ** repeat
    for repeat in repeats:
        for x in product(seed, repeat=repeat):
            yield ''.join(x)


# %% 定义一个迭代器，读取大密码字典文件
def read_big_dict(path: str):
    """
    定义一个迭代器，读取大字典文件\n
    :param path: str 字典文件路径字符串
    :return: 密码字典迭代器
    """
    with open(path) as f:
        for password in f:
            yield password.strip()


# %% 定义一个迭代器，对笛卡尔积的结果进行处理
def generate_passwords(iterable, repeat: int):
    """
    定义一个迭代器，返回字符串列表的迭代器\n
    :param iterable: 可迭代对象
    :param repeat: int 位数
    :return: 密码字符串迭代器
    """
    for x in product(iterable, repeat=repeat):
        yield ''.join(x)


# %% 根据复选框选项，生成种子
def generate_seed(booleans: (bool, )) -> str:
    """
    根据复选框选项生成种子\n
    :param booleans: (bool, )四个复选框是否被选中
    :return: str 种子字符串
    """
    result = ""
    if booleans[0]:
        result = result + "0123456789"
    if booleans[1]:
        result = result + "abcdefghijklmnopqrstuvwxyz"
    if booleans[2]:
        result = result + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if booleans[3]:
        result = result + "!@#$%^&*()[]{}<>_+=-"
    return result


# %% 测试
# if __name__ == "__main__":
    # print(write_dict("dict.txt", 2, 3, True, True, False, False, None))
    # my_dict = read_dict("dict.txt")
    # print(traverse_dict(my_dict, "test.zip", None, None))
    # print(list(generate_passwords("abcdef", 4)))
    # print(list(generate_all_passwords((True, True, False, False), (2, 3))))
    # for line in read_big_dict("dict.txt"):
    #     if line[:-1] == "02":
    #         print("02")
    #         break
    # print("end")
