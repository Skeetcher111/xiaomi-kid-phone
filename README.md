# Детский телефон Xiaomi за 10 минут

Скрипт на Python, который через adb чистит телефон Xiaomi, Redmi или POCO перед тем, как отдать его ребёнку: убирает рекламные и лишние приложения, ставит нужные из Google Play и делает скриншот экрана для проверки. Мы в MCPteam сами так готовили телефон дочке.

Что умеет:

- `list` показывает сторонние и уже отключённые приложения;
- `remove` удаляет приложение для пользователя (`pm uninstall --user 0`), а если система не даёт, отключает его;
- `restore` возвращает удалённое без компьютера с прошивкой, обычной командой;
- `play` открывает карточку приложения в Google Play и нажимает «Установить»;
- `apk` ставит файлы .apk, `shot` сохраняет скриншот.

Системные пакеты, без которых MIUI/HyperOS падает (оболочка, настройки, Play, сервисы Google, оверлеи), скрипт не трогает, даже если их передать. Каждое удаление пишется в `removed-<дата>.txt` вместе с командой возврата.

## Запуск

Нужны Python 3, adb (Android platform-tools) и включённая отладка по USB на телефоне. Для команды `play` ещё `pip install pillow`.

```
adb devices
python kid_phone.py -s <серийный_номер> list
python kid_phone.py -s <серийный_номер> remove com.miui.videoplayer com.mi.globalminusscreen
python kid_phone.py -s <серийный_номер> restore com.miui.videoplayer
python kid_phone.py -s <серийный_номер> play com.duolingo
```

Удаление `--user 0` обратимо и не требует root: приложение остаётся в прошивке и возвращается командой `restore` или сбросом настроек.

Проверить телефон на шпионские программы и трекеры можно нашей бесплатной программой MCP Guard: mcpteam.ru/mcpguard/ (исходники: github.com/Skeetcher111/mcp-guard).

## English

Small Python script that prepares a Xiaomi / Redmi / POCO phone for a child over adb: lists and removes bloatware for user 0 (falls back to disable), restores packages, installs apps from Google Play, takes screenshots. Critical MIUI/HyperOS packages are protected. No root needed, every removal is logged with a restore command.

Made by MCPteam, mcpteam.ru. MIT license.
