@ECHO OFF

SET _LOG_=log_execution.txt
SET CurrentPath=%CD%
SET PythonExecutable=C:\Anaconda3\python.exe
SET	ControlPath=..\Controls
SET ExePath=..\..

SET ROSTER="AM HR3 HBW.OMX"

%PythonExecutable% %ExePath%\program.py  %ControlPath%\test_Control_Service_4.ctl

SET ROSTER=
PAUSE