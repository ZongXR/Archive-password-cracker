# %% 导入包
from queue import Queue
from threading import Lock
from copy import deepcopy
from itertools import product
from PyQt5.QtCore import pyqtSignal, QThread


# %% 声明全局变量
lock = Lock()


# %% 生产者类
class PasswordsProducer(QThread):
    """
    生产者消费者模型的生产者类
    """
    # 定义一些常量
    PRODUCER_NUM = 1
    # 定义一些类变量
    producing_password = pyqtSignal(str)
    password_num = 0
    producing_password_num = pyqtSignal(int)

    def __init__(self, name: str, queue: Queue, digit_range: range, seed: str, batch_size: int):
        """
        生产者的构造方法\n
        :param name: 线程名称
        :param queue: 队列
        :param digit_range: range类对象，位数取值范围
        :param seed: 字符串对象，密码种子
        """
        super(PasswordsProducer, self).__init__()
        self.setObjectName(name)
        self.queue = queue
        self.digit_range = deepcopy(digit_range)
        self.seed = seed
        self.batch_size = batch_size
        # 设置非守护线程
        self.daemon = False

    def run(self):
        """
        运行生产者\n
        :return:
        """
        passwords = []
        for password in self.generate_passwords():
            # 发射信号，当前处理的密码及序号
            self.emit_signal(password)
            # 将要批量写入的密码组成元组
            passwords.append(password)
            if len(passwords) == self.batch_size:
                self.put_queue(passwords)
                passwords.clear()
        self.put_queue(passwords)
        # 生成完全部密码之后要释放毒丸
        for _ in range(PasswordsWriter.CONSUMER_NUM):
            self.put_queue(tuple())

    def generate_passwords(self) -> [str]:
        """
        生成密码的方法\n
        :return: 枚举密码的生成器
        """
        for digit in self.digit_range:
            for x in product(self.seed, repeat=digit):
                yield ''.join(x)

    def put_queue(self, passwords: [str]):
        """
        将密码字符串放入队列中\n
        :param passwords:由字符串组成的列表
        :return:
        """
        print("++++++++++++++%s producing passwords++++++++" % self.objectName())
        print(passwords)
        self.queue.put(tuple(passwords))

    def emit_signal(self, password: str):
        """
        向外发射信号\n
        :param password: 密码字符串
        :return:
        """
        self.producing_password.emit(password)
        PasswordsProducer.password_num = PasswordsProducer.password_num + 1
        self.producing_password_num.emit(PasswordsProducer.password_num)


# %% 消费者类
class PasswordsWriter(QThread):
    """
    生产者消费者模型的消费者类
    """
    # 定义一些常量
    CONSUMER_NUM = 3
    # 定义一些类变量
    consuming_passwords = pyqtSignal(tuple)
    passwords_num = 0
    consuming_passwords_num = pyqtSignal(int)

    def __init__(self, name: str, queue: Queue, file_path: str):
        """
        构造方法\n
        :param name: 线程名称
        :param queue: 队列
        :param file_path: 文件路径字符串
        """
        super(PasswordsWriter, self).__init__()
        self.setObjectName(name)
        self.queue = queue
        self.file_path = file_path
        # 设置非守护线程
        self.daemon = False

    def run(self):
        """
        运行消费者线程\n
        :return:
        """
        while True:
            content = self.queue.get()
            if not content:
                break
            # 发射信号，正在处理的密码
            self.emit_signal(content)
            print("---------------%s consuming passwords---------" % self.objectName())
            print(content)
            self.write_passwords(content)

    def write_passwords(self, content: (str,)):
        """
        将生成的密码列表写入到文件\n
        :param content: 由字符串组成的数组
        :return:
        """
        lock.acquire()
        with open(self.file_path, "a+") as f:
            f.writelines("\n".join(content) + "\n")
        lock.release()

    def emit_signal(self, content: (str, )):
        """
        向外发射信号\n
        :param content: 密码组成的元组
        :return:
        """
        self.consuming_passwords.emit(content)
        PasswordsWriter.passwords_num = PasswordsWriter.passwords_num + 1
        self.consuming_passwords_num.emit(PasswordsWriter.passwords_num)


if __name__ == "__main__":
    que = Queue()

    producer = PasswordsProducer('Producer', que, range(3, 4), "0123456789", 2)
    producer.start()

    consumers = []
    for i in range(PasswordsWriter.CONSUMER_NUM):
        consumer = PasswordsWriter("consumer " + str(i), que, "test.txt")
        consumers.append(consumer)
        consumer.start()

    producer.wait()
    for i in range(PasswordsWriter.CONSUMER_NUM):
        consumers[i].wait()

    print('==========All threads finished!========')
