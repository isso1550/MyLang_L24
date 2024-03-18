* `pip install antlr4-tools`
* dodać `C:\Users\Filip\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts` do path
* `antlr4` - instaluje JRE
    * Installed Java in C:\Users\Filip\.jre\jdk-11.0.22+7-jre; remove that dir to uninstall
* `pip install -r .\requirements.txt`
* napisac Expr.g4 i Driver.py
    * w driver zmienic tree na parser.nazwa(), tak ze nazwa to regula startowa
* `antlr4 -v 4.13.0 -Dlanguage=Python3 Expr.g4`
* napisać program
* `python Driver.py .\program.em`