# EU-LITE — дешёвый аналог EU-0.1 из деталей со склада

**Состояние на 25.10.2026: плата электрически разведена, KiCad ERC и DRC чистые; это ещё не выпуск для производства.** После заливки и проверки паритета DRC показывает **0 ошибок, 0 неподключённых цепей и 0 расхождений со схемой**. Усилен LED_IS Q501–R501 до 0,8 мм; добавлены заливки +24V_FUSED: коридор 4 мм к LED-предохранителю F103, 3-мм коридор к F105 и 4-мм от F102 к нижней шине; главная шина от входной зоны через F104 к F105 расширена до 4 мм после R706, сохранив 3 мм у его GND-площадки. INA238 U102 перемещён вверх на 0,8 мм; возврат `RTN_SHUNT` усилен заливкой у Q102 площадью около 8,7 мм² и силовыми дорожками 1,2–1,4 мм при сохранении Kelvin-съёмов. Справа стоят три параллельных KF301-2P на одном канале, рассчитанном примерно на 1,55 А / 75 Вт при 48 В. Модель общего тока питания с LED-нагрузкой — до 8,7 А при проектном пределе 9 А от БП 24 В / 10 А. Нагрев и работа при низкой яркости ещё требуют стендовой и программной проверки. Установлено 126 компонентов сверху и 37 снизу, включая RTC с обвязкой рядом с батарейкой. Q703 заменён на CSD19531KCS в TO-220. Закупка — **38,49 €** с НДС и доставкой (32,62 € детали + 5,87 € доставка) против 81,17 € у [EU-0.1](../PCB_EU/README.md#закупка) по строкам её BOM. Плата EU-0.1 и её файлы не менялись.

Проект по образцу [cheap-version](https://github.com/nikolajevs/ai/tree/7fa9410ddb7977c46e313506acb037693ad571e1/hardware/cheap-version) (дешёвая PCB_V1 из того же склада): всё, что есть на складе владельца ([stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv)), берётся оттуда; недостающее — из [снимка каталога цен Salvats / Electrobase от 23.10.2026](procurement_lite.json). Отличия от EU-0.1, расчёты и открытые вопросы — в [DESIGN.md](DESIGN.md).

## Что сохранено и что убрано

Сохранено: вход 24 В с защитой от переполюсовки и предохранителями, ESP32-WROOM-32E-N4 (те же GPIO), 12 В и 3,3 В, **один** LED-канал LM3429 (около 75 Вт / 1,55 А при 48 В суммарно на J501/J502/J503), **RGB-светодиод статуса** (GPIO4/16/17), PTC 100 Вт, помпа 24 В, два вентилятора 12 В с PWM, измерение мощности (INA238 вместо INA226), RTC MCP7940N с CR2032, microSD, SHT4x и поплавок.

Добавлено по просьбе владельца 24.10.2026: RGB-светодиод для индикации статуса и процессов (лист «Status»).

Убрано по решению владельца 24.10.2026: второй LED-канал (линейки) и тахометры вентиляторов. Дополнительно, для цены: аппаратная блокировка LED по UVLO/PGOOD (LM2903 + BAT54), USBLC6 на входе поплавка, ESD-диоды вентиляторов и радиатор с изоляцией. Последствия — в [DESIGN.md](DESIGN.md#отличия-от-eu-01) и [DESIGN.md, «Открытые вопросы»](DESIGN.md#открытые-вопросы).

## Файлы

| Файл | Назначение |
|---|---|
| [DESIGN.md](DESIGN.md) | Решения, отличия от EU-0.1, расчёты, склад без запаса, открытые вопросы |
| [PCB_EU_LITE.kicad_pro](PCB_EU_LITE.kicad_pro), [PCB_EU_LITE.kicad_sch](PCB_EU_LITE.kicad_sch) и 8 листов | Схема (KiCad 10, генерируется `tools/generate.py`) |
| [PCB_EU_LITE.kicad_pcb](PCB_EU_LITE.kicad_pcb), [placement.json](placement.json) | 163 посадки, электрически разведённая плата с четырёхслойной медью; DRC чистый. Инженерный черновик, не выпуск для производства |
| [BOM_allocated.csv](BOM_allocated.csv), [BOM_allocated.json](BOM_allocated.json) | Склад (`stock`, с остатком после сборки) и докупка (`buy`, с URL и датой цены) |
| [procurement_lite.json](procurement_lite.json) | Снимок каталога с резисторами уставки LED 4,7 кОм/620 Ом и карточкой OSTAPA57E2A владельца |
| [stock/sklad-2026-10-24.csv](stock/sklad-2026-10-24.csv) | Склад владельца (копия присланной выгрузки) |
| [design.json](design.json) | Полная спецификация выводов, цепей и компонентов |
| [review/connectivity.txt](review/connectivity.txt) | Сохранённый предыдущий полный прогон; актуальные 58 проверок для 75 Вт описаны в разделе «Проверки» |
| [review/Bench_checklist.md](review/Bench_checklist.md) | Что измерить при первом включении |
| [libraries/](libraries) | Символы проекта; собственные посадки PowerDI5, DTMSS-27, VSSOP-10 и SOIC-8; локальная копия BC-2001 с узким коридором GND только для EU-LITE и локальные копии складских посадок; стандартные 3D-модели используют установленную библиотеку KiCad |
| [tools/route_power.py](tools/route_power.py), [tools/route_complete.py](tools/route_complete.py), [tools/route_progress.py](tools/route_progress.py), [tools/route_bt_ground.py](tools/route_bt_ground.py), [tools/route_rtc.py](tools/route_rtc.py), [tools/route_switch_stage.py](tools/route_switch_stage.py), [tools/route_ground_stitch.py](tools/route_ground_stitch.py), [tools/route_prune_stubs.py](tools/route_prune_stubs.py), [tools/route_led_source.py](tools/route_led_source.py), [tools/route_led_terminals.py](tools/route_led_terminals.py) | Полигонная медь и воспроизводимые шаги частичной разводки, включая перенос и подключение RTC |

`EU_Mechanical` и `EU_Parts` по-прежнему общие с EU-0.1 (`../PCB_EU/libraries`, см. `fp-lib-table`); исключение — `LITE_Mechanical:Battery_COMF_BC-2001`, локальная копия с коридором GND для батарейного контакта. Исходные библиотеки EU-0.1 не менялись.

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

**Salvats** — 12,56 € с НДС

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
| [CRCW1206620RFKTABC](https://www.salvats.lv/lv/rezistori-smd-1206-025w/620r-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R506 |
| [CRCW120682K0FKTABC](https://www.salvats.lv/lv/rezistori-smd-1206-025w/82k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R101 |
| [CS2512-0R15-1%-HP](https://www.salvats.lv/lv/rezistori-smd-2512-1w3w/0r15-2512635x32mm-2w-1-smd-55125c-rezistors-thick-film-2512) | 1 | 0.32 | 0.32 | R502 |
| [CSD19531KCS](https://www.salvats.lv/lv/100v-n-fet-tht/csd19531kcs-tranzistors-n-fet-100v-vgs2233v-20v-100a-214w-0r0073-to-220) | 1 | 2.95 | 2.95 | Q703 |
| [LRP2512-R040-1%](https://www.salvats.lv/lv/rezistori-smd-2512-1w3w/0r04-2512635x32mm-3w-1-smd-55170c-rezistors-thick-film-2512) | 1 | 0.38 | 0.38 | R501 |
| [SMD1206 4K7 1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/4k7-1206-1-smd-rezistors-1206) | 1 | 0.04 | 0.04 | R505 |
| [SMD1206 56K 1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/56k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R507 |
| [SMD1206-10K-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/10k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R108 |
| [SMD1206-33K-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/33k-1206-1-smd-rezistors-1206) | 1 | 0.03 | 0.03 | R509 |
| [SMD1206-6K2-1%](https://www.salvats.lv/lv/rezistori-smd-1206-025w/6k2-1206-1-smd-rezistors-1206) | 2 | 0.03 | 0.06 | R102 R508 |
| [UPW1H221MPD](https://www.salvats.lv/lv/kondensatori-elektrolitiskie-zemas-induktivitates-low-esr/22050v-105c-o10x16mm-20-kondensatori-zemas-induktivitates-011r-5000h-nichicon-ar-lokaniem-izvadiem) | 2 | 0.63 | 1.26 | C101 C102 |
| [USBLC6-2SC6](https://www.salvats.lv/lv/u/usblc6-2sc6-smd-mikroshema-esd-protection-sot23-6) | 1 | 0.67 | 0.67 | U401 |
| [ZL201-10G](https://www.salvats.lv/lv/listes-un-nuju-ligzdas/254mm-uz-pcb-10pin-stekers-1) | 1 | 0.16 | 0.16 | J201 |

Со склада идёт 115 шт. в 38 позициях. KF301 используются 7 из 31 шт., остаётся 24; два новых клеммника не требуют закупки. Новые резисторы уставки LED добавляют 0,01 € к прежней сумме. Для Q703 выбран каталожный CSD19531KCS в TO-220; один BSC146N10LS5 остаётся в запасе для Q501. Без запаса остаются INA238, IRL2505, дроссель DTMSS-27 и два электролита EEVFK1J471M/EEEFT1E821AP. Полный список с остатками — [BOM_allocated.csv](BOM_allocated.csv).

Для D901 выбран OPTOSUPPLY OSTAPA57E2A. Цена 0,85 € с НДС и остаток 99 шт. взяты из карточки Electrobase, присланной владельцем 25.10.2026; наличие через корзину отдельно не проверялось. CSD19531KCS для Q703 добавлен из `catalog.db`: Salvats, 2,95 € с НДС, остаток 7 шт. в снимке от 23.10.2026; корзина не проверялась. Остальные цены и остатки — снимок каталога от 23.10.2026; C1206C100J5GACTU — из BOM EU-0.1 от 23.10.2026. Доставка 2,99 € (Electrobase) + 2,88 € (Salvats) взята из README EU-0.1 и не перепроверялась. Это не оферта и не заказ. AO3422 продаётся пачками по 5: два лишних.

## Проверки

Выполнено 25.10.2026 на **KiCad 10.0.5** (целевая 10.0.7 недоступна), Python с `pcbnew` и Shapely 2:

| Проверка | Результат |
|---|---|
| `generate.py`, `verify.py` | 158 деталей + 5 контрольных площадок; 58 проверок цепей, расчётов и BOM |
| `test_verify.py` | 29 преднамеренных дефектов отклонены, исходный проект проходит; включены переполюсовка J502, обход шунта J503 и старая уставка тока |
| `check_schematics.py` | 447 выводов прослежены по записанным листам, 0 проблем |
| KiCad ERC | **0 нарушений** |
| `check_placement.py` | Полный Shapely-прогон (18 193 проверки) относится к более ранней раскладке. После новых переносов отдельный нативный геометрический прогон выполнил 827 проверок для всех 163 позиций, коридоров разъёмов и доступа к пайке; Shapely 2 в доступном Python отсутствует, поэтому полный скрипт не запускался |
| `test_placement.py` | Не запускался после добавления THT-клеммников; полные регрессионные тесты размещения требуют Shapely 2 |
| KiCad DRC с заливкой зон и проверкой соответствия схеме | **0 ошибок, 0 предупреждений, 0 неподключённых элементов, 0 расхождений со схемой** |

**Размещение.** Все 163 посадочных места схемы находятся внутри платы 100×100 мм: 126 сверху, 36 SMD и BT301 с CR2032 снизу. Сохранены 4 отверстия и четырёхслойный стек. Сверху оставлены высокие и силовые компоненты; снизу размещены RGB, подтяжки microSD, RTC у батарейки, делитель вспомогательного БП и маломощное управление нагрузками. KiCad DRC и нативные проверки куртяр/коридоров прошли; физический корпус, высота деталей и ручная сборка не проверены.

**LED-выходы и мощность (25.10.2026).** Справа теперь три одинаковых KF301-2P: J501 (94;61), J502 (94;74), J503 (94;87) мм, все сверху под 90°. Вывод 1 — LED_POS после шунта R502, вывод 2 — GND; общий плюс соединён дорожкой 1 мм по F.Cu. Все три разъёма делят **один** токовый канал. R505/R506 = **4,7 кОм + 620 Ом, 1%, 1206**: примерно 1,55 А и 75 Вт суммарно при 48 В. Номинальная модель по таблице TI даёт 1,548 А / 74,3 Вт. Путь истоков Q501 к R501 теперь 0,8 мм по F.Cu с отдельной ветвью от каждого вывода; съём U501.12/TP04 сохранён у шунта.

Расчёт при 21,6 В, КПД 90%, L=43,5 мкГн, 400 кГц и допусках уставки: пик до **4,36 А**, минимальный IS-порог **5,32 А**, запас около **22%**. Нагрев не подтверждён. Общий бюджет с PTC/помпой/вентиляторами — до 8,7 А в модели, проектный предел 9 А; БП требуется 24 В / 10 А. Для 75 Вт в прошивке нужно поднять минимум nDIM до **5 отсчётов при 1 кГц/8 бит = 19,53 мкс**; сейчас `softwareEU/Board.h` даёт 3 отсчёта, эта правка и адаптация INA238 остаются открытыми. Подключаемые параллельно LED-ветви должны иметь согласованные Vf; деление тока между ними подтверждается измерением. [Расчёты и источники](DESIGN.md#led-канал).

**Разводка (25.10.2026).** L201 перенесён на (37,3;32) мм, 90°, а выходной C204 — на (33,8;31,5) мм, 180°. Узел `LOGIC_SW` U201.7–L201.1 сокращён примерно с 20 до **2,684 мм**, расширен с 0,2 до **0,6 мм** и полностью проходит по F.Cu без переходных отверстий. Между L201 и C204 также дорожка 0,6 мм; ветви +3V3 восстановлены дорожками 0,5 мм, +12V — 0,6 мм. Мешавший участок PUMP_GPIO перепроложен локально. C204 подключён к земле отдельным via 0,5/0,3 мм. Добавлены GND-vias (64;34) и (42;40,5) мм: они соединяют реальные земли C501/C515 и U201 с общей внутренней плоскостью. Удалены оставшиеся тупиковые дорожки и односторонние vias старых маршрутов с проверкой связности выводов после каждого прохода. Исправлена зеркальная сторона GND-коридора в локальной посадке BT301, предупреждение сравнения с библиотекой устранено. Ветви +24V_FUSED к F103 (4 мм), F105 (3 мм) и от F102 к нижней общей шине (4 мм) усилены заливкой F.Cu; площадь заливки от F102 выросла с 51,5 до 64,1 мм². Главная шина от входной зоны через F104 к F105 оставлена шириной 3 мм у GND-площадки R706 и расширена до 4 мм далее; заполненная медь двух участков занимает около 215 мм². U102 смещён вверх на 0,8 мм; три центральных участка `RTN_SHUNT` расширены до 1,4 мм, ещё три — до 1,3 мм. Две диагонали с ограниченным зазором к +24V_RAW оставлены 1,2 мм. У Q102 локальная заливка RTN_SHUNT расширена до 8,7 мм²; keepout IN+ и Kelvin-съём U102.9 сохранены. Зона LED-ветви обрезается зазорами вокруг D101 и цепей LED. Kelvin-съёмы U501.12/TP04 на R501.1 сохранены. Итоговый KiCad DRC после заливки и проверки схемы — 0 нарушений, 0 неподключённых цепей и 0 расхождений. Следующие аппаратные задачи — подтвердить Kelvin-подключение измерительных шунтов и измерить нагрев; Gerber не выпускался.

RTC U301, Y301, C301/C302/C303 остаются на B.Cu у батарейки; кварцевые цепи без vias, VBAT/I²C/+3V3 подключены. Общие подтяжки R308/R309 остались у ответвления I²C. Держатель BT301 подключён к GND через коридор нижней стороны и via вне держателя.

**Разъёмы и слот (25.10.2026).** Справа сверху вниз: SHT4x J401, FAN1 J411, FAN2 J421 и три параллельных LED-клеммника J501/J502/J503. Снизу: FLOAT J403, PTC J701 и PUMP J702. Вход 24 В J101 перенесён налево. UART J201 оставлен на координатах (4; 9,75) мм с прежней ориентацией, microSD J301 — у левого края под UART, карта выходит влево. Между их куртярами около 3 мм. В `placement.json` записаны направления подключения и коридоры доступа длиной 20 мм, шириной по корпусу +0,5 мм с каждого края; они проверяются против компонентов и крепежа. Это проектный резерв, не проверка конкретного штекера, радиуса изгиба кабеля или стенки корпуса.

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

**Далее:** проверить и при необходимости добавить тепловую медь для Q501 и D501, подтвердить Kelvin-подключение INA238, поднять программный минимум nDIM до 5 отсчётов и проверить токи/нагрев на эквиваленте LED 48 В. Электрическая разводка связна по KiCad DRC, но тепловая пригодность, монтаж корпуса и стендовые испытания не подтверждены. Gerber не выпускался. Сохранённые файлы `review/` не являются результатами актуальных KiCad-проверок; заказанная EU-0.1 не менялась.

Обновление данных каталога (нужна база `catalog.db` с тем же форматом): `python hardware/PCB_EU_LITE/tools/snapshot_prices.py CATALOG.db`, затем `generate.py` и `verify.py`. Генератор перезаписывает схемы: после ручной правки в KiCad сначала перенести её в `tools/generate.py`.
