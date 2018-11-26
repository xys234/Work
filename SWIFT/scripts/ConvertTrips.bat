SET PythonExecutable=C:\Anaconda3\python.exe
SET	ControlPath=C:\Projects\Repo\Work\SWIFT\scripts\test\cases

CALL 	%PythonExecutable%		ConvertTrips.py		%ControlPath%\ConvertTrips_4.ctl


REM CALL 	%PythonExecutable%		ConvertTrips.py		%ControlPath%\ConvertTrips_OTHER_AM.ctl
PAUSE