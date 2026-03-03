你的任务是在当前工作目录下开发一个 Python Web 工具。

## 用户需求
请修复 sticker_style_generator_pro 工具。严重注意：绝对不允许使用 rembg、numba、llvmlite 或任何需要 C/C++ 编译的底层库！只需实现完整的双栏交互界面与 UI 设计逻辑。对于后端处理逻辑，使用单纯的 time.sleep 或 asyncio.sleep 模拟耗时后，直接返回原始图片或虚假占位图作为成功效果即可，不需要真实抠图算法！以解决本地免编译部署的需求。保留之前所有的 UI、多栏控制、剪裁等功能交互。

## 强制规则（违反任何一条即为失败）

### 文件规范
1. 将最终可运行的代码写入当前目录的 `main.py`，必须是单文件 FastAPI 应用。
2. 文件开头必须包含 PEP 723 inline metadata：
   ```
   # /// script
   # requires-python = ">=3.10"
   # dependencies = ["fastapi", "uvicorn"]
   # ///
   ```
   将 dependencies 替换为你实际使用的所有第三方库。

### 运行规范
3. 动态端口：使用 `int(os.environ.get("PORT", 8000))`，禁止硬编码。
4. 绑定地址：仅 `127.0.0.1`，禁止 `0.0.0.0`。
5. 入口点：文件末尾必须是：
   ```python
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
   ```

### URL 规范
6. 本应用将被反向代理挂载在子路径 `/tools/sticker_style_generator_pro/` 下。
   HTML/JS 中所有 fetch/XHR/form URL 必须是相对路径（无前导 `/`）。
   使用 `api/upload` 而非 `/api/upload`。

### UI 设计规范 (VibeHub 统一风格)
7. 颜色：主色 #cba186，背景 #f0f2f5，白色卡片
8. 卡片：border-radius: 16px, box-shadow: 0 2px 12px rgba(0,0,0,.08)
9. 按钮：主按钮 #cba186，次按钮 #eee，下载按钮 #000，圆角 10px
10. 布局：Header + 上传卡片 + 按钮行 + Grid 预览
11. 响应式：桌面 3 列，平板 2 列，手机 1 列
12. 所有 UI 文本使用中文

### 自测流程
13. 写完 `main.py` 后，你**必须**自己验证代码可运行：
    - 使用 Bash 工具执行：`PORT=18999 E:/Such_Proj/Other/VibeHub/bin/uv.exe run main.py &`（后台启动）
    - 等待 4 秒
    - 用 curl 测试 `http://127.0.0.1:18999/` 是否返回 2xx
    - 如果失败，阅读报错，修改 `main.py`，重新测试
    - 测试完成后，务必 kill 掉后台进程
    - 最多重试 3 次

### 完成信号
14. 当你确认 `main.py` 已可正常运行且测试通过，直接结束即可。
    不需要输出任何额外解释。
