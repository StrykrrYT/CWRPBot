import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands
from cogs.purge import Purge 
from cogs.sync import Sync


class TestPurgeCommand(unittest.IsolatedAsyncioTestCase):
    purge_command = self.cog.purge
    purge_params = amount
    main_command = purge_command

    async def asyncSetUp(self):
        self.bot = MagicMock()  # Mock the bot instance
        cog = Purge
        self.cog = cog(self.bot)

        # Simulate a test interaction
        self.interaction = MagicMock()
        self.interaction.response = AsyncMock()

        # Mock a channel where messages can be purged
        self.channel = MagicMock()
        self.channel.purge = AsyncMock(return_value=[MagicMock() for _ in range(5)])  # Mock purging 5 messages
        self.channel.permissions_for.return_value.manage_messages = True  # Ensure manage_messages permission is mocked as True by default
        self.interaction.channel = self.channel

    async def test_purge_command(self):
        # Test valid amount
        amount = 10000
        await main_command(self.cog, self.interaction, purge_params)  # Pass self.cog as the first argument

        # Assert that interaction.response.send_message was called with expected parameters
        self.interaction.response.send_message.assert_called_once_with(f'Purged {amount} messages', ephemeral=True)

        # Assert that channel.purge was called with the correct amount of messages to delete
        self.channel.purge.assert_awaited_once_with(limit=amount)

    async def test_purge_invalid_amount(self):
        # Test invalid amount
        invalid_amount = -5
        await self.cog.purge(self.cog, self.interaction, invalid_amount)  # Pass self.cog as the first argument

        # Assert that interaction.response.send_message was called with an invalid amount message
        self.interaction.response.send_message.assert_called_once_with('Invalid amount. Please specify a positive number of messages to purge.', ephemeral=True)

        # Assert that channel.purge was not awaited due to invalid amount
        self.channel.purge.assert_not_awaited()

    async def test_purge_without_permissions(self):
        # Simulate lack of manage_messages permission
        self.channel.permissions_for.return_value.manage_messages = False

        amount = 5
        await self.cog.purge(self.cog, self.interaction, amount)  # Pass self.cog as the first argument

        # Assert that interaction.response.send_message was called with a permission error message
        self.interaction.response.send_message.assert_called_once_with("You don't have permission to manage messages in this channel.", ephemeral=True)

        # Assert that channel.purge was not awaited due to lack of permissions
        self.channel.purge.assert_not_awaited()

    async def test_purge_zero_amount(self):
        # Test with zero amount
        amount = 0
        await self.cog.purge(self.cog, self.interaction, amount)  # Pass self.cog as the first argument

        # Assert that interaction.response.send_message was called with an invalid amount message
        self.interaction.response.send_message.assert_called_once_with('Invalid amount. Please specify a positive number of messages to purge.', ephemeral=True)

        # Assert that channel.purge was not awaited due to zero amount
        self.channel.purge.assert_not_awaited()

    async def test_purge_large_amount(self):
        # Test with a large amount that exceeds typical message limits
        amount = 1000
        await self.cog.purge(self.cog, self.interaction, amount)  # Pass self.cog as the first argument

        # Assert that interaction.response.send_message was called with expected purging message
        self.interaction.response.send_message.assert_called_once_with(f'Purged {amount} messages', ephemeral=True)

        # Assert that channel.purge was called with the maximum allowed limit (if your bot imposes a limit)
        self.channel.purge.assert_awaited_once()

    async def test_purge_multiple_invocations(self):
        # Test multiple invocations of purge command without waiting for previous purges to complete
        amount = 10

        # Simulate concurrent invocations
        tasks = []
        for _ in range(5):
            tasks.append(self.cog.purge(self.cog, self.interaction, amount))

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Assert that interaction.response.send_message was called multiple times
        self.assertEqual(self.interaction.response.send_message.call_count, 5)

        # Assert that channel.purge was called the correct number of times
        self.assertEqual(self.channel.purge.call_count, 5)

if __name__ == '__main__':
    unittest.main()
