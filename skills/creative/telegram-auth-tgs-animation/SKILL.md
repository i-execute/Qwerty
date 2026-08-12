---
name: telegram-auth-tgs-animation
description: "Build a web page (React/HTML) that (1) authenticates a user by Telegram id via Mini App and (2) plays a .tgs animation (Telegram sticker)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, mini-app, tgs, lottie, auth, web]
---

# Skill: Telegram Mini App Auth + TGS Animation

Используй этот файл как инструкцию, когда нужно сделать веб-страницу
(React/HTML), которая: (1) авторизует пользователя по его Telegram id
через Mini App, (2) проигрывает .tgs-анимацию (Telegram-стикер).

## 1. Как работает авторизация в Telegram Mini App

Когда страница открыта **внутри Telegram** через кнопку с типом `web_app`
(а не просто по ссылке), Telegram инжектит в неё объект
`window.Telegram.WebApp`. У него есть:

- `tg.initData` — сырая подписанная строка (query-string формата
  `user=...&auth_date=...&hash=...`). Если страница открыта не из
  Telegram (просто в браузере) — `initData` будет пустой строкой.
- `tg.initDataUnsafe.user.id` — уже распарсенный id пользователя.
  Называется "unsafe", потому что его легко подделать в devtools —
  доверять ему можно только для *локального теста без бэкенда*.

### Подключение SDK
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```
Обязательно ДО своего кода. Если деплоер/шаблон, который собирает
итоговый html, не добавляет этот тег сам — подгрузи его вручную из
JS перед любой проверкой:

```js
function loadTelegramSDK() {
  return new Promise((resolve) => {
    if (window.Telegram && window.Telegram.WebApp) return resolve();
    const s = document.createElement("script");
    s.src = "https://telegram.org/js/telegram-web-app.js";
    s.onload = () => resolve();
    s.onerror = () => resolve();
    document.head.appendChild(s);
  });
}
```

### Проверка id (тестовый уровень, без бэкенда)
```js
await loadTelegramSDK();
const tg = window.Telegram?.WebApp;
if (!tg || !tg.initData) {
  // не из Telegram вообще, или открыто просто по ссылке
  return "401";
}
tg.ready();
tg.expand();
const id = Number(tg.initDataUnsafe?.user?.id);
return id === ALLOWED_USER_ID ? "success" : "401";
```

### Как это должно работать по-настоящему (продакшен)
`initDataUnsafe` не защищает от подделки на клиенте. Для реальной
защиты нужен бэкенд:
1. Клиент отправляет сырой `tg.initData` на сервер.
2. Сервер считает HMAC-SHA256 от параметров, используя ключ,
   производный от токена бота, и сравнивает с `hash` из initData.
3. Только если хэш совпал — доверяем `user.id` из данных.
Без этого шага любой человек с devtools может вписать себе чужой id.

### Частые причины "не работает"
- Открыли страницу просто ссылкой в браузере/чате, а не через
  кнопку `web_app` у бота → `initData` пустой → всегда 401.
- Собирающий html шаблон (свой деплоер, генератор и т.п.) не
  подключает `telegram-web-app.js` в `<head>` → `window.Telegram`
  вообще не существует. Проверяй это в первую очередь.
- id сравнивается как строка со строкой/числом без приведения типов
  — используй `Number(...)` с обеих сторон.

## 2. Как рендерить .tgs-анимацию (Telegram-стикер)

`.tgs` — это gzip-сжатый Lottie-json. Чтобы отобразить:
1. Скачать байты файла (raw-ссылка, НЕ github.com/.../blob/...,
   а `raw.githubusercontent.com/...` — blob-страница отдаёт HTML,
   а не файл).
2. Разгзипить через `pako.inflate(bytes, {to: "string"})`.
3. `JSON.parse` результата → это обычный Lottie JSON.
4. Отрендерить через `lottie-web`.

```js
async function loadScript(src) {
  return new Promise((resolve) => {
    const s = document.createElement("script");
    s.src = src;
    s.onload = () => resolve();
    s.onerror = () => resolve();
    document.head.appendChild(s);
  });
}

async function playTgs(container, tgsUrl) {
  try {
    if (!window.pako) await loadScript("https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js");
    if (!window.lottie) await loadScript("https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js");
    const buf = await fetch(tgsUrl).then((r) => r.arrayBuffer());
    const json = JSON.parse(window.pako.inflate(new Uint8Array(buf), { to: "string" }));
    window.lottie.loadAnimation({
      container,
      renderer: "svg",
      loop: true,
      autoplay: true,
      animationData: json,
    });
  } catch (e) {
    // всегда фолбэк — анимация не должна ронять страницу
    container.innerHTML = "🎉";
  }
}
```

### Важно
- Всегда оборачивай в try/catch — сеть/CORS/битый файл не должны
  ломать остальную страницу.
- Если это React-компонент — вызывай `playTgs` в `useEffect` по
  `ref` контейнера, и лучше оберни сам компонент в error boundary,
  чтобы даже падение рендера Lottie не убило остальное приложение.
- **Валидный Lottie JSON не гарантирует, что в нём есть нужный объект.**
  До вёрстки проверь `layers`, их имена, длительность (`ip`/`op`) и размер.
  Небольшой JSON с единственным слоем наподобие `aura` может проигрываться
  корректно, но содержать только фон/свечение, а не персонажа.
- Если персонаж должен быть гарантированно видимым, используй отдельный
  дочерний контейнер для Lottie как эффектный слой (аура/частицы), а сам
  силуэт — отдельным SVG/DOM-слоем поверх. Не передавай контейнер, которым
  уже владеет React-разметка персонажа, напрямую в `lottie.loadAnimation()`.
- Визуально проверяй минимум два кадра или наблюдение дольше одного цикла:
  слабая анимация на первом кадре может выглядеть статичной.

## 3. Типовые баги при верстке на весь экран
- `100vw` включает ширину скроллбара → появляется полоска сбоку.
  Используй `width: 100%` вместо `100vw`.
- `html, body` по умолчанию имеют `margin`. Если генератор html не
  сбрасывает — сбрасывай сам через инжектнутый `<style>`:
```css
html, body, #root { margin: 0; padding: 0; width: 100%; height: 100%; overflow-x: hidden; }
```

## 4. Чеклист перед деплоем
- [ ] `telegram-web-app.js` подключён (в шаблоне или динамически)
- [ ] Открывается именно через `web_app`-кнопку бота, не по ссылке
- [ ] id сравнивается с приведением типов (`Number(...)`)
- [ ] tgs-ссылка — raw, не blob
- [ ] рендер анимации в try/catch, не валит всю страницу
- [ ] html/body/root сброшены в 0 отступов, ширина 100%, не 100vw