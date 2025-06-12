from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    IMAGEN = 'negocio.jpg'
    user = update.effective_user
    print(f"Nuevo usuario: @{user.username} (ID: {user.id})")
    mensaje = (
        "Bienvenid@ al bot. Mediante este sistema puedes:\n"
        "/prestamo - Solicitar un préstamo de equipo médico.\n"
        "/ordentrabajo - Crear una orden de trabajo\n"
        "/cancelar - Detener el proceso en cualquier momento."
    )
    with open(IMAGEN, 'rb') as foto:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=foto, caption=mensaje)
