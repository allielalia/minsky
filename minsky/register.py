import asyncio
import os
import sys

import aiohttp

commands = [{'name': 'verify', 'description': 'Verify your Reddit account'}]

async def main(app_id: str, token: str, test_guild_id: str=None) -> None:
    headers = {'Authorization': f'Bot {token}',
               'Content-Type': 'application/json'}
    async with aiohttp.ClientSession(headers=headers) as session:
        if test_guild_id is not None:
            url = (f'https://discord.com/api/v10/applications/{app_id}/guilds/'
                   f'{test_guild_id}/commands')
        else:
            url = f'https://discord.com/api/v10/applications/{app_id}/commands'
        async with session.put(url, json=commands) as response:
            if response.ok:
                print('Registered commands!')
            else:
                print('Error registering commands!', file=sys.stderr)
                text = await response.text()
                print(text, file=sys.stderr)

if __name__ == '__main__':
    asyncio.run(main(os.environ['DISCORD_APPLICATION_ID'],
                     os.environ['DISCORD_TOKEN'],
                     os.environ.get('DISCORD_TEST_GUILD')))
