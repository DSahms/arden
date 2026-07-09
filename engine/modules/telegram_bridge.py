"""
TelegramBridge — connects Business Sam to Telegram.
User messages the bot from their phone.
Sam processes on the desktop and responds.
All encrypted via Telegram's MTProto protocol.
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from modules.morning_briefing import MorningBriefing
from modules.task_manager import TaskManager, Priority

logger = logging.getLogger(__name__)


class TelegramBridge:
    def __init__(self, token: str, assistant, allowed_user_id: int = None):
        """
        token: Telegram bot token from @BotFather
        assistant: running PlainAssistant instance
        allowed_user_id: your personal Telegram user ID (security — only YOU can talk to Sam)
        """
        self.token = token
        self.assistant = assistant
        self.allowed_user_id = allowed_user_id
        self.app = Application.builder().token(token).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("tasks", self._cmd_tasks))
        self.app.add_handler(CommandHandler("done", self._cmd_done))
        self.app.add_handler(CommandHandler("briefing", self._cmd_briefing))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    def _is_authorized(self, update: Update) -> bool:
        if self.allowed_user_id is None:
            return True
        return update.effective_user.id == self.allowed_user_id

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            await update.message.reply_text("Unauthorized.")
            return
        await update.message.reply_text(
            "Sam is online. I'm connected to your desktop.\n\n"
            "Commands:\n"
            "/briefing — Morning briefing\n"
            "/tasks — See all open tasks\n"
            "/done [task number] — Mark a task complete\n"
            "/help — Show this menu\n\n"
            "Or just talk to me normally."
        )

    async def _cmd_briefing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            return
        briefing = self.assistant.morning_briefing.generate()
        await update.message.reply_text(briefing)

    async def _cmd_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            return
        tasks = self.assistant.task_manager.get_open_tasks()
        if not tasks:
            await update.message.reply_text("No open tasks. You're clear.")
            return
        lines = ["Open tasks:\n"]
        for t in tasks:
            due = f" (due {t.due_date})" if t.due_date else ""
            lines.append(f"#{t.id} [{t.priority.value.upper()}] {t.content}{due}")
        await update.message.reply_text("\n".join(lines))

    async def _cmd_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            return
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /done [task number] — example: /done 3")
            return
        try:
            task_id = int(args[0])
            self.assistant.task_manager.mark_done(task_id)
            await update.message.reply_text(f"Task #{task_id} marked done. Good work.")
        except (ValueError, IndexError):
            await update.message.reply_text("Invalid task number.")

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            return
        await update.message.reply_text(
            "Sam — Business Edition\n\n"
            "/briefing — Daily briefing\n"
            "/tasks — Open task list\n"
            "/done [#] — Mark task complete\n\n"
            "Or just send a message and I'll respond."
        )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            await update.message.reply_text("Unauthorized.")
            return

        user_text = update.message.text
        await update.message.reply_chat_action("typing")

        try:
            # Route through the desktop assistant's existing process_text method
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.assistant.process_text,
                user_text
            )
            if response:
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("I processed that but had no response. Try again.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("Something went wrong on the desktop. Check the console.")

    def run(self):
        """Start the Telegram bot in polling mode."""
        logger.info("Telegram bridge starting...")
        self.app.run_polling(drop_pending_updates=True)
