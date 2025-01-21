import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from transformers import pipeline
import torch

# Configurar el modelo LLM -
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
pipe = pipeline("text-generation", model=model_name, torch_dtype=torch.bfloat16, device_map="auto")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()} , I am AnimalDSBot and I love animals. Thanks for chatting with me!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Please ask me something about your favourite animal so I can respond!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def process_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the text using the LLM model."""
    user_message = update.message.text
    inputs = pipe.tokenizer(f"User: {user_message}\nAI:", return_tensors="pt")
    
    with torch.no_grad():
        outputs = pipe.model.generate(**inputs, max_length=200, temperature=0.7, top_p=0.9, do_sample=True)

    response = pipe.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    response = response.replace(f"User: {user_message}", "").replace("AI:", "").strip()
    
    await update.message.reply_text(response if response else "I'm not sure how to respond to that.")

async def custom_responses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle specific custom messages."""
    text = update.message.text.lower()
    if text == "hello world":
        await update.message.reply_text("Hello, World!")
    elif text == "hi assistant":
        await update.message.reply_text("Hello! How can I assist you today?")
    else:
        # Utilizar la función process_with_ai para generar una respuesta
        await process_with_ai(update, context)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("8170401737:AAFDSVLU_4BDc_2LB6ZCTv20YFT6s2ydaSw").connect_timeout(30.0).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # On non-command i.e. message - handle custom responses or echo the message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, custom_responses))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()