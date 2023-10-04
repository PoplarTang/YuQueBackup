import threading
from concurrent.futures import ThreadPoolExecutor


class Worker:
    def __init__(self):
        self.thread = None
        self.pool = ThreadPoolExecutor(max_workers=5)

    def start_thread(self, target, args=None, kwargs=None):
        self.thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        self.thread.start()

    def start_pool(self, target, args=None, kwargs=None):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.pool.submit(target, *args, **kwargs)


if __name__ == '__main__':

    # 使用示例
    def my_task(message, count=1):
        for _ in range(count):
            print(message)


    worker = Worker()
    # worker.start_thread(my_task, args=("World",), kwargs={"count":3})  # 在新线程中运行自定义任务函数，并传递参数
    worker.start_pool(my_task, args=("Hello",), kwargs={"count": 5})  # 在线程池中运行自定义任务函数，并传递参数
