"""
运行一个独立线程，用于执行长期循环发送任务，可以随时执行异步任务，内部维护一个消息队列（例如：发送蓝牙、串口消息）

这段代码定义了一个 TaskWorker 类，该类继承自 QThread 类，并使用队列实现了任务的异步执行。

"""

from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal


class TaskWorker(QThread):
    taskResult = pyqtSignal(object)
    taskError = pyqtSignal(Exception)
    taskFinished = pyqtSignal()

    def __init__(self, target):
        super(TaskWorker, self).__init__()
        self.do_task = target
        self.task_queue = Queue()
        self.is_running = True

    def run(self):
        while self.is_running:
            # 不断从队列中取出任务并执行，如果没有任务则阻塞
            task_arg = self.task_queue.get()
            # 如果取出的任务为 None，且线程已设置为关闭，则退出线程
            if task_arg is None and not self.is_running:
                break
            try:
                result = self.do_task(task_arg)
                self.taskResult.emit(result)
            except Exception as e:
                self.taskError.emit(e)

        self.taskFinished.emit()

    def signal_connect(self, result_handler=None, finished_handler=None, error_handler=None):

        # Connect the refresh_worker's signal to the handler slot
        if result_handler is not None:
            self.taskResult.connect(result_handler)
        if finished_handler is not None:
            self.taskFinished.connect(finished_handler)
        if error_handler is not None:
            self.taskError.connect(error_handler)

        return

    def join_queue(self, task):
        if not self.is_running:
            return

        self.task_queue.put(task)

    def stop(self):
        self.is_running = False
        # Put a None task to the queue to stop the thread
        self.task_queue.put(None)
