# AX PP300 上位机 (FastAPI + Quasar + WebSocket)

AX PP300 升降压数控电源的 Web 上位机，基于 **FastAPI** 后端 + **Quasar/Vue3** 前端，前后端通过 **WebSocket** 实时通信。

环境统一使用 [**pixi**](https://pixi.sh) 管理，同时包含 Python 与 Node.js 依赖。

---

## 项目结构

```
.
├── backend/              # FastAPI 后端
│   ├── ax_pp300/
│   │   ├── protocol.py       # 串口协议封装（组帧/解析）
│   │   ├── serial_client.py  # 串口客户端 + 后台轮询 + 状态回调
│   │   └── main.py           # FastAPI 应用（REST + WebSocket）
│   ├── README.md
│   └── pyproject.toml
├── frontend/             # Quasar CLI (Vite) 前端
│   ├── src/
│   │   ├── pages/IndexPage.vue       # 主界面
│   │   ├── layouts/MainLayout.vue    # 布局
│   │   ├── composables/useWebSocket.ts
│   │   └── stores/powerStore.ts
│   ├── package.json
│   └── quasar.config.ts
├── pixi.toml             # pixi 工作区配置
└── README.md             # 本文件
```

---

## 环境要求

- Windows（因为串口通常是 `COMx`）
- 已安装 [pixi](https://pixi.sh)

> 首次运行会自动下载 Python 3.14+、Node.js 24+、pnpm 10+ 到 `.pixi/envs/default` 中，无需手动安装。

---

## 快速开始

### 1. 安装所有依赖

```powershell
pixi install
pixi run install-frontend
```

### 2. 启动后端（FastAPI + WebSocket）

```powershell
pixi run dev-backend
```

后端默认监听 `http://0.0.0.0:8000`，WebSocket 地址为 `ws://127.0.0.1:8000/ws`。

### 3. 启动前端（Quasar dev）

在**另一个终端**中执行：

```powershell
pixi run dev-frontend
```

前端开发服务器默认运行在 `http://localhost:9000`，打开后即可看到交互界面。

---

## 使用说明

### 前端界面功能

1. **串口连接**：输入串口号（如 `COM3`）和波特率，点击【连接串口】。
2. **WebSocket 连接**：点击【连接 WebSocket】或串口连接成功后会自动连接。
3. **实时数据**：连接成功后，页面会实时显示：
   - 输出电压 / 电流 / 功率
   - 输入电压
   - 设备温度
   - 恒压(CV) / 恒流(CC) 模式
   - 输出开关状态
4. **控制面板**：
   - 设置目标电压（mV）
   - 设置目标电流（mA）
   - 打开 / 关闭输出

### 后端 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 |
| POST | `/connect` | 连接串口 |
| POST | `/disconnect` | 断开串口 |
| GET | `/status` | 获取当前缓存状态 |
| POST | `/voltage` | 设置电压 |
| POST | `/current` | 设置电流 |
| POST | `/output` | 开关输出 |
| POST | `/ovp` | 过压保护 |
| POST | `/ocp` | 过流保护 |
| WebSocket | `/ws` | 实时状态推送 + 命令通道 |

---

## 通信协议

详见 `backend/README.md`。

简要说明：
- 发送帧：6 字节（`帧头 A5 + 标识帧 + 数据低八位 + 数据高八位 + 校验位 + 帧尾 5A`）
- 查询回传：15 字节，包含电压、电流、功率、输入电压、温度、模式、开关状态

---

## 常见问题

### `quasar build` 报错 `fileName must be strings...`

这是 **Vite 8 / Rolldown** 在 Windows 中文路径下的已知问题。开发模式（`quasar dev`）不受影响。

**解决方法**：将项目复制到纯英文路径（如 `D:\Projects\ax_pp300`）后再执行生产构建。

### 串口连接失败

- 确认电源已接通并连接到正确的 COM 口
- 检查波特率：协议未明确标注，默认 **9600**，若失败可尝试 **115200**

---

## 技术栈

- **后端**：Python, FastAPI, WebSocket, pyserial
- **前端**：Vue 3, Quasar Framework, TypeScript, Pinia
- **环境管理**：pixi (conda-forge + PyPI)
