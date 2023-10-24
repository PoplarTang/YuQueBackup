"""
PyQt5版GUI工具
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Ui_main_window import Ui_MainWindow
from settings_dialog import SettingsDialog
import sys
import store
from yuque.yuque_main import YuQueMain


class MainWindow(QMainWindow):
    log_update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # 创建对象
        self.ui = Ui_MainWindow()
        # 初始化内容
        self.ui.setupUi(self)

        self.access_token = None
        self.user_agent = None
        self.download_pic = False

        self.repo_all_model = QStandardItemModel()
        self.repo_all_model.setHorizontalHeaderLabels(["仓库名", "命名空间"])
        self.ui.tv_all.setModel(self.repo_all_model)
        # 设置表格列宽权重
        header = self.ui.tv_all.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.log_update_signal.connect(self.update_log)

        # 初始化ui
        self.init_ui()
        self.ui.tabWidget.setCurrentIndex(0)

    @pyqtSlot(str)
    def update_log(self, log):
        self.ui.edit_log.appendPlainText(log)
        # 滚动到底部
        self.ui.edit_log.moveCursor(QTextCursor.End)

    def show_config(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.update_config_state()

    def download_all(self):
        if not self.check_access_info():
            return

        yuque = YuQueMain(self.access_token, self.user_agent)
        yuque.log_signal = self.log_update_signal
        yuque.save_all_repos()

    def load_all(self):
        if not self.check_access_info():
            return

        self.log_update_signal.emit("加载所有仓库")

        try:
            yuque = YuQueMain(self.access_token, self.user_agent)
            repo_list = yuque.session.get_repo_list()  # -------------------> 获取仓库列表
            # 清除所有数据行, 但不清除标题
            self.repo_all_model.removeRows(0, self.repo_all_model.rowCount())

            for repo in repo_list["data"]:
                name, namespace, description = (
                    repo["name"],
                    repo["namespace"],
                    repo["description"],
                )
                self.repo_all_model.appendRow(
                    [QStandardItem(name), QStandardItem(namespace)]
                )
        except Exception as e:
            self.log_update_signal.emit(str(e))
        else:
            self.log_update_signal.emit("所有仓库加载完毕")

    def check_access_info(self):
        if (
            self.access_token is None
            or self.access_token == ""
            or self.user_agent is None
            or self.user_agent == ""
        ):
            QMessageBox.warning(self, "警告", "请先配置access_token和user_agent")
            self.log_update_signal.emit("请先配置access_token和user_agent")
            return False

        return True

    def init_ui(self):
        self.update_config_state()
        self.ui.btn_config.clicked.connect(self.show_config)
        self.ui.btn_all_load.clicked.connect(self.load_all)
        self.ui.btn_all_download.clicked.connect(self.download_all)

    def update_config_state(self):
        access_token, user_agent, download_pic = store.load_config()
        self.access_token = access_token
        self.user_agent = user_agent
        self.download_pic = download_pic

        if access_token:
            self.ui.cb_token_state.setChecked(True)
            self.ui.cb_token_state.setText("已配置")
        else:
            self.ui.cb_token_state.setChecked(False)
            self.ui.cb_token_state.setText("未配置")

        if user_agent:
            self.ui.cb_agent_state.setChecked(True)
            self.ui.cb_agent_state.setText("已配置")
        else:
            self.ui.cb_agent_state.setChecked(False)
            self.ui.cb_agent_state.setText("未配置")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
