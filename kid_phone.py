"""Настройка детского Android-телефона через adb пачкой (Xiaomi / Redmi / POCO).

  python kid_phone.py -s SERIAL list            # сторонние + отключённые
  python kid_phone.py -s SERIAL remove p1 p2 …  # uninstall --user 0, не вышло -> disable-user
  python kid_phone.py -s SERIAL restore p1 …    # install-existing + enable
  python kid_phone.py -s SERIAL play p1 …       # открыть карточку Play и нажать синюю «Установить»
  python kid_phone.py -s SERIAL apk a.apk …     # adb install
  python kid_phone.py -s SERIAL shot out.png

Журнал удалений: removed-<дата>.txt в текущей папке (там же команда возврата).
Пакеты из PROTECTED не удаляются никогда: без них на Xiaomi падают Оболочка/Xiaomi Cloud и пропадают кнопки навигации.
"""
import argparse, datetime, pathlib, subprocess, sys, time

ROOT = pathlib.Path.cwd()
LOG = ROOT / f"removed-{datetime.date.today()}.txt"
PROTECTED = {
    "com.google.android.apps.safetyhub", "com.miui.daemon", "com.miui.analytics", "com.miui.misightservice",
    "com.miui.thirdappassistant", "com.xiaomi.payment", "org.mipay.android.manager", "com.miui.bugreport",
    "com.miui.miservice", "com.xiaomi.aicr", "com.google.android.feedback", "com.android.systemui",
    "com.miui.home", "com.android.settings", "com.android.vending", "com.google.android.gms", "com.miui.securitycenter",
    "com.android.thememanager",  # без Тем ломаются обои MIUI
}


def blocked(pkg):
    return pkg in PROTECTED or "overlay" in pkg


def adb(s, *a):
    return subprocess.run(["adb", "-s", s, *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()


def sh(s, cmd):
    return adb(s, "shell", cmd)


def log(line):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def remove(s, pkgs):
    for p in pkgs:
        if blocked(p):
            print(p, "ЗАПРЕЩЁН — пропуск"); continue
        r = sh(s, f"pm uninstall --user 0 {p}")
        if "Success" not in r:
            r += "; disable: " + sh(s, f"pm disable-user --user 0 {p}")
        print(p, r); log(f"{p} {r}")
    log("вернуть: python kid_phone.py -s SERIAL restore <пакет>")


def restore(s, pkgs):
    for p in pkgs:
        print(p, sh(s, f"cmd package install-existing {p}"), sh(s, f"pm enable {p}"))


def blue_button(png):
    # ponytail: ищет самое большое синее пятно Play-кнопки, при смене дизайна Play — искать по uiautomator
    from PIL import Image
    im = Image.open(png).convert("RGB"); w, h = im.size; px = im.load()
    pts = [(x, y) for y in range(0, h, 4) for x in range(0, w, 4)
           if px[x, y][0] < 40 and 70 < px[x, y][1] < 110 and px[x, y][2] > 190]
    return (sum(p[0] for p in pts) // len(pts), sum(p[1] for p in pts) // len(pts)) if len(pts) > 200 else None


def shot(s, out):
    data = subprocess.run(["adb", "-s", s, "exec-out", "screencap", "-p"], capture_output=True).stdout
    pathlib.Path(out).write_bytes(data)


def play(s, pkgs):
    for p in pkgs:
        sh(s, f"am start -a android.intent.action.VIEW -d market://details?id={p}"); time.sleep(12)
        png = ROOT / f"play_{p}.png"; shot(s, png)
        xy = blue_button(png)
        if xy:
            sh(s, f"input tap {xy[0]} {xy[1]}")
        print(p, "нажато" if xy else "кнопки нет (уже стоит или недоступно)", xy or "")
        time.sleep(3)
    # кнопка в рекомендациях тоже синяя — после пачки сверить list с ожидаемым


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", required=True)
    ap.add_argument("cmd", choices=["list", "remove", "restore", "play", "apk", "shot"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    if a.cmd == "list":
        print("сторонние:\n" + sh(a.s, "pm list packages -3"))
        print("отключённые:\n" + sh(a.s, "pm list packages -d"))
    elif a.cmd == "remove": remove(a.s, a.args)
    elif a.cmd == "restore": restore(a.s, a.args)
    elif a.cmd == "play": play(a.s, a.args)
    elif a.cmd == "apk":
        for f in a.args: print(f, adb(a.s, "install", "-r", f))
    elif a.cmd == "shot": shot(a.s, a.args[0] if a.args else "shot.png")


if __name__ == "__main__":
    assert blocked("com.google.android.overlay.gmsconfig.personalsafety") and blocked("com.miui.daemon")
    assert not blocked("com.mi.globalminusscreen")
    main()
