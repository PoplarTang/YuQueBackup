
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Ui_settings_dialog import Ui_SettingsDialog
import sys
from store import *

class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        # 可以通过此设置，固定对话框的大小
        self.setFixedSize(self.width(), self.height())
        
        self.initUi()


    def initUi(self):
        # 先尝试加载本地的secret.yaml
        access_token, user_agent, download_pic = load_config()
        if access_token:
            self.ui.edit_token.setText(access_token)
        if user_agent:
            self.ui.edit_agent.setText(user_agent)
            
        self.ui.cb_download_pic.setChecked(download_pic)
        

    def accept(self):
        print("accept")
        access_token = self.ui.edit_token.text()
        user_agent = self.ui.edit_agent.text()
        download_pic = self.ui.cb_download_pic.isChecked()
        save_config(access_token, user_agent, download_pic)
        super().accept()

    def reject(self):
        super().reject()
        print("reject")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SettingsDialoglog()
    dialog.show()
    sys.exit(app.exec_())