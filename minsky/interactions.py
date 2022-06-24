from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, IntFlag
from typing import Optional, TypeAlias

from dacite import Config, from_dict as _from_dict

Snowflake: TypeAlias = str

class UserFlags(IntFlag):
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19

class PremiumType(IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2

@dataclass
class User:
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[UserFlags]
    premium_type: Optional[PremiumType]
    public_flags: Optional[UserFlags]

@dataclass
class GuildMember:
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    roles: list[Snowflake]
    joined_at: datetime
    premium_since: Optional[datetime]
    deaf: bool
    mute: bool
    pending: Optional[bool]
    permissions: Optional[str]
    communication_disabled_until: Optional[datetime]

@dataclass
class RoleTags:
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[str] # XXX?

@dataclass
class Role:
    id: Snowflake
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    mananged: bool
    mentionable: bool
    tags: RoleTags

class ChannelType(IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY =4
    GUILD_NEWS = 5
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15

@dataclass
class ThreadMetadata:
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime
    locked = bool
    invitable: Optional[bool]
    create_timestamp: Optional[datetime]

@dataclass
class Channel:
    id: Snowflake
    type: ChannelType
    name: Optional[str]
    parent_id: Optional[Snowflake]
    thread_metadata: Optional[str]
    permissions: Optional[str]

@dataclass
class Message:
    pass # XXX?

@dataclass
class ResolvedData:
    users: Optional[dict[Snowflake, User]]
    members: Optional[dict[Snowflake, GuildMember]]
    roles: Optional[dict[Snowflake, Role]]
    channels: Optional[dict[Snowflake, Channel]]
    messages: Optional[dict[Snowflake, Message]]
    #attachments: Optional[dict[Snowflake, Attachment]] # XXX?

class ApplicationCommandType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

@dataclass
class InteractionDataOption:
    name: str
    type: ApplicationCommandType
    value: Optional[str | int]
    options: Optional[list['InteractionDataOption']]
    focused: Optional[bool]

@dataclass
class InteractionData:
    id: Snowflake
    name: str
    type: ApplicationCommandType
    resolved: Optional[ResolvedData]
    options: Optional[list[InteractionDataOption]]
    guild_id: Optional[Snowflake]
    target_id: Optional[Snowflake]

@dataclass
class Interaction:
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    data: Optional[InteractionData]
    guild_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    member: Optional[GuildMember]
    user: Optional[User]
    token: str
    version: int
    #message: Optional[Message] # XXX?
    locale: Optional[str]
    guild_locale: Optional[str]

    @classmethod
    def from_dict(cls, data):
        return _from_dict(cls, data,
                Config(cast=[IntEnum, IntFlag, Snowflake],
                       forward_references={'InteractionDataOption':
                                               InteractionDataOption},
                       type_hooks={datetime: datetime.fromisoformat}))

class InteractionResponseType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9

class InteractionComponentType(IntEnum):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3
    TEXT_INPUT = 4

class InteractionButtonStyle(IntEnum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5

class InteractionComponent:
    def to_dict(self) -> dict:
        raise NotImplementedError

class InteractionComponentLink(InteractionComponent):
    def __init__(self, label: str, url: str) -> None:
        self.label: str = label
        self.url: str = url

    def to_dict(self) -> dict:
        return {'type': InteractionComponentType.BUTTON,
                'style': InteractionButtonStyle.LINK,
                'label': self.label,
                'url': self.url}

class InteractionComponentRow(InteractionComponent):
    def __init__(self) -> None:
        self.components = []

    def add_link(self, label: str, url: str) -> None:
        self.components.append(InteractionComponentLink(label, url))

    def to_dict(self) -> dict:
        data = {'type': InteractionComponentType.ACTION_ROW}
        if self.components:
            data['components'] = [c.to_dict() for c in self.components]
        return data

class MessageFlag(IntFlag):
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8

class InteractionResponsePong:
    @classmethod
    def to_dict(cls) -> dict:
        return {'type': InteractionResponseType.PONG}

class InteractionResponse:
    type: InteractionResponseType

    def __init__(self, *, content: Optional[str]=None,
                 crossposted: bool=False, is_crosspost: bool=False,
                 suppress_embeds: bool=False,
                 source_message_deleted: bool=False,
                 urgent: bool=False, has_thread: bool=False,
                 ephemeral: bool=False, loading: bool=False,
                 failed_to_mention_some_roles_in_thread: bool=False):
        self.content: Optional[str] = content
        self.components: list[InteractionComponent] = []
        self.flags: MessageFlag = 0
        if crossposted:
            self.flags |= MessageFlag.CROSSPOSTED
        if is_crosspost:
            self.flags |= MessageFlag.IS_CROSSPOST
        if suppress_embeds:
            self.flags |= MessageFlag.SUPPRESS_EMBEDS
        if source_message_deleted:
            self.flags |= MessageFlag.SOURCE_MESSAGE_DELETED
        if urgent:
            self.flags |= MessageFlag.URGENT
        if has_thread:
            self.flags |= MessageFlag.HAS_THREAD
        if ephemeral:
            self.flags |= MessageFlag.EPHEMERAL
        if loading:
            self.flags |= MessageFlag.LOADING
        if failed_to_mention_some_roles_in_thread:
            self.flags |= MessageFlag.FAILED_TO_MENTION_SOME_ROLES_IN_THREAD

    def add_row(self) -> InteractionComponentRow:
        row = InteractionComponentRow()
        self.components.append(row)
        return row

    def to_dict(self) -> dict:
        data = {}
        if self.content is not None:
            data['content'] = self.content
        if self.components:
            data['components'] = [c.to_dict() for c in self.components]
        if self.flags != 0:
            data['flags'] = self.flags
        return {'type': self.type, 'data': data}

class ChannelMessage(InteractionResponse):
    type = InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
