import requests

class DiscordApiError(Exception):
    pass

token = 'MTEyOTMzODMwODczNzExODIwOA.GNfO4B.pRdeDgQL-xUmc7NDYm27_VlqEIO7wNnmQkhEls'
guild_id = '866321255962902558'
user_id = '708933592163811338'

def user_in_server(token, guild_id, user_id):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://discord.com/api/guilds/{guild_id}/members/{user_id}', headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        raise DiscordApiError(f"Unexpected status code {response.status_code}: {response.text}")


if user_in_server(token, guild_id, user_id):
    print(f"Користувач з ID {user_id} є на сервері з ID {guild_id}")
else:
    print(f"Користувача з ID {user_id} немає на сервері з ID {guild_id}")
