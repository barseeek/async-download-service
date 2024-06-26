# Микросервис для скачивания файлов

Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить

Для работы микросервиса нужен Python версии не ниже 3.6.

```bash
pip install -r requirements.txt
```
## Конфигурация

Проект можно настроить с помощью переменных среды или аргументов командной строки. Доступные настройки включают:

- `DELAY`: Задержка (в секундах) между отправкой частей zip-файла. По умолчанию `0`.
- `CHUNK_SIZE`: Размер каждой части zip-файла в байтах. По умолчанию `512000` (500 КБ).
- `PHOTO_DIR`: Директория, содержащая фотографии для архивации. По умолчанию `"test_photos"`.
- `LOG_LEVEL`: Уровень логгирования. По умолчанию `INFO`

Вы можете создать файл `.env` в директории проекта для установки этих переменных или экспортировать их напрямую в свою среду.


## Как запустить

### Аргументы командной строки

Скрипт поддерживает несколько аргументов командной строки для удобной конфигурации:

- `-l` или `--logging`: Включить подробное логирование.
- `-d` или `--delay`: Установить задержку ответа в секундах (переопределяет переменную среды `DELAY`).
- `-p` или `--path`: Установить путь к директории с фотографиями (переопределяет переменную среды `PHOTO_DIR`).

```bash
python server.py -l -d 0.5 -p path/to/files
```

Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Как развернуть на сервере

```bash
python server.py
```

После этого перенаправить на микросервис запросы, начинающиеся с `/archive/`. Например:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).