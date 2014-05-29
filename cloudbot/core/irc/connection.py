from _ssl import PROTOCOL_SSLv23
import asyncio
import re
import ssl
from ssl import SSLContext

from cloudbot.core.permissions import PermissionManager
from cloudbot.core.irc.protocol import IRCProtocol

from cloudbot.core.events import BaseEvent


class BotConnection:
    """ A BotConnection represents each connection the bot makes to an IRC server
    :type bot: cloudbot.core.bot.CloudBot
    :type name: str
    :type channels: list[str]
    :type config: dict[str, unknown]
    :type ssl: bool
    :type server: str
    :type port: int
    :type logger: logging.Logger
    :type nick: str
    :type vars: dict
    :type history: dict[str, list[tuple]]
    :type message_queue: queue.Queue
    :type input_queue: queue.Queue
    :type output_queue: queue.Queue
    :type connection: IRCConnection
    :type permissions: PermissionManager
    :type connected: bool
    """

    def __init__(self, bot, name, server, nick, port=6667, use_ssl=False, logger=None, channels=None, config=None,
                 readable_name=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type name: str
        :type server: str
        :type nick: str
        :type port: int
        :type use_ssl: bool
        :type logger: logging.Logger
        :type channels: list[str]
        :type config: dict[str, unknown]
        """
        self.bot = bot
        self.loop = bot.loop
        self.name = name
        if readable_name:
            self.readable_name = readable_name
        else:
            self.readable_name = name
        if channels is None:
            self.channels = []
        else:
            self.channels = channels

        if config is None:
            self.config = {}
        else:
            self.config = config

        self.ssl = use_ssl
        self.server = server
        self.port = port
        self.logger = logger
        self.nick = nick
        self.vars = {}
        self.history = {}

        self.message_queue = bot.queued_events  # global parsed message queue, for parsed received messages

        self.input_queue = asyncio.Queue(loop=self.loop)
        self.output_queue = asyncio.Queue(loop=self.loop)

        # create permissions manager
        self.permissions = PermissionManager(self)

        # create the IRC connection
        self.connection = IRCConnection(self)

        self.connected = False

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the IRC server. This by itself doesn't start receiving or sending data.
        """
        # connect to the irc server
        yield from self.connection.connect()

        self.connected = True

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", [self.config.get('user', 'cloudbot'), "3", "*",
                          self.config.get('realname', 'CloudBot - http://git.io/cloudbot')])

    def stop(self):
        self.connection.stop()

    def set_pass(self, password):
        """
        :type password: str
        """
        if password:
            self.cmd("PASS", [password])

    def set_nick(self, nick):
        """
        :type nick: str
        """
        self.cmd("NICK", [nick])

    def join(self, channel):
        """ makes the bot join a channel
        :type channel: str
        """
        self.send("JOIN {}".format(channel))
        if channel not in self.channels:
            self.channels.append(channel)

    def part(self, channel):
        """ makes the bot leave a channel
        :type channel: str
        """
        self.cmd("PART", [channel])
        if channel in self.channels:
            self.channels.remove(channel)

    def msg(self, target, text):
        """ makes the bot send a PRIVMSG to a target
        :type text: str
        :type target: str
        """
        self.cmd("PRIVMSG", [target, text])

    def ctcp(self, target, ctcp_type, text):
        """ makes the bot send a PRIVMSG CTCP to a target
        :type ctcp_type: str
        :type text: str
        :type target: str
        """
        out = "\x01{} {}\x01".format(ctcp_type, text)
        self.cmd("PRIVMSG", [target, out])

    def cmd(self, command, params=None):
        """
        :type command: str
        :type params: list[str]
        """
        if params:
            params[-1] = ':' + params[-1]
            self.send("{} {}".format(command, ' '.join(params)))
        else:
            self.send(command)

    def send(self, string):
        """
        :type string: str
        """
        if not self.connected:
            raise ValueError("Connection must be connected to irc server to use send")
        self.logger.info("[{}] >> {}".format(self.readable_name, string))
        self.loop.call_soon_threadsafe(asyncio.async, self.output_queue.put(string))


class IRCConnection:
    """
    Handles an IRC Connection to a specific IRC server.

    :type logger: logging.Logger
    :type readable_name: str
    :type host: str
    :type port: int
    :type use_ssl: bool
    :type output_queue: asyncio.Queue
    :type message_queue: asyncio.Queue
    :type botconn: BotConnection
    :type ignore_cert_errors: bool
    :type timeout: int
    :type _connected: bool
    """

    def __init__(self, conn, ignore_cert_errors=True, timeout=300):
        """
        :type conn: BotConnection
        """
        self.logger = conn.logger
        self.readable_name = conn.readable_name
        self.host = conn.server
        self.port = conn.port
        self.use_ssl = conn.ssl
        self.output_queue = conn.output_queue  # lines to be sent out
        self.message_queue = conn.message_queue  # global queue for parsed lines that were received
        self.loop = conn.loop
        self.botconn = conn

        if self.use_ssl:
            self.ssl_context = SSLContext(PROTOCOL_SSLv23)
            if ignore_cert_errors:
                self.ssl_context.verify_mode = ssl.CERT_NONE
            else:
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context = None

        self.timeout = timeout
        # Stores if we're connected
        self._connected = False
        # transport and protocol
        self._transport = None
        self._protocol = None

    def describe_server(self):
        if self.use_ssl:
            return "+{}:{}".format(self.host, self.port)
        else:
            return "{}:{}".format(self.host, self.port)

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the irc server
        """
        if self._connected:
            self.logger.info("[{}] Reconnecting".format(self.readable_name))
            self._transport.close()
        else:
            self._connected = True
            self.logger.info("[{}] Connecting".format(self.readable_name))

        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: IRCProtocol(self), host=self.host, port=self.port, ssl=self.ssl_context,
        )

    def stop(self):
        if not self._connected:
            return
        self._transport.close()
        self._connected = False