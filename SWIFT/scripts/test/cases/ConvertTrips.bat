@ECHO OFF

SET _LOG_=log_execution.txt
SET CurrentPath=%CD%
SET PythonExecutable=C:\Anaconda3\python.exe
SET	ControlPath=C:\Projects\Repo\Work\SWIFT\scripts\test\cases
SET ScriptPath=C:\Projects\Repo\Work\SWIFT\scripts

REM CD %ScriptPath%

REM IF EXIST %_LOG_% DEL /Q %_LOG_%

REM CALL:Run64p 1  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HBW_AM.ctl
REM CALL:Run64p 2  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HBW_MD.ctl
REM CALL:Run64p 3  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HBW_PM.ctl
REM CALL:Run64p 4  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HBW_OV.ctl

REM CALL:Run64p 5  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HNW_AM.ctl
REM CALL:Run64p 6  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HNW_MD.ctl
REM CALL:Run64p 7  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HNW_PM.ctl
REM CALL:Run64p 8  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_HNW_OV.ctl

REM CALL:Run64p 9   %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHO_AM.ctl
REM CALL:Run64p 10  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHO_MD.ctl
REM CALL:Run64p 11  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHO_PM.ctl
REM CALL:Run64p 12  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHO_OV.ctl

REM CALL:Run64p 13  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHW_AM.ctl
REM CALL:Run64p 14  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHW_MD.ctl
REM CALL:Run64p 15  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHW_PM.ctl
REM CALL:Run64p 16  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_NHW_OV.ctl

REM CALL:Run64p 17  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_OTHER_AM.ctl
REM CALL:Run64p 18  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_OTHER_MD.ctl
REM CALL:Run64p 19  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_OTHER_PM.ctl
REM CALL:Run64p 20  %ScriptPath%\convert_trips.py  %ControlPath%\ConvertTrips_OTHER_OV.ctl

REM CALL:WaitForParallel 1  
REM CALL:WaitForParallel 2  
REM CALL:WaitForParallel 3  
REM CALL:WaitForParallel 4  
                     
REM CALL:WaitForParallel 5  
REM CALL:WaitForParallel 6  
REM CALL:WaitForParallel 7  
REM CALL:WaitForParallel 8  
                     
REM CALL:WaitForParallel 9  
REM CALL:WaitForParallel 10 
REM CALL:WaitForParallel 11 
REM CALL:WaitForParallel 12 
                     
REM CALL:WaitForParallel 13 
REM CALL:WaitForParallel 14 
REM CALL:WaitForParallel 15 
REM CALL:WaitForParallel 16 

REM CALL:WaitForParallel  17
REM CALL:WaitForParallel  18
REM CALL:WaitForParallel  19
REM CALL:WaitForParallel  20

CALL:Run64    	%ScriptPath%\trip_prep.py 	  %ControlPath%\TripPrep_MergeTrips.ctl

GOTO:EOF

REM CALL 	%PythonExecutable%		convert_trips.py		%ControlPath%\ConvertTrips_4.ctl
REM CALL 	%PythonExecutable%		convert_trips.py		%ControlPath%\ConvertTrips_OTHER_AM.ctl


:Run64
    TITLE %~n0.bat
    CALL:RunRoutine  %~1  %~2
GOTO:EOF

:Run64p
    REM TITLE %~n0.bat : %~2
    CALL:RunRoutinep  %~1  %~2  %~3 
GOTO:EOF


:RunRoutine

    ECHO.                                                    > running.bat
    ECHO. %PythonExecutable% 	%~1 	%2       			>> running.bat
    ECHO. EXIT %%_EXITCODE_%%                               >> running.bat
    ECHO.                                                   >> running.bat

    CALL:PrintMessage  "Executing %2"

    CALL running.bat
	DEL /Q running.bat
	
GOTO:EOF

:RunRoutinep


    ECHO.                                                    > parallel_%~1.bat
    ECHO. IF EXIST parallel_%1.done DEL /Q parallel_%1.done >> parallel_%~1.bat
    ECHO. %PythonExecutable% 	%~2 	%3       			>> parallel_%~1.bat

    ECHO. SET _EXITCODE_=%%ERRORLEVEL%%                     >> parallel_%~1.bat
    ECHO. ECHO %%_EXITCODE_%% ^> parallel_%1.done           >> parallel_%~1.bat

    ECHO. EXIT %%_EXITCODE_%%                               >> parallel_%~1.bat
    ECHO.                                                   >> parallel_%~1.bat

    CALL:PrintMessage  "Executing parallel_%~1.bat"

    START "parallel_%~1.bat"  /NORMAL parallel_%~1.bat
    REM START "parallel_%~1.bat" /MIN /NORMAL parallel_%~1.bat

GOTO:EOF



:WaitForParallel

    TITLE %~n0.bat

    IF "%~1" NEQ "" (

        SET /a waitcnt=0
        ECHO.
        ECHO. Waiting for parallel_%~1.done

        IF EXIST parallel_%~1.done GOTO:waitfinished

        REM This gave a lot of headache, when DOS sees labels, it does not keep old variables, do not leave a blank line after label
        :gobackandwait
        CHOICE /C C /M "..[%waitcnt%] waiting 30 sec, press C to continue " /D:C /T:30
        SET /a waitcnt+=1

        IF EXIST parallel_%~1.done (
            GOTO:waitfinished
        ) ELSE (
            GOTO:gobackandwait
        )

        :waitfinished
        CALL:PrintMessage  "Completed parallel_%~1.bat"
        DEL /Q parallel_%~1.done
        DEL /Q parallel_%~1.bat
    )

GOTO:EOF

:PrintMessage

    SET dt=%date:~10,4%/%date:~4,2%/%date:~7,2%_%time:~0,2%:%time:~3,2%:%time:~6,2%
    ECHO %dt%: %~1
    ECHO %dt%: %~1 >> %_LOG_%
    SET dt=

GOTO:EOF