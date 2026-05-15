@echo off
echo ========================================
echo Hermes 案卷评查系统 - 前端安装脚本
echo ========================================
echo.

cd frontend

echo [1/3] 正在安装 npm 依赖...
call npm install
if %errorlevel% neq 0 (
    echo ❌ npm 安装失败！
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] 依赖安装完成！
echo.
echo [3/3] 正在启动开发服务器...
echo.
echo ========================================
echo 🚀 服务器将在 http://localhost:5173 启动
echo ========================================
echo.

call npm run dev
