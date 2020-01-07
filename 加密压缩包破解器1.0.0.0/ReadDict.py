# %% 导入包
from PyQt5.QtCore import QThread, pyqtSignal
from queue import Queue


# %% 定义一个类，读取外部字典
class ReadDict(QThread):
    """
    生产者类
    """
    # 定义一些类变量
    password_num = 0
    # 定义一些信号
    producing_password = pyqtSignal(str)
    producing_password_num = pyqtSignal(int)

    def __init__(self, name: str, queue: Queue, dict_path: str, batch_size: int):
        """
        构造方法\n
        :param name: 线程名称
        :param queue: 队列
        :param dict_path: 外部字典文件路径字符串
        :param batch_size: 批量处理的密码数量
        """
        super(ReadDict, self).__init__()
        self.setObjectName(name)
        self.queue = queue
        self.dict_path = dict_path
        self.batch_size = batch_size

    def run(self):
        """
        运行线程\n
        :return:
        """
        passwords = []
        for password in self.generate_passwords():
            # 发射信号，当前处理的密码及序号
            self.emit_signal(password)
            # 将要批量写入的密码组成元组
            passwords.append(password)
            if len(passwords) == self.batch_size:
                self.queue.put(tuple(passwords))
                passwords.clear()
        self.queue.put(tuple(passwords))
        # 生成完全部密码之后要释放毒丸
        self.queue.put(tuple())

    def generate_passwords(self) -> [str]:
        """
        从文件枚举密码\n
        :return: 枚举密码的生成器
        """
        with open(self.dict_path) as f:
            for password in f:
                yield password.strip()

    def emit_signal(self, password: str):
        """
        向外发射信号\n
        :param password: 密码字符串
        :return:
        """
        self.producing_password.emit(password)
        ReadDict.password_num = ReadDict.password_num + 1
        self.producing_password_num.emit(ReadDict.password_num)
