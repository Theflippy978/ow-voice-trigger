# 守望先锋语音触发器

> 基于 PySide6 的 Windows 桌面工具，玩守望先锋时按下技能键自动播放语音包。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.11-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 快速开始

### 下载

1. 前往 [Releases](https://github.com/Theflippy978/ow-voice-trigger/ow-voice-trigger/releases) 页面
2. 下载最新版 `OW语音触发器.exe`

### 运行

双击运行即可，程序会自动生成 `sounds/` 目录和 `config.json` 配置文件。

> 建议右键"以管理员身份运行"，确保全局键盘钩子正常工作。

### 预置配置（可选）

Release 中还提供了个人整理的英雄配置（preset_config.json，重命名为 config.json 覆盖即可）和常用英雄的语音包合集（sounds_pack.zip，解压到程序同目录即可），可直接下载使用。

---

## 使用说明

### 1. 创建英雄

1. 点击左侧面板 **"新建"** 创建英雄（如"源氏"）
2. 在右侧设置切换热键（如 `Alt+1`）
3. 点击 **"保存快捷键"**

### 2. 添加按键绑定

1. 选中英雄 → 点击 **"+ 添加绑定"**
2. 输入名称（如"大招语音"）
3. 点击 **"录制"** 后按下目标按键（支持组合键如 `Ctrl+Q`，也支持纯修饰键如 `Shift`）
4. 点击 **"+"** 添加音频文件（mp3 / wav）
5. 设置冷却时间和播放模式
6. 点击确定

### 3. 游戏中使用

1. 点击左下角 **"开始监听"**
2. 进入守望先锋，按下绑定键即可播放语音
3. 按英雄热键（如 `Alt+1`）快速切换配置

### 音频文件

语音文件存放在 `sounds/` 目录，支持的格式：

| 格式 | 说明 |
|------|------|
| `.mp3` | 有损压缩，文件小 |
| `.wav` | 无损格式，延迟低 |

将音频文件直接放入 `sounds/` 目录，然后在绑定中添加即可。

## 功能特性

- **多英雄配置** — 为每个英雄独立设置按键绑定和语音包
- **快捷键切换** — 每个英雄可设独立热键，游戏中随时切换
- **多音频绑定** — 每个按键可绑定多个语音文件
- **游戏检测** — 仅在守望先锋前台时响应按键
- **主题切换** — 深色 / 浅色 / 跟随系统，自动读取 Windows 主题设置
- **窗口记忆** — 自动保存位置和大小，下次打开恢复原状
- **按键录制** — 点击录制后直接按下目标键，支持组合键和纯修饰键
- **音频缓存** — Sound 对象复用，避免重复加载文件
- **多语言检测** — 同时支持中英文游戏窗口标题

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 程序无法启动 | 右键"以管理员身份运行"，检查杀毒软件是否拦截 |
| 按键没反应 | 确认已点击"开始监听"，且守望先锋在前台 |
| 语音没声音 | 检查是否"以管理员身份运行"，是否添加了音频文件，主音量是否大于 0 |
| 杀毒软件误报 | PyInstaller 单文件打包常见问题，选择"允许运行" |
| 热键切换不生效 | 确认热键已保存，且目标英雄处于启用状态 |

---

## 开发指南

> 以下内容面向开发者，普通用户无需阅读。

### 环境要求

- Python >= 3.10
- Windows 10 / 11

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/Theflippy978/ow-voice-trigger/ow-voice-trigger.git
cd ow-voice-trigger

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

### 打包发布

双击 `build.bat`，自动完成以下步骤：

1. 安装打包依赖（PyInstaller、Pillow、pefile）
2. 执行 `pyinstaller --clean ow.spec`
3. 调用 `fix_icon.py` 修复 PE 图标资源
4. 清理缓存（`build/`、`__pycache__/` 目录）

输出文件：`dist/OW语音触发器.exe`

### 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 开发语言 |
| PySide6 (Qt 6) | GUI 框架，QSS 主题系统 |
| pygame-ce | 低延迟音频播放 |
| pynput | 全局键盘钩子 |
| psutil | 进程枚举，游戏检测 |
| PyInstaller | 单文件打包发布 |

### 项目结构

```
ow-voice-trigger/
│
├── main.py                  # 程序入口 · DPI 适配 · 主题初始化
├── build.bat                # 一键打包脚本
├── fix_icon.py              # 打包后图标资源修复工具
├── icon.ico                 # 应用图标
├── ow.spec                  # PyInstaller 配置（已裁剪无用 Qt 模块）
├── requirements.txt         # 依赖清单
│
├── core/                    # 核心逻辑层
│   ├── config.py            # 配置管理 · JSON 读写 · 工厂方法
│   ├── config.json          # 用户配置文件（默认模板）
│   ├── audio.py             # 音频播放 · 随机/顺序/随机不重复
│   ├── keyboard.py          # 全局键盘监听 · 游戏窗口检测
│   └── key_recorder.py      # 按键录制 · 独立线程 + Qt 信号桥
│
└── ui/                      # 界面层
    ├── main_window.py       # 主窗口 · 英雄列表 · 绑定树 · 监听控制
    ├── hero_dialog.py       # 英雄创建对话框
    ├── binding_dialog.py    # 绑定编辑对话框（含按键录制）
    ├── checkbox.py          # 自定义复选框（带对号绘制）
    └── styles.py            # 深色 / 浅色 QSS 样式表
```

### 核心模块

#### 配置管理 (`core/config.py`)

- JSON 持久化，原子写入（临时文件 + replace）防损坏
- 损坏时自动从备份恢复，多备份轮询
- 工厂方法创建英雄和绑定结构
- 兼容开发模式与 PyInstaller 冻结模式

#### 音频播放 (`core/audio.py`)

- Sound 对象缓存复用，避免重复加载文件
- 单文件：直接播放；播放前停止当前声音，避免叠加
- 多文件：随机 / 顺序 / 随机不重复 三种模式
- 全局主音量 + 绑定独立音量 双层控制
- 线程锁保护顺序/随机不重复状态

#### 键盘监听 (`core/keyboard.py`)

- `pynput` 全局钩子，`suppress=False` 不影响游戏输入
- `psutil` 遍历进程 + Win32 API 检测前台窗口
- 进程 + 窗口检测 500ms 缓存，减少重复遍历开销
- 多语言标题匹配（同时支持 "Overwatch" 和 "守望先锋"）
- 修饰键状态追踪，支持组合键绑定
- 支持纯修饰键触发（如单独按 `Shift` 即可触发）
- 冷却计时器基于绑定 ID 独立计算

#### 按键录制 (`core/key_recorder.py`)

- 独立工作线程录制，通过 Qt 信号桥 (`_RecordBridge`) 回调主线程
- 释放所有按键后自动结束，超时 5 秒保护
- 支持纯修饰键（仅按修饰键无主键时也能录制）
- 调用方通过 `on_record_start` / `on_record_end` 回调暂停/恢复监听

### 自定义主题

`ui/styles.py` 包含完整的 `DARK_STYLE` 和 `LIGHT_STYLE` QSS，可直接修改颜色变量。

## 许可证

MIT License
