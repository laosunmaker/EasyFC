"""文件分类器 ViewModel"""

import json
import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QThread

from models.file_classifier import ExtensionClassifier, DelimiterClassifier


class ClassificationWorker(QThread):
    """分类工作线程"""

    progress_updated = Signal(int, str)
    finished = Signal(dict)
    error_occurred = Signal(str)

    def __init__(
        self,
        classification_mode: int,
        source_folder: str,
        target_folder: str,
        delete_source: bool,
        extension_map_json: str = "",
        delimiter_start: str = "_",
        delimiter_end: str = "_",
        delimiter_start_pos: int = 1,
        delimiter_end_pos: int = 2,
        scan_subfolder: bool = True,
        specify_depth: bool = False,
        scan_depth: int = 1,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._classification_mode = classification_mode
        self._source_folder = source_folder
        self._target_folder = target_folder
        self._delete_source = delete_source
        self._extension_map_json = extension_map_json
        self._delimiter_start = delimiter_start
        self._delimiter_end = delimiter_end
        self._delimiter_start_pos = delimiter_start_pos
        self._delimiter_end_pos = delimiter_end_pos
        self._scan_subfolder = scan_subfolder
        self._specify_depth = specify_depth
        self._scan_depth = scan_depth

    def run(self):
        """执行分类任务"""
        try:
            from utils.file_utils import get_folder_files_by_depth

            self.progress_updated.emit(10, "正在扫描文件...")

            if self._scan_subfolder:
                if self._specify_depth:
                    max_depth = self._scan_depth
                else:
                    max_depth = 100
            else:
                max_depth = 1

            files = get_folder_files_by_depth(self._source_folder, max_depth=max_depth)
            total_files = len(files)

            if total_files == 0:
                self.finished.emit({
                    "success_count": 0,
                    "failed_count": 0,
                    "failed_files": [],
                    "success_files": [],
                    "total_files": 0
                })
                return

            self.progress_updated.emit(20, f"找到 {total_files} 个文件，开始分类...")

            if self._classification_mode == 0:
                result = self._classify_by_extension(files, total_files)
            else:
                result = self._classify_by_delimiter(files, total_files)

            self.progress_updated.emit(100, "分类完成")
            self.finished.emit(result)

        except Exception as e:
            self.error_occurred.emit(f"分类失败: {str(e)}")

    def _classify_by_extension(self, files: list, total_files: int) -> dict:
        """使用扩展名分类"""
        extension_map = json.loads(self._extension_map_json)

        classifier = ExtensionClassifier(
            extensions_map=extension_map,
            target_dir=self._target_folder,
            delete_source=self._delete_source
        )

        result = classifier.classify(files, progress_callback=self._create_progress_callback(total_files))
        result["total_files"] = total_files
        return result

    def _classify_by_delimiter(self, files: list, total_files: int) -> dict:
        """使用分隔符分类"""
        classifier = DelimiterClassifier(
            target_dir=self._target_folder,
            delimiter_start_str=self._delimiter_start,
            delimiter_end_str=self._delimiter_end,
            delimiter_start_pos=self._delimiter_start_pos,
            delimiter_end_pos=self._delimiter_end_pos,
            delete_source=self._delete_source
        )

        result = classifier.classify(files, progress_callback=self._create_progress_callback(total_files))
        result["total_files"] = total_files
        return result

    def _create_progress_callback(self, total_files: int):
        """创建进度回调函数"""
        def callback(processed: int, file_name: str):
            if total_files > 0:
                percent = int(20 + (processed / total_files) * 80)
                display_name = self._truncate_filename(file_name, max_length=40)
                self.progress_updated.emit(percent, f"正在处理: {display_name}")

        return callback

    @staticmethod
    def _truncate_filename(filename: str, max_length: int = 40) -> str:
        """截断过长的文件名"""
        if len(filename) <= max_length:
            return filename

        name, ext = os.path.splitext(filename)
        ext_len = len(ext)

        available_len = max_length - ext_len - 3
        if available_len < 5:
            return filename[:max_length - 3] + "..."

        truncated_name = name[:available_len] + "..."
        return truncated_name + ext


class FileClassifierViewModel(QObject):
    """文件分类器 ViewModel"""

    classification_started = Signal()
    classification_finished = Signal(dict)
    progress_updated = Signal(int, str)
    error_occurred = Signal(str)
    status_changed = Signal(str)

    source_folder_changed = Signal(str)
    target_folder_changed = Signal(str)
    classification_mode_changed = Signal(int)
    delete_source_changed = Signal(bool)
    extension_map_changed = Signal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._source_folder: str = ""
        self._target_folder: str = ""
        self._classification_mode: int = 0
        self._delete_source: bool = False
        self._extension_map_json: str = self._load_extension_map_from_config()
        self._delimiter_start: str = "_"
        self._delimiter_end: str = "_"
        self._delimiter_start_pos: int = 1
        self._delimiter_end_pos: int = 2
        self._is_classifying: bool = False
        self._worker: Optional[ClassificationWorker] = None
        self._classification_result: Optional[dict] = None
        self._scan_subfolder: bool = True
        self._specify_depth: bool = False
        self._scan_depth: int = 1

    def _default_extension_map(self) -> str:
        """默认扩展名映射"""
        default_map = {
            "txt": "文本文件",
            "doc": "Word 文档",
            "docx": "Word 文档",
            "xls": "Excel 文档",
            "xlsx": "Excel 文档",
            "ppt": "PowerPoint 演示文稿",
            "pptx": "PowerPoint 演示文稿",
            "jpg": "JPEG 图像",
            "jpeg": "JPEG 图像",
            "png": "PNG 图像",
            "gif": "GIF 图像",
            "bmp": "BMP 图像",
            "svg": "SVG 图像",
            "mp4": "MP4 视频",
            "avi": "AVI 视频",
            "mov": "MOV 视频",
            "mkv": "MKV 视频",
            "wmv": "WMV 视频",
            "mp3": "MP3 音频",
            "wav": "WAV 音频",
            "flac": "FLAC 音频",
            "aac": "AAC 音频",
            "zip": "压缩文件",
            "rar": "压缩文件",
            "7z": "压缩文件",
            "tar": "压缩文件",
            "gz": "压缩文件",
            "py": "Python 文件",
            "java": "Java 文件",
            "js": "JavaScript 文件",
            "ts": "TypeScript 文件",
            "html": "HTML 文件",
            "css": "CSS 文件",
            "json": "JSON 文件",
            "xml": "XML 文件",
            "md": "Markdown 文件",
            "sql": "SQL 文件",
            "cpp": "C++ 文件",
            "c": "C 文件",
            "h": "头文件",
            "cs": "C# 文件",
            "go": "Go 文件",
            "rs": "Rust 文件",
            "php": "PHP 文件",
            "rb": "Ruby 文件",
            "swift": "Swift 文件",
            "kt": "Kotlin 文件",
            "exe": "可执行文件",
            "msi": "安装程序",
            "apk": "Android 安装包",
            "ipa": "iOS 安装包",
            "pdf": "PDF 文件",
            "csv": "CSV 表格",
            "tif": "TIFF 图像",
            "tiff": "TIFF 图像",
            "webp": "WebP 图像",
            "ico": "图标文件",
            "psd": "Photoshop 文件",
            "ai": "Illustrator 文件",
            "raw": "RAW 图像",
            "heic": "HEIC 图像",
            "heif": "HEIF 图像",
            "flv": "FLV 视频",
            "webm": "WebM 视频",
            "m4v": "M4V 视频",
            "mpg": "MPEG 视频",
            "mpeg": "MPEG 视频",
            "3gp": "3GP 视频",
            "rmvb": "RMVB 视频",
            "ogv": "OGG 视频",
            "ogg": "OGG 音频或视频",
            "oga": "OGG 音频",
            "wma": "WMA 音频",
            "m4a": "M4A 音频",
            "opus": "Opus 音频",
            "mid": "MIDI 音频",
            "midi": "MIDI 音频",
            "aiff": "AIFF 音频",
            "au": "AU 音频",
            "bz2": "BZip2 压缩文件",
            "bz": "BZip 压缩文件",
            "xz": "XZ 压缩文件",
            "lz": "LZ 压缩文件",
            "lzh": "LZH 压缩文件",
            "cab": "CAB 压缩文件",
            "jar": "Java 归档文件",
            "war": "WAR 文件",
            "ear": "EAR 文件",
            "class": "Java 字节码文件",
            "jsp": "JSP 文件",
            "asp": "ASP 文件",
            "aspx": "ASP.NET 文件",
            "vue": "Vue 文件",
            "jsx": "JSX 文件",
            "tsx": "TSX 文件",
            "sass": "Sass 文件",
            "scss": "SCSS 文件",
            "less": "Less 文件",
            "yaml": "YAML 文件",
            "yml": "YAML 文件",
            "toml": "TOML 文件",
            "ini": "INI 配置文件",
            "cfg": "配置文件",
            "conf": "配置文件",
            "properties": "Properties 文件",
            "env": "环境变量文件",
            "sh": "Shell 脚本",
            "bash": "Bash 脚本",
            "zsh": "Zsh 脚本",
            "ps1": "PowerShell 脚本",
            "bat": "批处理文件",
            "cmd": "命令脚本",
            "vbs": "VBScript 文件",
            "lua": "Lua 文件",
            "pl": "Perl 文件",
            "pm": "Perl 模块",
            "r": "R 文件",
            "m": "MATLAB 或 Objective-C 文件",
            "mat": "MATLAB 数据文件",
            "scala": "Scala 文件",
            "groovy": "Groovy 文件",
            "dart": "Dart 文件",
            "elm": "Elm 文件",
            "erl": "Erlang 文件",
            "ex": "Elixir 文件",
            "exs": "Elixir 脚本",
            "fs": "F# 文件",
            "fsx": "F# 脚本",
            "hs": "Haskell 文件",
            "lhs": "Haskell 文件",
            "ml": "OCaml 文件",
            "mli": "OCaml 接口文件",
            "pas": "Pascal 文件",
            "pp": "Pascal 文件",
            "dpr": "Delphi 项目文件",
            "dfm": "Delphi 窗体文件",
            "vb": "Visual Basic 文件",
            "vbp": "VB 项目文件",
            "frm": "VB 窗体或 MySQL 表定义文件",
            "bas": "BASIC 文件",
            "for": "Fortran 文件",
            "f90": "Fortran 90 文件",
            "f95": "Fortran 95 文件",
            "asm": "汇编语言文件",
            "s": "汇编语言文件",
            "nasm": "NASM 汇编文件",
            "cmake": "CMake 文件",
            "make": "Makefile",
            "mk": "Makefile",
            "gradle": "Gradle 文件",
            "sbt": "SBT 文件",
            "pom": "Maven POM 文件",
            "iml": "IntelliJ 模块文件",
            "sln": "Visual Studio 解决方案",
            "csproj": "C# 项目文件",
            "vcxproj": "C++ 项目文件",
            "xcodeproj": "Xcode 项目",
            "pbxproj": "Xcode 项目文件",
            "storyboard": "iOS 界面文件",
            "xib": "iOS 界面文件",
            "plist": "Plist 文件",
            "strings": "字符串资源文件",
            "rc": "资源文件",
            "resx": "资源文件",
            "manifest": "清单文件",
            "ttf": "TrueType 字体",
            "otf": "OpenType 字体",
            "woff": "WOFF 字体",
            "woff2": "WOFF2 字体",
            "eot": "嵌入式 OpenType 字体",
            "fon": "字体文件",
            "afm": "Adobe 字体度量",
            "pfm": "字体度量文件",
            "epub": "EPUB 电子书",
            "mobi": "MOBI 电子书",
            "azw": "AZW 电子书",
            "azw3": "AZW3 电子书",
            "fb2": "FictionBook 电子书",
            "djvu": "DjVu 文档",
            "chm": "CHM 帮助文件",
            "hlp": "帮助文件",
            "rtf": "RTF 文档",
            "odt": "OpenDocument 文本",
            "ods": "OpenDocument 表格",
            "odp": "OpenDocument 演示文稿",
            "odg": "OpenDocument 图形",
            "odf": "OpenDocument 公式",
            "sxw": "StarOffice 文本",
            "sxc": "StarOffice 表格",
            "sxi": "StarOffice 演示文稿",
            "wps": "WPS 文档",
            "et": "WPS 表格",
            "dps": "WPS 演示文稿",
            "vsd": "Visio 绘图",
            "vsdx": "Visio 绘图",
            "pub": "Publisher 文档",
            "one": "OneNote 文档",
            "onetoc2": "OneNote 目录",
            "mdb": "Access 数据库",
            "accdb": "Access 数据库",
            "db": "数据库文件",
            "sqlite": "SQLite 数据库",
            "db3": "SQLite 数据库",
            "sqlitedb": "SQLite 数据库",
            "myd": "MySQL 数据文件",
            "myi": "MySQL 索引文件",
            "ibd": "InnoDB 表空间",
            "mdf": "SQL Server 数据库",
            "ldf": "SQL Server 日志",
            "ndf": "SQL Server 辅助数据文件",
            "dmp": "数据库转储文件",
            "bak": "备份文件",
            "tmp": "临时文件",
            "temp": "临时文件",
            "log": "日志文件",
            "dat": "数据文件",
            "bin": "二进制文件",
            "dll": "动态链接库",
            "so": "共享库文件",
            "dylib": "动态库文件",
            "lib": "静态库文件",
            "a": "静态库文件",
            "o": "目标文件",
            "obj": "目标文件或 OBJ 3D 模型",
            "pdb": "程序数据库",
            "ilk": "增量链接文件",
            "map": "映射文件",
            "sym": "符号文件",
            "exp": "导出文件",
            "def": "模块定义文件",
            "sys": "系统文件",
            "drv": "驱动程序",
            "vxd": "虚拟设备驱动",
            "reg": "注册表文件",
            "inf": "安装信息文件",
            "ins": "Internet 安装设置",
            "isp": "Internet 通信设置",
            "cat": "安全目录文件",
            "cer": "证书文件",
            "crt": "证书文件",
            "der": "DER 证书",
            "pem": "PEM 证书",
            "key": "密钥文件",
            "p12": "PKCS12 证书",
            "pfx": "PFX 证书",
            "csr": "证书签名请求",
            "crl": "证书吊销列表",
            "sst": "证书存储",
            "stl": "STL 3D 模型或证书信任列表",
            "torrent": "BT 种子文件",
            "nfo": "信息文件",
            "diz": "描述文件",
            "cue": "CUE 文件",
            "m3u": "播放列表",
            "m3u8": "M3U8 播放列表",
            "pls": "播放列表",
            "asx": "Windows Media 播放列表",
            "wpl": "WPL 播放列表",
            "xspf": "XSPF 播放列表",
            "ics": "iCalendar 或日历文件",
            "vcs": "vCalendar 文件",
            "vcf": "vCard 文件",
            "eml": "电子邮件",
            "msg": "Outlook 邮件",
            "pst": "Outlook 数据文件",
            "ost": "Outlook 离线数据文件",
            "mbox": "邮箱文件",
            "emlx": "Apple 邮件",
            "dwg": "AutoCAD 绘图",
            "dxf": "DXF 文件",
            "iges": "IGES 文件",
            "igs": "IGES 文件",
            "step": "STEP 文件",
            "stp": "STEP 文件",
            "fbx": "FBX 3D 模型",
            "3ds": "3DS Max 文件",
            "max": "3ds Max 场景",
            "blend": "Blender 文件",
            "ma": "Maya 文件",
            "mb": "Maya 文件",
            "c4d": "Cinema 4D 文件",
            "lxo": "Modo 文件",
            "lwo": "LightWave 文件",
            "skp": "SketchUp 文件",
            "rvt": "Revit 文件",
            "ifc": "IFC 文件",
            "nwd": "Navisworks 文件",
            "dwf": "DWF 文件",
            "pcap": "数据包捕获文件",
            "cap": "数据包捕获文件",
            "iso": "光盘镜像",
            "img": "磁盘镜像",
            "dmg": "Mac 磁盘镜像",
            "vmdk": "VMware 虚拟磁盘",
            "vhd": "虚拟硬盘",
            "vhdx": "虚拟硬盘",
            "qcow2": "QEMU 虚拟磁盘",
            "ova": "OVA 虚拟机",
            "ovf": "OVF 虚拟机",
            "vmx": "VMware 配置",
            "vbox": "VirtualBox 配置",
            "dockerfile": "Dockerfile",
            "lock": "锁定文件",
            "sum": "校验和文件",
            "sig": "签名文件",
            "asc": "ASCII 签名",
            "sha256": "SHA256 校验文件",
            "md5": "MD5 校验文件",
            "parquet": "Parquet 数据文件",
            "avro": "Avro 数据文件",
            "orc": "ORC 数据文件",
            "h5": "HDF5 或 Keras 模型文件",
            "hdf5": "HDF5 文件",
            "netcdf": "NetCDF 文件",
            "nc": "NetCDF 文件",
            "fits": "FITS 文件",
            "sav": "SPSS 数据文件",
            "spv": "SPSS 输出文件",
            "por": "SPSS 便携文件",
            "dta": "Stata 数据文件",
            "sas7bdat": "SAS 数据文件",
            "xpt": "SAS 传输文件",
            "rdata": "R 数据文件",
            "rds": "R 数据文件",
            "rda": "R 数据文件",
            "pickle": "Python 序列化文件",
            "pkl": "Python 序列化文件",
            "joblib": "Joblib 文件",
            "npy": "NumPy 数组",
            "npz": "NumPy 压缩数组",
            "pt": "PyTorch 模型",
            "pth": "PyTorch 模型",
            "onnx": "ONNX 模型",
            "pb": "TensorFlow 模型",
            "tflite": "TensorFlow Lite 模型",
            "mlmodel": "Core ML 模型",
            "caffemodel": "Caffe 模型",
            "prototxt": "Caffe 配置",
            "weights": "权重文件",
            "safetensors": "SafeTensors 模型",
            "ds_store": "桌面存储服务"
        }
        return json.dumps(default_map, ensure_ascii=False, indent=4)

    def _load_extension_map_from_config(self) -> str:
        """从配置文件加载扩展名映射，失败时使用默认配置"""
        try:
            from utils.extension_config_manager import ExtensionConfigManager
            config_manager = ExtensionConfigManager()
            if config_manager.load_configs():
                return json.dumps(config_manager.mappings, ensure_ascii=False, indent=4)
        except Exception:
            pass
        return self._default_extension_map()

    @Property(str)
    def source_folder(self) -> str:
        return self._source_folder

    @source_folder.setter
    def source_folder(self, value: str):
        self._source_folder = value
        self.source_folder_changed.emit(value)

    @Property(str)
    def target_folder(self) -> str:
        return self._target_folder

    @target_folder.setter
    def target_folder(self, value: str):
        self._target_folder = value
        self.target_folder_changed.emit(value)

    @Property(int)
    def classification_mode(self) -> int:
        return self._classification_mode

    @classification_mode.setter
    def classification_mode(self, value: int):
        self._classification_mode = value
        self.classification_mode_changed.emit(value)

    @Property(bool)
    def delete_source(self) -> bool:
        return self._delete_source

    @delete_source.setter
    def delete_source(self, value: bool):
        self._delete_source = value
        self.delete_source_changed.emit(value)

    @Property(str)
    def extension_map_json(self) -> str:
        return self._extension_map_json

    @extension_map_json.setter
    def extension_map_json(self, value: str):
        self._extension_map_json = value
        self.extension_map_changed.emit(value)

    @Property(str)
    def delimiter_start(self) -> str:
        return self._delimiter_start

    @delimiter_start.setter
    def delimiter_start(self, value: str):
        self._delimiter_start = value

    @Property(str)
    def delimiter_end(self) -> str:
        return self._delimiter_end

    @delimiter_end.setter
    def delimiter_end(self, value: str):
        self._delimiter_end = value

    @Property(int)
    def delimiter_start_pos(self) -> int:
        return self._delimiter_start_pos

    @delimiter_start_pos.setter
    def delimiter_start_pos(self, value: int):
        self._delimiter_start_pos = value

    @Property(int)
    def delimiter_end_pos(self) -> int:
        return self._delimiter_end_pos

    @delimiter_end_pos.setter
    def delimiter_end_pos(self, value: int):
        self._delimiter_end_pos = value

    @Property(bool)
    def is_classifying(self) -> bool:
        return self._is_classifying

    @property
    def classification_result(self) -> Optional[dict]:
        return self._classification_result

    @Property(bool)
    def scan_subfolder(self) -> bool:
        return self._scan_subfolder

    @scan_subfolder.setter
    def scan_subfolder(self, value: bool):
        self._scan_subfolder = value

    @Property(bool)
    def specify_depth(self) -> bool:
        return self._specify_depth

    @specify_depth.setter
    def specify_depth(self, value: bool):
        self._specify_depth = value

    @Property(int)
    def scan_depth(self) -> int:
        return self._scan_depth

    @scan_depth.setter
    def scan_depth(self, value: int):
        self._scan_depth = value

    @Slot()
    def validate_inputs(self) -> tuple[bool, str]:
        """验证输入参数"""
        if not self._source_folder or not os.path.exists(self._source_folder):
            return False, "请选择有效的源文件夹"

        if not self._target_folder:
            return False, "请选择目标文件夹"

        if self._classification_mode == 0:
            try:
                extension_map = json.loads(self._extension_map_json)
                if not isinstance(extension_map, dict):
                    return False, "扩展名映射必须是 JSON 对象"
            except json.JSONDecodeError as e:
                return False, f"JSON 格式错误: {str(e)}"
        else:
            if not self._delimiter_start:
                return False, "起始分隔符不能为空"
            if not self._delimiter_end:
                return False, "结束分隔符不能为空"

        return True, ""

    @Slot()
    def start_classification(self):
        """开始分类"""
        if self._is_classifying:
            return

        valid, error_msg = self.validate_inputs()
        if not valid:
            self.error_occurred.emit(error_msg)
            return

        self._is_classifying = True
        self.classification_started.emit()
        self.status_changed.emit("正在初始化...")

        self._worker = ClassificationWorker(
            classification_mode=self._classification_mode,
            source_folder=self._source_folder,
            target_folder=self._target_folder,
            delete_source=self._delete_source,
            extension_map_json=self._extension_map_json,
            delimiter_start=self._delimiter_start,
            delimiter_end=self._delimiter_end,
            delimiter_start_pos=self._delimiter_start_pos,
            delimiter_end_pos=self._delimiter_end_pos,
            scan_subfolder=self._scan_subfolder,
            specify_depth=self._specify_depth,
            scan_depth=self._scan_depth
        )

        self._worker.progress_updated.connect(self._on_worker_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error_occurred.connect(self._on_worker_error)

        self._worker.start()

    def _on_worker_progress(self, value: int, message: str):
        """工作线程进度更新"""
        self.progress_updated.emit(value, message)

    def _on_worker_finished(self, result: dict):
        """工作线程完成"""
        self._is_classifying = False
        self._worker = None
        self._classification_result = result
        self.classification_finished.emit(result)

    def _on_worker_error(self, error: str):
        """工作线程错误"""
        self._is_classifying = False
        self._worker = None
        self.error_occurred.emit(error)

    @Slot()
    def reset_settings(self):
        """重置设置"""
        self._source_folder = ""
        self._target_folder = ""
        self._extension_map_json = self._load_extension_map_from_config()
        self._delimiter_start = "_"
        self._delimiter_end = "_"
        self._delimiter_start_pos = 1
        self._delimiter_end_pos = 2
        self._delete_source = False

        self.source_folder_changed.emit("")
        self.target_folder_changed.emit("")
        self.extension_map_changed.emit(self._extension_map_json)
        self.delete_source_changed.emit(False)
        self.status_changed.emit("就绪")

    @Slot()
    def load_default_extension_map(self):
        """加载默认扩展名映射（从配置文件）"""
        self._extension_map_json = self._load_extension_map_from_config()
        self.extension_map_changed.emit(self._extension_map_json)
