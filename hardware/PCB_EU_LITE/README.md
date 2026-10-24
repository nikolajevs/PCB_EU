# EU-LITE — дешёвый аналог EU-0.1 из деталей со склада

**Состояние на 24.10.2026: схема и BOM готовы к проверке в KiCad; PCB нет.** Закупка по каталогу цен: **34.50 €** с НДС и доставкой (28.63 € детали + 5.87 € доставка) против 81,17 € у [EU-0.1](../PCB_EU/README.md#закупка) по строкам её BOM. Плата EU-0.1 и её файлы не менялись.

Проект по образцу [cheap-version](https://github.com/nikolajevs/ai/tree/7fa9410ddb7977c46e313506acb037693ad571e1/hardware/cheap-version) (дешёвая PCB_V1 из того же склада): всё, что есть на складе владельца ([stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv)), берётся оттуда; недостающее — из [снимка каталога цен Salvats / Electrobase от 23.10.2026](procurement_lite.json). Отличия от EU-0.1, расчёты и открытые вопросы — в [DESIGN.md](DESIGN.md).

## Что сохранено и что убрано

Сохранено: вход 24 В с защитой от переполюсовки и предохранителями, ESP32-WROOM-32E-N4 (те же GPIO), 12 В и 3,3 В, **один** LED-канал LM3429 (панель ≈1,117 А), PTC 100 Вт, помпа 24 В, два вентилятора 12 В с PWM, измерение мощности (INA238 вместо INA226), RTC MCP7940N с CR2032, microSD, SHT4x и поплавок.

Убрано по решению владельца 24.10.2026: второй LED-канал (линейки) и тахометры вентиляторов. Дополнительно, для цены: аппаратная блокировка LED по UVLO/PGOOD (LM2903 + BAT54), USBLC6 на входе поплавка, ESD-диоды вентиляторов и радиатор с изоляцией. Последствия — в [DESIGN.md](DESIGN.md#отличия-от-eu-01) и [DESIGN.md, «Открытые вопросы»](DESIGN.md#открытые-вопросы).

## Файлы

| Файл | Назначение |
|---|---|
| [DESIGN.md](DESIGN.md) | Решения, отличия от EU-0.1, расчёты, склад без запаса, открытые вопросы |
| [PCB_EU_LITE.kicad_pro](PCB_EU_LITE.kicad_pro), [PCB_EU_LITE.kicad_sch](PCB_EU_LITE.kicad_sch) и 7 листов | Схема (KiCad 10, генерируется `tools/generate.py`) |
| [BOM_allocated.csv](BOM_allocated.csv), [BOM_allocated.json](BOM_allocated.json) | Склад (`stock`, с остатком после сборки) и докупка (`buy`, с URL и датой цены) |
| [procurement_lite.json](procurement_lite.json) | Снимок каталога цен для 31 докупаемого артикула |
| [stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv) | Склад владельца (копия присланной выгрузки) |
| [design.json](design.json) | Полная спецификация выводов, цепей и компонентов |
| [review/connectivity.txt](review/connectivity.txt) | 54 проверки цепей, расчётов и закупки |
| [review/Bench_checklist.md](review/Bench_checklist.md) | Что измерить при первом включении |
| [libraries/](libraries) | Символы проекта, две посадки cheap-version (PowerDI5, DTMSS-27) и их 3D |

Остальные посадки берутся из библиотек EU-0.1 (`../PCB_EU/libraries`, см. `fp-lib-table`) и стандартных библиотек KiCad.

## Закупка


**Electrobase** — 19.21 € с НДС

| Деталь (артикул) | Шт. к покупке | Цена, € | Сумма, € | Позиции на плате |
|---|---:|---:|---:|---|
| [ABS07-32.768KHZ-7-T](https://electrobase.lv/katalogs/kvarca-generatori-tht/resonator-ceramic-32768khz-20ppm-7pf-smd-32x15x09mm) | 1 | 0.79 | 0.79 | Y301 |
| [AO3422](https://electrobase.lv/katalogs/tranzistori-ar-n-veida-kanalu-smd/transistor-n-mosfet-unipolar-55v-17a-800mw-sot23) | 5 (пачка по 5, нужно 3) | 0.26 | 1.30 | Q411 Q421 Q704 |
| [C1206C100J5GACTU](https://electrobase.lv/katalogs/kondensatori-mlcc-smd-0201/capacitor-ceramic-mlcc-10pf-50vdc-c0g-5-smd-1206) | 2 | 0.25 | 0.50 | C301 C302 |
| [ESP32-WROOM-32E-N4](https://electrobase.lv/katalogs/moduli-iot-wifi-bluetooth-lora/module-iot-bluetooth-low-energywifi-smd-0) | 1 | 7.48 | 7.48 | U202 |
| [JNRH1207-220M-A](https://electrobase.lv/katalogs/induktori-tht/inductor-wire-smd-22uh-ioper-54a-r-525o-30-isat-56a) | 1 | 0.54 | 0.54 | L101 |
| [LM3429MH/NOPB](https://electrobase.lv/katalogs/led-draiveri/ic-driver-boostbuck-boost-led-driver-htssop14-5a-372v-ch-1) | 1 | 4.86 | 4.86 | U501 |
| [MCP7940N-I/SN](https://electrobase.lv/katalogs/rtc-shemas/ic-rtc-circuit-i2c-sram-64bsram-1855vdc-so8-4085degc-tube-0) | 1 | 1.50 | 1.50 | U301 |
| [MEM2061-01-188-00-A](https://electrobase.lv/katalogs/savienojumi-kartem/connector-cards-microsd-push-push-smt-gold-flash-pin-8-0) | 1 | 1.74 | 1.74 | J301 |
| [SMBJ26A-E3/52](https://electrobase.lv/katalogs/diodes-transil-smd-vienvirziena/diode-tvs-600w-289319v-143a-unidirectional-5-smbj) | 1 | 0.50 | 0.50 | D101 |

**Salvats** — 9.42 € с НДС

| Деталь (артикул) | Шт. к покупке | Цена, € | Сумма, € | Позиции на плате |
|---|---:|---:|---:|---|
| [3403.0166.11](https://www.salvats.lv/lv/drosinataji-smd-10x3x3mm-umt-leni/1a-umt-drosinataji-leni-250vac125vdc-101x3x3mm-smd) | 1 | 0.75 | 0.75 | F105 |
| [3403.0169.11](https://www.salvats.lv/lv/drosinataji-smd-10x3x3mm-umt-leni/2a-umt-drosinataji-leni-250vac125vdc-101x3x3mm-smd) | 2 | 0.78 | 1.56 | F104 F401 |
| [3413.0224.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-63a-63v-fast) | 1 | 0.86 | 0.86 | F103 |
| [3413.0327.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-8a-63v-fast) | 1 | 0.80 | 0.80 | F102 |
| [3413.0330.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-15a-63v-fast) | 1 | 0.75 | 0.75 | F101 |
| [BAT-CR2032/P](https://www.salvats.lv/lv/litija-baterijas/cr2032-litija-baterija-30v-o20x32mm-panasonic-442g) | 1 | 0.75 | 0.75 | комплектующее (CR2032 для BT301) |
| [BC-2001](https://www.salvats.lv/lv/baterijas-turetaji-1/bateriju-turetajs-metaliska-cemme-cr2032-1-baterija) | 1 | 0.33 | 0.33 | BT301 |
| [BC847B-DIO](https://www.salvats.lv/lv/npn-tranzistori-smd/bc847b1f-smd-tranzistors-npn-50v-01a-300mhz-sot23) | 1 | 0.06 | 0.06 | Q701 |
| [BC857B](https://www.salvats.lv/lv/pnp-tranzistori-smd/bc857b3f-smd-tranzistors-pnp-50v-01a-hfe220475-035w-200mhz-sot23) | 1 | 0.08 | 0.08 | Q702 |
| [BZV55C12](https://www.salvats.lv/lv/stabilitroni-smd-bzv55/12v-stabilitrons-smd-bzv55-5-05w-minimelf) | 1 | 0.13 | 0.13 | D103 |
| [C1206C102JCGACTU](https://www.salvats.lv/lv/kondensatori-keramiskie-smd-1206-1/1nf-1206-c0g-500v-5-smd-kondensators-1206) | 1 | 0.25 | 0.25 | C506 |
| [CL31C101JBCNNNC](https://www.salvats.lv/lv/kondensatori-keramiskie-smd-1206-1/100pf-1206-npo-50j-smd-kondensators-1206) | 1 | 0.07 | 0.07 | C507 |
| [CRCW12061K20FKTABC](https://www.salvats.lv/lv/rezistori-smd-1206-025w/1k2-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R506 |
| [CRCW120682K0FKTABC](https://www.salvats.lv/lv/rezistori-smd-1206-025w/82k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R101 |
| [CS2512-0R15-1%-HP](https://www.salvats.lv/lv/rezistori-smd-2512-1w3w/0r15-2512635x32mm-2w-1-smd-55125c-rezistors-thick-film-2512) | 1 | 0.32 | 0.32 | R502 |
| [LRP2512-R040-1%](https://www.salvats.lv/lv/rezistori-smd-2512-1w3w/0r04-2512635x32mm-3w-1-smd-55170c-rezistors-thick-film-2512) | 1 | 0.38 | 0.38 | R501 |
| [SMD1206 56K 1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/56k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R507 |
| [SMD1206-10K-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/10k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R108 |
| [SMD1206-33K-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/33k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R509 |
| [SMD1206-6K2-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/6k2-1206-1-smd-rezistors-1206) | 3 | 0.03 | 0.09 | R102 R505 R508 |
| [UPW1H221MPD](https://www.salvats.lv/lv/kondensatori-elektrolitiskie-zemas-induktivitates-low-esr/22050v-105c-o10x16mm-20-kondensatori-zemas-induktivitates-011r-5000h-nichicon-ar-lokaniem-izvadiem) | 2 | 0.63 | 1.26 | C101 C102 |
| [USBLC6-2SC6](https://www.salvats.lv/lv/u/usblc6-2sc6-smd-mikroshema-esd-protection-sot23-6) | 1 | 0.67 | 0.67 | U401 |
| [ZL201-10G](https://www.salvats.lv/lv/listes-un-nuju-ligzdas/254mm-uz-pcb-10pin-stekers-1) | 1 | 0.16 | 0.16 | J201 |

Со склада идёт 105 шт. в 37 позициях (в основном пассивные, оба понижающих преобразователя, ключи, диод и дроссель LED, INA238, IRL2505, клеммы, разъёмы, кнопки). Склад без запаса: две BSC146N10LS5, INA238, IRL2505, дроссель DTMSS-27, электролиты EEVFK1J471M и EEEFT1E821AP. Полный список с остатками — [BOM_allocated.csv](BOM_allocated.csv).

Цены и наличие — из снимка каталога от 23.10.2026 (C1206C100J5GACTU — из BOM EU-0.1 от 23.10.2026, в снимке его нет); доставка 2,99 € (Electrobase) + 2,88 € (Salvats) взята из README EU-0.1 и не перепроверялась. Это не оферта и не заказ. Закупка только в магазинах разрешённого списка (решение 23.10.2026): Semikom в снимке нет, Lemona не использована. AO3422 продаётся пачками по 5: два лишних.

## Проверки

Выполнено 24.10.2026 в среде **без KiCad**:

| Проверка | Результат |
|---|---|
| `python hardware/PCB_EU_LITE/tools/generate.py` | схемы, `design.json`, BOM; 143 деталей, 5 контрольных площадок |
| `python hardware/PCB_EU_LITE/tools/verify.py` | 54 проверки: выводы и цепи каждого блока, расчёт 12 В, 3,3 В, тока LED, OVP, порога ILIM, шунта INA238, покупка и остатки склада |
| `python hardware/PCB_EU_LITE/tools/test_verify.py` | мутационный тест: 21 намеренный дефект (перепутанные выводы, неверные номиналы, превышение склада, чужой магазин) отвергнут проверкой, неизменённый проект проходит |
| `python hardware/PCB_EU_LITE/tools/check_schematics.py` | записанные листы разобраны как S-выражения: 414 выводов прослежены до меток цепей и совпадают с `design.json`; UUID уникальны |

**Не выполнено:** ERC и открытие схемы в KiCad 10.0.7, любая проверка посадок, разводка, DRC, Gerber, сборка прошивки и испытания на плате. Выводы ST1S14, ST1S10, INA238, BSC146N10LS5 и SBRT15U100SP5 не перечитаны по первичным даташитам: сеть закрыта (см. [DESIGN.md](DESIGN.md#открытые-вопросы)). Результат — спецификация, а не готовая плата.

Обновление данных каталога (нужна база `catalog.db` с тем же форматом): `python hardware/PCB_EU_LITE/tools/snapshot_prices.py CATALOG.db`, затем `generate.py` и `verify.py`. Генератор перезаписывает схемы: после ручной правки в KiCad сначала перенести её в `tools/generate.py`.
