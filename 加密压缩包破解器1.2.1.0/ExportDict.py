# %% 导入包
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from WriteDict import PasswordsWriter, PasswordsProducer
from queue import Queue
from copy import deepcopy
from string import digits, ascii_lowercase, ascii_uppercase, punctuation


# %% 定义一个类，用于管理导出字典的后台任务
class ExportDict(QThread):
    """
    管理导出字典的后台任务的类
    """
    # 定义一些常量
    EXPORT_COMPLETED = "导出密码完成!"
    # 定义一些信号
    producing_password = pyqtSignal(str)
    producing_password_num = pyqtSignal(int)
    consuming_passwords = pyqtSignal(str)
    consuming_passwords_num = pyqtSignal(int)

    def __init__(
            self, name: str, seed_selection: (bool,), digit_range: range,
            file_path: str, consumer_number: int, batch_size: int
    ):
        """
        构造方法\n
        :param name: 线程名称
        :param seed_selection: 最上面的几个复选框的勾选情况
        :param digit_range: 位数取值范围
        :param file_path: 文件路径字符串
        :param consumer_number: 消费者数量
        :param batch_size: 密码元组长度
        """
        super(ExportDict, self).__init__()
        self.setObjectName(name)
        self.seed = ExportDict.generate_seed(seed_selection)
        self.digit_range = deepcopy(digit_range)
        self.file_path = file_path
        self.consumer_number = consumer_number
        self.batch_size = batch_size
        self.producer = None
        self.producer: PasswordsProducer
        self.consumers = []

    @staticmethod
    def generate_seed(seed_selection: (bool,)) -> str:
        """
        根据复选框选项生成种子\n
        :param seed_selection: 最上方的复选框勾选情况，由bool构成的数组
        :return: 由字符串构成的种子
        """
        result = ""
        if seed_selection[0]:
            result = result + digits
        if seed_selection[1]:
            result = result + ascii_lowercase
        if seed_selection[2]:
            result = result + ascii_uppercase
        if seed_selection[3]:
            result = result + punctuation
        return result

    def run(self):
        """
        运行线程\n
        :return:
        """
        queue = Queue()
        PasswordsProducer.password_num = 0
        PasswordsWriter.passwords_num = 0
        PasswordsWriter.CONSUMER_NUM = self.consumer_number
        # 启动生产者
        self.producer = PasswordsProducer(
            "producer", queue, self.digit_range, self.seed, self.batch_size
        )
        self.producer.producing_password.connect(self.on_producing_password, type=Qt.DirectConnection)
        self.producer.producing_password_num.connect(self.on_producing_password_num, type=Qt.DirectConnection)
        self.producer.start()
        # 启动消费者
        self.consumers = []
        for i in range(PasswordsWriter.CONSUMER_NUM):
            consumer = PasswordsWriter("consumer " + str(i), queue, self.file_path)
            consumer.consuming_passwords.connect(self.on_consuming_passwords, type=Qt.DirectConnection)
            consumer.consuming_passwords_num.connect(self.on_consuming_passwords_num, type=Qt.DirectConnection)
            self.consumers.append(consumer)
            consumer.start()
        # 等待生产者结束
        self.producer.wait()
        self.producer = None
        self.producing_password_complete()
        # 等待消费者结束
        for consumer in self.consumers:
            consumer.wait()
        self.consumers.clear()
        print("Export dict done")
        self.consuming_passwords_complete()

    def stop(self):
        """
        终止线程\n
        :return:
        """
        self.producer.stop()
        for consumer in self.consumers:
            consumer.stop()

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
        print("生成密码序号", password_num)
        self.producing_password_num.emit(password_num)

    def on_consuming_passwords(self, passwords: str):
        """
        处理消费者密码元组信号的槽函数\n
        :param passwords: 由字符串组成的元组
        :return:
        """
        self.consuming_passwords.emit("正在写入密码 " + ' '.join(passwords))

    def on_consuming_passwords_num(self, passwords_num: int):
        """
        处理消费者密码元组序数的槽函数\n
        :param passwords_num: 密码元组的序数
        :return:
        """
        print("写入密码序号", passwords_num)
        self.consuming_passwords_num.emit(passwords_num)

    def producing_password_complete(self):
        """
        生产者生成完密码后调用的函数\n
        :return:
        """
        self.producing_password.emit("生成密码完成")
        self.producing_password_num.emit(self.get_passwords_count() + 1)

    def consuming_passwords_complete(self):
        """
        消费者写完密码后调用的函数\n
        :return:
        """
        self.consuming_passwords.emit(ExportDict.EXPORT_COMPLETED)
        self.consuming_passwords_num.emit(self.get_batch_count() + 1)


if __name__ == "__main__":
    my_thread = ExportDict("export dict thread", (True, False, False, False), range(2, 3), "text.txt", 6, 2)
    my_thread.start()
    my_thread.wait()