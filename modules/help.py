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
#  HELPFUL TEXT STYLES (Minimalist & Modern)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_header(text: str) -> str:
    """Formatted header minimalis modern"""
    return f"✨ <b>{text}</b> ✨\n──────────────────────────────"


def format_subheader(text: str) -> str:
    """Subheader dengan garis tipis"""
    return f"🔹 {text}"


def format_command(cmd: str, desc: str, module: str = None) -> str:
    """Format command yang rapi dan minimalis"""
    line = f"• <code>{cmd}</code>"
    if desc:
        line += f" ─ <i>{desc}</i>"
    if module:
        line += f"\n  └─ Modul: {module}"
    return line


def format_separator() -> str:
    """Garis pemisah"""
    return "──────────────────────────────"


def format_footer() -> str:
    """Footer minimalis"""
    return "──────────────────────────────"


def format_module_list() -> str:
    """Format daftar semua module"""
    lines = [format_header("MOON USERBOT — DAFTAR PERINTAH")]
    
    sorted_modules = sorted(modules_help.keys())
    
    for module in sorted_modules:
        commands = modules_help[module]
        cmd_count = len(commands)
        
        lines.append(f"\n🔹 <b>{module.upper()}</b> ({cmd_count} perintah)")
        cmd_list = " • ".join([f"<code>{prefix}{cmd_name.split()[0]}</code>" for cmd_name in commands.keys()])
        lines.append(f"  {cmd_list}")
        
    lines.append("\n" + format_separator())
    lines.append(f"📊 Modul: <b>{len(sorted_modules)}</b> | Perintah: <b>{sum(len(v) for v in modules_help.values())}</b>")
    lines.append(format_separator())
    
    return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELP COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("✨ <b>Sistem bantuan sedang diinisialisasi...</b>")
        return

    # Help utama (semua module)
    if len(message.command) == 1:
        await module_manager.help_navigator.send_page(message)
        return
    
    # Help untuk module tertentu
    elif message.command[1].lower() in modules_help:
        module_name = message.command[1].lower()
        commands = modules_help[module_name]
        
        lines = [
            format_header(f"MODUL: {module_name.upper()}"),
            f"📦 Total Perintah: <b>{len(commands)}</b>",
            "──────────────────────────────\n",
        ]
        
        for cmd_name, desc in commands.items():
            cmd_base = cmd_name.split()[0]
            cmd_args = cmd_name.split(maxsplit=1)
            
            cmd_str = f"{prefix}{cmd_base}"
            if len(cmd_args) > 1:
                cmd_str += f" <code>{cmd_args[1]}</code>"
            
            lines.append(f"• <code>{cmd_str}</code>")
            lines.append(f"  └─ <i>{desc}</i>\n")
        
        lines.append("──────────────────────────────")
        lines.append(f"[ ◀️ Kembali ke Menu Utama: <code>{prefix}help</code> ]")
        
        await message.edit("\n".join(lines))
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
                        format_header(f"PERINTAH: {prefix.upper()}{command_name.upper()}"),
                        f"📂 Modul: <b>{module_name.title()}</b>",
                        f"📝 Deskripsi: <i>{desc}</i>",
                        f"💡 Penggunaan: <code>{cmd_str}</code>",
                        "──────────────────────────────",
                        f"[ ◀️ Kembali ke Menu Utama: <code>{prefix}help</code> ]"
                    ]
                    
                    module_found = True
                    await message.edit("\n".join(lines))
                    return
        
        # Search fallback
        if not module_found:
            found = await module_manager.help_navigator.send_search_results(message, command_name)
            if not found:
                await message.edit(
                    f"⚠️ <b>TIDAK DITEMUKAN</b>\n"
                    f"──────────────────────────────\n"
                    f"Modul/perintah <code>{command_name}</code> tidak ditemukan.\n\n"
                    f"💡 Gunakan <code>{prefix}help</code> untuk daftar lengkap."
                )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SEARCH COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("hs", prefix) & filters.me)
async def search_cmd(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("✨ <b>Sistem bantuan sedang diinisialisasi...</b>")
        return

    if len(message.command) < 2:
        await message.edit(
            f"💡 <b>PENGGUNAAN</b>\n"
            f"──────────────────────────────\n"
            f"Ketik: <code>{prefix}hs [kata_kunci]</code>"
        )
        return

    query = " ".join(message.command[1:]).lower()
    found = await module_manager.help_navigator.send_search_results(message, query)
    
    if not found:
        await message.edit(
            f"⚠️ <b>TIDAK DITEMUKAN</b>\n"
            f"──────────────────────────────\n"
            f"Tidak ada hasil untuk: <code>{query}</code>"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NAVIGATION COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command(["pn", "pp", "pq"], prefix) & filters.me)
@with_reply
async def handle_navigation(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("✨ <b>Sistem bantuan sedang diinisialisasi...</b>")
        return

    reply_message = message.reply_to_message
    if reply_message and ("MOON USERBOT HELP" in reply_message.text or "Halaman:" in reply_message.text):
        cmd = message.command[0].lower()
        
        if cmd == "pn":
            if module_manager.help_navigator.next_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            await message.edit("⚠️ <b>Tidak ada halaman lagi</b>")
        
        elif cmd == "pp":
            if module_manager.help_navigator.prev_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            await message.edit("⚠️ <b>Ini adalah halaman pertama</b>")
        
        elif cmd == "pq":
            await reply_message.delete()
            return await message.edit("❌ <b>Menu bantuan ditutup</b>")


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
