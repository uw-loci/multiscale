import os
os.environ['PYJNIUS_JAR'] = r'C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\share\pyjnius\pyjnius.jar'
os.environ['PATH'] = r'C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\jre\bin\server;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\install\Library\jre\bin\server;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\install\Library\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\jre\bin\server;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\mingw-w64\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\usr\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Scripts;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\Library\mingw-w64\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\Library\usr\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\Library\bin;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\Scripts;C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\bin;C:\Program Files (x86)\Common Files\Oracle\Java\javapath;C:\ProgramData\Oracle\Java\javapath;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\Program Files\MATLAB\R2017a\runtime\win64;C:\Program Files\MATLAB\R2017a\bin;C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\110\Tools\Binn\;C:\Program Files (x86)\Microsoft SQL Server\120\Tools\Binn\;C:\Program Files\Microsoft SQL Server\120\Tools\Binn\;C:\Program Files\Microsoft SQL Server\120\DTS\Binn\;C:\Program Files (x86)\Windows Kits\8.1\Windows Performance Toolkit\;C:\apache-maven-3.3.9\bin;C:\ProgramData\chocolatey\bin;C:\Program Files (x86)\AMD\ATI.ACE\Core-Static;C:\Program Files (x86)\Aperio\Common;C:\Program Files\PuTTY\;C:\Program Files\Java\jdk1.8.0_91\bin\;C:\Program Files (x86)\Google\Chrome\Application;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\ProgramData\Oracle\Java\javapath;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Program Files\MATLAB\R2016a\runtime\win64;C:\Program Files\MATLAB\R2016a\bin;C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\110\Tools\Binn\;C:\Program Files (x86)\Microsoft SQL Server\120\Tools\Binn\;C:\Program Files\Microsoft SQL Server\120\Tools\Binn\;C:\Program Files\Microsoft SQL Server\120\DTS\Binn\;C:\Program Files (x86)\Windows Kits\8.1\Windows Performance Toolkit\;C:\Users\mpinkert\AppData\Local\Programs\Git\cmd;C:\Users\mpinkert\AppData\Local\Microsoft\WindowsApps;C:\Users\mpinkert\AppData\Local\Programs\MiKTeX 2.9\miktex\bin\x64'
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk1.8.0_91'
os.environ['JDK_HOME'] = r'C:\Users\mpinkert\AppData\Local\Continuum\anaconda3\envs\pyimagej\Library'
import imagej
ij = imagej.init(r'C:\Users\mpinkert\Desktop\Fiji.app')

from jnius import autoclass, JavaException, cast


macro = """
run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x=3 grid_size_y=1 tile_overlap=27 first_file_index_i=0 directory=F:\\Research\\LINK\\US\\2018-08-17\\ file_names=FirstImage3D_Overlap-27_{i}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save memory (but be slower)] image_output=[Write to disk] output_directory=[F:\\Research\\LINK\\US\\2018-08-17\\grid output]");
"""

try:
        test = ij.script().run('macro.ijm', macro, True).get()
except JavaException as e:
        print("e.classname    -- {}".format(e.classname))
        print("e.innermessage -- {}".format(e.innermessage))
        for st in e.stacktrace:
                print(st)
