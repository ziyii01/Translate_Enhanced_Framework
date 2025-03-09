# Translate Enhanced Framework

## 功能

可以方便地批量调用繁化姬API

支持使用命令行或引用py库对外部代码进行扩展

## 食用方法

### 下载

有两种方式可供选择

* 使用python环境运行  
  需要安装python和相关依赖库: `pip install -U httpx chardet`
* 使用exe运行  
  前往[Actions](https://github.com/ziyii01/Translate_Enhanced_Framework/actions)下载最新编译的exe，或者前往[Releases](https://github.com/ziyii01/Translate_Enhanced_Framework/releases)找到手动上传的exe  
  (二者是一样的，Actions中会自动编译每个版本，Releases中是将自动编译的版本手动发布的)

### 运行

```
# 使用命令行键入
py TEF.py
TEF.exe

# 使用命令行传参
py TEF.py [command 1, command 2, ...]
TEF.exe [command 1, command 2, ...]

# 查看 help
TEF.exe help
```


## 鸣谢

本项目使用[繁化姬](https://docs.zhconvert.org/)

### 繁化姬注意事项

* 商業使用請參見[商業使用](https://docs.zhconvert.org/commercial/)。
* 若您發布的成品仍然依賴於繁化姬的 API 服務， 您必須在程式中明確地寫出「本程式使用了繁化姬的 API 服務」 並讓使用者知道「繁化姬商用必須付費」， 並且於程式中附上繁化姬網頁的「超連結（hyperlink）」。
