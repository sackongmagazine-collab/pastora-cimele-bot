' Reinicia o bot Pastora Cimele (para instancias antigas antes de subir)
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c ""D:\pastora_cimele_bot\run_bot_hidden.bat""", 0, True
WshShell.Popup "Bot Pastora Cimele iniciado.", 3, "Pastora Cimele", 64
Set WshShell = Nothing