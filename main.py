import requests
import json
from tkinter import filedialog as fd
from tkinter import Tk
import win32com.client
from ctypes import windll
from random import uniform as randfloat
from time import sleep
from rich.progress import Progress
from rich import print as rprint
from rich.console import Console

#a bit of self advertisement ;)
c = Console()
c.rule('[bold yellow]Made by FanaticExplorer', style='bold blue')
# Get all settings
try:
    with open('settings.json') as f:
        settings = json.load(f)
except IOError as e:
    rprint(f"[red bold]Помилка під час відкриття файлу: {e}")
    exit(1)

# Checking that all values are here
required_keys = ['token','servers', 'min_interval', 'max_interval']
if not all(key in settings for key in required_keys):
    raise ValueError("Не вистачає ключів. " +
                    'У файлі "settings.json" мають бути ключі '+ 
                    '"token", "servers", "min_interval", "max_interval". '+
                    "У випадку проблем звертайтеся до виконавця проекту.")

#Create exception for API error
class DiscordApiError(Exception):
    pass

windll.shcore.SetProcessDpiAwareness(1) # Making Python less blurry

# Set the usual filetypes (where files will be saved)
filetypes = (
    ('Текстовий файл', '*.txt'),
    ('Усі файли', '*.*')
)

# Retrieve the "Documents" folder path
shell = win32com.client.Dispatch("WScript.Shell")
documents_dir = shell.SpecialFolders("MyDocuments")


root = Tk() # Create a window, so the file dialog will have the correct icon
root.geometry('1x1+999999999+9999999999') # Teleporting it to the end islands, so it won't flicker on the user's screen
root.iconbitmap('search.ico') # Setting the icon
root.withdraw() # And closing the window

# Asking the user to select an input file
# They won't proceed if they don't choose a file
in_file = None
while not in_file:
    in_file = fd.askopenfile(
        title='Виберіть файл зі списком користувачів',
        initialdir=documents_dir,
        filetypes=filetypes
    )




lines = in_file.read().split('\n') # Splitting the file text into lines...
lines = [value for value in lines if value != ""] # ... and removing empty lines

# Asking the user to select an output file
out_file_yes = None
while not out_file_yes:
    out_file_yes = fd.asksaveasfile(
        title='Виберіть шлях до файлу, куди треба записати позитивний результат',
        initialdir=documents_dir,
        filetypes=filetypes,
        defaultextension=filetypes
    )
out_path_yes = out_file_yes.name

out_file_no = None
while not out_file_no:
    out_file_no = fd.asksaveasfile(
        title='Виберіть шлях до файлу, куди треба записати негативний результат',
        initialdir=documents_dir,
        filetypes=filetypes,
        defaultextension=filetypes
    )
out_path_no = out_file_no.name

# Declaring parsing function
def user_in_server(token, guild_id, user_id):
    headers = {
        'Authorization': token,
    }

    try:
        response = requests.get(f'https://discord.com/api/guilds/{guild_id}/members/{user_id}', 
                                headers=headers)
    except requests.exceptions.RequestException as e:
        rprint(f"[red bold]Error making request to Discord API: {e}")
        return False


    if response.status_code == 200: # If the request was successful
        return True
    elif response.status_code == 404: # If the user was not found
        return False
    else:
        raise DiscordApiError(f"Unexpected status code {response.status_code}: {response.text}")

with Progress(transient=True) as progress:
    server_task = progress.add_task(f"[cyan]Прогресс по серверам:", total=len(settings['servers']))
    user_task = progress.add_task("[magenta]Прогресс по користувачам в группі:", total=len(lines))
    for server in settings['servers']:
        for user in lines:
            if user_in_server(settings['token'], server, user):
                rprint(f"[green]Користувач з ID {user} є на сервері з ID {server}")
                # Updating file with new values
                with open(out_path_yes, 'a') as f:
                    f.write(f"{user} - {server}\n")
            else:
                rprint(f"[red]Користувача з ID {user} немає на сервері з ID {server}")
                with open(out_path_no, 'a') as f:
                    f.write(f"{user} - {server}\n")

            progress.update(user_task, advance=1)
            
            # Sleep for random time in range, which was set in settings.json
            sleep(randfloat(settings['min_interval'], settings['max_interval']))
        progress.update(server_task, advance=1)