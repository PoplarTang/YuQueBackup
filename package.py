import PyInstaller.__main__

# 这里的是不需要打包进去的三方模块，可以减少软件包的体积
excluded_modules = [
    "scipy",
    "matplotlib",
]

append_string = []
for mod in excluded_modules:
    append_string += [f'--exclude-module={mod}']

PyInstaller.__main__.run([
    '-y',  # 如果dist文件夹内已经存在生成文件，则不询问用户，直接覆盖
    # '-p', 'src', # 设置 Python 导入模块的路径（和设置 PYTHONPATH 环境变量的作用相似）。也可使用路径分隔符（Windows 使用分号;，Linux 使用冒号:）来分隔多个路径
    'main_window.py',  # 主程序入口
    # '--onedir',  # -D 文件夹
    '--onefile', # -F 单文件
    # '--nowindowed', # -c 无窗口
    '--windowed',  # -w 有窗口
    '-n', '语雀备份助手',
    '-i', 'ui/img/yq_logo.ico',
    '--add-data=ui/img;ui/img',  # 用法：pyinstaller main.py –add-data=src;dest。windows以;分割，mac,linux以:分割
    *append_string
])
