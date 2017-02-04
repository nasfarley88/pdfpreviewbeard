import tempfile
import subprocess as sp
import logging
import re

from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror

logger = logging.getLogger(__name__)


def is_pdf(bot, message):
    try:
        return re.match(r".*\.pdf$", message["document"]["file_name"])
    except KeyError:
        return False


class PdfPreviewBeard(BeardChatHandler):

    __userhelp__ = """Automatically produces the first page of a pdf as an image."""

    __commands__ = [
        (is_pdf, 'send_pdf_preview', None)
    ]

    @onerror
    async def send_pdf_preview(self, msg):
        logger.info("Attempting to upload photo")
        file_id = msg["document"]["file_id"]
        logger.info("Getting file from telegram")
        await self.sender.sendChatAction('upload_photo')

        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            # pdf_tg_file.download(pdf_file.name)
            await self._bot.download_file(file_id, pdf_file.file)
            try:
                png_file_bytes = sp.check_output([
                    "/bin/pdftoppm",
                    "-singlefile",
                    "-png",
                    pdf_file.name
                ])
            except FileNotFoundError:
                await self.sender.sendMessage(
                    "pdftppm not found! Please install pdftoppm"
                    " on the host machine for this bot.")
                return

        with tempfile.NamedTemporaryFile(suffix=".png") as png_file:
            png_file.write(png_file_bytes)
            png_file.seek(0)
            sp.check_call("cp {} ~/tmp/".format(png_file.name), shell=True)
            await self.sender.sendPhoto(open(png_file.name, "rb"))
