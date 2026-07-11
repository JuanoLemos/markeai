Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' WindowStyle 0 = hidden, False = no wait
objShell.Run "cmd.exe /c update.bat", 0, False
