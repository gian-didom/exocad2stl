import logging, os
from telegram.ext import Updater, MessageHandler, filters, CallbackContext, CommandHandler, ContextTypes
from telegram import Update
from telegram.ext import ApplicationBuilder
import exocadutils as eu
from datetime import datetime
from shutil import make_archive

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Flow:
# - Download HTML
# - Extract Script tag
# - Extract CTM data
# - Save CTM to disk
# - Convert CTM to STL
# - Send STL

class OpenCTMConverterTelegramBot:
    
    def __init__(self, BOT_TOKEN, BASE_PATH='') -> None:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        if BASE_PATH:
            self.base_path = BASE_PATH
        updater = application.updater
        # html_handler = MessageHandler(filters.FileExtension('html'), OpenCTMConverterTelegramBot.handle_html)
        html_handler = MessageHandler(filters.ATTACHMENT, self.handle_html)
        application.add_handler(html_handler)
        text_handler = MessageHandler(filters.TEXT, OpenCTMConverterTelegramBot.handle_text)
        application.add_handler(text_handler)
        # Command handler
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        

    async def handle_response(function_dict, function_arguments, update: Update, context: CallbackContext):
        
        # Forward to SplitWise handler
        if function_dict['type'] == 'splitwise':
            # Call Splitwise API
            expense, errors = function_dict['function'](**function_arguments)
            # Handle response
            await OpenCTMConverterTelegramBot.handle_splitwise_response(expense, errors, update, context)
            return
        
        # Settings handler
        if function_dict['type'] == 'settings':
            # Call handler only
            result, message = function_dict['function'](**function_arguments)
            await OpenCTMConverterTelegramBot.handle_settings_response(result, message, update, context)
            return
        
        return "Function not found!"

             
    async def handle_text(update: Update, context: CallbackContext, transcribed_text = None):
        print("Messaggio ricevuto!")


    async def handle_attachment(update: Update, context: CallbackContext):
        document = update.message.document
        # Check if the document has extension .html, if yes, defer to handle_html. If not, return
        if document.file_name.endswith('.html'):
            return await OpenCTMConverterTelegramBot.handle_html(update, context)
        else:
            print("This document is not an HTML file.")
            return

    async def handle_html(self, update: Update, context: CallbackContext):
        print("File HTML ricevuto!")
        # Extract HTML
        document = update.message.document
        # Download audio
        html_file_path = await self.download_html(document, update, context)
        html_file_name = document.file_name.replace('.html', '')
        # Make dir in ctm and stl
        os.makedirs(os.path.join(self.base_path, 'ctm', html_file_name), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'stl', html_file_name), exist_ok=True)
        
        # Extract JS scripts
        scripts = []
        with open(html_file_path, 'r') as f:
            html_content = f.read()
            scripts = eu.extract_js_scripts(html_content)
        
        print(f"Processing {len(scripts)} <script> tags...")
        
        ctm_data = []
        for (j, script) in enumerate(scripts):
            # Extend ctm_data with the result of extract_ctm_data
            try:
                this_ctm_data = eu.extract_ctm_data(script)
                ctm_data.extend(this_ctm_data)
            except:
                print(f"No CTM data found in script {j}")
        
        # Process CTM data
        stl_file_names = []
        for (j, ctm) in enumerate(ctm_data):
            # Generate filename based on current date and an index
            ctm_file_name = f"ctm_{html_file_name}_{j}.ctm"
            ctm_file_path = os.path.join(self.base_path, 'ctm', html_file_name, ctm_file_name)
            stl_file_path = os.path.join(self.base_path, 'stl', html_file_name, ctm_file_name.replace('.ctm', '.stl'))
            try:
                eu.save_ctm_to_file(ctm, ctm_file_path)
                mesh = eu.convert_ctm_to_mesh(ctm_file_path)
                eu.save_mesh_to_file(mesh, stl_file_path)
                stl_file_names.append(stl_file_path)
            except Exception as e:
                print(f"Failed to save mesh to file {stl_file_path} due to exception: {e}")
                update.message.reply_text(f"Failed to convert mesh to file `{stl_file_path}` due to exception: `{e}`", parse_mode='MarkdownV2')
        
        # Zip all the downloaded files in a zi folder
        if len(stl_file_names) > 0:
            zip_file_name = html_file_name + '.zip'
            stl_folder_path = os.path.join(self.base_path, 'stl', html_file_name)
            zip_file_path = os.path.join(self.base_path, 'zip', zip_file_name)
            # Zip the self.base_path/stl/{html_file_name} folder in a self.base_path/zip/html_file_name.zip file
            make_archive(os.path.splitext(zip_file_path)[0], 'zip', stl_folder_path)
            
            
            # Now send back all the converted files
            with open(zip_file_path, 'rb') as f:
                await update.message.reply_document(f)
                
        else:
            print("No mesh data retrieved from HTML file.")
                

    
    # async def download_html(document, update: Update, context: CallbackContext) -> str
    # Downloads the HTML file from the Telegram message and saves it to disk
    async def download_html(self, document, update: Update, context: CallbackContext) -> str:
        file_id = document.file_id
        html_file_name = document.file_name
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(os.path.join(self.base_path, 'html', f'{html_file_name}'))
        await update.message.reply_text("File HTML scaricato con successo!")
        return os.path.join(self.base_path, 'html', f'{html_file_name}')