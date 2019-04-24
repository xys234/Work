@ECHO OFF

SET DISTPATH=C:\Projects\SWIFT\Deliverables\Software\dist
SET WORKPATH=C:\Projects\SWIFT\Deliverables\Software\build
SET STMA_SOFTWARE_PATH=C:\Projects\SWIFT\SWIFT_Workspace\Software\STM_A

pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  convert_trips.spec
pyinstaller --distpath %DISTPATH% --workpath %WORKPATH%  trip_prep.spec

COPY /Y /D %DISTPATH%\convert_trips\*.*			%STMA_SOFTWARE_PATH%\.	
COPY /Y /D %DISTPATH%\trip_prep\trip_prep.*		%STMA_SOFTWARE_PATH%\.	

SET DISTPATH=
SET WORKPATH=