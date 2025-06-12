import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

def iniciar_bot(
    token,
    start_handler,
    iniciar_prestamo_handler,
    recibir_detalles_prestamo_handler,
    recibir_foto_prestamo_handler,
    cancelar_handler,
    iniciar_orden_handler,
    recibir_detalles_orden_handler,
    recibir_foto_orden_handler,
    detalles_prestamo_state,
    foto_prestamo_state,
    detalles_orden_state,
    foto_orden_state
):

    try:
        app = Application.builder().token(token).build()

        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("prestamo", iniciar_prestamo_handler)],
            states={
                detalles_prestamo_state: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_detalles_prestamo_handler)],
                foto_prestamo_state: [MessageHandler(filters.PHOTO, recibir_foto_prestamo_handler)]
            },
            fallbacks=[CommandHandler("cancelar", cancelar_handler)]
        ))

        app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("ordentrabajo", iniciar_orden_handler)],
            states={
                detalles_orden_state: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_detalles_orden_handler)],
                foto_orden_state: [MessageHandler(filters.PHOTO, recibir_foto_orden_handler)]
            },
            fallbacks=[CommandHandler("cancelar", cancelar_handler)]
        ))

        print("Bot iniciado y listo para operar.")
        app.run_polling()
    except Exception as e:
        print(f"Error en el bot: {e}")
        os._exit(1)
