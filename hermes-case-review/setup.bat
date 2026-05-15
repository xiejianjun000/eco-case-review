"""
HERMES 案卷评查系统 - 快速部署脚本
用于 Windows 环境
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """执行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"命令: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} 成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败！")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 HERMES 案卷评查系统 - 快速部署")
    print("="*60)
    
    # 1. 检查 Python
    print("\n🔍 检查 Python 环境...")
    try:
        version = sys.version_info
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("⚠️  建议使用 Python 3.8+")
    except:
        print("❌ 未找到 Python，请先安装 Python 3.8+")
        return
    
    # 2. 创建虚拟环境
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    
    if not venv_dir.exists():
        if not run_command(
            f'python -m venv "{venv_dir}"',
            "创建虚拟环境"
        ):
            return
    else:
        print("\n✅ 虚拟环境已存在")
    
    # 3. 激活虚拟环境并安装依赖
    pip_exe = venv_dir / "Scripts" / "pip.exe"
    
    if not run_command(
        f'"{pip_exe}" install -r requirements.txt',
        "安装依赖包"
    ):
        return
    
    # 4. 复制环境变量文件
    env_example = project_dir / ".env.example"
    env_file = project_dir / ".env"
    
    if not env_file.exists() and env_example.exists():
        run_command(
            f'copy "{env_example}" "{env_file}"',
            "创建环境变量文件"
        )
        print("\n⚠️  请编辑 .env 文件，填入您的 API Key")
        print(f"   文件位置: {env_file}")
    
    # 5. 运行测试
    print("\n\n🧪 运行测试...")
    pytest_exe = venv_dir / "Scripts" / "pytest.exe"
    run_command(
        f'"{pytest_exe}" tests/test_engine.py -v',
        "执行单元测试"
    )
    
    # 6. 完成
    print("\n\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    print("\n下一步操作：")
    print("\n1. 编辑 .env 文件，填入 API Key:")
    print(f"   code {env_file}")
    print("\n2. 使用 CLI:")
    print("   venv\\Scripts\\python -m src.main review ./case.json")
    print("\n3. 启动 API 服务:")
    print("   venv\\Scripts\\python -m src.api.routes")
    print("\n4. 访问 API 文档:")
    print("   http://localhost:8000/docs")
    print("\n5. 查看帮助:")
    print("   venv\\Scripts\\python -m src.main --help")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
