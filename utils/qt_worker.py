"""
线程管理器，用于管理线程的创建、启动、停止等。
包含两种线程启动方式：
1. start 运行一个独立线程，用于执行一次性短期任务（例如：并行任务，多线程下载）、长期循环接收任务（例如：阻塞式接收蓝牙、串口消息）
2. start_in_thread_pool 在一个线程池里运行任务，用于执行非定期触发型短期任务，避免线程资源浪费（例如：数据库操作、文件写入、网络数据下载）

其中包含了一个 Worker 类
	● Worker 类用于创建线程任务
Worker 类继承自 QRunnable 类，用于创建线程任务。
    ● 其中包含了一个 run 方法，用于执行线程任务
    ● 一个 signal_connect 方法，用于连接信号槽
    ● 一个 stop 方法，用于停止线程任务
    ● 一个 emit_msg 方法，用于发送消息。
"""
import inspect
from typing import Callable

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThread, QThreadPool


class WorkerSignals(QObject):
    signal_finished = pyqtSignal()
    signal_error = pyqtSignal(Exception)
    signal_result = pyqtSignal(object)
    signal_msg = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, target: Callable, args=None, kwargs=None):
        super().__init__()
        self.setAutoDelete(True)  # 自动删除，避免内存泄漏
        self.__func = target
        self.__args = args if args else ()
        self.__kwargs = kwargs if kwargs else {}
        self.__signals = WorkerSignals()
        self.is_running = False
        self.worker_thread: WorkerThread = None

    def run(self):
        self.is_running = True
        try:
            # 如果func的第一个参数是Worker类型，则将self作为第一个参数传入
            if self.__is_worker_func(self.__func):
                result = self.__func(self, *self.__args, **self.__kwargs)
            else:
                # 否则，直接传入参数
                result = self.__func(*self.__args, **self.__kwargs)
            self.__signals.signal_result.emit(result)
        except Exception as e:
            self.__signals.signal_error.emit(e)
        finally:
            self.is_running = False
            self.__signals.signal_finished.emit()

    def signal_connect(self, msg_handler=None, result_handler=None, finished_handler=None, error_handler=None):
        if msg_handler:
            self.__signals.signal_msg.connect(msg_handler)
        if result_handler:
            self.__signals.signal_result.connect(result_handler)
        if finished_handler:
            self.__signals.signal_finished.connect(finished_handler)
        if error_handler:
            self.__signals.signal_error.connect(error_handler)
        return self

    def stop(self):
        self.is_running = False

    def emit_msg(self, msg):
        self.__signals.signal_msg.emit(msg)

    def start(self, daemon=True):
        """
        1. 运行一个独立线程，用于执行一次性短期任务（例如：并行任务，多线程下载）、长期循环接收任务（例如：阻塞式接收蓝牙、串口消息）
        :return:
        """
        self.worker_thread = WorkerThread(self)
        self.worker_thread.daemon = daemon
        self.worker_thread.start()
        return self.worker_thread

    def start_in_thread_pool(self):
        """
        2. 在一个线程池里运行任务，用于执行非定期的短期任务，避免线程资源浪费（例如：文件写出、网络数据下载）
        :param refresh_worker: 任务
        """
        QThreadPool.globalInstance().start(self)

    @classmethod
    def __is_worker_func(cls, func: Callable):
        """
        判断一个函数是否是worker函数，worker函数的第一个参数必须是Worker类型
        :param func:
        :return:
        """
        sig = inspect.signature(func)
        # 判断第一个参数是否是Worker类型，或者参数名是否是worker
        param_keys = list(sig.parameters.keys())
        if len(param_keys) > 0:
            first_param = sig.parameters[param_keys[0]]
            if first_param.annotation == Worker:
                return True
            if first_param.name == "worker":
                return True

        return False


class WorkerThread(QThread):

    def __init__(self, worker: Worker):
        super().__init__()
        self.__worker = worker

    def run(self):
        self.__worker.run()
