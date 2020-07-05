pyinstaller -D -w ^
-i res/icon.ico ^
--hidden-import AboutDialog.py ^
--hidden-import AddEnvironVar.py ^
--hidden-import CrackPassword.py ^
--hidden-import ExportDict.py ^
--hidden-import MainWindow.py ^
--hidden-import ReadDict.py ^
--hidden-import WriteDict.py ^
--version-file version.txt ^
--add-data "UI;UI" ^
--add-data "res;res" ^
--add-data "UnRAR64.dll;." ^
main.py