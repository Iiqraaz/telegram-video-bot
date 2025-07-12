from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import re
import subprocess
import os

BOT_TOKEN = "7669855613:AAFOUENyxUNivQ5E0OO54fCKy-6Ux668deA"
WELCOME_VIDEO_LINK = "https://t.me/cryptonaryspotandfuture/132"
BOT_USERNAME = "@allclipssavebot"

URL_PATTERNS = [
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be|instagram\.com|tiktok\.com|twitter\.com|x\.com|"
    r"reddit\.com|pinterest\.com|soundcloud\.com|spotify\.com|apple\.com|vimeo\.com|likee\.video|"
    r"vk\.com|rutube\.ru|ok\.ru|tumblr\.com|dailymotion\.com|twitch\.tv)/"
]

def is_supported_url(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in URL_PATTERNS)

def download_video(url: str, output_path: str = "video.mp4") -> bool:
    try:
        subprocess.run([
            "yt-dlp",
            "--no-playlist",
            "-f", "best[ext=mp4][filesize<50M]/best[ext=mp4]/best",
            "-o", output_path,
            url
        ], check=True)
        return os.path.exists(output_path)
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Search on YouTube", switch_inline_query="")],
        [InlineKeyboardButton("🌀 Add bot to chat", url=f"https://t.me/{BOT_USERNAME[1:]}?startgroup=true")],
        [InlineKeyboardButton("🤝 Invite a friend", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_video(
        video=WELCOME_VIDEO_LINK,
        caption=(
            "✨ *Welcome to AllClipsSaveBot!*\n\n"
            "Send any link from YouTube, Instagram, TikTok, etc., and I’ll download it fast for you.\n\n"
            "_Use the buttons below for more_"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    if is_supported_url(message_text):
        try:
            await context.bot.set_message_reaction(
                chat_id=update.message.chat_id,
                message_id=update.message.message_id,
                reaction=[ReactionTypeEmoji(emoji='👀')]
            )
        except:
            pass

        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{update.message.message_id}.mp4"

        if download_video(message_text, file_path):
            try:
                await context.bot.send_chat_action(update.effective_chat.id, action="upload_video")
                await update.message.reply_video(video=open(file_path, "rb"))
            except:
                await update.message.reply_text("⚠️ Couldn't send video. Might be too large.")
            finally:
                os.remove(file_path)
        else:
            await update.message.reply_text("❌ Failed to download or unsupported format.")
    else:
        pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a link from any supported platform and I’ll fetch the video for you.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
