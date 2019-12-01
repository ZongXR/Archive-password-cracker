pyinstaller -D -w ^
-i icon.ico ^
--hidden-import tools.py ^
--add-data "mainUI.ui;." ^
--version-file version.txt ^
main_window.py