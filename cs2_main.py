import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
BOT_TOKEN = ("8811872623:AAES47Shvlyo4oCVwNtPSNeH8aMg-DLujPY")

CDN = "https://d3pnc3zdmk6lr.cloudfront.net/uploads"

class CFGStates(StatesGroup):
    sens = State()
    zoom_sens = State()
    fov = State()
    viewmodel = State()
    resolution = State()
    volume = State()
    binds = State()

user_lang = {}
user_cfg = {}

# ─────────────────────────────────────────────────────────────────────────────
# РОЗКИДИ — реальні дані з csnades.app
# Структура: NADES[map][util_type] = { "Ціль": [ {name, img, url, throw, side, desc} ] }
# ─────────────────────────────────────────────────────────────────────────────
NADES = {

    # ══════════════════════════════════════════════════════
    # MIRAGE
    # ══════════════════════════════════════════════════════
    "Mirage": {
        "smokes": {
            "Window": [
                {
                    "name": "Window з Underpass",
                    "img": f"{CDN}/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40.jpg",
                    "url": "https://csnades.app/mirage/window-smoke-from-underpass",
                    "throw": "left click", "side": "TT",
                    "desc": "Класичний смок у вікно. Стань в underpass, прицілься в верхній кут арки."
                },
                {
                    "name": "Window з T-Spawn (альт)",
                    "img": f"{CDN}/85f95329-ad1f-4a95-9ed6-110d3afee119/Screenshot%202023-09-07%2000-43-00.jpg",
                    "url": "https://csnades.app/mirage/window-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Альтернатива — можна кидати одночасно з Connector smoke."
                },
            ],
            "Jungle": [
                {
                    "name": "Jungle з Top Mid",
                    "img": f"{CDN}/d84ce29c-4874-4801-9e66-89061400c8c0/Screenshot%202023-09-08%2001-17-23.jpg",
                    "url": "https://csnades.app/mirage/jungle-smoke-from-top-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Потрібно бачити коричневе вікно. Якщо граната влетить у стіну — підстроїться ліворуч."
                },
                {
                    "name": "Jungle з T-Ramp",
                    "img": f"{CDN}/d84ce29c-4874-4801-9e66-89061400c8c0/Screenshot%202023-09-08%2001-17-23.jpg",
                    "url": "https://csnades.app/mirage/jungle-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Для solo A execute. Прицілься в трубу на краю даху, стань впритул до стіни."
                },
            ],
            "Connector": [
                {
                    "name": "Connector з T-Spawn",
                    "img": f"{CDN}/85f95329-ad1f-4a95-9ed6-110d3afee119/Screenshot%202023-09-07%2000-43-00.jpg",
                    "url": "https://csnades.app/mirage/connector-smoke-from-t-spawn-3",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Crouch & walk jumpthrow. Для rush та exec на A."
                },
                {
                    "name": "Connector з Short",
                    "img": f"{CDN}/85f95329-ad1f-4a95-9ed6-110d3afee119/Screenshot%202023-09-07%2000-43-00.jpg",
                    "url": "https://csnades.app/mirage/connector-smoke-from-short",
                    "throw": "left click", "side": "CT",
                    "desc": "CT defensive. Відрізає connector під час ретейку A."
                },
            ],
            "Stairs (A site)": [
                {
                    "name": "Stairs з T-Spawn",
                    "img": f"{CDN}/9e94ed14-100d-4887-8487-a925c55e783e/Screenshot%202023-09-07%2002-08-39.jpg",
                    "url": "https://csnades.app/mirage/stairs-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke Deep Stairs з T Spawn. Для A rush, поєднуй з jungle smoke."
                },
                {
                    "name": "Stairs з Underpass",
                    "img": f"{CDN}/9e94ed14-100d-4887-8487-a925c55e783e/Screenshot%202023-09-07%2002-08-39.jpg",
                    "url": "https://csnades.app/mirage/stairs-smoke-from-underpass",
                    "throw": "left click", "side": "TT",
                    "desc": "Простіший варіант — стань в underpass, прицілься в верхній правий кут мосту."
                },
            ],
            "Short (B)": [
                {
                    "name": "Short з Back Alley",
                    "img": f"{CDN}/4dd56839-8e95-4da8-ae14-556df964be34/Screenshot%202023-09-10%2013-41-02.jpg",
                    "url": "https://csnades.app/mirage/short-smoke-from-back-alley",
                    "throw": "left click", "side": "TT",
                    "desc": "Цілься прямо в край верхньої частини вежі. Вертикальний запас великий, горизонтальний — малий."
                },
                {
                    "name": "Short з T-Mid",
                    "img": f"{CDN}/4dd56839-8e95-4da8-ae14-556df964be34/Screenshot%202023-09-10%2013-41-02.jpg",
                    "url": "https://csnades.app/mirage/short-smoke-from-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Для B split — прикриває short позицію CT."
                },
            ],
            "B Center": [
                {
                    "name": "B Center з Back Alley",
                    "img": f"{CDN}/1c1b9c3a-3f06-44be-b23f-b6e04961711a/Screenshot%202023-09-10%2014-47-15.jpg",
                    "url": "https://csnades.app/mirage/b-site-smoke-from-back-alley",
                    "throw": "left click", "side": "TT",
                    "desc": "Вирівняй горизонтально з серединою темної рамки зліва. Для B Split або eco plant."
                },
                {
                    "name": "B Center з Van",
                    "img": f"{CDN}/1c1b9c3a-3f06-44be-b23f-b6e04961711a/Screenshot%202023-09-10%2014-47-15.jpg",
                    "url": "https://csnades.app/mirage/b-center-smoke-from-van",
                    "throw": "left click", "side": "TT",
                    "desc": "Простіший прицільний орієнтир — жовта пляма на стіні ван. Stand & click."
                },
            ],
            "Firebox (CT)": [
                {
                    "name": "Firebox з Ticket",
                    "img": f"{CDN}/d1634db2-fa40-45eb-86ea-0c556323bef4/Screenshot%202023-11-14%2009-03-26.jpg",
                    "url": "https://csnades.app/mirage/firebox-smoke-from-ticket",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive smoke — закриває CT peak під час ретейку A site."
                },
            ],
            "Ticket Booth": [
                {
                    "name": "Ticket з Short",
                    "img": f"{CDN}/d1634db2-fa40-45eb-86ea-0c556323bef4/Screenshot%202023-11-14%2009-03-26.jpg",
                    "url": "https://csnades.app/mirage/ticket-booth-smoke-from-short",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Закриває ticket booth під час CT holdу. Прицілься в верхній лівий кут від'їзду."
                },
            ],
            "Van (B site)": [
                {
                    "name": "Van з T-Spawn",
                    "img": f"{CDN}/1c1b9c3a-3f06-44be-b23f-b6e04961711a/Screenshot%202023-09-10%2014-47-15.jpg",
                    "url": "https://csnades.app/mirage/van-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Smoke на Van — для B execute. Стань у T-spawn, цілься в антену."
                },
            ],
        },
        "flashes": {
            "Window": [
                {
                    "name": "Window Flash з Mid Bench",
                    "img": None,
                    "url": "https://csnades.app/mirage/window-flash-from-mid-bench",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Self pop flash. Можна використовувати і для підтримки тіммейта."
                },
                {
                    "name": "Window Pop Flash з Underpass",
                    "img": None,
                    "url": "https://csnades.app/mirage/window-pop-flash-from-underpass",
                    "throw": "left click", "side": "TT",
                    "desc": "Throw, потім одразу рухайся в window. Флешка вибухає одночасно з входом."
                },
            ],
            "Apps": [
                {
                    "name": "Apps Flash з Van",
                    "img": None,
                    "url": "https://csnades.app/mirage/apps-flash-from-van",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Support flash для тіммейта що бере apps. Crouch, aim темна точка, W 1 секунду + jumpthrow."
                },
            ],
            "Short (A)": [
                {
                    "name": "Short Pop Flash з Jungle",
                    "img": None,
                    "url": "https://csnades.app/mirage/short-pop-flash-from-jungle",
                    "throw": "right click", "side": "TT",
                    "desc": "Підкидаєш правою кнопкою — флешка вибухає перед Short, сліпить CT. Виходь одразу після кидка."
                },
            ],
            "CT / A site": [
                {
                    "name": "CT Pop Flash з Stairs",
                    "img": None,
                    "url": "https://csnades.app/mirage/ct-pop-flash-from-stairs",
                    "throw": "left click", "side": "TT",
                    "desc": "Стань на сходах, кинь HIGH — флешка вибухає над CT area. Відверни погляд після кидка."
                },
            ],
        },
        "molotovs": {
            "A Default": [
                {
                    "name": "A Default з Connector",
                    "img": None,
                    "url": "https://csnades.app/mirage/a-default-molotov-from-connector",
                    "throw": "left click", "side": "CT",
                    "desc": "Не дає TT плантувати в default. Також для ретейку A site."
                },
                {
                    "name": "A Default з Ticket",
                    "img": None,
                    "url": "https://csnades.app/mirage/a-default-molotov-from-ticket",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Кидаєш з Ticket Booth — перекриває весь default. Ідеально для retake."
                },
            ],
            "Window": [
                {
                    "name": "Window Molotov з Top Mid",
                    "img": None,
                    "url": "https://csnades.app/mirage/window-molotov-from-top-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Stand & run jumpthrow. Виганяє CT з вікна."
                },
            ],
            "B van": [
                {
                    "name": "B Van Molotov з Alley",
                    "img": None,
                    "url": "https://csnades.app/mirage/b-van-molotov-from-alley",
                    "throw": "left click", "side": "TT",
                    "desc": "Прикриває van corner перед B execute. Прицілься в кут між van і стіною."
                },
            ],
            "Jungle": [
                {
                    "name": "Jungle Molotov з Ramp",
                    "img": None,
                    "url": "https://csnades.app/mirage/jungle-molotov-from-ramp",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Defensive — виганяє TT з jungle під час CT retake A."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # INFERNO
    # ══════════════════════════════════════════════════════
    "Inferno": {
        "smokes": {
            "Balcony (Banana)": [
                {
                    "name": "Balcony з T-Spawn",
                    "img": f"{CDN}/412f6ecf-23f4-4467-820d-8b5cd0ef1463/Screenshot%202023-12-08%2023-58-26.jpg",
                    "url": "https://csnades.app/inferno/balcony-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває balcony — CT не побачить TT з banana. Один з найважливіших смоків карти."
                },
                {
                    "name": "Balcony з Top Banana",
                    "img": f"{CDN}/412f6ecf-23f4-4467-820d-8b5cd0ef1463/Screenshot%202023-12-08%2023-58-26.jpg",
                    "url": "https://csnades.app/inferno/balcony-smoke-from-top-banana",
                    "throw": "left click", "side": "TT",
                    "desc": "Кидається вже під час пушу banana — прицілься в верхній кут балкона."
                },
            ],
            "Half Wall (Banana)": [
                {
                    "name": "Half Wall з Fountain",
                    "img": f"{CDN}/412f6ecf-23f4-4467-820d-8b5cd0ef1463/Screenshot%202023-12-08%2023-58-26.jpg",
                    "url": "https://csnades.app/inferno/banana-smoke-from-fountain",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Відрізає banana від car area під час CT retake або holdу."
                },
            ],
            "Car (B site)": [
                {
                    "name": "Car з T-Spawn",
                    "img": f"{CDN}/158b3070-5ada-4dbe-adc6-8fba8a2afc06/Screenshot%202023-11-18%2023-12-32.jpg",
                    "url": "https://csnades.app/inferno/car-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Стандартний car smoke для B execute. Стань на T spawn і прицілься в димар."
                },
            ],
            "Moto (A site)": [
                {
                    "name": "Moto з 2nd Mid",
                    "img": f"{CDN}/158b3070-5ada-4dbe-adc6-8fba8a2afc06/Screenshot%202023-11-18%2023-12-32.jpg",
                    "url": "https://csnades.app/inferno/moto-smoke-from-2nd-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Смок Moto з 2nd mid для exec на A site."
                },
                {
                    "name": "Moto з Apartments",
                    "img": f"{CDN}/158b3070-5ada-4dbe-adc6-8fba8a2afc06/Screenshot%202023-11-18%2023-12-32.jpg",
                    "url": "https://csnades.app/inferno/moto-smoke-from-apartments",
                    "throw": "left click", "side": "TT",
                    "desc": "Кидаєш з апартів — для швидкого A rush через апарти."
                },
            ],
            "CT (A site)": [
                {
                    "name": "CT з 2nd Mid",
                    "img": f"{CDN}/774352ab-407e-4f3b-8897-42dff5e334d4/Screenshot%202023-08-28%2016-12-26.jpg",
                    "url": "https://csnades.app/inferno/ct-smoke-from-2nd-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Відрізає CT від A site при execute. Поєднується з Moto і Arch."
                },
            ],
            "Arch (A site)": [
                {
                    "name": "Arch з T-Spawn",
                    "img": f"{CDN}/774352ab-407e-4f3b-8897-42dff5e334d4/Screenshot%202023-08-28%2016-12-26.jpg",
                    "url": "https://csnades.app/inferno/arch-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває arch — CT не зможе пікати з Arch позиції під час A execute."
                },
            ],
            "CT Banana": [
                {
                    "name": "CT/Banana з Ruins",
                    "img": f"{CDN}/774352ab-407e-4f3b-8897-42dff5e334d4/Screenshot%202023-08-28%2016-12-26.jpg",
                    "url": "https://csnades.app/inferno/b-entrance-smoke-from-ruins",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Ретейк. Pracює на 128 та 64 tick."
                },
            ],
        },
        "flashes": {
            "Banana": [
                {
                    "name": "Banana Pop Flash з T-Spawn",
                    "img": f"{CDN}/64752cb4-4226-40c9-a9c3-0b10c709a1a6/Screenshot%202023-09-12%2015-37-32.jpg",
                    "url": "https://csnades.app/inferno/banana-flash-from-t-spawn",
                    "throw": "right click", "side": "TT",
                    "desc": "Кидаєш правою кнопкою над кутом — флешка вибухає перед CT на banana. Виходь одразу."
                },
                {
                    "name": "Banana Flash з Fountain",
                    "img": None,
                    "url": "https://csnades.app/inferno/banana-flash-from-fountain",
                    "throw": "left click", "side": "CT",
                    "desc": "Support flash з Fountain — сліпить TT що пушать banana."
                },
            ],
            "Apartments": [
                {
                    "name": "Apartments Flash з CT",
                    "img": None,
                    "url": "https://csnades.app/inferno/apartments-flash-from-ct",
                    "throw": "left click", "side": "CT",
                    "desc": "Сліпить TT що виходять з апартів на A site."
                },
            ],
            "A site": [
                {
                    "name": "A Site Pop Flash з Arch",
                    "img": None,
                    "url": "https://csnades.app/inferno/a-site-pop-flash-from-arch",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Вибухає над A site — сліпить всіх CT позиціях: Moto, CT, Pit."
                },
            ],
        },
        "molotovs": {
            "Balcony": [
                {
                    "name": "Balcony Molotov з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/inferno/balcony-molotov-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Виганяє CT з balcony перед B execute. Прицілься в правий кут балкона."
                },
            ],
            "Car (B site)": [
                {
                    "name": "Car Molotov з B entrance",
                    "img": None,
                    "url": "https://csnades.app/inferno/car-molotov-from-b-entrance",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Defensive — не дає TT плантувати біля Car. Корисно для retake."
                },
            ],
            "Pit (A site)": [
                {
                    "name": "Pit Molotov з Apartments",
                    "img": f"{CDN}/37f8cba2-6f66-408b-885f-75686d044373/Screenshot%202023-09-16%2015-06-28.jpg",
                    "url": "https://csnades.app/inferno/pit-molotov-from-apps",
                    "throw": "left click", "side": "TT",
                    "desc": "Виганяє CT з Pit позиції під час A execute. Ключовий молоток для exec."
                },
            ],
            "Banana": [
                {
                    "name": "Banana Molotov з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/inferno/banana-slow-molotov-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Сповільнює CT пуш banana на початку раунду — дає час дістатися Half Wall."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # DUST 2
    # ══════════════════════════════════════════════════════
    "Dust2": {
        "smokes": {
            "Long Corner (Blue)": [
                {
                    "name": "Long Corner з T-Spawn",
                    "img": f"{CDN}/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-23.jpg",
                    "url": "https://csnades.app/dust2/long-corner-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Стандартний Long smoke. Стань у T spawn, прицілься в ліхтар."
                },
                {
                    "name": "Long Corner з Cat",
                    "img": f"{CDN}/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-23.jpg",
                    "url": "https://csnades.app/dust2/long-corner-smoke-from-cat",
                    "throw": "left click", "side": "TT",
                    "desc": "Якщо вже дістався Cat — кидаєш з там. Прицілься в правий кут балки."
                },
            ],
            "A Cross (CT spawn)": [
                {
                    "name": "CT Cross з Long",
                    "img": f"{CDN}/c60d078b-053a-477f-9bbc-21942471b008/Screenshot%202023-10-13%2011-53-20.jpg",
                    "url": "https://csnades.app/dust2/ct-cross-smoke-from-long",
                    "throw": "left click", "side": "TT",
                    "desc": "Закриває CT cross для безпечного виходу на A site з Long. Критичний для exec."
                },
                {
                    "name": "CT Cross з Pit",
                    "img": f"{CDN}/c60d078b-053a-477f-9bbc-21942471b008/Screenshot%202023-10-13%2011-53-20.jpg",
                    "url": "https://csnades.app/dust2/ct-cross-smoke-from-pit",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Альтернатива з Pit — дає кут для плантування та holdу."
                },
            ],
            "B Door": [
                {
                    "name": "B Door з Catwalk",
                    "img": f"{CDN}/c60d078b-053a-477f-9bbc-21942471b008/Screenshot%202023-10-13%2011-53-20.jpg",
                    "url": "https://csnades.app/dust2/b-door-smoke-from-catwalk",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Stand & walk jumpthrow. Для exec або support на B site."
                },
                {
                    "name": "B Door з T-Spawn",
                    "img": f"{CDN}/c60d078b-053a-477f-9bbc-21942471b008/Screenshot%202023-10-13%2011-53-20.jpg",
                    "url": "https://csnades.app/dust2/b-door-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Можна кидати не виходячи з T spawn — ідеально для раннього B push."
                },
            ],
            "B Window": [
                {
                    "name": "B Window з T-Spawn",
                    "img": f"{CDN}/c60d078b-053a-477f-9bbc-21942471b008/Screenshot%202023-10-13%2011-53-20.jpg",
                    "url": "https://csnades.app/dust2/b-window-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває B Window (CT позиція над дверима). Для safe B execute."
                },
            ],
            "Mid Doors": [
                {
                    "name": "Mid Doors з T-Spawn",
                    "img": f"{CDN}/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-23.jpg",
                    "url": "https://csnades.app/dust2/mid-doors-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Smoke на Mid Doors для безпечного пуша Cat. Прицілься в трубу над дверима."
                },
                {
                    "name": "Mid Doors з Catwalk",
                    "img": f"{CDN}/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-23.jpg",
                    "url": "https://csnades.app/dust2/mid-doors-smoke-from-catwalk",
                    "throw": "left click", "side": "TT",
                    "desc": "Якщо вже на cat — quick smoke щоб безпечно перейти в short."
                },
            ],
            "A Short": [
                {
                    "name": "A Short з Long Doors",
                    "img": f"{CDN}/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-23.jpg",
                    "url": "https://csnades.app/dust2/a-short-smoke-from-long-doors",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває Short для безпечного A execute. Прицілься в верхній кут."
                },
            ],
        },
        "flashes": {
            "A Long": [
                {
                    "name": "Long Pop Flash з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/dust2/long-pop-flash-from-t-spawn",
                    "throw": "right click", "side": "TT",
                    "desc": "Правою кнопкою — флешка над Long кутом, сліпить CT. Виходь одразу."
                },
                {
                    "name": "Long Boost Flash з CT",
                    "img": None,
                    "url": "https://csnades.app/dust2/long-flash-from-ct",
                    "throw": "left click", "side": "CT",
                    "desc": "CT defensive flash — сліпить TT що виходять на Long."
                },
            ],
            "B Site": [
                {
                    "name": "B Site Pop Flash з Tunnels",
                    "img": None,
                    "url": "https://csnades.app/dust2/b-site-pop-flash-from-tunnels",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Кидаєш через стелю тунелю — вибухає над B site, сліпить CT."
                },
            ],
            "Mid": [
                {
                    "name": "Mid Flash з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/dust2/mid-flash-from-t-spawn",
                    "throw": "right click", "side": "TT",
                    "desc": "Сліпить CT на Mid при спробі пуша Cat."
                },
            ],
        },
        "molotovs": {
            "B Site (default)": [
                {
                    "name": "B Default Molotov з Tunnels",
                    "img": None,
                    "url": "https://csnades.app/dust2/b-default-molotov-from-tunnels",
                    "throw": "left click", "side": "TT",
                    "desc": "Перекриває default plant position — CT не може плантувати без ризику."
                },
            ],
            "B Plat": [
                {
                    "name": "B Plat Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/dust2/b-plat-molotov-from-ct",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Defensive — виганяє TT з Plat позиції під час retake B."
                },
            ],
            "A Pit": [
                {
                    "name": "A Pit Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/dust2/a-pit-molotov-from-ct",
                    "throw": "left click", "side": "CT",
                    "desc": "Виганяє TT з Pit на retake A. Прицілься в край сходів."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # NUKE
    # ══════════════════════════════════════════════════════
    "Nuke": {
        "smokes": {
            "Garage": [
                {
                    "name": "Garage з T-Spawn",
                    "img": f"{CDN}/478c81a9-2fe2-4c5a-ad4b-9e5a02e9d533/Screenshot%202023-09-20%2013-43-36.jpg",
                    "url": "https://csnades.app/nuke/garage-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Смок Garage з T-Spawn — відкриває шлях для пуша через garage."
                },
                {
                    "name": "Garage з Ramp",
                    "img": f"{CDN}/478c81a9-2fe2-4c5a-ad4b-9e5a02e9d533/Screenshot%202023-09-20%2013-43-36.jpg",
                    "url": "https://csnades.app/nuke/garage-smoke-from-ramp",
                    "throw": "left click", "side": "TT",
                    "desc": "Якщо вже на ramp — alt smoke на garage для B exec."
                },
            ],
            "Vents": [
                {
                    "name": "Vents з T-Spawn",
                    "img": f"{CDN}/477a803c-df32-4cdb-b155-39f4deaa5978/Screenshot%202023-09-20%2014-18-42.jpg",
                    "url": "https://csnades.app/nuke/vent-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Rush smoke для Vents з T-Spawn — для split B через vents і ramp."
                },
            ],
            "CT (Upper)": [
                {
                    "name": "CT Smoke з Hut",
                    "img": f"{CDN}/477a803c-df32-4cdb-b155-39f4deaa5978/Screenshot%202023-09-20%2014-18-42.jpg",
                    "url": "https://csnades.app/nuke/ct-smoke-from-hut",
                    "throw": "left click", "side": "TT",
                    "desc": "Закриває CT peak на Upper site. Прицілься в кут антени."
                },
            ],
            "Radio (A site)": [
                {
                    "name": "Radio з Outside",
                    "img": f"{CDN}/478c81a9-2fe2-4c5a-ad4b-9e5a02e9d533/Screenshot%202023-09-20%2013-43-36.jpg",
                    "url": "https://csnades.app/nuke/radio-smoke-from-outside",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke Radio — для execute на A Upper з Outside entry."
                },
            ],
            "Heaven": [
                {
                    "name": "Heaven з T-Spawn",
                    "img": f"{CDN}/477a803c-df32-4cdb-b155-39f4deaa5978/Screenshot%202023-09-20%2014-18-42.jpg",
                    "url": "https://csnades.app/nuke/heaven-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває Heaven позицію. Ключовий смок для exec на Upper A."
                },
            ],
        },
        "flashes": {
            "Hut": [
                {
                    "name": "Hut Pop Flash з Outside",
                    "img": None,
                    "url": "https://csnades.app/nuke/hut-pop-flash-from-outside",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Pop flash перед hut — вибухає одночасно з входом. Сліпить всіх всередині."
                },
            ],
            "Ramp": [
                {
                    "name": "Ramp Flash з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/nuke/ramp-flash-from-t-spawn",
                    "throw": "right click", "side": "TT",
                    "desc": "Сліпить CT що holdять ramp. Кидати під кутом правою кнопкою."
                },
            ],
        },
        "molotovs": {
            "Lower B (Default)": [
                {
                    "name": "Lower Default Molotov з Ramp",
                    "img": None,
                    "url": "https://csnades.app/nuke/lower-default-molotov-from-ramp",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive molotov — перекриває default plant на Lower B."
                },
            ],
            "Vents": [
                {
                    "name": "Vents Molotov з Upper",
                    "img": None,
                    "url": "https://csnades.app/nuke/vents-molotov-from-upper",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Виганяє TT що спускаються через vents. Кидати через люк зверху."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # ANUBIS
    # ══════════════════════════════════════════════════════
    "Anubis": {
        "smokes": {
            "Connector": [
                {
                    "name": "Connector з T-Spawn",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/connector-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Init smoke для контролю connector — для split або fake B."
                },
                {
                    "name": "Connector з Mid",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/connector-smoke-from-mid",
                    "throw": "left click", "side": "TT",
                    "desc": "Якщо вже взяв mid control — швидкий smoke на connector."
                },
            ],
            "CT (B site)": [
                {
                    "name": "CT з B entrance",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/ct-smoke-from-b-entrance",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke CT на B site — для execute або default plant."
                },
            ],
            "Palace (A site)": [
                {
                    "name": "Palace CT з Mid",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/palace-ct-smoke-from-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває CT peak на A site — для A execute через апарти/mid."
                },
            ],
            "Column (A site)": [
                {
                    "name": "Column з T-Spawn",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/column-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Smoke на колону — ключовий для А execute через воду."
                },
            ],
            "Water (Bridge)": [
                {
                    "name": "Bridge з T-Spawn",
                    "img": f"{CDN}/998732b4-c384-4679-ba70-ae4277b34d9d/Screenshot%202023-11-04%2014-40-10.jpg",
                    "url": "https://csnades.app/anubis/bridge-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Відрізає CT від мосту під час водного переходу — перша гранатa раунду."
                },
            ],
        },
        "flashes": {
            "A site": [
                {
                    "name": "A Site Pop Flash з Water",
                    "img": None,
                    "url": "https://csnades.app/anubis/a-site-pop-flash-from-water",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Pop flash через стіну — вибухає над A site, сліпить CT і AWPer."
                },
            ],
            "B site": [
                {
                    "name": "B Site Flash з Entrance",
                    "img": None,
                    "url": "https://csnades.app/anubis/b-site-flash-from-entrance",
                    "throw": "right click", "side": "TT",
                    "desc": "Сліпить CT на B site перед входом. Кидати правою кнопкою, вхід одразу після."
                },
            ],
        },
        "molotovs": {
            "B Default": [
                {
                    "name": "B Default Molotov з Entrance",
                    "img": None,
                    "url": "https://csnades.app/anubis/b-default-molotov-from-entrance",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — перекриває B default plant. Для CT retake або антиплант."
                },
            ],
            "A Default": [
                {
                    "name": "A Default Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/anubis/a-default-molotov-from-ct",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Defensive molotov — перекриває default A plant position."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # ANCIENT
    # ══════════════════════════════════════════════════════
    "Ancient": {
        "smokes": {
            "Donut (Mid)": [
                {
                    "name": "Donut з T-Spawn",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/donut-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Stand & walk jumpthrow. Init smoke для mid контролю."
                },
                {
                    "name": "Donut з CT Drop",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/donut-smoke-from-ct-drop",
                    "throw": "left click", "side": "CT",
                    "desc": "CT defensive — відрізає Donut від Mid під час retake A."
                },
            ],
            "CT (A site)": [
                {
                    "name": "CT з T-Spawn",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/ct-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває CT peak на A site — для A execute з temple."
                },
            ],
            "Pillar (A site)": [
                {
                    "name": "Pillar з Mid",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/pillar-smoke-from-mid",
                    "throw": "left click", "side": "TT",
                    "desc": "Smoke на Pillar — кут за яким ховається AWPer CT. Ключовий для exec."
                },
            ],
            "B Hall": [
                {
                    "name": "B Hall з T-Spawn",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/b-hall-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke на B Hall для безпечного пуша B через hall."
                },
            ],
            "CT Hall": [
                {
                    "name": "CT Hall з T-Spawn",
                    "img": f"{CDN}/d5dfc817-ea6d-4823-ab8e-e863d5acf28f/Screenshot%202023-10-04%2018-03-09.jpg",
                    "url": "https://csnades.app/ancient/ct-hall-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Відрізає CT hall від site — для anti-flank під час плантування."
                },
            ],
        },
        "flashes": {
            "A site": [
                {
                    "name": "A Pop Flash з Temple",
                    "img": None,
                    "url": "https://csnades.app/ancient/a-pop-flash-from-temple",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Pop flash через стелю temple — вибухає над A, сліпить CT і Pillar AWPer."
                },
            ],
            "B site": [
                {
                    "name": "B Flash з Hall",
                    "img": None,
                    "url": "https://csnades.app/ancient/b-flash-from-hall",
                    "throw": "right click", "side": "TT",
                    "desc": "Кидаєш правою кнопкою в кут — сліпить CT що holdять B entrance."
                },
            ],
            "Mid": [
                {
                    "name": "Mid Donut Flash з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/ancient/mid-flash-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Сліпить CT що контролюють Donut перед входом в mid."
                },
            ],
        },
        "molotovs": {
            "A Default": [
                {
                    "name": "A Default Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/ancient/a-default-molotov-from-ct",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — перекриває default A plant position. Ключовий для retake A."
                },
            ],
            "B Default": [
                {
                    "name": "B Default Molotov з Hall",
                    "img": None,
                    "url": "https://csnades.app/ancient/b-default-molotov-from-hall",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Defensive molotov — виганяє TT з default B plant."
                },
            ],
            "Pillar": [
                {
                    "name": "Pillar Molotov з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/ancient/pillar-molotov-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Виганяє CT з Pillar позиції — часто там стоїть AWPer."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # VERTIGO
    # ══════════════════════════════════════════════════════
    "Vertigo": {
        "smokes": {
            "A Site": [
                {
                    "name": "A Site з Ramp",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/a-site-smoke-from-ramp-3",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke для A execute. Цілься в стик між балками (shift), W трохи вперед + jumpthrow."
                },
                {
                    "name": "A Site Mid Smoke з T-Spawn",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/a-site-mid-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Альтернативний A smoke — закриває mid area сайту."
                },
            ],
            "CT (A side)": [
                {
                    "name": "CT Smoke з Mid",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/ct-smoke-from-mid",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває CT peak — для execute на A після mid контролю."
                },
            ],
            "Scaffold (B)": [
                {
                    "name": "Scaffold з T-Spawn",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/scaffold-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke на Scaffold — закриває CT peak на B site."
                },
            ],
            "Elevator (B)": [
                {
                    "name": "Elevator Smoke з T-Spawn",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/elevator-smoke-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Smoke на Elevator shaft — для execute B з правої сторони."
                },
            ],
            "Mid": [
                {
                    "name": "Mid Smoke з T-Ramp",
                    "img": f"{CDN}/1d705305-cf12-4562-baef-f1079955a15a/Screenshot%202023-12-11%2000-36-56.jpg",
                    "url": "https://csnades.app/vertigo/mid-smoke-from-t-ramp",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke на mid — для безпечного виходу і ротації між сайтами."
                },
            ],
        },
        "flashes": {
            "A Ramp": [
                {
                    "name": "A Ramp Flash з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/vertigo/a-ramp-flash-from-t-spawn",
                    "throw": "right click", "side": "TT",
                    "desc": "Pop flash перед виходом на A ramp — сліпить CT що holdять зверху."
                },
            ],
            "B Site": [
                {
                    "name": "B Pop Flash з Catwalk",
                    "img": None,
                    "url": "https://csnades.app/vertigo/b-pop-flash-from-catwalk",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Кидаєш через стелю — вибухає над B site, сліпить Scaffold і CT."
                },
            ],
        },
        "molotovs": {
            "A Default": [
                {
                    "name": "A Default Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/vertigo/a-default-molotov-from-ct",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — перекриває default A plant position."
                },
            ],
            "B Scaff": [
                {
                    "name": "Scaffold Molotov з CT",
                    "img": None,
                    "url": "https://csnades.app/vertigo/scaffold-molotov-from-ct",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Виганяє TT з Scaffold під час B retake."
                },
            ],
            "A Ramp": [
                {
                    "name": "A Ramp Molotov з T-Spawn",
                    "img": None,
                    "url": "https://csnades.app/vertigo/a-ramp-molotov-from-t-spawn",
                    "throw": "left click", "side": "TT",
                    "desc": "Slow molotov на A ramp — для anti-rush або часового виграшу."
                },
            ],
        },
    },
}

MAPS = list(NADES.keys())
UTIL_KEYS = ["smokes", "flashes", "molotovs"]
UTIL_EMOJI = {"smokes": "💨", "flashes": "⚡", "molotovs": "🔥"}
UTIL_UA = {"smokes": "Смоки", "flashes": "Флешки", "molotovs": "Молоки/Підпали"}
UTIL_EN = {"smokes": "Smokes", "flashes": "Flashes", "molotovs": "Molotovs"}

CFG_LABELS = {
    "uk": {"sens": "🖱 Сенс", "zoom_sens": "🔭 Zoom sens", "fov": "🎯 FOV",
           "viewmodel": "👁 Viewmodel", "resolution": "🖥 Роздільна здатність",
           "volume": "🔊 Гучність", "binds": "⌨️ Біндки"},
    "en": {"sens": "🖱 Sensitivity", "zoom_sens": "🔭 Zoom sens", "fov": "🎯 FOV",
           "viewmodel": "👁 Viewmodel", "resolution": "🖥 Resolution",
           "volume": "🔊 Volume", "binds": "⌨️ Binds"}
}
CFG_Q = {
    "uk": {"sens": "Введи сенс (0.85):", "zoom_sens": "Zoom sensitivity (1.0):",
           "fov": "FOV (68):", "viewmodel": "Viewmodel preset (desktop):",
           "resolution": "Роздільна здатність (1280x960):", "volume": "Гучність (0.5):",
           "binds": "Біндки (bind q lastinv; ...):"},
    "en": {"sens": "Enter sensitivity (0.85):", "zoom_sens": "Zoom sensitivity (1.0):",
           "fov": "FOV (68):", "viewmodel": "Viewmodel preset (desktop):",
           "resolution": "Resolution (1280x960):", "volume": "Volume (0.5):",
           "binds": "Binds (bind q lastinv; ...):"}
}

TEXTS = {
    "uk": {
        "welcome": "🎮 Привіт, <b>{name}</b>!\nCS2 Helper — розкиди і CFG.\nВибери розділ 👇",
        "btn_lineups": "🗺 Розкид", "btn_cfg": "🎮 Мій CFG", "btn_settings": "⚙️ Налаштування",
        "choose_map": "🗺 Вибери карту:", "choose_util": "Вибери тип для <b>{map}</b>:",
        "choose_target": "Куди летить граната на <b>{map}</b> ({util})?",
        "no_nades": "😔 Поки немає розкидів. Незабаром!",
        "nade_caption": "🎯 <b>{name}</b>\n🗺 {map} — {util}\n\n⚙️ Кидок: <b>{throw}</b>\n👤 Сторона: <b>{side}</b>\n\n💬 {desc}\n\n🔗 <a href='{url}'>csnades.app</a>",
        "cfg_empty": "😔 Немає CFG.\nНатисни ✏️ щоб заповнити.", "cfg_title": "🎮 <b>Твій CFG:</b>\n\n",
        "btn_fill_cfg": "✏️ Заповнити", "btn_edit_cfg": "✏️ Редагувати", "btn_clear_cfg": "🗑 Очистити",
        "cfg_cleared": "✅ CFG очищено.", "fill_start": "Заповнюємо CFG!\n\nПропустити поле — напиши <code>-</code>",
        "cfg_saved": "✅ CFG збережено!", "settings_title": "⚙️ <b>Налаштування</b>",
        "btn_lang": "🌐 Мова: UA", "btn_about": "ℹ️ Про бота", "choose_lang": "Вибери мову:",
        "lang_changed": "✅ Мову змінено",
        "about": "🎮 <b>CS2 Helper Bot</b>\n\nВерсія: 3.0\n• 🗺 Розкиди для 7 карт (смоки, флешки, молоки)\n• 📍 Меню позицій куди летить граната\n• ⬅️➡️ Навігація між варіантами\n• 🎮 CFG зберігання\n• 🌐 UA/EN\n\nДані: csnades.app ❤️",
        "btn_back": "◀️ Назад",
        "btn_buy": "💰 Закуп",
    },
    "en": {
        "welcome": "🎮 Hello, <b>{name}</b>!\nCS2 Helper — lineups and CFG.\nChoose a section 👇",
        "btn_lineups": "🗺 Lineups", "btn_cfg": "🎮 My CFG", "btn_settings": "⚙️ Settings",
        "choose_map": "🗺 Choose map:", "choose_util": "Choose type for <b>{map}</b>:",
        "choose_target": "Where does the nade land on <b>{map}</b> ({util})?",
        "no_nades": "😔 No lineups yet. Coming soon!",
        "nade_caption": "🎯 <b>{name}</b>\n🗺 {map} — {util}\n\n⚙️ Throw: <b>{throw}</b>\n👤 Side: <b>{side}</b>\n\n💬 {desc}\n\n🔗 <a href='{url}'>csnades.app</a>",
        "cfg_empty": "😔 No CFG saved.\nPress ✏️ to fill it.", "cfg_title": "🎮 <b>Your CFG:</b>\n\n",
        "btn_fill_cfg": "✏️ Fill", "btn_edit_cfg": "✏️ Edit", "btn_clear_cfg": "🗑 Clear",
        "cfg_cleared": "✅ CFG cleared.", "fill_start": "Let's fill your CFG!\n\nSkip a field — type <code>-</code>",
        "cfg_saved": "✅ CFG saved!", "settings_title": "⚙️ <b>Settings</b>",
        "btn_lang": "🌐 Language: EN", "btn_about": "ℹ️ About", "choose_lang": "Choose language:",
        "lang_changed": "✅ Language changed",
        "about": "🎮 <b>CS2 Helper Bot</b>\n\nVersion: 3.0\n• 🗺 Lineups for 7 maps (smokes, flashes, molotovs)\n• 📍 Target position menu\n• ⬅️➡️ Variant navigation\n• 🎮 CFG storage\n• 🌐 UA/EN\n\nData: csnades.app ❤️",
        "btn_back": "◀️ Back",
        "btn_buy": "💰 Buy",
    }
}

def t(uid, key, **kw):
    lang = user_lang.get(uid, "uk")
    text = TEXTS[lang].get(key, key)
    return text.format(**kw) if kw else text

def main_kb(uid):
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=t(uid, "btn_lineups")),
            KeyboardButton(text=t(uid, "btn_cfg")),
        ],
        [
            KeyboardButton(text=t(uid, "btn_buy")),
            KeyboardButton(text=t(uid, "btn_settings")),
        ],
    ], resize_keyboard=True, is_persistent=True)

def maps_kb():
    rows = []
    for i in range(0, len(MAPS), 3):
        rows.append([InlineKeyboardButton(text=m, callback_data=f"map_{m}") for m in MAPS[i:i+3]])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def util_kb(uid, map_name):
    lang = user_lang.get(uid, "uk")
    labels = UTIL_UA if lang == "uk" else UTIL_EN
    rows = []
    for k in UTIL_KEYS:
        targets = NADES.get(map_name, {}).get(k, {})
        count = sum(len(v) for v in targets.values())
        label = f"{UTIL_EMOJI[k]} {labels[k]} ({count})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"util_{map_name}_{k}")])
    rows.append([InlineKeyboardButton(text=t(uid, "btn_back"), callback_data="back_maps")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def targets_kb(uid, map_name, util_key):
    targets = NADES.get(map_name, {}).get(util_key, {})
    rows = []
    for target in targets:
        count = len(targets[target])
        label = f"📍 {target} ({count})"
        enc = target.replace(" ", "~").replace("(", "LB").replace(")", "RB").replace("/", "SL")
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tgt_{map_name}_{util_key}_{enc}_0")])
    rows.append([InlineKeyboardButton(text=t(uid, "btn_back"), callback_data=f"util_{map_name}_{util_key}_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def nade_nav_kb(uid, map_name, util_key, enc_target, page, total):
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"tgt_{map_name}_{util_key}_{enc_target}_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total}", callback_data="noop"))
    if page < total - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"tgt_{map_name}_{util_key}_{enc_target}_{page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[
        nav,
        [InlineKeyboardButton(text=t(uid, "btn_back"), callback_data=f"util_{map_name}_{util_key}")],
    ])

def cfg_kb(uid, has_cfg):
    if has_cfg:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(uid, "btn_edit_cfg"), callback_data="fill_cfg")],
            [InlineKeyboardButton(text=t(uid, "btn_clear_cfg"), callback_data="clear_cfg")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(uid, "btn_fill_cfg"), callback_data="fill_cfg")],
    ])

def settings_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(uid, "btn_lang"), callback_data="change_lang")],
        [InlineKeyboardButton(text=t(uid, "btn_about"), callback_data="about")],
    ])

def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])

def decode_target(enc):
    return enc.replace("~", " ").replace("LB", "(").replace("RB", ")").replace("SL", "/")

# ─── Бот ─────────────────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    name = message.from_user.first_name or "Друже"
    await message.answer(t(uid, "welcome", name=name), reply_markup=main_kb(uid), parse_mode="HTML")

# ── Розкид ───────────────────────────────────────────────────────────────────
@dp.message(F.text.in_(["🗺 Розкид", "🗺 Lineups"]))
async def section_lineups(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(t(uid, "choose_map"), reply_markup=maps_kb())

@dp.callback_query(F.data.startswith("map_"))
async def choose_map(cb: CallbackQuery):
    uid = cb.from_user.id
    chat_id = cb.message.chat.id
    map_name = cb.data[4:]
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(chat_id, t(uid, "choose_util", map=map_name),
                           reply_markup=util_kb(uid, map_name), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "back_maps")
async def back_maps(cb: CallbackQuery):
    uid = cb.from_user.id
    chat_id = cb.message.chat.id
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(chat_id, t(uid, "choose_map"), reply_markup=maps_kb())
    await cb.answer()

@dp.callback_query(F.data.startswith("util_"))
async def show_util(cb: CallbackQuery):
    uid = cb.from_user.id
    chat_id = cb.message.chat.id
    parts = cb.data.split("_", 2)
    map_name = parts[1]
    rest = parts[2]
    if rest.endswith("_back"):
        util_key = rest[:-5]
    else:
        util_key = rest

    lang = user_lang.get(uid, "uk")
    labels = UTIL_UA if lang == "uk" else UTIL_EN
    targets = NADES.get(map_name, {}).get(util_key, {})

    # Якщо це кнопка "Назад" з меню позицій — показуємо вибір типу гранати
    if rest.endswith("_back"):
        try:
            await cb.message.delete()
        except Exception:
            pass
        await bot.send_message(chat_id, t(uid, "choose_util", map=map_name),
                               reply_markup=util_kb(uid, map_name), parse_mode="HTML")
        await cb.answer()
        return

    util_label = f"{UTIL_EMOJI[util_key]} {labels[util_key]}"

    if not targets:
        try:
            await cb.message.delete()
        except Exception:
            pass
        await bot.send_message(chat_id, t(uid, "no_nades"), reply_markup=util_kb(uid, map_name))
        await cb.answer()
        return

    text = t(uid, "choose_target", map=map_name, util=util_label)
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(chat_id, text, reply_markup=targets_kb(uid, map_name, util_key), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data.startswith("tgt_"))
async def show_nade_for_target(cb: CallbackQuery):
    uid = cb.from_user.id
    # tgt_{map}_{util}_{enc_target}_{page}
    parts = cb.data.split("_", 4)
    map_name = parts[1]
    util_key = parts[2]
    enc_target = parts[3]
    page = int(parts[4])
    target = decode_target(enc_target)

    lang = user_lang.get(uid, "uk")
    labels = UTIL_UA if lang == "uk" else UTIL_EN
    nades = NADES.get(map_name, {}).get(util_key, {}).get(target, [])
    if not nades:
        await cb.answer("Немає розкидів")
        return

    nade = nades[page]
    util_label = f"{UTIL_EMOJI[util_key]} {labels[util_key]}"
    caption = t(uid, "nade_caption",
                name=nade["name"], map=map_name, util=util_label,
                throw=nade["throw"], side=nade["side"],
                desc=nade["desc"], url=nade["url"])
    kb = nade_nav_kb(uid, map_name, util_key, enc_target, page, len(nades))

    chat_id = cb.message.chat.id
    try:
        await cb.message.delete()
    except Exception:
        pass

    img = nade.get("img")
    if img:
        try:
            await bot.send_photo(chat_id, photo=img, caption=caption, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await bot.send_message(chat_id, caption + "\n\n⚠️ Фото недоступне", reply_markup=kb, parse_mode="HTML")
    else:
        await bot.send_message(chat_id, caption, reply_markup=kb, parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery):
    await cb.answer()


# ══════════════════════════════════════════════════════
# ЗАКУП — логіка рекомендацій
# ══════════════════════════════════════════════════════

# BUY[side][situation][money_tier] = (title, items, tip)
# money_tier: 0=$0-1400, 1=$1400-2400, 2=$2400-3800, 3=$3800+
BUY_ADVICE = {
    "TT": {
        "pistol": {  # перший раунд
            0: ("Пістоль раунд", "Glock (дефолт) + 1-2 флешки", "Зеконом максимум — наступний раунд важливіший."),
            1: ("Пістоль раунд", "Glock (дефолт) + 1-2 флешки", "Зеконом максимум — наступний раунд важливіший."),
            2: ("Пістоль раунд", "Glock (дефолт) + 1-2 флешки", "Зеконом максимум — наступний раунд важливіший."),
            3: ("Пістоль раунд", "Glock (дефолт) + 1-2 флешки", "Зеконом максимум — наступний раунд важливіший."),
        },
        "win": {
            0: ("Eco", "Тільки пістоль (Glock)", "Зеконом — не витрачай гроші, копи на повний закуп."),
            1: ("Форс", "Mac-10 / MP9 + легка броня", "Можна форснути з SMG, але краще зекономити."),
            2: ("Напів-закуп", "AK-47 або M4 + броня без шолому", "Броня обов'язкова. Шолом якщо залишились гроші."),
            3: ("Повний закуп", "AK-47 + повна броня + граната + пістоль", "Full buy! AK + броня + шолом + смок + флешка."),
        },
        "loss": {
            0: ("Eco", "Тільки пістоль (Glock)", "Зеконом повністю. Ціль — зекономити на наступний раунд."),
            1: ("Eco / Форс", "Glock або Mac-10", "Якщо команда форсить — бери Mac-10. Якщо ні — зеконом."),
            2: ("Напів-закуп", "AK-47 + броня без шолому", "Є шанс виграти раунд. Бери AK + броню мінімум."),
            3: ("Повний закуп", "AK-47 + повна броня + утиліти", "Full buy! Не економ на гранатах."),
        },
    },
    "CT": {
        "pistol": {
            0: ("Пістоль раунд", "USP-S (дефолт) + 1-2 флешки", "Зеконом максимум."),
            1: ("Пістоль раунд", "USP-S (дефолт) + 1-2 флешки", "Зеконом максимум."),
            2: ("Пістоль раунд", "USP-S (дефолт) + 1-2 флешки", "Зеконом максимум."),
            3: ("Пістоль раунд", "USP-S (дефолт) + 1-2 флешки", "Зеконом максимум."),
        },
        "win": {
            0: ("Eco", "Тільки пістоль (USP-S)", "Зеконом — копи на повний закуп."),
            1: ("Форс", "MP5 / P250 + легка броня", "SMG + броня якщо команда форсить разом."),
            2: ("Напів-закуп", "M4A4/M4A1-S + броня без шолому", "M4 + броня обов'язково. Шолом якщо є гроші."),
            3: ("Повний закуп", "M4A4/M4A1-S + повна броня + гранати", "Full buy! M4 + броня + шолом + смок + молоток."),
        },
        "loss": {
            0: ("Eco", "Тільки пістоль (USP-S)", "Зеконом повністю."),
            1: ("Eco / Форс", "USP-S або MP5", "Якщо команда форсить — бери MP5. Якщо ні — зеконом."),
            2: ("Напів-закуп", "M4 + броня без шолому", "M4 + броня мінімум. Без гранат якщо треба."),
            3: ("Повний закуп", "M4 + повна броня + утиліти", "Full buy! Смок + молоток обов'язково."),
        },
    },
}

MONEY_TIERS = [
    ("💸 $0 — $1400", 0),
    ("💵 $1400 — $2400", 1),
    ("💶 $2400 — $3800", 2),
    ("💰 $3800+", 3),
]

SITUATION_UA = {"pistol": "🔫 Перший раунд", "win": "✅ Виграли", "loss": "❌ Програли"}
SITUATION_EN = {"pistol": "🔫 Pistol round", "win": "✅ Won", "loss": "❌ Lost"}

def buy_side_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 TT (Терористи)", callback_data="buy_side_TT")],
        [InlineKeyboardButton(text="🔵 CT (Контр-терористи)", callback_data="buy_side_CT")],
    ])

def buy_situation_kb(uid, side):
    lang = user_lang.get(uid, "uk")
    sits = SITUATION_UA if lang == "uk" else SITUATION_EN
    rows = [[InlineKeyboardButton(text=sits[s], callback_data=f"buy_sit_{side}_{s}")] for s in ["pistol", "win", "loss"]]
    rows.append([InlineKeyboardButton(text=t(uid, "btn_back"), callback_data="buy_back_side")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def buy_money_kb(uid, side, sit):
    rows = [[InlineKeyboardButton(text=label, callback_data=f"buy_money_{side}_{sit}_{tier}")] for label, tier in MONEY_TIERS]
    rows.append([InlineKeyboardButton(text=t(uid, "btn_back"), callback_data=f"buy_back_sit_{side}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Закуп хендлери ────────────────────────────────────────────────────────────
@dp.message(F.text.in_(["💰 Закуп", "💰 Buy"]))
async def section_buy(message: Message):
    uid = message.from_user.id
    lang = user_lang.get(uid, "uk")
    text = "💰 <b>Калькулятор закупу</b>\n\nВибери свою сторону:" if lang == "uk" else "💰 <b>Buy calculator</b>\n\nChoose your side:"
    await message.answer(text, reply_markup=buy_side_kb(uid), parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_side_"))
async def buy_side(cb: CallbackQuery):
    uid = cb.from_user.id
    side = cb.data.split("_")[2]
    lang = user_lang.get(uid, "uk")
    text = f"{'🟡 TT' if side == 'TT' else '🔵 CT'} — {'яка ситуація?' if lang == 'uk' else 'what is the situation?'}"
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(cb.message.chat.id, text, reply_markup=buy_situation_kb(uid, side), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "buy_back_side")
async def buy_back_side(cb: CallbackQuery):
    uid = cb.from_user.id
    lang = user_lang.get(uid, "uk")
    text = "💰 <b>Калькулятор закупу</b>\n\nВибери свою сторону:" if lang == "uk" else "💰 <b>Buy calculator</b>\n\nChoose your side:"
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(cb.message.chat.id, text, reply_markup=buy_side_kb(uid), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data.startswith("buy_back_sit_"))
async def buy_back_sit(cb: CallbackQuery):
    uid = cb.from_user.id
    side = cb.data.split("_")[3]
    lang = user_lang.get(uid, "uk")
    text = f"{'🟡 TT' if side == 'TT' else '🔵 CT'} — {'яка ситуація?' if lang == 'uk' else 'what is the situation?'}"
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(cb.message.chat.id, text, reply_markup=buy_situation_kb(uid, side), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data.startswith("buy_sit_"))
async def buy_sit(cb: CallbackQuery):
    uid = cb.from_user.id
    parts = cb.data.split("_")
    side = parts[2]
    sit = parts[3]
    lang = user_lang.get(uid, "uk")
    sits = SITUATION_UA if lang == "uk" else SITUATION_EN
    text = f"{sits[sit]} — {'скільки грошей?' if lang == 'uk' else 'how much money?'}"
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(cb.message.chat.id, text, reply_markup=buy_money_kb(uid, side, sit), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data.startswith("buy_money_"))
async def buy_money(cb: CallbackQuery):
    uid = cb.from_user.id
    parts = cb.data.split("_")
    side = parts[2]
    sit = parts[3]
    tier = int(parts[4])
    lang = user_lang.get(uid, "uk")

    advice = BUY_ADVICE[side][sit][tier]
    title, items, tip = advice

    money_label = MONEY_TIERS[tier][0]
    sits = SITUATION_UA if lang == "uk" else SITUATION_EN
    side_label = "🟡 TT" if side == "TT" else "🔵 CT"

    if lang == "uk":
        text = (
            f"💰 <b>Рекомендація закупу</b>\n\n"
            f"👤 Сторона: <b>{side_label}</b>\n"
            f"📊 Ситуація: <b>{sits[sit]}</b>\n"
            f"💵 Гроші: <b>{money_label}</b>\n\n"
            f"🛒 <b>{title}</b>\n"
            f"<code>{items}</code>\n\n"
            f"💡 {tip}"
        )
        back_text = "🔄 Ще раз"
    else:
        text = (
            f"💰 <b>Buy recommendation</b>\n\n"
            f"👤 Side: <b>{side_label}</b>\n"
            f"📊 Situation: <b>{sits[sit]}</b>\n"
            f"💵 Money: <b>{money_label}</b>\n\n"
            f"🛒 <b>{title}</b>\n"
            f"<code>{items}</code>\n\n"
            f"💡 {tip}"
        )
        back_text = "🔄 Again"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data=f"buy_sit_{side}_{sit}")],
        [InlineKeyboardButton(text=t(uid, "btn_back"), callback_data=f"buy_back_sit_{side}")],
    ])
    try:
        await cb.message.delete()
    except Exception:
        pass
    await bot.send_message(cb.message.chat.id, text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()

# ── CFG ──────────────────────────────────────────────────────────────────────
@dp.message(F.text.in_(["🎮 Мій CFG", "🎮 My CFG"]))
async def section_cfg(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    cfg = user_cfg.get(uid)
    if not cfg:
        await message.answer(t(uid, "cfg_empty"), reply_markup=cfg_kb(uid, False), parse_mode="HTML")
        return
    lang = user_lang.get(uid, "uk")
    labels = CFG_LABELS[lang]
    text = t(uid, "cfg_title")
    for field in ["sens", "zoom_sens", "fov", "viewmodel", "resolution", "volume", "binds"]:
        text += f"{labels[field]}: <code>{cfg.get(field, '—')}</code>\n"
    await message.answer(text, reply_markup=cfg_kb(uid, True), parse_mode="HTML")

@dp.callback_query(F.data == "fill_cfg")
async def fill_cfg(cb: CallbackQuery, state: FSMContext):
    uid = cb.from_user.id
    await cb.message.answer(t(uid, "fill_start"), parse_mode="HTML")
    await asyncio.sleep(0.1)
    lang = user_lang.get(uid, "uk")
    await cb.message.answer(CFG_Q[lang]["sens"])
    await state.set_state(CFGStates.sens)
    await cb.answer()

@dp.callback_query(F.data == "clear_cfg")
async def clear_cfg_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    user_cfg.pop(uid, None)
    await cb.message.answer(t(uid, "cfg_cleared"))
    await cb.answer()

async def cfg_step(message: Message, state: FSMContext, field: str, next_state, next_field: str):
    uid = message.from_user.id
    data = await state.get_data()
    val = message.text.strip()
    data[field] = "—" if val == "-" else val
    await state.set_data(data)
    if next_state:
        lang = user_lang.get(uid, "uk")
        await message.answer(CFG_Q[lang][next_field])
        await state.set_state(next_state)
    else:
        user_cfg[uid] = data
        await state.clear()
        await message.answer(t(uid, "cfg_saved"), reply_markup=main_kb(uid))

@dp.message(CFGStates.sens)
async def s1(m, state): await cfg_step(m, state, "sens", CFGStates.zoom_sens, "zoom_sens")
@dp.message(CFGStates.zoom_sens)
async def s2(m, state): await cfg_step(m, state, "zoom_sens", CFGStates.fov, "fov")
@dp.message(CFGStates.fov)
async def s3(m, state): await cfg_step(m, state, "fov", CFGStates.viewmodel, "viewmodel")
@dp.message(CFGStates.viewmodel)
async def s4(m, state): await cfg_step(m, state, "viewmodel", CFGStates.resolution, "resolution")
@dp.message(CFGStates.resolution)
async def s5(m, state): await cfg_step(m, state, "resolution", CFGStates.volume, "volume")
@dp.message(CFGStates.volume)
async def s6(m, state): await cfg_step(m, state, "volume", CFGStates.binds, "binds")
@dp.message(CFGStates.binds)
async def s7(m, state): await cfg_step(m, state, "binds", None, "")

# ── Налаштування ─────────────────────────────────────────────────────────────
@dp.message(F.text.in_(["⚙️ Налаштування", "⚙️ Settings"]))
async def section_settings(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(t(uid, "settings_title"), reply_markup=settings_kb(uid), parse_mode="HTML")

@dp.callback_query(F.data == "change_lang")
async def change_lang(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.answer(t(uid, "choose_lang"), reply_markup=lang_kb())
    await cb.answer()

@dp.callback_query(F.data.in_(["lang_uk", "lang_en"]))
async def set_lang(cb: CallbackQuery):
    uid = cb.from_user.id
    user_lang[uid] = "uk" if cb.data == "lang_uk" else "en"
    await cb.message.answer(t(uid, "lang_changed"), reply_markup=main_kb(uid))
    await cb.answer()

@dp.callback_query(F.data == "about")
async def about(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.answer(t(uid, "about"), parse_mode="HTML")
    await cb.answer()

# ── Запуск ───────────────────────────────────────────────────────────────────
async def main():
    print("✅ CS2 Bot v3.0 started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())