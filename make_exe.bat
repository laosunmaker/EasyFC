@echo off
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
if not "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR%\"
set "OUTPUT_DIR=%SCRIPT_DIR%out"
echo 清理输出目录...
if exist "%OUTPUT_DIR%" rd /s /q "%OUTPUT_DIR%"
echo 步骤1:开始编译...
python -m nuitka ^
--onefile ^
--msvc=latest ^
--output-dir=%OUTPUT_DIR% ^
--enable-plugin=pyside6 ^
--plugin-enable=pylint-warnings ^
--windows-icon-from-ico=%SCRIPT_DIR%file.ico ^
--output-filename=EasyFC ^
--jobs=8 --lto=yes --prefer-source-code ^
--windows-console-mode=disable --remove-output %SCRIPT_DIR%main.py

if %errorlevel% neq 0 (
    echo 编译失败，退出码: %errorlevel%
    pause >nul
    exit /b %errorlevel%
)

echo 步骤2:复制资源文件...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
echo 复制图标文件...
copy /Y "%SCRIPT_DIR%file.ico" "%OUTPUT_DIR%\" >nul
echo 创建样式文件夹...
if not exist "%OUTPUT_DIR%\styles" mkdir "%OUTPUT_DIR%\styles"
echo 复制样式文件...
copy /Y "%SCRIPT_DIR%styles\file_classifier.qss" "%OUTPUT_DIR%\styles\" >nul
echo 创建配置文件夹...
if not exist "%OUTPUT_DIR%\config" mkdir "%OUTPUT_DIR%\config"
echo 复制配置文件...
copy /Y "%SCRIPT_DIR%config\delimiter_configs.json" "%OUTPUT_DIR%\config\" >nul
copy /Y "%SCRIPT_DIR%config\extension_configs.json" "%OUTPUT_DIR%\config\" >nul
echo 复制完成！

if exist "%OUTPUT_DIR%\EasyFC.exe" (
    echo 打包成功！文件位置: %OUTPUT_DIR%\EasyFC.exe
) else (
    echo 警告: 未找到生成的 exe 文件
)

echo 按任意键退出...
pause >nul
