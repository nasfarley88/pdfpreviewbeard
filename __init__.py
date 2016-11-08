import tempfile
import subprocess as sp
import logging
import re

from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from skybeard.beards import Beard

logger = logging.getLogger(__name__)


def is_pdf(message):
    try:
        return re.match(r".*\.pdf$", message.document.file_name)
    except AttributeError:
        return False

@run_async
def send_pdf_preview(self, bot, update):
    logger.info("Attempting to upload photo")
    from pprint import pprint
    pprint(update.message)
    file_id = update.message.document.file_id
    logger.info("Getting file from telegram")
    pdf_tg_file = bot.getFile(file_id)

    with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
        pdf_tg_file.download(pdf_file.name)
        png_file_bytes = sp.check_output([
            "/bin/pdftoppm",
            "-singlefile",
            "-png",
            pdf_file.name
        ])

    update.message.reply_photo(png_file_bytes)

class PdfPreviewBeard(Beard):

    def initialise(self):
        self.disp.add_handler(CommandHandler("pdfpreviewhelp", self.help))
        self.disp.add_handler(MessageHandler(is_pdf, send_pdf_preview))

    def help(self, bot, update):
        update.message.reply_text(
            """TL;DR This beard shows you the first page of any pdfs it sees."""
        )


