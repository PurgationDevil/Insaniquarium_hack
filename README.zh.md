<p align="center">
  <a href="README.md">English</a> |
  <strong>简体中文</strong>
</p>

仅做技术讨论，切勿用于商业用途

# 🐠 怪怪水族馆 修改器 (Insaniquarium Deluxe Trainer)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 一款用于《怪怪水族馆》(Insaniquarium Deluxe) 的存档修改器 + 内存修改器。

---

## ✨ 功能

### 💰 内存修改（实时生效）
- 一键连接游戏
- 读取/修改金币
- 锁定金币（花不完）

### 📂 存档修改（永久保存）
- 贝壳数量修改
- 关卡进度修改（大关/小关）
- 循环次数（Boss 击杀）
- 虚拟鱼缸宠物上限
- 一键解锁全部宠物/蛋
- 一键解锁虚拟鱼缸背景
- 一键获得银奖杯
- 一键解锁挑战模式按钮
- 🌟 一键全解锁（所有内容）
- 存档备份

### 🗂️ 存档支持
- 自动查找游戏进程
- 自动定位存档路径
- 手动切换 `user1` / `user2` / `user3` 存档

---

## 🖼️ 截图

| 主界面 | 存档修改器 |
|---|---|
| ![主界面](./screenshot_main.png) | ![存档界面](./screenshot_save.png) |

---

## 🚀 使用方法

### 方法一：下载 EXE（推荐）
1. 前往 [Releases](../../releases) 下载最新版 `InsaniquariumTrainer.exe`
2. 以**管理员身份**运行
3. 点击「连接游戏」即可开始修改

### 方法二：源码运行
```bash
# 1. 克隆仓库或直接网页下载 Insaniquarium_hack_v1.0.py 文件
git clone https://github.com/PurgationDevil/Insaniquarium_hack.git
cd 仓库名

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python Insaniquarium_hack_v1.0.py
```

---

## 📦 依赖

- Python 3.10+
- pymem
- tkinter（内置）
- psutil

---

## ⚠️ 注意事项

1. **内存修改**：游戏运行时生效，重启后失效
2. **存档修改**：**请先关闭游戏再修改存档**，否则游戏会覆盖你的修改
3. 建议修改前先点击「备份存档」，防止坏档
4. 如果杀毒软件报毒，属于误报（因为涉及内存读写）

---

## 🛠️ 开发环境打包

```bash
pyinstaller -F -w 怪怪水族馆外挂1.0.py
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)

---

## 🙏 致谢

- [Cheat Engine](https://www.cheatengine.org/) - 内存逆向工具
- [pymem](https://github.com/srounet/pymem) - Python 内存读写库

---

## 📬 反馈

邮箱：3395915226@qq.com

---

**⭐ 如果这个项目对你有帮助，欢迎给个 Star！** ⭐
