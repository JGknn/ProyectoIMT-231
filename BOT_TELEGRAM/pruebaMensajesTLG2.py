import logging  #registro de eventos
from telegram import Update, ReplyKeyboardRemove  #actualización de telegram (mensaje, comando, etc)
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime
import os
import cv2


TOKEN = '7854191859:AAEFK--ZL3_uA6i49h9nfHQcG-LEHJ-gAuY'  #Token unico del bot
IMAGEN = 'negocio.jpg' 
ARCHIVO_SOLICITUDES = 'solicitudes.txt'
logging.basicConfig(level=logging.INFO) #configuracion del sistema de logging que muestra mensajes de nivel INFO y superior
DETALLES, FOTO = range(2)
datos_usuario = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): #funcion asincrona que se ejecutara cuando el usuario envie "/start"
	USER_ID = update.effective_user.id #obtiene el chat_id del usuario que interactuó con el bot
	USERNAME = update.effective_user.username #obtiene el nombre de usuario @ del mismo
	print(f"Nuevo usuario: @{USERNAME} (ID: {USER_ID})")

	MENSAJE = "Bienvenido al bot. Usa los comandos:\n/prestamo para solicitar un préstamo\n/ordentrabajo para crear una orden de trabajo"

	with open(IMAGEN, 'rb') as FOTO: #abre la imagen en modo "binario de lectura"
		await context.bot.send_photo(chat_id=update.effective_chat.id, photo=FOTO, caption=MENSAJE) #envia foto al chat con texto de pie de foto


async def iniciar_prestamo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text("Por favor, escribe el detalle del préstamo. Con el formato:\nArea: Enfermeria Equipo: Monitor Codigo: 123asd")
	return DETALLES

async def recibir_detalles(update: Update, context: ContextTypes.DEFAULT_TYPE):
	USER_ID = update.effective_user.id
	USERNAME = update.effective_user.username
	texto = update.message.text

	datos_usuario[USER_ID] = {"username": USERNAME, "detalles": texto, "fecha": datetime.now()}

	await update.message.reply_text("Ahora, envíe una foto del QR en el equipo.")
	return FOTO

async def recibir_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
	USER_ID = update.effective_user.id

	if not update.message.photo:
		await update.message.reply_text("Por favor, envíe una **foto**, no texto.")
		return FOTO

	foto = update.message.photo[-1]
	file = await context.bot.get_file(foto.file_id)
    
	ruta_temporal = f"temp_{USER_ID}.jpg"
	await file.download_to_drive(ruta_temporal)

	try:
		imagen = cv2.imread(ruta_temporal)
		detector = cv2.QRCodeDetector()
		datos_qr, puntos, _ = detector.detectAndDecode(imagen)

		if not datos_qr:
			datos_qr = "QR no detectado"
	except Exception as e:
		datos_qr = f"Error al leer QR: {e}"

	os.remove(ruta_temporal)

	datos_usuario[USER_ID]["foto_id"] = foto.file_id
	datos_usuario[USER_ID]["qr"] = datos_qr

	info = datos_usuario[USER_ID]
	registro = (
        f"{info['fecha']} - PRESTAMO - Usuario: @{info['username']} (ID: {USER_ID}) - "
        f"Detalles: {info['detalles']} - FotoID: {foto.file_id} - QR: {datos_qr}\n")

	with open(ARCHIVO_SOLICITUDES, 'a') as file:
		file.write(registro)

	await update.message.reply_text("✅ Solicitud de préstamo recibida y registrada.", reply_markup=ReplyKeyboardRemove())

	datos_usuario.pop(USER_ID, None)
	return ConversationHandler.END







async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text("Operación cancelada.", reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END

async def orden_trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	USER_ID = update.effective_user.id
	USERNAME = update.effective_user.username
    
	if not context.args:
		await update.message.reply_text("Por favor, escribe el detalle de la orden. Con el formato:\nTipo de trabajo: --- Area: --- Urgencia: ---")
		return

	solicitud = ' '.join(context.args)
	registro = f"{datetime.now()} - ORDEN_TRABAJO - Usuario: @{USERNAME} (ID: {USER_ID}) - Detalles: {solicitud}\n"

	with open(ARCHIVO_SOLICITUDES, 'a') as file:
		file.write(registro)

	await update.message.reply_text("✅ Orden de trabajo recibida y registrada.")



if __name__ == '__main__': #comprueba si el script se ejecuta directamente (no importado como modulo)
	app = Application.builder().token(TOKEN).build() #crea la aplicación del bot usando el token

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler("prestamo", iniciar_prestamo)],
		states={DETALLES: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_detalles)],FOTO: [MessageHandler(filters.PHOTO, recibir_foto)],},
		fallbacks=[CommandHandler("cancelar", cancelar)],)

	app.add_handler(CommandHandler("start", start))
	app.add_handler(conv_handler)

	app.add_handler(CommandHandler("ordentrabajo", orden_trabajo))
	print("Bot iniciado. Esperando comandos...") #mensaje para indicar que el bot esta listo
	app.run_polling() #pone el bot en modo "polling", es decir consulta constantemente al servidor de telegram por actualizaciones
