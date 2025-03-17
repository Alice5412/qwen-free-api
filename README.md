# Qwen Browser API

这是一个通过Selenium浏览器(谷歌浏览器)自动化技术，将通义千问网页版封装为OpenAI兼容API的服务。

## 项目结构

```
.
├── api/                    # API相关模块
│   ├── __init__.py         # API初始化
│   └── routes.py           # API路由定义
├── browser/                # 浏览器相关模块
│   ├── __init__.py         # 浏览器模块初始化
│   ├── actions.py          # 浏览器操作函数
│   └── pool.py             # 浏览器池管理
├── utils/                  # 工具函数
│   ├── __init__.py         # 工具包初始化
│   ├── retry.py            # 重试装饰器
│   └── text.py             # 文本处理函数
├── config.py               # 配置管理
├── main.py                 # 主入口文件
├── login_example.py        # 登录脚本
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖列表
└── README.md               # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 登录说明

### 首次使用

如果您是首次使用本项目，需要先进行登录操作以创建浏览器用户数据。请按照以下步骤操作：

1. 首先运行登录脚本：

```bash
python login_example.py
```

2. 脚本会自动打开浏览器并导航到通义千问登录页面
3. 在脚本中填入您的登录信息（邮箱和密码）
4. 登录成功后，系统会保存您的登录状态到 `selenium_user_data` 目录
5. 按 Enter 键退出登录程序

### 注意事项

- 登录信息会保存在项目根目录下的 `selenium_user_data` 文件夹中
- 登录成功后，后续使用主程序时无需重复登录
- 如果登录状态失效，请重新运行登录脚本
- 请确保您的账号密码在 `login_example.py` 文件中正确配置


### 故障排除

如果遇到登录问题：

1. 确认网络连接正常
2. 验证账号密码是否正确
3. 尝试删除 `selenium_user_data` 目录后重新登录
4. 检查控制台输出的错误信息

## 配置说明

在`config.yaml`文件中可以修改以下配置：

```yaml
# 浏览器配置
headless: true              # 是否使用无头模式
page_load_timeout: 20       # 页面加载超时时间(秒)
wait_timeout: 15            # 等待元素超时时间(秒)
retry_max: 3                # 操作失败最大重试次数
retry_delay: 0.5            # 重试间隔时间(秒)
poll_interval: 0.2          # 轮询间隔时间(秒)

# 服务器配置
host: "0.0.0.0"             # 服务器监听地址
port: 5000                  # 服务器监听端口
```

## 启动服务

```bash
python main.py
```

## API使用

服务启动后，可以通过openAI的api方式进行调用，支持流式输出和非流式。

### 示例请求

您可以使用以下示例请求来调用API：

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "your_model_name",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你是谁？"}
  ],
  "stream": false
}'
```

- `base_url`: `http://localhost:5000/v1/chat/completions`
- `api`: 随意
- `model`: 随意

## 注意事项

1. 首次启动时会自动创建`selenium_user_data`目录用于存储浏览器数据，确保已经安装谷歌浏览器
2. 服务启动后会自动进行一次自调用测试，确保服务正常运行
3. 请求队列最大长度为5，超过会等待，最长等待时间为30秒

## 安全提示

- 请勿在公共环境中存储您的登录凭据
- 建议在本地开发环境中使用此项目
- 不要将包含您登录信息的文件提交到版本控制系统

## 贡献指南

欢迎对本项目进行贡献！以下是贡献的步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 免责声明

本项目仅供学习和研究使用，不得用于商业用途。使用本项目时请遵守通义千问的使用条款和相关法律法规。作者不对使用本项目产生的任何后果负责。
