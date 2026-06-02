#  KinguBot - telegram userbot
#  Based on Moon-Userbot
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math

from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix

# ═══════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════

BOT_NAME = "KinguBot"
MODULES_PER_PAGE = 8

# Store current page state per chat
_page_state = {}


# ═══════════════════════════════════════════════════
#  UI DESIGN HELPERS
# ═══════════════════════════════════════════════════

def _bar(width: int = 28) -> str:
    return "─" * width


def _header() -> str:
    return (
        f"╭{'─' * 30}╮\n"
        f"│  ⚡ <b>{BOT_NAME}</b>  ·  <i>Help Center</i>\n"
        f"╰{'─' * 30}╯"
    )


def _footer_nav(page: int, total: int, chat_id: int) -> str:
    """Build navigation footer with page indicator."""
    # Page dots
    dots = ""
    for i in range(1, total + 1):
        dots += "●" if i == page else "○"
        if i < total:
            dots += " "

    nav_left = f"<code>{prefix}hp</code>" if page > 1 else "    "
    nav_right = f"<code>{prefix}hn</code>" if page < total else "    "

    lines = [
        _bar(30),
        f"  {nav_left}   {dots}   {nav_right}",
        f"  ◀ prev          next ▶" if total > 1 else "",
        _bar(30),
        f"  💡 <code>{prefix}help &lt;module&gt;</code> for details",
        f"  🔍 <code>{prefix}hs &lt;keyword&gt;</code> to search",
    ]
    return "\n".join(line for line in lines if line)


def _render_module_card(name: str, commands: dict) -> str:
    """Render a single module as a compact card."""
    cmd_count = len(commands)
    cmd_names = [f"<code>{prefix}{c.split()[0]}</code>" for c in commands.keys()]
    cmd_line = "  ".join(cmd_names)

    return (
        f"  ▸ <b>{name}</b>  <i>({cmd_count})</i>\n"
        f"    {cmd_line}"
    )


def _build_page(chat_id: int) -> str:
    """Build the help page text for current page state."""
    sorted_modules = sorted(modules_help.keys())
    total_modules = len(sorted_modules)
    total_commands = sum(len(v) for v in modules_help.values())
    total_pages = max(1, math.ceil(total_modules / MODULES_PER_PAGE))

    page = _page_state.get(chat_id, 1)
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    _page_state[chat_id] = page

    start = (page - 1) * MODULES_PER_PAGE
    end = start + MODULES_PER_PAGE
    page_modules = sorted_modules[start:end]

    # Header
    lines = [_header(), ""]

    # Stats bar
    lines.append(
        f"  📦 <b>{total_modules}</b> modules  ·  ⚙️ <b>{total_commands}</b> commands  ·  📄 <b>{page}/{total_pages}</b>"
    )
    lines.append("")

    # Module cards
    for mod_name in page_modules:
        lines.append(_render_module_card(mod_name, modules_help[mod_name]))
        lines.append("")

    # Navigation footer
    lines.append(_footer_nav(page, total_pages, chat_id))

    return "\n".join(lines)


def _build_module_detail(module_name: str) -> str:
    """Build detailed help for a specific module."""
    commands = modules_help[module_name]

    lines = [
        f"╭{'─' * 30}╮",
        f"│  📦 <b>{module_name.upper()}</b>",
        f"│  <i>{len(commands)} command(s) available</i>",
        f"╰{'─' * 30}╯",
        "",
    ]

    for cmd_full, desc in commands.items():
        parts = cmd_full.split(maxsplit=1)
        cmd_name = parts[0]
        cmd_args = f" <code>{parts[1]}</code>" if len(parts) > 1 else ""

        lines.append(f"  ▸ <code>{prefix}{cmd_name}</code>{cmd_args}")
        lines.append(f"    <i>{desc}</i>")
        lines.append("")

    lines.append(_bar(30))
    lines.append(f"  ◀ <code>{prefix}help</code> back to menu")

    return "\n".join(lines)


def _build_search_results(query: str) -> str | None:
    """Search modules and commands, return formatted results."""
    query_lower = query.lower()
    results_modules = []
    results_commands = []

    for mod_name, commands in modules_help.items():
        # Match module name
        if query_lower in mod_name.lower():
            results_modules.append(mod_name)

        # Match command names or descriptions
        for cmd_full, desc in commands.items():
            cmd_base = cmd_full.split()[0].lower()
            if query_lower in cmd_base or query_lower in desc.lower():
                results_commands.append((cmd_base, desc, mod_name))

    if not results_modules and not results_commands:
        return None

    lines = [
        f"╭{'─' * 30}╮",
        f"│  🔍 Search: <code>{query}</code>",
        f"╰{'─' * 30}╯",
        "",
    ]

    if results_modules:
        lines.append("  <b>Modules</b>")
        for mod in results_modules[:5]:
            cmd_count = len(modules_help[mod])
            lines.append(f"    ▸ <b>{mod}</b> <i>({cmd_count} cmds)</i>")
        lines.append("")

    if results_commands:
        lines.append("  <b>Commands</b>")
        for cmd_name, desc, mod in results_commands[:10]:
            lines.append(f"    ▸ <code>{prefix}{cmd_name}</code> — <i>{desc}</i>")
            lines.append(f"      └ <code>{mod}</code>")
        lines.append("")

    lines.append(_bar(30))
    lines.append(f"  💡 <code>{prefix}help &lt;name&gt;</code> for details")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════

@Client.on_message(filters.command(["help", "helpme", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    """Main help command — show paginated module list or module detail."""
    chat_id = message.chat.id

    if len(message.command) == 1:
        # Show page 1
        _page_state[chat_id] = 1
        text = _build_page(chat_id)
        await message.edit(text, disable_web_page_preview=True)
        return

    arg = message.command[1].lower()

    # Check if it's a module name
    if arg in modules_help:
        text = _build_module_detail(arg)
        await message.edit(text, disable_web_page_preview=True)
        return

    # Check if it's a command name → find its module
    for mod_name, commands in modules_help.items():
        for cmd_full in commands:
            if cmd_full.split()[0].lower() == arg:
                text = _build_module_detail(mod_name)
                await message.edit(text, disable_web_page_preview=True)
                return

    # Nothing found
    await message.edit(
        f"╭{'─' * 30}╮\n"
        f"│  ⚠️ <b>Not Found</b>\n"
        f"╰{'─' * 30}╯\n\n"
        f"  <code>{arg}</code> is not a valid module or command.\n\n"
        f"  💡 <code>{prefix}help</code> — view all modules\n"
        f"  💡 <code>{prefix}hs {arg}</code> — try searching",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("hn", prefix) & filters.me)
async def help_next(_, message: Message):
    """Next page."""
    chat_id = message.chat.id
    total_pages = max(1, math.ceil(len(modules_help) / MODULES_PER_PAGE))
    current = _page_state.get(chat_id, 1)

    if current < total_pages:
        _page_state[chat_id] = current + 1
        text = _build_page(chat_id)

        # If replying to a help message, edit that; otherwise edit self
        if message.reply_to_message:
            await message.reply_to_message.edit(text, disable_web_page_preview=True)
            await message.delete()
        else:
            await message.edit(text, disable_web_page_preview=True)
    else:
        await message.edit(
            f"  ⚠️ <i>Already on the last page ({current}/{total_pages})</i>",
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command("hp", prefix) & filters.me)
async def help_prev(_, message: Message):
    """Previous page."""
    chat_id = message.chat.id
    current = _page_state.get(chat_id, 1)

    if current > 1:
        _page_state[chat_id] = current - 1
        text = _build_page(chat_id)

        if message.reply_to_message:
            await message.reply_to_message.edit(text, disable_web_page_preview=True)
            await message.delete()
        else:
            await message.edit(text, disable_web_page_preview=True)
    else:
        await message.edit(
            f"  ⚠️ <i>Already on the first page (1/{max(1, math.ceil(len(modules_help) / MODULES_PER_PAGE))})</i>",
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command(["hg"], prefix) & filters.me)
async def help_goto(_, message: Message):
    """Go to a specific page number."""
    chat_id = message.chat.id
    total_pages = max(1, math.ceil(len(modules_help) / MODULES_PER_PAGE))

    if len(message.command) < 2:
        await message.edit(
            f"  💡 <code>{prefix}hg &lt;page_number&gt;</code>",
            disable_web_page_preview=True,
        )
        return

    try:
        target = int(message.command[1])
    except ValueError:
        await message.edit("  ⚠️ <i>Please enter a valid page number.</i>")
        return

    if target < 1 or target > total_pages:
        await message.edit(
            f"  ⚠️ <i>Page {target} does not exist. (1–{total_pages})</i>"
        )
        return

    _page_state[chat_id] = target
    text = _build_page(chat_id)

    if message.reply_to_message:
        await message.reply_to_message.edit(text, disable_web_page_preview=True)
        await message.delete()
    else:
        await message.edit(text, disable_web_page_preview=True)


@Client.on_message(filters.command("hs", prefix) & filters.me)
async def help_search(_, message: Message):
    """Search modules and commands."""
    if len(message.command) < 2:
        await message.edit(
            f"╭{'─' * 30}╮\n"
            f"│  🔍 <b>Search</b>\n"
            f"╰{'─' * 30}╯\n\n"
            f"  <code>{prefix}hs &lt;keyword&gt;</code>",
            disable_web_page_preview=True,
        )
        return

    query = " ".join(message.command[1:])
    result = _build_search_results(query)

    if result:
        await message.edit(result, disable_web_page_preview=True)
    else:
        await message.edit(
            f"╭{'─' * 30}╮\n"
            f"│  🔍 No results for <code>{query}</code>\n"
            f"╰{'─' * 30}╯\n\n"
            f"  💡 <code>{prefix}help</code> — browse all modules",
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command(["plugins", "modules"], prefix) & filters.me)
async def plugins_cmd(_, message: Message):
    """Quick overview of all plugins (compact list)."""
    sorted_modules = sorted(modules_help.keys())
    total = len(sorted_modules)
    total_cmds = sum(len(v) for v in modules_help.values())

    lines = [
        f"╭{'─' * 30}╮",
        f"│  📋 <b>{BOT_NAME}</b>  ·  <i>Plugins</i>",
        f"╰{'─' * 30}╯",
        "",
        f"  📦 <b>{total}</b> modules  ·  ⚙️ <b>{total_cmds}</b> commands",
        "",
    ]

    # Compact 3-column list
    cols = 3
    rows = math.ceil(total / cols)
    for r in range(rows):
        row_items = []
        for c in range(cols):
            idx = r + c * rows
            if idx < total:
                row_items.append(f"<code>{sorted_modules[idx]}</code>")
        lines.append("  " + "  ·  ".join(row_items))

    lines.append("")
    lines.append(_bar(30))
    lines.append(f"  💡 <code>{prefix}help &lt;module&gt;</code> for details")

    await message.edit("\n".join(lines), disable_web_page_preview=True)


# ═══════════════════════════════════════════════════
#  UTILITY
# ═══════════════════════════════════════════════════

def add_command_help(module_name, commands):
    """Legacy helper for registering module commands."""
    if module_name in modules_help:
        command_dict = modules_help[module_name]
    else:
        command_dict = {}

    for x in commands:
        for y in x:
            if y is not x:
                command_dict[x[0]] = x[1]

    modules_help[module_name] = command_dict


# ═══════════════════════════════════════════════════
#  REGISTER HELP MODULE
# ═══════════════════════════════════════════════════

modules_help["help"] = {
    "help [module]": "Show help menu or module details",
    "h [module]": "Alias for help",
    "hn": "Next help page",
    "hp": "Previous help page",
    "hg [page]": "Jump to specific page",
    "hs [keyword]": "Search modules & commands",
    "plugins": "List all plugins (compact)",
    "modules": "Alias for plugins",
}
