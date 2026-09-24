' Para o bot Pastora Cimele
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "taskkill /F /FI ""IMAGENAME eq pythonw.exe"" /FI ""COMMANDLINE eq *main.py*""", 0, True
WshShell.Run "taskkill /F /FI ""IMAGENAME eq python.exe"" /FI ""COMMANDLINE eq *main.py*""", 0, True
WshShell.Popup "Bot Pastora Cimele parado.", 3, "Pastora Cimele", 64
Set WshShell = Nothing