"""
Pluggable Command, Regex, and Conversational State Dispatcher for WhatsApp bots.
Zero dependencies on application-specific databases or models.
"""

import inspect
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Pattern

from whatsapp_gateway.bot.context import MessageContext

logger = logging.getLogger("whatsapp_gateway.dispatcher")


class BotDispatcher:
    """
    Decoupled router for WhatsApp messages supporting:
    - Named commands (e.g. 'help', 'start', 'quiz')
    - Regular expressions (e.g. scripture citations, order numbers)
    - Stateful multi-turn handlers (e.g. 'WAITING_QUIZ_ANSWER')
    - Fallback handler
    """

    def __init__(self, command_prefix: str = ""):
        self.command_prefix = command_prefix
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._regex_handlers: List[Dict[str, Any]] = []
        self._state_handlers: Dict[str, Callable] = {}
        self._fallback_handler: Optional[Callable] = None

    def command(
        self,
        name: str,
        aliases: Optional[List[str]] = None,
        description: str = "",
    ):
        """Decorator to register a command handler."""
        def decorator(func: Callable):
            cmd_info = {
                "func": func,
                "name": name.lower(),
                "aliases": [a.lower() for a in (aliases or [])],
                "description": description,
            }
            self._commands[name.lower()] = cmd_info
            for alias in (aliases or []):
                self._commands[alias.lower()] = cmd_info
            return func
        return decorator

    def regex(
        self,
        pattern: str,
        flags: int = re.IGNORECASE,
        description: str = "",
    ):
        """Decorator to register a regex pattern handler."""
        compiled = re.compile(pattern, flags)
        def decorator(func: Callable):
            self._regex_handlers.append({
                "func": func,
                "pattern": compiled,
                "description": description,
            })
            return func
        return decorator

    def state(self, state_name: str):
        """Decorator to register a handler for active conversational state."""
        def decorator(func: Callable):
            self._state_handlers[state_name] = func
            return func
        return decorator

    def fallback(self, func: Callable):
        """Decorator to register a fallback handler when no route matches."""
        self._fallback_handler = func
        return func

    def generate_help_text(self, header: str = "*📖 WhatsApp Assistant Menu:*") -> str:
        """Dynamically builds a WhatsApp-formatted help menu from registered commands."""
        lines = [header, ""]
        seen_funcs = set()

        for name, cmd in self._commands.items():
            func = cmd["func"]
            if func in seen_funcs:
                continue
            seen_funcs.add(func)
            desc = cmd["description"] or "No description"
            aliases_str = f" _(or {', '.join(cmd['aliases'])})_" if cmd["aliases"] else ""
            lines.append(f"• *{self.command_prefix}{cmd['name']}*{aliases_str} — {desc}")

        for item in self._regex_handlers:
            if item["description"]:
                lines.append(f"• _{item['description']}_")

        lines.append("")
        lines.append("_Send any of the above commands to interact!_")
        return "\n".join(lines)

    async def dispatch(self, ctx: MessageContext) -> bool:
        """
        Dispatches the incoming message to the appropriate handler.
        Returns True if a handler was executed, False otherwise.
        """
        text = ctx.text.strip()
        if not text:
            return False

        # 1. Check for Active Conversational State
        session = await ctx.get_state()
        if session and session.get("state") in self._state_handlers:
            state_name = session["state"]
            handler = self._state_handlers[state_name]
            logger.debug("Routing to state handler '%s' for sender %s", state_name, ctx.sender)
            await self._invoke_handler(handler, ctx)
            return True

        # 2. Check for Named Commands
        first_word = text.split()[0].lower() if text else ""
        if self.command_prefix and first_word.startswith(self.command_prefix):
            cmd_name = first_word[len(self.command_prefix):]
        else:
            cmd_name = first_word

        if cmd_name in self._commands:
            handler = self._commands[cmd_name]["func"]
            logger.debug("Routing to command '%s' for sender %s", cmd_name, ctx.sender)
            await self._invoke_handler(handler, ctx)
            return True

        # 3. Check for Regex Pattern Matches
        for r_entry in self._regex_handlers:
            match = r_entry["pattern"].search(text)
            if match:
                ctx.matches = match
                logger.debug("Routing to regex pattern '%s' for sender %s", r_entry["pattern"].pattern, ctx.sender)
                await self._invoke_handler(r_entry["func"], ctx)
                return True

        # 4. Fallback Handler
        if self._fallback_handler:
            logger.debug("Routing to fallback handler for sender %s", ctx.sender)
            await self._invoke_handler(self._fallback_handler, ctx)
            return True

        return False

    async def _invoke_handler(self, func: Callable, ctx: MessageContext) -> None:
        """Invokes a sync or async handler safely."""
        try:
            if inspect.iscoroutinefunction(func):
                await func(ctx)
            else:
                func(ctx)
        except Exception as exc:
            logger.exception("Error during WhatsApp handler execution: %s", exc)
            await ctx.reply_text(
                "⚠️ *Error processing request*: An unexpected internal error occurred. Please try again."
            )
