# LPR GateBox (Home Assistant)

Интеграция Home Assistant для **LPR GateBox**.

## Что даёт

- **Сенсоры**:
  - Последний распознанный номер
  - Уверенность
  - Статус / сообщение
  - Время последнего события
- **Binary sensor**: доступность RTSP-потока (по данным GateBox)
- **Camera entity**: последний кадр `.../api/v1/rtsp/frame.jpg`

## Установка через HACS

1. HACS → **Integrations** → меню (⋮) → **Custom repositories**
2. Repository: `https://github.com/pirsasha/lpr_gatebox-ha`
3. Category: **Integration**
4. Установить → перезапустить Home Assistant
5. Settings → Devices & Services → **Add Integration** → *LPR GateBox*
6. Ввести адрес GateBox: `http://<IP>:8080`

## Настройки

После добавления интеграции: **Configure**:
- *Включать debug-события*
- *Heartbeat SSE, сек*
- *Интервал опроса SSE, мс*

## Требования

GateBox должен быть доступен по сети (обычно порт **8080**).

## Поддержка

Issues: https://github.com/pirsasha/lpr_gatebox-ha/issues
