import argparse
import logging
import os
import signal
from subprocess import TimeoutExpired

import aiofiles
import asyncio

from asyncio import create_subprocess_exec
from aiohttp import web
from pathlib import Path

INTERVAL_SECS = os.getenv('DELAY', 0)
CHUNK_SIZE = os.getenv('CHUNK_SIZE', 500 * 1024)
PHOTOS_DIRECTORY = os.getenv('PHOTO_DIR', 'test_photos')

logger = logging.getLogger(__name__)


async def archive(request):
    cwd = Path.cwd()
    archive_hash = request.match_info.get('archive_hash', '')
    if Path(cwd / PHOTOS_DIRECTORY / archive_hash).exists():
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment;filename="archive_{archive_hash}.zip"'
        await response.prepare(request)
        files = await create_subprocess_exec("zip", "-r", "-", ".",
                                             stdout=asyncio.subprocess.PIPE, cwd=cwd / PHOTOS_DIRECTORY / archive_hash)
        try:
            while True:
                data = await files.stdout.read(CHUNK_SIZE)
                if files.stdout.at_eof():
                    logger.info("Download complete")
                    break
                await response.write(data)
                logger.info("Sending archive chunk ...")
                await asyncio.sleep(INTERVAL_SECS)
        except asyncio.CancelledError:
            logger.warning("Download cancelled")
        except ConnectionError:
            logger.warning("Connection error")
        except (BaseException, Exception):
            logger.error("Unexpected error")
        finally:
            await kill_process(files)
        return response

    else:
        logger.warning("Can't find path to archive")
        return web.HTTPNotFound(text="Архив не существует или был удален")


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def kill_process(process):
    try:
        process.kill()
        logger.info(f"Process with {process.pid} killed")
    except OSError as e:
        logger.error(f"Ошибка при завершении процесса PID {process.pid}: {e}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Aiohttp Server")
    parser.add_argument("-l", "--logging", action='store_true')
    parser.add_argument("-d", "--delay", type=float, default=INTERVAL_SECS, help="Set response delay in seconds")
    parser.add_argument("-p", "--path", type=str, default=PHOTOS_DIRECTORY, help="Set path to photos directory")
    args = parser.parse_args()
    INTERVAL_SECS = args.delay
    PHOTOS_DIRECTORY = Path(args.path)
    enable_log = args.logging
    if not enable_log:
        logging.disable(level=logging.CRITICAL)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=os.getenv('LOGLEVEL', 'INFO'))
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)

