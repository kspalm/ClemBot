import asyncio
import logging

from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class StartupService(BaseService):
    """
    Service to reload discord state into the database on restart
    this is to account for any leaves or joins, new roles, new channels etc
    that happened while the bot was offline
    """

    def __init__(self, *, bot):
        super().__init__(bot)

    async def load_guilds(self):
        tasks = []
        for guild in self.bot.guilds:
            if not await self.bot.guild_route.get_guild(guild.id):
                log.info(f'Loading guild {guild.name}: {guild.id}')
                tasks.append(asyncio.create_task(self.bot.guild_route.add_guild(guild.id, guild.name)))
        await asyncio.gather(*tasks)

    async def load_users(self):
        db_users = await self.bot.user_route.get_users_ids()
        new_users = [u for u in self.bot.users if u.id not in db_users]

        await self.bot.user_route.create_user_bulk(new_users)

    async def load_users_guilds(self):
        await self.bot.guild_route.update_guild_users(self.bot.guilds)

    async def load_roles(self):
        await self.bot.guild_route.update_guild_roles(self.bot.guilds)

    async def load_channels(self):
        await self.bot.guild_route.update_guild_channels(self.bot.guilds)

    @staticmethod
    def get_full_name(author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self):

        log.info('Starting bot startup internal state reset')

        # First load any new guilds so that we can reference them
        log.info('Resetting Guilds')
        await self.load_guilds()

        # Reset active roles, send all roles to the backend and delete any not present and add any that are new
        log.info('Resetting Guild Roles state')
        await self.load_roles()

        # Load new users, this will pull known users and compare to current users and only add the new ones
        log.info('Resetting Users')
        await self.load_users()

        # Load user guild relationships, takes every guild and sends a complete list of users to the backend
        # to replace the current known state
        log.info('Resetting User_Guilds state')
        await self.load_users_guilds()

        # Reset active channels, send all channels to the backend and delete any not present and add any that are new
        log.info('Resetting Guild Channels state')
        await self.load_channels()

        self.bot.is_starting_up = False
