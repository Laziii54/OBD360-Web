# OBD360 × n8n ინტეგრაცია

OBD360-ის AI Assistant მუშაობს n8n workflow-ების მეშვეობით. Angular აპლიკაცია არასდროს
აკეთებს პირდაპირ AI პროვაიდერთან კავშირს: ის აგზავნის მოთხოვნას ASP.NET Core ბექენდზე,
ბექენდი — n8n webhook-ზე, ხოლო n8n — Google Gemini-სთან.

```
Angular (AI Assistant)
        │  POST /api/v1/ai/latest-scan-report  ან  /api/v1/ai/ask
        ▼
ASP.NET Core API  ──POST──▶  n8n webhook  ──▶  Google Gemini
        ▲                         │
        └────── { "text": ... } ──┘
```

## რა არის აქ

| ფაილი | დანიშნულება |
| --- | --- |
| `obd360-scan-report.workflow.json` | სკანირების ანგარიშის workflow (`/webhook/obd360/scan-report`) |
| `obd360-assistant-ask.workflow.json` | შემდგომი კითხვების workflow (`/webhook/obd360/ask`) |
| `obd360-critical-dtc.workflow.json` | კრიტიკული DTC შეტყობინება Telegram-ში (`/webhook/obd360/critical-dtc`) |
| `start-n8n.cmd` / `start-n8n.ps1` | n8n-ის გაშვება Windows-ზე (npm ინსტალაციით) |
| `stop-n8n.cmd` / `stop-n8n.ps1` | n8n-ის გაჩერება |
| `docker-compose.yml` | n8n-ის გაშვება Docker-ით (არასავალდებულო) |

ბექენდის მხარე:

* `backend/Obd360.Api/Integrations/N8n/` — კონფიგურაცია, resilient HTTP კლიენტი, პასუხის პარსერი და პრომპტების აწყობა.
* `GET  /api/v1/ai/status` — n8n-ის კონფიგურაცია/ხელმისაწვდომობა.
* `POST /api/v1/ai/latest-scan-report` — ბოლო სკანირების AI ანგარიში.
* `POST /api/v1/ai/ask` — კითხვა ასისტენტს (ინახება `AiConversations`/`AiMessages` ცხრილებში).
* `GET  /api/v1/ai/conversation` — ბოლო საუბრის ისტორია.

## 1. n8n-ის გაშვება (Windows, npm)

n8n უკვე დაინსტალირებულია ამ კომპიუტერზე. გასაშვებად გახსენი `n8n` საქაღალდე და
ორჯერ დააწკაპუნე **`start-n8n.cmd`**-ს, ან ტერმინალში:

```powershell
cd "C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\n8n"
.\start-n8n.ps1
```

n8n გაიხსნება <http://localhost:5678>-ზე. გაჩერება: `Ctrl+C` ან **`stop-n8n.cmd`**.

> თუ ტერმინალი `backend` საქაღალდეშია, ბრძანება იქნება `..\n8n\start-n8n.cmd`
> (ან ჯერ გადადი `cd ..\n8n`-ში). `n8n\start-n8n.cmd` მუშაობს მხოლოდ მაშინ, როცა
> უკვე პროექტის მთავარ საქაღალდეში ხარ.

თუ n8n სხვა კომპიუტერზე გჭირდება:

```powershell
npm install -g n8n@2.47.4
```

> Docker ვარიანტი: `docker compose up -d` (მხოლოდ თუ Docker Desktop დაინსტალირებულია).

## 2. Workflow-ების იმპორტი და გააქტიურება

### ვარიანტი A — n8n UI

1. გახსენი n8n → **Workflows** → **Import from File**.
2. ატვირთე `obd360-scan-report.workflow.json`.
3. გაიმეორე `obd360-assistant-ask.workflow.json`-ისთვის.
4. გახსენი თითოეული workflow და ჩართე **Active** გადამრთველი.

### ვარიანტი B — CLI

```powershell
docker exec obd360-n8n n8n import:workflow --input=/workflows/obd360-scan-report.workflow.json
docker exec obd360-n8n n8n import:workflow --input=/workflows/obd360-assistant-ask.workflow.json
```

npm ინსტალაციის შემთხვევაში:

```powershell
n8n import:workflow --input="C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\n8n\obd360-scan-report.workflow.json"
n8n import:workflow --input="C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\n8n\obd360-assistant-ask.workflow.json"
n8n import:workflow --input="C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\n8n\obd360-critical-dtc.workflow.json"
n8n publish:workflow --id=<workflow-id>
```

> მნიშვნელოვანია: ბექენდი იყენებს **production** webhook-ს (`/webhook/...`), ამიტომ workflow
> სავალდებულოდ უნდა იყოს **Active** (ან `publish:workflow`). თუ მხოლოდ „Test workflow“-ს
> იყენებ, URL იქნება `/webhook-test/...` და ბექენდი 404-ს მიიღებს.

## 3. Gemini კრედენშელი

workflow-ები იყენებენ n8n-ის კრედენშელს ტიპით **Google Gemini(PaLM) Api** და მოდელს
`models/gemini-3.1-flash-lite` (სწრაფი პასუხები). ორივე workflow-ში ეს კრედენშელი მიბმულია
ნოდზე **Call Gemini**.

თუ workflow-ს სხვა n8n ინსტანსში აიმპორტებ:

1. n8n → **Credentials** → **Add credential** → **Google Gemini(PaLM) Api**.
2. შეიყვანე Google AI Studio-ს API key.
3. გახსენი თითოეული workflow → **Call Gemini** → აირჩიე ეს კრედენშელი.
4. შეინახე და გაააქტიურე workflow.

მოდელის შეცვლა: **Call Gemini** ნოდის URL-ში შეცვალე `gemini-3.1-flash-lite` სხვა მოდელით
(მაგ. `gemini-3.1-flash` — უფრო დეტალური პასუხები, მაგრამ ნელი).

## 4. ბექენდის კონფიგურაცია

`appsettings.Development.json`-ში უკვე მითითებულია:

```json
"N8n": {
  "BaseUrl": "http://localhost:5678",
  "ScanReportPath": "/webhook/obd360/scan-report",
  "AskPath": "/webhook/obd360/ask",
  "AlertPath": "/webhook/obd360/critical-dtc",
  "TimeoutSeconds": 90
}
```

სხვა გარემოში ან სხვა n8n ინსტანსისთვის გამოიყენე user secrets:

```powershell
cd backend/Obd360.Api
dotnet user-secrets set "N8n:BaseUrl" "https://n8n.example.com"
```

სრული URL-ის მითითებაც შესაძლებელია (`BaseUrl`-ის ნაცვლად):

```powershell
dotnet user-secrets set "N8n:WebhookUrl" "https://n8n.example.com/webhook/obd360/scan-report"
dotnet user-secrets set "N8n:AskWebhookUrl" "https://n8n.example.com/webhook/obd360/ask"
```

აპლიკაციის გაშვება:

```powershell
cd backend/Obd360.Api
dotnet run
```

## 5. შემოწმება

1. გახსენი OBD360 → **AI Assistant**.
2. გვერდის თავში უნდა ჩანდეს `n8n დაკავშირებულია` (მწვანე).
3. თუ სკანირება არსებობს, ანგარიში ავტომატურად ჩაიტვირთება; ქვემოთ შეგიძლია დასვა კითხვა.
4. **Settings → n8n Integration** ბარათი აჩვენებს workflow-ების კონფიგურაციას და სერვერის ხელმისაწვდომობას.

სწრაფი შემოწმება curl-ით:

```powershell
$body = @{ prompt = 'ავტომობილი: Toyota Camry. კოდი P0300. ახსენი მარტივად.' } | ConvertTo-Json
$body | Set-Content -Path "$env:TEMP\obd360-webhook.json" -Encoding utf8

curl.exe -X POST http://localhost:5678/webhook/obd360/scan-report `
  -H "Content-Type: application/json" `
  --data-binary "@$env:TEMP\obd360-webhook.json"
```

პასუხი უნდა იყოს:

```json
{ "text": "..." }
```

## 6. Troubleshooting

| სიმპტომი | მიზეზი / გადაწყვეტა |
| --- | --- |
| `n8n არ არის კონფიგურირებული` | `N8n:BaseUrl` ცარიელია (ან `N8n:WebhookUrl`). დააყენე user secrets-ით. |
| `n8n მიუწვდომელია` | n8n არ მუშაობს. გაუშვი `start-n8n.cmd` და შეამოწმე http://localhost:5678. |
| HTTP 404 workflow-დან | workflow არ არის **Active**, ან webhook path არ ემთხვევა (`obd360/scan-report`). |
| HTTP 401/403 | Gemini API key არასწორია ან არ არის მიბმული კრედენშელი. |
| HTTP 500 | ნახე n8n-ის **Executions** → ბოლო შესრულება; ხშირად მოდელი გადატვირთულია. |
| `503 UNAVAILABLE` | მოდელი დროებით გადატვირთულია — სცადე სხვა მოდელი ან გაიმეორე მოგვიანებით. |
| `n8n-მა ცარიელი პასუხი დააბრუნა` | workflow-ს აკლია **Respond to Webhook** ან Gemini-მ პასუხი დააბლოკა. |
| პასუხი 90 წამზე მეტხანს მოდის | გაზარდე `N8n:TimeoutSeconds` (მაქს. 300) ან გამოიყენე უფრო სწრაფი მოდელი. |

## 7. რას აგზავნის ბექენდი

`POST /webhook/obd360/scan-report`:

```json
{
  "prompt": "…მზა ქართული პრომპტი…",
  "kind": "scan-report",
  "locale": "ka",
  "vehicle": "Camry",
  "scannedAt": "2026-11-11T16:05:35Z",
  "codes": [
    {
      "code": "P0300",
      "title": "შემთხვევითი/მრავალჯერადი ცილინდრის გამოტოვება",
      "description": "…",
      "causes": ["…"],
      "difficulty": "medium",
      "diyPossible": true
    }
  ]
}
```

`POST /webhook/obd360/ask` დამატებით აგზავნის `question`-ს და `history`-ს. საუბრის ისტორია
უკვე ჩართულია თვით `prompt`-შიც, ამიტომ workflow მას პირდაპირ Gemini-ს უგზავნის.

ორივე workflow აბრუნებს `{ "text": "..." }`-ს. ბექენდი ასევე იღებს `{ "output": ... }`,
მასივს, ან Anthropic/OpenAI-ის „ნედლ“ პასუხს — `N8nResponseParser` ცდილობს ყველა
გავრცელებული ფორმატის ამოცნობას.

## 8. კრიტიკული DTC → Telegram

`obd360-critical-dtc.workflow.json` იღებს `POST /webhook/obd360/critical-dtc`-ს. ბექენდი
ამ webhook-ს ავტომატურად იძახებს ყოველი ახალი სკანირების შემდეგ, თუ მასში DTC კოდებია.
შეტყობინება მიდის Telegram-ში.

### Telegram bot-ის მომზადება

1. Telegram-ში გახსენი **@BotFather** → `/newbot` → მიიღე bot token.
2. გაუშვი bot და მისწერე რაიმე შეტყობინება.
3. Chat ID-ის მისაღებად გახსენი:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   და იპოვე `"chat":{"id":...}`.
4. n8n-ის გაშვებამდე დააყენე env ცვლადები:

```powershell
$env:OBD360_TELEGRAM_BOT_TOKEN = "123456:ABC..."
$env:OBD360_TELEGRAM_CHAT_ID = "123456789"
.\start-n8n.ps1
```

ან `start-n8n.ps1`-ში ჩაწერე ეს ორი ხაზი (კომენტარები მოხსენი).

### შემოწმება

```powershell
$body = @{
  vehicle = 'Chevrolet Volt'
  vin = '1G1RB6E42DU101631'
  codes = @('P0A80', 'P0300')
  scannedAt = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json

$body | Set-Content "$env:TEMP\critical-dtc.json" -Encoding utf8

curl.exe -X POST http://localhost:5678/webhook/obd360/critical-dtc `
  -H "Content-Type: application/json" `
  --data-binary "@$env:TEMP\critical-dtc.json"
```

პასუხი: `{ "status": "accepted" }`. თუ Telegram-ში შეტყობინება არ მოვიდა, ნახე
n8n → **Executions** → `Send Telegram` ნოდის შეცდომა (ჩვეულებრივ, არასწორი token ან chat ID).

> env ცვლადების გარეშე workflow მაინც პასუხობს `accepted`-ით, მაგრამ Telegram-ში არ აგზავნის.
> ეს განზრახ არის: სკანირება არ უნდა ჩავარდეს შეტყობინების გაგზავნის გამო.
