@ECHO OFF

SET _LOG_=log_execution.txt
SET CurrentPath=%CD%
SET PythonExecutable=C:\Anaconda3\python.exe
SET	ControlPath=C:\Projects\Repo\Work\STM\tests\Controls
SET ExePath=C:\Projects\Repo\Work\STM\services

%PythonExecutable% %ExePath%\control_service.py  %ControlPath%\test_Control_Service_1.ctl
PAUSE