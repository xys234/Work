@ECHO OFF

SET DISTPATH=C:\Projects\SWIFT\Deliverables\Software\dist
SET WORKPATH=C:\Projects\SWIFT\Deliverables\Software\build
SET STMA_SOFTWARE_PATH=C:\Projects\SWIFT\SWIFT_Workspace\Software\STM_A
REM SET STMA_SOFTWARE_PATH=L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Software\STM\STM_A

REM pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  trip_prep.spec
REM COPY /Y /D %DISTPATH%\trip_prep\trip_prep.*		%STMA_SOFTWARE_PATH%\.	

REM pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  convert_trips.spec
REM COPY /Y /D %DISTPATH%\convert_trips\*.*			%STMA_SOFTWARE_PATH%\.	

pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  network_prep.spec
COPY /Y /D %DISTPATH%\network_prep\*.*			%STMA_SOFTWARE_PATH%\.

REM pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  stma.spec
REM COPY /Y /D %DISTPATH%\stma\stma.*			%STMA_SOFTWARE_PATH%\.	

SET DISTPATH=
SET WORKPATH=