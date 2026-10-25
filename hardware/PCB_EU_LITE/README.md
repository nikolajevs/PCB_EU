# EU-LITE — дешёвый аналог EU-0.1 из деталей со склада

**Состояние на 25.10.2026: схема и BOM проверены в KiCad (ERC 0); PCB — размещение внутри контура, разводки нет.** Установлено 130 посадок сверху и 31 снизу: батарейный держатель и 30 небольших SMD-компонентов для освобождения места на верхней стороне. Закупка — **35,53 €** с НДС и доставкой (29,66 € детали + 5,87 € доставка) против 81,17 € у [EU-0.1](../PCB_EU/README.md#закупка) по строкам её BOM. Плата EU-0.1 и её файлы не менялись.

Проект по образцу [cheap-version](https://github.com/nikolajevs/ai/tree/7fa9410ddb7977c46e313506acb037693ad571e1/hardware/cheap-version) (дешёвая PCB_V1 из того же склада): всё, что есть на складе владельца ([stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv)), берётся оттуда; недостающее — из [снимка каталога цен Salvats / Electrobase от 23.10.2026](procurement_lite.json). Отличия от EU-0.1, расчёты и открытые вопросы — в [DESIGN.md](DESIGN.md).

## Что сохранено и что убрано

Сохранено: вход 24 В с защитой от переполюсовки и предохранителями, ESP32-WROOM-32E-N4 (те же GPIO), 12 В и 3,3 В, **один** LED-канал LM3429 (панель ≈1,117 А), **RGB-светодиод статуса** (GPIO4/16/17), PTC 100 Вт, помпа 24 В, два вентилятора 12 В с PWM, измерение мощности (INA238 вместо INA226), RTC MCP7940N с CR2032, microSD, SHT4x и поплавок.

Добавлено по просьбе владельца 24.10.2026: RGB-светодиод для индикации статуса и процессов (лист «Status»).

Убрано по решению владельца 24.10.2026: второй LED-канал (линейки) и тахометры вентиляторов. Дополнительно, для цены: аппаратная блокировка LED по UVLO/PGOOD (LM2903 + BAT54), USBLC6 на входе поплавка, ESD-диоды вентиляторов и радиатор с изоляцией. Последствия — в [DESIGN.md](DESIGN.md#отличия-от-eu-01) и [DESIGN.md, «Открытые вопросы»](DESIGN.md#открытые-вопросы).

## Файлы

| Файл | Назначение |
|---|---|
| [DESIGN.md](DESIGN.md) | Решения, отличия от EU-0.1, расчёты, склад без запаса, открытые вопросы |
| [PCB_EU_LITE.kicad_pro](PCB_EU_LITE.kicad_pro), [PCB_EU_LITE.kicad_sch](PCB_EU_LITE.kicad_sch) и 8 листов | Схема (KiCad 10, генерируется `tools/generate.py`) |
| [PCB_EU_LITE.kicad_pcb](PCB_EU_LITE.kicad_pcb), [placement.json](placement.json) | Воспроизводимое размещение: 130 посадок сверху, 30 малых SMD и BT301 снизу, 4 монтажных отверстия; без дорожек, переходных и полигонов |
| [BOM_allocated.csv](BOM_allocated.csv), [BOM_allocated.json](BOM_allocated.json) | Склад (`stock`, с остатком после сборки) и докупка (`buy`, с URL и датой цены) |
| [procurement_lite.json](procurement_lite.json) | Снимок цен 32 позиций каталога и карточки OSTAPA57E2A, присланной владельцем |
| [stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv) | Склад владельца (копия присланной выгрузки) |
| [design.json](design.json) | Полная спецификация выводов, цепей и компонентов |
| [review/connectivity.txt](review/connectivity.txt) | 56 проверок цепей, расчётов и закупки |
| [review/Bench_checklist.md](review/Bench_checklist.md) | Что измерить при первом включении |
| [libraries/](libraries) | Символы проекта; собственные посадки PowerDI5, DTMSS-27 (образцы cheap-version), VSSOP-10 и SOIC-8 (для INA238 и MCP7940N) — и локальные копии всех 27 складских посадок, на которые ссылается схема; их стандартные 3D-модели используют установленную библиотеку KiCad |

`EU_Mechanical` и `EU_Parts` по-прежнему общие с EU-0.1 (`../PCB_EU/libraries`, см. `fp-lib-table`); остальные посадки — локальные копии, проект не зависит от глобальной библиотеки KiCad конкретной машины.

## Закупка

**Electrobase** — 20,06 € с НДС (0,85 € — цена из карточки, присланной владельцем 25.10.2026)

| Деталь (артикул) | Шт. к покупке | Цена, € | Сумма, € | Позиции на плате |
|---|---:|---:|---:|---|
| [ABS07-32.768KHZ-7-T](https://electrobase.lv/katalogs/kvarca-generatori-tht/resonator-ceramic-32768khz-20ppm-7pf-smd-32x15x09mm) | 1 | 0.79 | 0.79 | Y301 |
| [AO3422](https://electrobase.lv/katalogs/tranzistori-ar-n-veida-kanalu-smd/transistor-n-mosfet-unipolar-55v-17a-800mw-sot23) | 5 (пачка по 5, нужно 3) | 0.26 | 1.30 | Q411 Q421 Q704 |
| [C1206C100J5GACTU](https://electrobase.lv/katalogs/kondensatori-mlcc-smd-0201/capacitor-ceramic-mlcc-10pf-50vdc-c0g-5-smd-1206) | 2 | 0.25 | 0.50 | C301 C302 |
| [ESP32-WROOM-32E-N4](https://electrobase.lv/katalogs/moduli-iot-wifi-bluetooth-lora/module-iot-bluetooth-low-energywifi-smd-0) | 1 | 7.48 | 7.48 | U202 |
| [JNRH1207-220M-A](https://electrobase.lv/katalogs/induktori-tht/inductor-wire-smd-22uh-ioper-54a-r-525o-30-isat-56a) | 1 | 0.54 | 0.54 | L101 |
| [OSTAPA57E2A](https://electrobase.lv/katalogs/diodes-led-tht-18mm/led-rgb-5mm-140deg-front-convex-231vdc-noof-term-4-round) | 1 | 0.85 | 0.85 | D901 |
| [LM3429MH/NOPB](https://electrobase.lv/katalogs/led-draiveri/ic-driver-boostbuck-boost-led-driver-htssop14-5a-372v-ch-1) | 1 | 4.86 | 4.86 | U501 |
| [MCP7940N-I/SN](https://electrobase.lv/katalogs/rtc-shemas/ic-rtc-circuit-i2c-sram-64bsram-1855vdc-so8-4085degc-tube-0) | 1 | 1.50 | 1.50 | U301 |
| [MEM2061-01-188-00-A](https://electrobase.lv/katalogs/savienojumi-kartem/connector-cards-microsd-push-push-smt-gold-flash-pin-8-0) | 1 | 1.74 | 1.74 | J301 |
| [SMBJ26A-E3/52](https://electrobase.lv/katalogs/diodes-transil-smd-vienvirziena/diode-tvs-600w-289319v-143a-unidirectional-5-smbj) | 1 | 0.50 | 0.50 | D101 |

**Salvats** — 9,60 € с НДС

| Деталь (артикул) | Шт. к покупке | Цена, € | Сумма, € | Позиции на плате |
|---|---:|---:|---:|---|
| [3403.0166.11](https://www.salvats.lv/lv/drosinataji-smd-10x3x3mm-umt-leni/1a-umt-drosinataji-leni-250vac125vdc-101x3x3mm-smd) | 1 | 0.75 | 0.75 | F105 |
| [3403.0169.11](https://www.salvats.lv/lv/drosinataji-smd-10x3x3mm-umt-leni/2a-umt-drosinataji-leni-250vac125vdc-101x3x3mm-smd) | 2 | 0.78 | 1.56 | F104 F401 |
| [3413.0224.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-63a-63v-fast) | 1 | 0.86 | 0.86 | F103 |
| [3413.0327.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-8a-63v-fast) | 1 | 0.80 | 0.80 | F102 |
| [3413.0330.11](https://www.salvats.lv/lv/drosinataji-smd-1206-32x16x06mm/drosinatajs-smd-1206-15a-63v-fast) | 1 | 0.75 | 0.75 | F101 |
| [BAT-CR2032/P](https://www.salvats.lv/lv/litija-baterijas/cr2032-litija-baterija-30v-o20x32mm-panasonic-442g) | 1 | 0.75 | 0.75 | комплектующее (CR2032 для BT301) |
| [BC-2001](https://www.salvats.lv/lv/baterijas-turetaji-1/bateriju-turetajs-metaliska-cemme-cr2032-1-baterija) | 1 | 0.33 | 0.33 | BT301 |
| [BC847B-DIO](https://www.salvats.lv/lv/npn-tranzistori-smd/bc847b1f-smd-tranzistors-npn-50v-01a-300mhz-sot23) | 4 | 0.06 | 0.24 | Q701 Q901 Q902 Q903 |
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

Со склада идёт 114 шт. в 38 позициях (в основном пассивные, оба понижающих преобразователя, ключи, диод и дроссель LED, INA238, IRL2505, клеммы, разъёмы, кнопки). Склад без запаса: две BSC146N10LS5, INA238, IRL2505, дроссель DTMSS-27, электролиты EEVFK1J471M и EEEFT1E821AP. Полный список с остатками — [BOM_allocated.csv](BOM_allocated.csv).

Для D901 выбран OPTOSUPPLY OSTAPA57E2A. Цена 0,85 € с НДС и остаток 99 шт. взяты из карточки Electrobase, присланной владельцем 25.10.2026; наличие через корзину отдельно не проверялось. Остальные цены и остатки — снимок каталога от 23.10.2026; C1206C100J5GACTU — из BOM EU-0.1 от 23.10.2026. Доставка 2,99 € (Electrobase) + 2,88 € (Salvats) взята из README EU-0.1 и не перепроверялась. Это не оферта и не заказ. AO3422 продаётся пачками по 5: два лишних.

## Проверки

Выполнено 25.10.2026 на **KiCad 10.0.5** (целевая 10.0.7 недоступна), Python с `pcbnew` и Shapely 2:

| Проверка | Результат |
|---|---|
| `generate.py`, `verify.py` | 156 деталей + 5 контрольных площадок; 56 проверок цепей, расчётов и BOM |
| `test_verify.py` | 26 намеренных дефектов отвергнуты, исходный проект проходит; исправлен запуск теста на Windows с UTF-8 |
| `check_schematics.py` | 445 выводов прослежены по записанным листам, 0 проблем |
| KiCad ERC | **0 нарушений** |
| `check_placement.py` | **18 202 проверки**: соответствие 435 выводов netlist, зазоры сверху ≥0,15 мм и снизу ≥1 мм (≥2 мм у батареи), доступ к пайке THT с запасом 0,5 мм, контур, крепёж, антенна, UART, края и коридоры подключения |
| `test_placement.py` | Идентичная повторная генерация; 13 геометрических/электрических дефектов отвергнуты; плата с дорожкой защищена от перезаписи; исходные платы и настройки проектов не изменены |
| KiCad DRC с проверкой соответствия схеме | **0 нарушений**, **338 неподключённых элементов** (плата без разводки), **0 расхождений со схемой** |

**Размещение.** Все 161 посадочное место схемы внутри платы 100×100 мм; 130 компонентов сверху, 30 малых SMD снизу и BT301 с CR2032. Сохранены 4 отверстия и номинальный четырёхслойный стек. Сверху оставлены высокие и силовые компоненты; снизу размещены цепи RGB, подтяжки microSD/RTC, делитель вспомогательного БП и маломощное управление нагрузками. Проверены зазоры куртяров: 0,15 мм сверху, 1 мм между посадками снизу и 2 мм до батарейного держателя; THT остаётся доступен для пайки. Двумерная проверка не подтверждает ручной монтаж, высоту корпуса и нагрев.

**Разъёмы и слот (25.10.2026).** Справа сверху вниз: SHT4x J401, FAN1 J411, FAN2 J421 и LED J501. Снизу: FLOAT J403, PTC J701 и PUMP J702. Вход 24 В J101 перенесён налево. UART J201 оставлен на координатах (4; 9,75) мм с прежней ориентацией, microSD J301 — у левого края под UART, карта выходит влево. Между их куртярами около 3 мм. В `placement.json` записаны направления подключения и коридоры доступа длиной 20 мм, шириной по корпусу +0,5 мм с каждого края; они проверяются против компонентов и крепежа. Это проектный резерв, не проверка конкретного штекера, радиуса изгиба кабеля или стенки корпуса.

**J411/J421 — угловые 90°, шаг 2,54 мм.** Новая локальная посадка `LITE_Parts:KF2510_1x04_P2.54mm_RightAngle` воспроизводится `tools/generate_connectors.py`. Геометрический ориентир — [чертёж производителя LHE, A2543-WR04 / 2510-4AW, стр. 14](https://www.lhecn.com/wp-content/uploads/2019/01/a25432510.pdf): шаг 2,54 мм, ширина 10,16 мм, габариты 11,5×5,7 мм. Отверстия 1,0 мм вместо указанных в чертеже 0,9 мм, площадки 1,8 мм и запас куртяра 0,5 мм — проектные решения. 3D — условная габаритная модель. Распиновка не менялась: 1 GND, 2 +12V, 3 NC, 4 PWM. Производитель, угловое исполнение и ключ складского «KF2510 / KF2540 4P» не подтверждены физически: перед монтажом сверить с фактической деталью. Учёт склада и сумма BOM не изменены.

**D901.** Для OSTAPA57E2A сделана отдельная THT-посадка с отверстием 1,0 мм и площадкой 1,8 мм; по даташиту выводы имеют ширину 0,5 ±0,1 мм и шаг 1,25 мм. Перед установкой выводы нужно развести до шага 2,54 мм. Это проектная формовка, её нужно примерить на фактическом светодиоде до пайки. Даташит изготовителя указывает плоский торец, карточка Electrobase называет корпус выпуклым. KiCad DRC больше не находит ошибок кольца.

**Воспроизводимость.** `build_board.py` берёт из EU-0.1 только контур и монтажные отверстия; электрические посадки читает из локальных библиотек, все поля и цепи — из свежего netlist, координаты — из `placement.json`. Медь и старые подписи EU-0.1 не переносятся. Сохранение платы изолировано от настоящего `.kicad_pro`: KiCad 10.0.5 больше не затирает его чужими/пустыми настройками. Генератор схем сохраняет регистрацию всех локальных библиотек. Исправлены пути общих 3D-моделей; для U101/U201 стандартная STEP-модель с точным именем отсутствует в установленной KiCad 10.0.5, её визуализация ещё не закрыта.

Из корня репозитория (для Python использовать интерпретатор KiCad с Shapely 2):

```text
python hardware/PCB_EU_LITE/tools/generate_connectors.py
python hardware/PCB_EU_LITE/tools/generate.py
python hardware/PCB_EU_LITE/tools/generate_led.py
kicad-cli sch export netlist --format kicadxml -o NETLIST.xml hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_sch
python hardware/PCB_EU_LITE/tools/build_board.py NETLIST.xml
python hardware/PCB_EU_LITE/tools/check_placement.py NETLIST.xml
python hardware/PCB_EU_LITE/tools/test_placement.py NETLIST.xml
kicad-cli sch erc --format json -o ERC.json hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_sch
kicad-cli pcb drc --schematic-parity --format json -o DRC.json hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_pcb
```

**Далее:** проверить размещение под короткие силовые петли и Kelvin-подключение шунта, развести питание и сигналы, добавить тепловую медь, монтажную шелкографию и выполнить полный DRC. Gerber, адаптация прошивки, стендовые и тепловые испытания не выполнялись. Сохранённые файлы `review/` не являются отчётами этой проверки платы; результаты текущего этапа перечислены выше и в PR. Заказанная EU-0.1 не менялась.

Обновление данных каталога (нужна база `catalog.db` с тем же форматом): `python hardware/PCB_EU_LITE/tools/snapshot_prices.py CATALOG.db`, затем `generate.py` и `verify.py`. Генератор перезаписывает схемы: после ручной правки в KiCad сначала перенести её в `tools/generate.py`.
