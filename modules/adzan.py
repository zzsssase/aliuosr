"""
✘ **Bantuan Untuk Adzan**

๏ **Perintah:** `adzan` <nama kota>
◉ **Keterangan:** Dapatkan jadwal adzan.
"""
import json

import requests

from . import *


@ayra_cmd(pattern="اذان(?:\\s|$)([\\s\\S]*)")
async def cek(event):
    LOKASI = event.pattern_match.group(1)
    if not LOKASI:
        await event.eor("<i>Silahkan Masukkan Nama Kota Anda</i>")
        return True
    url = f"http://muslimsalat.com/{LOKASI}.json?key=bd099c5825cbedb9aa934e255a81a5fc"
    request = requests.get(url)
    if request.status_code != 200:
        return await eor(event, get_string("adzan1").format(LOKASI))
    result = json.loads(request.text)
    catresult = f"""
**مواقيت الصلاة كالتالي:**
**📆 تاريخ **`{result['items'][0]['date_for']}`
**📍 المدينة** `{result['query']}` | `{result['country']}`
**الفجر  : **`{result['items'][0]['shurooq']}`
**الصباح : **`{result['items'][0]['fajr']}`
**الظهر  : **`{result['items'][0]['dhuhr']}`
**العصر  : **`{result['items'][0]['asr']}`
**المغرب : **`{result['items'][0]['maghrib']}`
**العشاء : **`{result['items'][0]['isha']}`
**سورس الامبراطور 🇾🇪**
"""
    await eor(event, catresult)
