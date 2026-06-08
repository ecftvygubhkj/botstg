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
BOT_TOKEN = os.getenv("BOT_TOKEN")

CDN = "https://d3pnc3zdmk6lr.cloudfront.net/uploads"

DEFAULT_IMG = {
    "smokes":   "https://i.imgur.com/smoke_placeholder.jpg",
    "flashes":  "https://i.imgur.com/flash_placeholder.jpg",
    "molotovs": "https://i.imgur.com/molotov_placeholder.jpg",
}

class CFGStates(StatesGroup):
    sens = State()
    zoom_sens = State()
    fov = State()
    viewmodel = State()
    resolution = State()
    volume = State()
    binds = State()

class SearchStates(StatesGroup):
    waiting = State()

user_lang = {}
user_cfg = {}
favorites = {}
user_stats = {}  # uid -> {"views": int}
search_results = {}  # uid -> list of nade matches

# ─────────────────────────────────────────────────────────────────────────────
# РОЗКИДИ — реальні дані з csnades.app
# Структура: NADES[map][util_type] = { "Ціль": [ {name, img, url, throw, side, desc} ] }
# ─────────────────────────────────────────────────────────────────────────────
NADES = {
    'Mirage': {
        'smokes': {
            'B Site': [
                {
                    'name': 'B Site з Back Alley',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/1c1b9c3a-3f06-44be-b23f-b6e04961711a/Screenshot%202023-09-10%2014-47-15.jpg',
                    'url': 'https://csnades.app/mirage/b-site-smoke-from-back-alley',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Вирівняй горизонтально з серединою темної рамки зліва. Для B Split або eco plant.',
                },
            ],
            'Right Arch': [
                {
                    'name': 'Right Arch з Back Alley',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/86ce05f2-9311-4441-96b4-b9f5f4c619b7/Screenshot%202023-09-13%2020-14-45.jpg',
                    'url': 'https://csnades.app/mirage/right-arch-smoke-from-back-alley',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Закриває правий арч на A site. Для A execute з CT сторони.',
                },
            ],
            'Short (A)': [
                {
                    'name': 'Short з Underpass',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/5f607d86-cb64-4f30-b3bf-ad744a88553e/Screenshot%202023-12-08%2002-31-18.jpg',
                    'url': 'https://csnades.app/mirage/short-smoke-from-underpass',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Для B split — прикриває short позицію CT.',
                },
            ],
            'Connector': [
                {
                    'name': 'Connector з Top T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/55557817-78e7-40bc-9af2-bfcd8cc89541/Screenshot%202023-09-07%2000-34-47.jpg',
                    'url': 'https://csnades.app/mirage/connector-smoke-from-top-t-spawn',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Crouch & walk jumpthrow. Для rush та exec на A.',
                },
            ],
            'Stairs (A site)': [
                {
                    'name': 'Stairs з T-Roof',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/dd38d5f0-4e5b-4780-8795-045da260e699/Screenshot%202023-11-15%2010-48-24.jpg',
                    'url': 'https://csnades.app/mirage/stairs-smoke-from-t-roof',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Smoke Deep Stairs з T Roof. Для A rush, поєднуй з jungle smoke.',
                },
                {
                    'name': 'Stairs з T-Roof (альт)',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/dd38d5f0-4e5b-4780-8795-045da260e699/Screenshot%202023-11-15%2010-48-24.jpg',
                    'url': 'https://csnades.app/mirage/clmc628ge005sig7454dlrqtc',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Альтернативний варіант stairs smoke з T roof.',
                },
            ],
            'Ticket Booth': [
                {
                    'name': 'Ticket з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/406c3394-def7-4366-aae3-6fdb24a28ed1/Screenshot%202023-11-15%2013-17-21.jpg',
                    'url': 'https://csnades.app/mirage/ticket-smoke-from-t-spawn-2',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Закриває ticket booth під час A execute.',
                },
            ],
            'Jungle': [
                {
                    'name': 'Jungle з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/c88a3fb9-cb74-4921-87cd-aad25a3f1b55/Screenshot%202023-09-08%2019-59-10%20%282%29.jpg',
                    'url': 'https://csnades.app/mirage/jungle-smoke-from-t-spawn',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Для solo A execute. Прицілься в трубу на краю даху, стань впритул до стіни.',
                },
            ],
            'Window': [
                {
                    'name': 'Window з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/1a148316-3fdc-4763-94e1-dd4457cd266a/Screenshot%202024-01-31%2018-39-26.jpg',
                    'url': 'https://csnades.app/mirage/cltqi4lk70000l008vv07pyqf',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Класичний смок у вікно з T spawn.',
                },
                {
                    'name': 'Kitchen Window з Back Alley',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/dc5fd27e-0829-43d1-9a24-a555ed0d7a64/Screenshot%202023-09-10%2013-37-10.jpg',
                    'url': 'https://csnades.app/mirage/kitchen-window-smoke-from-back-alley',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Закриває kitchen window для безпечного A execute.',
                },
            ],
            'Jungle + Connector': [
                {
                    'name': 'Jungle+Connector з T-Roof',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/669dbf4b-3502-47db-ba31-1901cbdb03ea/Screenshot%202023-09-08%2020-23-22.jpg',
                    'url': 'https://csnades.app/mirage/jungle+connector-smoke-from-t-roof',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Подвійний смок — закриває jungle і connector одночасно.',
                },
            ],
        },
        'flashes': {
            'Ramp': [
                {
                    'name': 'Over Ramp Flash з Ramp',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/4572457d-136b-4b52-a2dc-da633ce75868/Screenshot%202023-09-08%2021-05-11.jpg',
                    'url': 'https://csnades.app/mirage/over-ramp-flash-from-ramp',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Сліпить CT за ramp. Виходь одразу після кидка.',
                },
            ],
            'B Site': [
                {
                    'name': 'Over Boxes Flash з Side Alley',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/dd817f38-ecd6-474d-a173-0a8f31af24c2/Screenshot%202023-09-08%2002-28-35.jpg',
                    'url': 'https://csnades.app/mirage/over-boxes-flash-from-side-alley',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Через ящики на B — сліпить CT на site.',
                },
            ],
            'Window': [
                {
                    'name': 'Window Flash з Mid Bench',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/a300db8e-5574-423d-91f2-a6d25455bb47/Screenshot%202023-09-09%2020-23-43.jpg',
                    'url': 'https://csnades.app/mirage/window-flash-from-mid-bench',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Self pop flash. Можна використовувати і для підтримки тіммейта.',
                },
            ],
            'Apps': [
                {
                    'name': 'Apps Flash з B Window',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/062903bf-573f-4560-8628-cda36c5e27e0/Screenshot%202023-11-12%2023-48-30.jpg',
                    'url': 'https://csnades.app/mirage/apps-flash-from-b-window',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'Support flash для тіммейта що бере apps.',
                },
            ],
            'Connector': [
                {
                    'name': 'Connector Flash з Top Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/052b0de0-c2b3-4876-9b6d-da7bf28ca975/Screenshot%202023-09-08%2012-27-17.jpg',
                    'url': 'https://csnades.app/mirage/connector-flash-from-top-mid-2',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Сліпить CT в connector при пуші mid.',
                },
            ],
        },
        'molotovs': {
            'Bench (B site)': [
                {
                    'name': 'Bench Molotov з Apps',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/15fe27bd-0d57-4fe0-855d-7d2d8133b8a0/Screenshot%202023-09-10%2015-41-11.jpg',
                    'url': 'https://csnades.app/mirage/bench-molotov-from-apps',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Перекриває bench corner перед B execute.',
                },
            ],
            'Window': [
                {
                    'name': 'Window Molotov з Top Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/d885f2bf-cb61-419b-b57c-a5652d05d3a0/Screenshot%202023-09-11%2000-44-46.jpg',
                    'url': 'https://csnades.app/mirage/window-molotov-from-top-mid',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Stand & run jumpthrow. Виганяє CT з вікна.',
                },
            ],
            'Ramp': [
                {
                    'name': 'Ramp Molotov з CT',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/9e3ec005-5fee-430c-86db-43b719c4f546/Screenshot%202023-09-10%2023-53-36.jpg',
                    'url': 'https://csnades.app/mirage/ramp-molotov-from-ct',
                    'throw': 'left click',
                    'side': 'CT',
                    'desc': 'Defensive — виганяє TT з ramp під час CT retake A.',
                },
            ],
            'Ninja (B site)': [
                {
                    'name': 'Ninja Molotov з Jungle',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/d250e77a-fa34-4791-959a-7e44071eccb2/Screenshot%202023-11-12%2023-36-06.jpg',
                    'url': 'https://csnades.app/mirage/ninja-molotov-from-jungle',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'Виганяє TT з ninja spot на B site.',
                },
            ],
            'Connector': [
                {
                    'name': 'Connector Molotov з Top Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/589e18d4-b2c2-4dcc-bf6c-3773d0448b94/Screenshot%202023-09-08%2010-10-12.jpg',
                    'url': 'https://csnades.app/mirage/connector-molotov-from-top-mid',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Виганяє CT з connector позиції.',
                },
            ],
            'Firebox': [
                {
                    'name': 'Firebox Molotov з Tetris',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/f57b5945-e685-4c62-babe-a7895ef1ce53/Screenshot%202023-09-07%2002-01-26.jpg',
                    'url': 'https://csnades.app/mirage/firebox-molotov-from-tetris',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Перекриває firebox — CT не може там стояти.',
                },
            ],
        },
    },
    'Inferno': {
        'smokes': {
            'Half Wall (Banana)': [
                {
                    'name': 'Half Wall з Fountain',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/412f6ecf-23f4-4467-820d-8b5cd0ef1463/Screenshot%202023-12-08%2023-58-28.jpg',
                    'url': 'https://csnades.app/inferno/banana-smoke-from-fountain',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'Відрізає banana від car area під час CT retake або holdу.',
                },
            ],
            'Car (B site)': [
                {
                    'name': 'Car з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/c6a5d9b8-3f23-4377-8705-724a791f73d1/Screenshot%202023-11-18%2014-05-09.jpg',
                    'url': 'https://csnades.app/inferno/car-smoke-from-t-spawn',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Стандартний car smoke для B execute. Стань на T spawn і прицілься в димар.',
                },
            ],
            'Moto (A site)': [
                {
                    'name': 'Moto з 2nd Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/158b3070-5ada-4dbe-adc6-8fba8a2afc06/Screenshot%202023-11-18%2023-12-33.jpg',
                    'url': 'https://csnades.app/inferno/moto-smoke-from-2nd-mid',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Смок Moto з 2nd mid для exec на A site.',
                },
            ],
            'CT Banana': [
                {
                    'name': 'CT/Banana з Ruins',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/774352ab-407e-4f3b-8897-42dff5e334d4/Screenshot%202023-08-28%2016-12-28.jpg',
                    'url': 'https://csnades.app/inferno/b-entrance-smoke-from-ruins',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'Ретейк. Pracює на 128 та 64 tick.',
                },
            ],
        },
        'flashes': {
            'Banana': [
                {
                    'name': 'Banana Pop Flash з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/64752cb4-4226-40c9-a9c3-0b10c709a1a6/Screenshot%202023-09-12%2015-37-36.jpg',
                    'url': 'https://csnades.app/inferno/banana-flash-from-t-spawn',
                    'throw': 'right click',
                    'side': 'TT',
                    'desc': 'Кидаєш правою кнопкою над кутом — флешка вибухає перед CT на banana. Виходь одразу.',
                },
            ],
        },
        'molotovs': {
            'Pit (A site)': [
                {
                    'name': 'Pit Molotov з Apartments',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/37f8cba2-6f66-408b-885f-75686d044373/Screenshot%202023-09-16%2015-06-31.jpg',
                    'url': 'https://csnades.app/inferno/pit-molotov-from-apps',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Виганяє CT з Pit позиції під час A execute. Ключовий молоток для exec.',
                },
            ],
        },
    },
    'Dust2': {
        'smokes': {
            'Tunnels (B)': [
                {
                    'name': 'Tunnel з CT Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/389e3c2e-8bd6-4089-abff-3924d9944a1c/Screenshot%202023-10-13%2012-09-53.jpg',
                    'url': 'https://csnades.app/dust2/tunnel-smoke-from-ct-mid',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Закриває tunnel entrance для безпечного B execute.',
                },
                {
                    'name': 'Window з Outside Tunnel',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/080eafcd-e37b-455d-ae07-6c835eab9f8a/Screenshot%202023-09-30%2016-27-51.jpg',
                    'url': 'https://csnades.app/dust2/window-smoke-from-outside-tunnel',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Закриває CT window над тунелем.',
                },
                {
                    'name': 'B Door з Outside Tunnel',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/40531e52-5d55-44a3-9922-1fabb3d73f15/Screenshot%202023-10-13%2012-04-15.jpg',
                    'url': 'https://csnades.app/dust2/b-door-smoke-from-outside-tunnel',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Smoke B door для безпечного виходу з тунелю.',
                },
            ],
            'Xbox (Mid)': [
                {
                    'name': 'Xbox з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/d87fe69e-b852-4195-b69b-22af4d5ffb9a/Screenshot%202023-09-30%2015-06-25.jpg',
                    'url': 'https://csnades.app/dust2/xbox-smoke-from-t-spawn',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Закриває Xbox box — для безпечного пуша на Cat.',
                },
            ],
            'A Cross': [
                {
                    'name': 'A Cross з Long',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/b6fecf74-781e-4fd1-9254-32183ad22cdf/Screenshot%202023-09-30%2015-24-49.jpg',
                    'url': 'https://csnades.app/dust2/a-cross-smoke-from-long',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Закриває cross для безпечного виходу з Long на A site.',
                },
            ],
            'Long (A)': [
                {
                    'name': 'Long Door з Short Boost',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/cee96fbd-89b8-41ed-a713-7538429bfbbf/Screenshot%202023-09-30%2017-07-42.jpg',
                    'url': 'https://csnades.app/dust2/long-door-smoke-from-short-boost',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Smoke Long door з short boost позиції.',
                },
                {
                    'name': 'Long Corner з T-Spawn',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/7b6fca39-8d42-4805-a042-9201e8522262/Screenshot%202023-09-30%2015-10-34.jpg',
                    'url': 'https://csnades.app/dust2/long-corner-smoke-from-t-spawn',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Закриває long corner (blue) — для безпечного виходу на Long.',
                },
            ],
        },
        'flashes': {
            'B Site': [
                {
                    'name': 'B Site Flash з Upper Tunnel',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/6c4bfda3-1412-4597-8a87-bf139c3e94dc/Screenshot%202023-09-30%2018-10-53.jpg',
                    'url': 'https://csnades.app/dust2/b-site-flash-from-upper-tunnel',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Pop flash на B site — кидай перед виходом з тунелю.',
                },
            ],
            'Short (A)': [
                {
                    'name': 'Short Flash з Lower Tunnel',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/b4b543c8-4541-42e5-be79-70db14aed870/Screenshot%202023-09-30%2017-55-25.jpg',
                    'url': 'https://csnades.app/dust2/short-flash-from-lower-tunnel',
                    'throw': 'right click',
                    'side': 'TT',
                    'desc': 'Сліпить CT на short з нижнього тунелю.',
                },
            ],
            'Long (A)': [
                {
                    'name': 'Long Flash з Outside Long',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/4ce1d479-2719-4fc3-abe9-c1facd6c8313/Screenshot%202023-09-30%2017-17-28.jpg',
                    'url': 'https://csnades.app/dust2/long-flash-from-outside-long',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Сліпить CT що тримає Long при виході з T spawn.',
                },
            ],
            'CT Mid': [
                {
                    'name': 'B Site Flash з CT Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/2c41e459-582e-4f28-b651-7017a62aa34d/Screenshot%202023-10-13%2012-37-53.jpg',
                    'url': 'https://csnades.app/dust2/b-site-flash-from-ct-mid',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'CT defensive flash — сліпить TT що виходять на B.',
                },
            ],
        },
        'molotovs': {
            'Car (Long)': [
                {
                    'name': 'Car Molotov з Long',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/1ccc9d77-4b27-4477-a0ec-6f035a54d634/Screenshot%202023-10-13%2014-08-58.jpg',
                    'url': 'https://csnades.app/dust2/car-molotov-from-long',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Перекриває car corner перед A execute.',
                },
            ],
            'A Site': [
                {
                    'name': 'A Site Molotov з Short',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/32f0a149-4ba9-4233-a7a2-d36a3c6b1e97/Screenshot%202023-09-30%2016-01-37.jpg',
                    'url': 'https://csnades.app/dust2/a-site-molotov-from-short',
                    'throw': 'left jumpthrow',
                    'side': 'TT',
                    'desc': 'Перекриває default plant на A site.',
                },
            ],
            'Mid Doors': [
                {
                    'name': 'Mid Doors Molotov з Lower Tunnel',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/56e30e2f-6a81-4b4b-876c-553a0dcbbbbf/Screenshot%202023-10-13%2013-28-37.jpg',
                    'url': 'https://csnades.app/dust2/mid-doors-molotov-from-lower-tunnel',
                    'throw': 'left click',
                    'side': 'TT',
                    'desc': 'Виганяє CT з mid doors позиції.',
                },
            ],
            'B Site': [
                {
                    'name': 'B Site Molotov з CT Mid',
                    'img': 'https://d3pnc3zdmk6lr.cloudfront.net/uploads/9ee25c87-6213-47ed-a219-c1ee42d0a629/Screenshot%202023-10-13%2014-24-34.jpg',
                    'url': 'https://csnades.app/dust2/b-site-molotov-from-ct-mid',
                    'throw': 'left jumpthrow',
                    'side': 'CT',
                    'desc': 'Defensive — виганяє TT з B default під час retake.',
                },
            ],
        },
    },
}

EXTRA_MAPS_DISABLED = {
    # ══════════════════════════════════════════════════════
    # TRAIN
    # ══════════════════════════════════════════════════════
    "Train": {
        "smokes": {
            "Ivy (B site)": [
                {
                    "name": "Ivy з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/train/ivy-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває Ivy — головна позиція CT на B site. Для B execute."
                },
            ],
            "Ladder Room": [
                {
                    "name": "Ladder Room з Upper B",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/train/ladder-room-smoke",
                    "throw": "left click", "side": "TT",
                    "desc": "Відрізає Ladder Room від B site при execute."
                },
            ],
            "CT (A site)": [
                {
                    "name": "CT з T-Spawn (A exec)",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/train/ct-smoke-a-site",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Блокує CT при A execute. Поєднуй з Connector smoke."
                },
            ],
            "Connector": [
                {
                    "name": "Connector з T Mid",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/train/connector-smoke",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke на Connector — для безпечного виходу з T Mid на A."
                },
            ],
        },
        "flashes": {
            "B Site": [
                {
                    "name": "B Pop Flash з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/a300db8e-5574-423d-91f2-a6d25455bb47/Screenshot%202023-09-09%2020-23-41_small.jpg",
                    "url": "https://csnades.app/train/b-pop-flash",
                    "throw": "right click", "side": "TT",
                    "desc": "Сліпить CT на B site при вході. Кидай і одразу рухайся."
                },
            ],
            "A Site": [
                {
                    "name": "A Pop Flash з T-Ramp",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/a300db8e-5574-423d-91f2-a6d25455bb47/Screenshot%202023-09-09%2020-23-41_small.jpg",
                    "url": "https://csnades.app/train/a-pop-flash",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Вибухає над A site, сліпить CT і Pop Dog позицію."
                },
            ],
        },
        "molotovs": {
            "Ivy (B site)": [
                {
                    "name": "Ivy Molotov з Upper B",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/2d62aea5-ae78-4d8c-aaff-7b684ed6af2c/Screenshot%202023-11-14%2011-11-29_small.jpg",
                    "url": "https://csnades.app/train/ivy-molotov",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — виганяє TT з Ivy під час B retake."
                },
            ],
            "A Default": [
                {
                    "name": "A Default Molotov з CT",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/2d62aea5-ae78-4d8c-aaff-7b684ed6af2c/Screenshot%202023-11-14%2011-11-29_small.jpg",
                    "url": "https://csnades.app/train/a-default-molotov",
                    "throw": "left jumpthrow", "side": "CT",
                    "desc": "Блокує A default plant під час retake або holdу."
                },
            ],
        },
    },

    # ══════════════════════════════════════════════════════
    # OVERPASS
    # ══════════════════════════════════════════════════════
    "Overpass": {
        "smokes": {
            "Short (B site)": [
                {
                    "name": "Short з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/overpass/short-smoke-from-t-spawn",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Закриває Short — для безпечного B execute через Fountain."
                },
                {
                    "name": "Short з Fountain",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/overpass/short-smoke-from-fountain",
                    "throw": "left click", "side": "TT",
                    "desc": "Якщо вже дістався Fountain — кидаєш звідти для підтримки."
                },
            ],
            "CT (B site)": [
                {
                    "name": "CT Smoke з Fountain",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/overpass/ct-smoke-b-site",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Відрізає CT peak при B execute. Критичний смок для сайту."
                },
            ],
            "Stairs (A site)": [
                {
                    "name": "Stairs з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/overpass/stairs-smoke-a-site",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Smoke на Stairs для A execute — відрізає CT позицію зверху."
                },
            ],
            "Canal": [
                {
                    "name": "Canal Smoke з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/91f5b560-f5d4-4e7c-9ddc-af97a2798de7/Screenshot%202023-09-10%2020-03-40_small.jpg",
                    "url": "https://csnades.app/overpass/canal-smoke",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — відрізає Canal від B при CT holdі."
                },
            ],
        },
        "flashes": {
            "B Site": [
                {
                    "name": "B Pop Flash з Fountain",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/a300db8e-5574-423d-91f2-a6d25455bb47/Screenshot%202023-09-09%2020-23-41_small.jpg",
                    "url": "https://csnades.app/overpass/b-pop-flash",
                    "throw": "right click", "side": "TT",
                    "desc": "Правою кнопкою над Short — вибухає над B site при вході."
                },
            ],
            "Short": [
                {
                    "name": "Short Flash з T-Spawn",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/a300db8e-5574-423d-91f2-a6d25455bb47/Screenshot%202023-09-09%2020-23-41_small.jpg",
                    "url": "https://csnades.app/overpass/short-flash",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Сліпить CT що holdять Short під час B execute."
                },
            ],
        },
        "molotovs": {
            "B Default": [
                {
                    "name": "B Default Molotov з Canal",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/2d62aea5-ae78-4d8c-aaff-7b684ed6af2c/Screenshot%202023-11-14%2011-11-29_small.jpg",
                    "url": "https://csnades.app/overpass/b-default-molotov",
                    "throw": "left click", "side": "CT",
                    "desc": "Defensive — не дає TT плантувати в B default."
                },
            ],
            "Short (B)": [
                {
                    "name": "Short Molotov з Fountain",
                    "img": "https://d3pnc3zdmk6lr.cloudfront.net/uploads/2d62aea5-ae78-4d8c-aaff-7b684ed6af2c/Screenshot%202023-11-14%2011-11-29_small.jpg",
                    "url": "https://csnades.app/overpass/short-molotov",
                    "throw": "left jumpthrow", "side": "TT",
                    "desc": "Виганяє CT з Short під час B execute."
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
        "welcome": "🎮 Привіт, <b>{name}</b>!\nCS2 Helper v4.0 — розкиди, CFG, обране.\nВибери розділ 👇",
        "btn_lineups": "🗺 Розкид", "btn_cfg": "🎮 Мій CFG", "btn_settings": "⚙️ Налаштування",
        "btn_favorites": "⭐ Обране", "btn_search": "🔎 Пошук", "btn_buy": "💰 Закуп",
        "choose_map": "🗺 Вибери карту:", "choose_util": "Вибери тип для <b>{map}</b>:",
        "choose_target": "Куди летить граната на <b>{map}</b> ({util})?",
        "no_nades": "😔 Поки немає розкидів. Незабаром!",
        "nade_caption": "🎯 <b>{name}</b>\n🗺 {map} — {util}\n\n⚙️ Кидок: <b>{throw}</b>\n👤 Сторона: <b>{side}</b>\n\n💬 {desc}\n\n🔗 <a href='{url}'>csnades.app</a>",
        "cfg_empty": "😔 Немає CFG.\nНатисни ✏️ щоб заповнити.", "cfg_title": "🎮 <b>Твій CFG:</b>\n\n",
        "btn_fill_cfg": "✏️ Заповнити", "btn_edit_cfg": "✏️ Редагувати", "btn_clear_cfg": "🗑 Очистити",
        "btn_export_cfg": "📁 Скачати .cfg",
        "cfg_cleared": "✅ CFG очищено.", "fill_start": "Заповнюємо CFG!\n\nПропустити поле — напиши <code>-</code>",
        "cfg_saved": "✅ CFG збережено!", "settings_title": "⚙️ <b>Налаштування</b>",
        "btn_lang": "🌐 Мова: UA", "btn_about": "ℹ️ Про бота", "choose_lang": "Вибери мову:",
        "lang_changed": "✅ Мову змінено",
        "about": "🎮 <b>CS2 Helper Bot v4.0</b>\n\n• 🗺 Розкиди для 9 карт (смоки, флешки, молоки)\n• ⭐ Обране — збережені розкиди\n• 🔎 Пошук по назві позиції\n• 📁 Генератор CFG файлу\n• 💰 Калькулятор закупу\n• 🌐 UA/EN\n\nДані: csnades.app ❤️",
        "btn_back": "◀️ Назад",
        "fav_empty": "⭐ Ти ще не додав жодного розкиду в обране.\n\nЗнайди розкид і натисни <b>⭐ В обране</b>.",
        "fav_title": "⭐ <b>Твоє обране ({count}):</b>\n\n",
        "fav_item": "{i}. {name}\n   🗺 {map} · {util} · {target}\n",
        "search_prompt": "🔎 Введи назву позиції або локації для пошуку:\n\nПриклади: <code>window</code>, <code>connector</code>, <code>banana</code>, <code>b site</code>",
        "search_no_results": "😔 Нічого не знайдено за запитом <b>{query}</b>.\n\nСпробуй: <code>window</code>, <code>short</code>, <code>ct</code>",
        "search_results": "🔎 Результати за <b>{query}</b> ({count}):\n\nВибери розкид:",
        "stats_title": "📊 <b>Твоя статистика:</b>\n\n👁 Переглянуто розкидів: <b>{views}</b>\n⭐ В обраному: <b>{favs}</b>\n🗺 Карт досліджено: <b>{maps}</b>",
    },
    "en": {
        "welcome": "🎮 Hello, <b>{name}</b>!\nCS2 Helper v4.0 — lineups, CFG, favorites.\nChoose a section 👇",
        "btn_lineups": "🗺 Lineups", "btn_cfg": "🎮 My CFG", "btn_settings": "⚙️ Settings",
        "btn_favorites": "⭐ Favorites", "btn_search": "🔎 Search", "btn_buy": "💰 Buy",
        "choose_map": "🗺 Choose map:", "choose_util": "Choose type for <b>{map}</b>:",
        "choose_target": "Where does the nade land on <b>{map}</b> ({util})?",
        "no_nades": "😔 No lineups yet. Coming soon!",
        "nade_caption": "🎯 <b>{name}</b>\n🗺 {map} — {util}\n\n⚙️ Throw: <b>{throw}</b>\n👤 Side: <b>{side}</b>\n\n💬 {desc}\n\n🔗 <a href='{url}'>csnades.app</a>",
        "cfg_empty": "😔 No CFG saved.\nPress ✏️ to fill it.", "cfg_title": "🎮 <b>Your CFG:</b>\n\n",
        "btn_fill_cfg": "✏️ Fill", "btn_edit_cfg": "✏️ Edit", "btn_clear_cfg": "🗑 Clear",
        "btn_export_cfg": "📁 Download .cfg",
        "cfg_cleared": "✅ CFG cleared.", "fill_start": "Let's fill your CFG!\n\nSkip a field — type <code>-</code>",
        "cfg_saved": "✅ CFG saved!", "settings_title": "⚙️ <b>Settings</b>",
        "btn_lang": "🌐 Language: EN", "btn_about": "ℹ️ About", "choose_lang": "Choose language:",
        "lang_changed": "✅ Language changed",
        "about": "🎮 <b>CS2 Helper Bot v4.0</b>\n\n• 🗺 Lineups for 9 maps (smokes, flashes, molotovs)\n• ⭐ Favorites — saved lineups\n• 🔎 Search by position name\n• 📁 CFG file generator\n• 💰 Buy calculator\n• 🌐 UA/EN\n\nData: csnades.app ❤️",
        "btn_back": "◀️ Back",
        "fav_empty": "⭐ You haven't saved any lineups yet.\n\nFind a lineup and tap <b>⭐ Favorite</b>.",
        "fav_title": "⭐ <b>Your favorites ({count}):</b>\n\n",
        "fav_item": "{i}. {name}\n   🗺 {map} · {util} · {target}\n",
        "search_prompt": "🔎 Enter a position or location to search:\n\nExamples: <code>window</code>, <code>connector</code>, <code>banana</code>, <code>b site</code>",
        "search_no_results": "😔 Nothing found for <b>{query}</b>.\n\nTry: <code>window</code>, <code>short</code>, <code>ct</code>",
        "search_results": "🔎 Results for <b>{query}</b> ({count}):\n\nChoose a lineup:",
        "stats_title": "📊 <b>Your stats:</b>\n\n👁 Lineups viewed: <b>{views}</b>\n⭐ In favorites: <b>{favs}</b>\n🗺 Maps explored: <b>{maps}</b>",
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
            KeyboardButton(text=t(uid, "btn_favorites")),
        ],
        [
            KeyboardButton(text=t(uid, "btn_search")),
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
            [InlineKeyboardButton(text=t(uid, "btn_export_cfg"), callback_data="export_cfg")],
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

    # Трекінг статистики
    if uid not in user_stats:
        user_stats[uid] = {"views": 0, "maps": set()}
    user_stats[uid]["views"] += 1
    user_stats[uid]["maps"].add(map_name)

    caption = t(uid, "nade_caption",
                name=nade["name"], map=map_name, util=util_label,
                throw=nade["throw"], side=nade["side"],
                desc=nade["desc"], url=nade["url"])
    kb = nade_nav_kb(uid, map_name, util_key, enc_target, page, len(nades))

    # Кнопка відео/посилання
    kb.inline_keyboard.insert(0, [
        InlineKeyboardButton(text="📹 Відкрити на csnades.app", url=nade["url"])
    ])

    # Кнопка обраного
    fav_key = f"{map_name}_{util_key}_{enc_target}_{page}"
    user_favs = favorites.get(uid, [])
    already_fav = any(
        f"{f['map']}_{f['util']}_{f['enc_target']}_{f['page']}" == fav_key
        for f in user_favs
    )
    fav_btn_text = "✅ В обраному" if already_fav else "⭐ В обране"
    kb.inline_keyboard.insert(1, [
        InlineKeyboardButton(
            text=fav_btn_text,
            callback_data=f"fav_{map_name}_{util_key}_{enc_target}_{page}"
        )
    ])

    chat_id = cb.message.chat.id
    try:
        await cb.message.delete()
    except Exception:
        pass

    img = nade.get("img") or DEFAULT_IMG.get(util_key)
    if img:
        try:
            await bot.send_photo(chat_id, photo=img, caption=caption, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await bot.send_message(chat_id, caption + "\n\n⚠️ Фото недоступне", reply_markup=kb, parse_mode="HTML")
    else:
        await bot.send_message(chat_id, caption, reply_markup=kb, parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data.startswith("fav_"))
async def add_favorite(cb: CallbackQuery):
    uid = cb.from_user.id
    parts = cb.data.split("_", 4)
    map_name = parts[1]
    util_key = parts[2]
    enc_target = parts[3]
    page = int(parts[4])
    target = decode_target(enc_target)

    if uid not in favorites:
        favorites[uid] = []

    fav_key = f"{map_name}_{util_key}_{enc_target}_{page}"
    existing = next(
        (i for i, f in enumerate(favorites[uid])
         if f"{f['map']}_{f['util']}_{f['enc_target']}_{f['page']}" == fav_key),
        None
    )
    if existing is not None:
        favorites[uid].pop(existing)
        await cb.answer("❌ Видалено з обраного")
    else:
        nades_list = NADES.get(map_name, {}).get(util_key, {}).get(target, [])
        name = nades_list[page]["name"] if nades_list else "?"
        favorites[uid].append({
            "map": map_name, "util": util_key,
            "enc_target": enc_target, "page": page, "name": name
        })
        await cb.answer("⭐ Додано в обране")
    
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

# ── CFG Export ───────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "export_cfg")
async def export_cfg(cb: CallbackQuery):
    uid = cb.from_user.id
    cfg = user_cfg.get(uid)
    if not cfg:
        await cb.answer("Немає CFG", show_alert=True)
        return

    lines = [
        "// Generated by CS2 Helper Bot",
        "",
        f"sensitivity {cfg.get('sens', '—')}",
        f"zoom_sensitivity_ratio_mouse {cfg.get('zoom_sens', '—')}",
        f"viewmodel_fov {cfg.get('fov', '—')}",
    ]
    vm = cfg.get("viewmodel", "—")
    if vm not in ("—", "-"):
        presets = {"desktop": 1, "couch": 2, "classic": 3}
        vm_num = presets.get(vm.lower(), vm)
        lines.append(f"viewmodel_presetpos {vm_num}")

    res = cfg.get("resolution", "—")
    if "x" in res.lower():
        lines.append(f"// resolution: {res}")

    vol = cfg.get("volume", "—")
    if vol not in ("—", "-"):
        lines.append(f"volume {vol}")

    binds = cfg.get("binds", "—")
    if binds not in ("—", "-"):
        lines.append("")
        lines.append("// Binds")
        for bind in binds.split(";"):
            b = bind.strip()
            if b:
                lines.append(b)

    cfg_text = "\n".join(lines)
    from io import BytesIO
    from aiogram.types import BufferedInputFile
    buf = BytesIO(cfg_text.encode("utf-8"))
    file = BufferedInputFile(buf.read(), filename="my_cs2_config.cfg")
    await cb.message.answer_document(file, caption="🎮 Твій CS2 config файл готовий!")
    await cb.answer()


# ── Обране ───────────────────────────────────────────────────────────────────
def favorites_kb(uid):
    user_favs = favorites.get(uid, [])
    rows = []
    for i, f in enumerate(user_favs):
        target = decode_target(f["enc_target"])
        label = f"📍 {f['map']} · {target}"
        rows.append([InlineKeyboardButton(
            text=label,
            callback_data=f"tgt_{f['map']}_{f['util']}_{f['enc_target']}_{f['page']}"
        )])
        rows.append([InlineKeyboardButton(
            text="❌ Видалити",
            callback_data=f"fav_{f['map']}_{f['util']}_{f['enc_target']}_{f['page']}_del"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

@dp.message(F.text.in_(["⭐ Обране", "⭐ Favorites"]))
async def section_favorites(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    user_favs = favorites.get(uid, [])
    if not user_favs:
        await message.answer(t(uid, "fav_empty"), parse_mode="HTML")
        return
    text = t(uid, "fav_title", count=len(user_favs))
    for i, f in enumerate(user_favs, 1):
        target = decode_target(f["enc_target"])
        util_label = UTIL_UA.get(f["util"], f["util"]) if user_lang.get(uid, "uk") == "uk" else UTIL_EN.get(f["util"], f["util"])
        text += t(uid, "fav_item", i=i, name=f.get("name", "?"), map=f["map"], util=util_label, target=target)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"📍 {f['map']} · {decode_target(f['enc_target'])}",
            callback_data=f"tgt_{f['map']}_{f['util']}_{f['enc_target']}_{f['page']}"
        )] for f in user_favs
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ── Пошук ────────────────────────────────────────────────────────────────────
def do_search(query: str):
    q = query.lower().strip()
    results = []
    for map_name, utils in NADES.items():
        for util_key, targets in utils.items():
            for target, nades_list in targets.items():
                if q in target.lower() or q in map_name.lower():
                    for page, nade in enumerate(nades_list):
                        if q in target.lower() or q in nade["name"].lower() or q in map_name.lower():
                            enc = target.replace(" ", "~").replace("(", "LB").replace(")", "RB").replace("/", "SL")
                            results.append({
                                "label": f"🗺 {map_name} · {target}",
                                "cb": f"tgt_{map_name}_{util_key}_{enc}_{page}",
                                "name": nade["name"],
                            })
    return results[:20]  # максимум 20 результатів

@dp.message(F.text.in_(["🔎 Пошук", "🔎 Search"]))
async def section_search(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(t(uid, "search_prompt"), parse_mode="HTML")
    await state.set_state(SearchStates.waiting)

@dp.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    uid = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t(uid, "search_prompt"), parse_mode="HTML")
        await state.set_state(SearchStates.waiting)
        return
    query = args[1]
    await _do_search_reply(message, uid, query)

@dp.message(SearchStates.waiting)
async def search_input(message: Message, state: FSMContext):
    uid = message.from_user.id
    query = message.text.strip()
    await state.clear()
    await _do_search_reply(message, uid, query)

async def _do_search_reply(message: Message, uid: int, query: str):
    results = do_search(query)
    if not results:
        await message.answer(t(uid, "search_no_results", query=query), parse_mode="HTML")
        return
    text = t(uid, "search_results", query=query, count=len(results))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=r["label"], callback_data=r["cb"])]
        for r in results
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ── Статистика ───────────────────────────────────────────────────────────────
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    uid = message.from_user.id
    stats = user_stats.get(uid, {"views": 0, "maps": set()})
    favs_count = len(favorites.get(uid, []))
    maps_count = len(stats.get("maps", set()))
    await message.answer(
        t(uid, "stats_title", views=stats["views"], favs=favs_count, maps=maps_count),
        parse_mode="HTML"
    )


# ── Запуск ───────────────────────────────────────────────────────────────────
async def main():
    print("✅ CS2 Bot v4.0 started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
