Right click folder in default file exporer of win10.

cmd.exe /K "D:\ProgramData\Anaconda3\Scripts\activate.bat ""D:\ProgramData\Anaconda3\envs\cellpose"" & ""python.exe D:\ProgramData\Anaconda3\Scripts\jupyter-notebook-script.py {current_folder}"""

Note:
1. parameters of cmd
  cmd [/c|/k] [/s] [/q] [/d] [/a|/u] [/t:{<b><f> | <f>}] [/e:{on | off}] [/f:{on | off}] [/v:{on | off}] [<string>]

  + *"/c"*	Carries out the command specified by string and then stops.
  + *"/k"*	Carries out the command specified by string and continues.

  To use multiple commands for <string>, separate them by the command separator &&. For example:
    <command1>&&<command2>&&<command3>
  If the directory path and files have spaces in their name, they must be enclosed in double quotation marks. For example:
    mkdir Test&&mkdir "Test 2"&&move "Test 2" Test

2. In listary
   Current folder: {current_folder}
