import os
from functools import wraps
from typing import Optional

from aiohttp import web
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from minsky.interactions import (ChannelMessage, Interaction,
                                 InteractionResponsePong, InteractionType)

routes = web.RouteTableDef()

@routes.post('/api/discord/interactions')
async def discord_interaction(request: web.Request) -> web.Response:
    if request.app.public_key is not None:
        vk = VerifyKey(bytes.fromhex(request.app.public_key))
        signature = request.headers.get('X-Signature-Ed25519', '')
        timestamp = request.headers.get('X-Signature-Timestamp', '')
        charset = request.charset or 'utf-8'
        body = await request.text()
        try:
            vk.verify(f'{timestamp}{body}'.encode(charset),
                      bytes.fromhex(signature))
        except BadSignatureError:
            return web.Response(status=401)

    interaction = Interaction.from_dict(await request.json())
    match interaction.type:
        case InteractionType.PING:
            return web.json_response(InteractionResponsePong.to_dict())
        case InteractionType.APPLICATION_COMMAND:
            # XXX: Check if user already has verified role
            # XXX: Check if user has Reddit connected to their profile
            # XXX: Smuggle interaction ID into auth URL?
            msg = ChannelMessage('Please verify your Reddit account.',
                                 ephemeral=True)
            msg.add_row().add_link('Verify', 'https://www.reddit.com/')
            return web.json_response(msg.to_dict())
        case _:
            return web.Response(status=400)

async def reddit_auth_callback(request: web.Request) -> web.Response:
    pass

app = web.Application()
app.public_key: Optional[str] = None
app.log_channel_id: Optional[str] = None
app.verified_role_id: Optional[str] = None
app.add_routes(routes)

if __name__ == '__main__':
    app.public_key = os.environ['DISCORD_PUBLIC_KEY']
    app.log_channel_id = os.environ['DISCORD_LOG_CHANNEL_ID']
    app.verified_role_id = os.environ['DISCORD_VERIFIED_ROLE_ID']
    web.run_app(app)
