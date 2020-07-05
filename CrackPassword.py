# %% 导入包
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from ExportDict import ExportDict
from copy import deepcopy
from multiprocessing import Pool
from multiprocessing import Manager
from WriteDict import PasswordsProducer
from ReadDict import ReadDict
from zipfile import ZipFile, BadZipFile
from unrar.rarfile import RarFile, BadRarFile
from queue import Queue
from zlib import error


# %% 定义破解密码的后台线程类
class CrackPassword(QThread):
    """
    这个类是破解密码的后台线程类
    """
    # 定义一些常量
    CRACK_FAILED = "破解失败，没找到密码"
    CRACK_SUCCEED = "破解成功，密码是"
    CRACKING_PASSWORD = "正在尝试密码"
    NO_PASSWORD = "破解成功，密码为空"
    # 定义一些类变量
    passwords_num = 0
    # 定义一些信号
    producing_password = pyqtSignal(str)
    producing_password_num = pyqtSignal(int)
    consuming_passwords = pyqtSignal(str)
    consuming_passwords_num = pyqtSignal(int)

    def __init__(
            self, name: str, seed_selection: (bool, ), digit_range: range,
            dict_path: str, consumer_number: int, batch_size: int,
            dict_source: int, zipfile_path: str, extract_path: str
    ):
        """
        构造方法\n
        :param name: 线程名称
        :param seed_selection: 最上面的几个复选框的勾选情况
        :param digit_range: 位数取值范围
        :param dict_path: 外部密码文件路径字符串
        :param consumer_number: 消费者数量
        :param batch_size: 密码元组长度
        :param dict_source: 字典源，选择内部字典(0)还是外部字典(1)
        :param zipfile_path: 压缩文件路径
        :param extract_path: 解压路径
        """
        super(CrackPassword, self).__init__()
        self.setObjectName(name)
        self.seed = ExportDict.generate_seed(seed_selection)
        self.digit_range = deepcopy(digit_range)
        self.dict_path = dict_path
        self.consumer_number = consumer_number
        self.batch_size = batch_size
        self.dict_source = dict_source
        self.zipfile_path = zipfile_path
        self.extract_path = extract_path
        self.producer = None
        self.stop_flag = False
        self.pool = None

    def run(self):
        self.stop_flag = False
        # 定义一个队列
        queue = Manager().Queue()
        emit_queue = Manager().Queue()
        CrackPassword.passwords_num = 0
        self.producer = QThread()
        # 如果使用内置字典，定义一个生产者并运行
        if self.dict_source == 0:
            PasswordsProducer.password_num = 0
            self.producer = PasswordsProducer("producer", queue, self.digit_range, self.seed, self.batch_size)
        # 如果使用外置字典，读取文件并运行
        elif self.dict_source == 1:
            ReadDict.password_num = 0
            self.producer = ReadDict("producer", queue, self.dict_path, self.batch_size)
        self.producer.producing_password.connect(self.on_producing_password, type=Qt.DirectConnection)
        self.producer.producing_password_num.connect(self.on_producing_password_num, type=Qt.DirectConnection)
        self.producer.start()
        # 定义若干消费者并运行
        self.pool = Pool(processes=self.consumer_number)
        result = self.pool.apply_async(extract_function, args=(queue, self.zipfile_path, self.extract_path, emit_queue))
        while True:
            if self.stop_flag:
                self.producer.stop()
                self.producing_password.emit("")
                self.pool.terminate()
                self.emit_signal(tuple())
                self.pool.join()
                self.pool = self.producer = None
                return None
            passwords = emit_queue.get()
            self.emit_signal(passwords)
            if len(passwords) == 0 or type(passwords) == str:
                break
        result.wait()
        self.producer.wait()
        self.pool.terminate()
        self.pool.join()
        self.pool = self.producer = None

    def stop(self):
        """
        终止线程\n
        :return:
        """
        self.stop_flag = True

    def on_producing_password(self, password: str):
        """
        处理生产者密码信号的槽函数\n
        :return:
        """
        self.producing_password.emit("正在生成密码 " + password)

    def on_producing_password_num(self, password_num: int):
        """
        处理生产者密码序数信号的槽函数\n
        :param password_num: 密码序数
        :return:
        """
        self.producing_password_num.emit(password_num)

    def emit_signal(self, signal):
        """
        向外发射信号，告知正在处理哪批密码\n
        :param signal: 信号：如果取出元组，说明正在寻找元组里的密码；如果取出空元组，说明密码找遍了全不对；如果返回字符串，说明找到了密码就是字符串；如果取到了空字符串，说明压缩包密码为空
        :return:
        """
        CrackPassword.passwords_num = CrackPassword.passwords_num + 1
        if type(signal) == tuple:
            # 如果参数是长度为0的元组，说明吃到毒丸，破解失败
            if len(signal) == 0:
                self.consuming_passwords.emit(CrackPassword.CRACK_FAILED)
                self.consuming_passwords_num.emit(self.get_batch_count() + 1)
            # 如果参数是普通元组，说明正在尝试这些密码
            else:
                self.consuming_passwords.emit(CrackPassword.CRACKING_PASSWORD + ' '.join(signal))
                self.consuming_passwords_num.emit(CrackPassword.passwords_num)
        elif type(signal) == str:
            # 如果是长度为0的字符串，说明密码为空
            if len(signal) == 0:
                self.consuming_passwords.emit(CrackPassword.NO_PASSWORD)
                self.consuming_passwords_num.emit(self.get_batch_count() + 1)
            # 如果是普通字符串，说明字符串就是密码
            else:
                self.consuming_passwords.emit(CrackPassword.CRACK_SUCCEED + signal)
                self.consuming_passwords_num.emit(self.get_batch_count() + 1)

    def get_passwords_count(self) -> int:
        """
        计算总共由多少密码被生成出来\n
        :return: 密码总数
        """
        result = 0
        for digit in self.digit_range:
            result = len(self.seed) ** digit + result
        return result

    def get_batch_count(self) -> int:
        """
        计算总共走了多少批密码，即tuple数量\n
        :return: 元组总数
        """
        return self.get_passwords_count() // self.batch_size + 1


def extract_function(queue: Queue, zipfile_path: str, extract_path: str, emit_queue: Queue) -> str:
    """
    统一的解压函数，通过return返回找到的密码，通过emit_queue返回正在寻找的密码\n
    :param queue: 连接生产者与消费者的队列
    :param zipfile_path: 压缩文件路径字符串
    :param extract_path: 解压路径字符串
    :param emit_queue: 用于传递信号的队列：如果取出元组，说明正在寻找元组里的密码；如果取出空元组，说明密码找遍了全不对；如果返回字符串，说明找到了密码就是字符串；如果取到了空字符串，说明压缩包密码为空
    :return: 如果找到了密码，则返回密码；如果没找到密码，返回None
    """
    # 如果空密码解压成功，返回空字符串
    if extract_no_password(zipfile_path, extract_path):
        result = ""
        emit_queue.put(result)
        return result
    while True:
        passwords = queue.get()
        # 吃到了毒丸，跳出循环
        if not passwords:
            # 告诉外界，吃到了毒丸
            emit_queue.put(tuple())
            break
        if zipfile_path.lower().endswith(".zip"):
            result = extract_zip(passwords, zipfile_path, extract_path)
            emit_queue.put(passwords)
            if result is not None:
                emit_queue.put(result)
                return result
        elif zipfile_path.lower().endswith(".rar"):
            result = extract_rar(passwords, zipfile_path, extract_path)
            emit_queue.put(passwords)
            if result is not None:
                emit_queue.put(result)
                return result


def extract_zip(passwords: (str, ), zipfile_path: str, extract_path: str) -> str:
    """
    解压zip文件\n
    :param passwords: 密码组成的元组
    :param zipfile_path: 压缩文件路径字符串
    :param extract_path: 解压路径字符串
    :return: 如果找到了密码，返回密码字符串；如果没找到密码，返回None
    """
    with ZipFile(zipfile_path) as file:
        for password in passwords:
            # 如果是空密码则跳过
            if len(password) == 0:
                continue
            try:
                file.extractall(path=extract_path, members=None, pwd=bytes(password, "utf8"))
            except RuntimeError:
                print("尝试密码 %s 失败" % password)
            except BadZipFile:
                print("尝试密码 %s 失败" % password)
            except error:
                print("尝试密码 %s 失败" % password)
            except Exception as e:
                print("尝试密码", password, "遇到未知错误", type(e), e)
            else:
                print("尝试密码 %s 成功" % password)
                return password


def extract_rar(passwords: (str, ), zipfile_path: str, extract_path: str) -> str:
    """
    解压rar文件\n
    :param passwords: 密码组成的元组
    :param zipfile_path: 压缩文件路径字符串
    :param extract_path: 解压路径字符串
    :return: 如果找到了密码，返回密码字符串；如果没找到密码，返回None
    """
    with RarFile(zipfile_path) as file:
        for password in passwords:
            # 如果是空密码则跳过
            if len(password) == 0:
                continue
            try:
                file.extractall(path=extract_path, members=None, pwd=password)
            except RuntimeError:
                print("尝试密码 %s 失败" % password)
            except BadRarFile:
                print("尝试密码 %s 失败" % password)
            except Exception as e:
                print("尝试密码", password, "遇到未知错误", type(e), e)
            else:
                print("尝试密码 %s 成功" % password)
                return password


def extract_no_password(zipfile_path: str, extract_path: str) -> bool:
    """
    尝试用空密码解压\n
    :param zipfile_path: 压缩文件路径字符串
    :param extract_path: 解压路径字符串
    :return: 是否能解压成功
    """
    if zipfile_path.lower().endswith(".zip"):
        with ZipFile(zipfile_path) as file:
            try:
                file.extractall(path=extract_path, members=None, pwd=None)
            except RuntimeError:
                return False
            except BadZipFile:
                return False
            except error:
                return False
            except Exception as e:
                print("遇到未知错误", type(e), e)
            else:
                return True
    elif zipfile_path.lower().endswith(".rar"):
        with RarFile(zipfile_path) as file:
            try:
                file.extractall(path=extract_path, members=None, pwd=None)
            except RuntimeError:
                return False
            except BadZipFile:
                return False
            except error:
                return False
            except Exception as e:
                print("遇到未知错误", type(e), e)
            else:
                return True


if __name__ == "__main__":
    my_thread = CrackPassword(
        "crack_password", (True, False, False, False), range(3, 4),
        "test.txt", 12, 5, 0, "test.zip", ""
    )
    my_thread.start()
    my_thread.wait()
