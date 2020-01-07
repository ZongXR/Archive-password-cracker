# 压缩包密码破解
This repository provides codes to crack archive with password
## 主要功能
通过暴力枚举的方式，破解压缩包密码，后期将搭建md5-password共享平台。
## 版本迭代
### 0.1.0.0
支持内置字典以及外部字典破解</br>
支持将内置字典导出至外部文件</br>
通过多进程读写文件方式提速</br>
简单的UI窗口</br>
![screen_shot](https://github.com/GoogleLLP/Archive-password-cracker/blob/master/%E5%8A%A0%E5%AF%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E7%A0%B4%E8%A7%A3%E5%99%A80.1.0.0/screen_shot.PNG)</br>
### 1.0.0.0
新增.rar文件支持</br>
后台多进程任务使用生产者消费者模式</br>
优化代码执行逻辑</br>
修复后台任务运行时，主界面卡死的bug</br>
新增导出字典，破解的进度展示，优化用户体验</br>
修复若干bug</br>
![main_window](https://raw.githubusercontent.com/GoogleLLP/Archive-password-cracker/master/%E5%8A%A0%E5%AF%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E7%A0%B4%E8%A7%A3%E5%99%A81.0.0.0/screen_shots/main_window.PNG)</br>
![cracking_password](https://raw.githubusercontent.com/GoogleLLP/Archive-password-cracker/master/%E5%8A%A0%E5%AF%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E7%A0%B4%E8%A7%A3%E5%99%A81.0.0.0/screen_shots/cracking.PNG)</br>
![crack_succeed](https://raw.githubusercontent.com/GoogleLLP/Archive-password-cracker/master/%E5%8A%A0%E5%AF%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E7%A0%B4%E8%A7%A3%E5%99%A81.0.0.0/screen_shots/succeed.PNG)</br>
![about_dialog](https://raw.githubusercontent.com/GoogleLLP/Archive-password-cracker/master/%E5%8A%A0%E5%AF%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E7%A0%B4%E8%A7%A3%E5%99%A81.0.0.0/screen_shots/about.PNG)
