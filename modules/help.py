#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
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

from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.module import ModuleManager
from utils.scripts import format_module_help, with_reply

module_manager = ModuleManager.get_instance()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPFUL TEXT STYLES (Text-only, clean, luxurious)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_header(text: str) -> str:
    """Formatted header dengan garis mewah"""
    return f"╔══════════════════════════════════════════╗
║  {text}  ║
╚══════════════════════════════════════════╝"


def format_subheader(text: str) -> str:
    """Subheader dengan garis sederhana"""
    return f"├─ {text}"


def format_command(cmd: str, desc: str, module: str = None) -> str:
    """Format command yang rapi dan mewah"""
    line = f"│ • <code>{cmd}</code>"
    if desc:
        line += f" ─ <i>{desc}</i>"
    if module:
        line += f"
│         Module: {module}"
    return line


def format_separator() -> str:
    """Garis pemisah"""
    return "│" + "─" * 42 + "│"


def format_footer() -> str:
    """Footer mewah"""
    return "╚══════════════════════════════════════════╝"


def format_module_list() -> str:
    """Format daftar semua module"""
    lines = [format_header("MOON USERBOT — COMMAND LIST")]
    
    sorted_modules = sorted(modules_help.keys())
    
    for i, module in enumerate(sorted_modules, 1):
        commands = list(modules_help[module].keys())
        cmd_count = len(commands)
        
        lines.append(f"
┌ <b>{module.upper()}</b> ({cmd_count} commands)")
        lines.append("│")
        
        for cmd_name, desc in commands.items():
            cmd_base = cmd_name.split()[0]
            lines.append(f"│ • <code>{prefix}{cmd_base}</code> ─ <i>{desc}</i>")
        
        lines.append("└" + "─" * 42)
    
    lines.append(f"
<b>Total:</b> {len(sorted_modules)} modules • {sum(len(v) for v in modules_help.values())} commands")
    lines.append(format_footer())
    
    return "
".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELP COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("╔══════════════════════════════════════════╗
║  <b>Help system initializing...</b>              ║
╚══════════════════════════════════════════╝")
        return

    # Help utama (semua module)
    if len(message.command) == 1:
        help_text = format_module_list()
        await module_manager.help_navigator.send_page(message)
        return
    
    # Help untuk module tertentu
    elif message.command[1].lower() in modules_help:
        module_name = message.command[1].lower()
        commands = modules_help[module_name]
        
        lines = [
            format_header(f"MODULE: {module_name.upper()}"),
            f"
<b>Description:</b> <i>{module_name} module</i>",
            f"
<b>Commands:</b> ({len(commands)} total)",
            "
┌" + "─" * 41 + "┐",
        ]
        
        for cmd_name, desc in commands.items():
            cmd_base = cmd_name.split()[0]
            cmd_args = cmd_name.split(maxsplit=1)
            
            cmd_str = f"{prefix}{cmd_base}"
            if len(cmd_args) > 1:
                cmd_str += f" <code>{cmd_args[1]}</code>"
            
            lines.append(f"│ • <code>{cmd_str}</code>")
            lines.append(f"│   └─ <i>{desc}</i>")
        
        lines.extend([
            "└" + "─" * 41 + "┘",
            "
" + format_footer(),
        ])
        
        await message.edit("
".join(lines))
        return

    # Help untuk command spesifik
    else:
        command_name = message.command[1].lower()
        module_found = False
        
        for module_name, commands in modules_help.items():
            for cmd_full, desc in commands.items():
                if cmd_full.split()[0] == command_name:
                    cmd_parts = cmd_full.split(maxsplit=1)
                    cmd_str = f"{prefix}{cmd_parts[0]}"
                    if len(cmd_parts) > 1:
                        cmd_str += f" <code>{cmd_parts[1]}</code>"
                    
                    lines = [
                        format_header("COMMAND HELP"),
                        f"
<b>Command:</b> <code>{cmd_str}</code>",
                        f"
<b>Module:</b> {module_name}",
                        f"
<b>Description:</b> <i>{desc}</i>",
                        f"
<b>Usage:</b>
<code>{cmd_str}</code>",
                        "
" + format_footer(),
                    ]
                    
                    module_found = True
                    await message.edit("
".join(lines))
                    return
        
        # Search fallback
        if not module_found:
            found = await module_manager.help_navigator.send_search_results(message, command_name)
            if not found:
                await message.edit(
                    f"╔══════════════════════════════════════════╗
"
                    f"║  <b>Not Found</b>                              ║
"
                    f"╠══════════════════════════════════════════╣
"
                    f"║  Module/command <code>{command_name}</code> tidak ditemukan   ║
"
                    f"║                                          ║
"
                    f"║  Gunakan: <code>{prefix}help</code> untuk daftar lengkap      ║
"
                    f"╚══════════════════════════════════════════╝"
                )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SEARCH COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("hs", prefix) & filters.me)
async def search_cmd(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("╔══════════════════════════════════════════╗
║  <b>Help system initializing...</b>              ║
╚══════════════════════════════════════════╝")
        return

    if len(message.command) < 2:
        await message.edit(
            f"╔══════════════════════════════════════════╗
"
            f"║  <b>Usage</b>                                  ║
"
            f"╠══════════════════════════════════════════╣
"
            f"║  <code>{prefix}hs [query]</code>                     ║
"
            f"╚══════════════════════════════════════════╝"
        )
        return

    query = " ".join(message.command[1:]).lower()
    found = await module_manager.help_navigator.send_search_results(message, query)
    
    if not found:
        await message.edit(
            f"╔══════════════════════════════════════════╗
"
            f"║  <b>No Results</b>                             ║
"
            f"╠══════════════════════════════════════════╣
"
            f"║  Tidak ditemukan untuk: <code>{query}</code>           ║
"
            f"╚══════════════════════════════════════════╝"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NAVIGATION COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command(["pn", "pp", "pq"], prefix) & filters.me)
@with_reply
async def handle_navigation(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("╔══════════════════════════════════════════╗
║  <b>Help system initializing...</b>              ║
╚══════════════════════════════════════════╝")
        return

    reply_message = message.reply_to_message
    if reply_message and "Help Page No:" in message.reply_to_message.text:
        cmd = message.command[0].lower()
        
        if cmd == "pn":
            if module_manager.help_navigator.next_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            await message.edit(
                "╔══════════════════════════════════════════╗
"
                "║  <b>No More Pages</b>                          ║
"
                "╚══════════════════════════════════════════╝"
            )
        
        elif cmd == "pp":
            if module_manager.help_navigator.prev_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            await message.edit(
                "╔══════════════════════════════════════════╗
"
                "║  <b>First Page</b>                             ║
"
                "╚══════════════════════════════════════════╝"
            )
        
        elif cmd == "pq":
            await reply_message.delete()
            return await message.edit(
                "╔══════════════════════════════════════════╗
"
                "║  <b>Help Closed</b>                            ║
"
                "╚══════════════════════════════════════════╝"
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MODULE HELP REGISTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

modules_help["help"] = {
    "help [module/command]": "View all modules / specific module help",
    "h [module/command]": "Quick help alias",
    "hs [query]": "Search commands by keyword",
    "pn": "Next page (reply to help)",
    "pp": "Previous page (reply to help)",
    "pq": "Quit help (reply to help)",
                           }
