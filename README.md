# OBD360 Web

OBD360 Web არის ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა, რომელიც მუშაობს OBD-II Bluetooth ადაპტერთან და აერთიანებს რეალურ დროში მონაცემებს, DTC კოდების ანალიზს, სკანირების ისტორიას, ტექნიკური მომსახურების შეხსენებებსა და AI ასისტენტს.

## ფუნქციონალი

- **რეგისტრაცია / ავტორიზაცია** — JWT access token + rotating refresh cookie.
- **Garage** — მანქანების დამატება, რედაქტირება, წაშლა, ძებნა.
- **Bluetooth** — Web Bluetooth-ით OBD-II ადაპტერთან დაკავშირება.
- **Live Data** — ძრავის ბრუნი, სიჩქარე, ტემპერატურა და სხვა PID-ები.
- **DTC Scanner** — შეცდომების კოდების წაკითხვა და გასუფთავება.
- **DTC Catalog** — 13 629 კოდის ქართული/ინგლისური აღწერა.
- **ECU Modules / Freeze Frame / Graphs** — მოდულები, freeze frame და გრაფიკები.
- **Scan History** — წინა სკანირებების ისტორია.
- **Maintenance Reminders** — შეხსენებები თარიღით; გარბენით — სამომავლო გაუმჯობესება.
- **AI Assistant** — n8n + Google Gemini-ს მეშვეობით ქართულენოვანი დიაგნოსტიკური ახსნები.
- **Critical DTC Alert** — n8n workflow კრიტიკული კოდებისთვის (Telegram).

## არქიტექტურა

| ფენა | ტექნოლოგია |
|---|---|
| Frontend | Angular 22, TypeScript, Signals, Web Bluetooth API |
| Backend | ASP.NET Core Web API (.NET 10), EF Core, SQL Server |
| Auth | ASP.NET Identity, JWT, refresh token cookie |
| Automation | n8n 2.47.4, webhook workflows |
| AI | Google Gemini (`gemini-3.1-flash-lite`) |
| Tests | xUnit + Vitest, 29 backend + 19 frontend |

C4 მოდელი: [docs/c4/OBD360 C4.pdf](<docs/c4/OBD360 C4.pdf>) — System Context, Container და Component დიაგრამები.

## REST API vs MVC

ეს პროექტი არის **REST API + Angular SPA**, არა server-side MVC.

| MVC (server-side) | ჩვენი პროექტი |
|---|---|
| Controller აბრუნებს HTML View-ს (`.cshtml`) | Controller აბრუნებს JSON-ს |
| `AddControllersWithViews()` | `AddControllers()` |
| გვერდები სერვერზე გენერირდება | გვერდებს Angular აწყობს |
| `Views/` საქაღალდე | არ არის `Views/` |

როგორ დავამტკიცოთ:

1. `Program.cs` — `builder.Services.AddControllers();`
2. `[ApiController]` ყველა controller-ზე.
3. `ActionResult<T>` / JSON პასუხები.
4. Angular `HttpClient` იძახებს `/api/v1/...` მისამართებს.
5. DevTools → Network → response არის JSON.

## მონაცემთა ბაზის დიზაინი

| რესურსი | მდებარეობა |
|---|---|
| 15 მოდელი | `backend/Obd360.Core/Entities/`, `Infrastructure/Identity/` |
| 21 ცხრილი | `database/schema.sql` |
| EF Core კონფიგურაცია | `backend/Obd360.Infrastructure/Data/ApplicationDbContext.cs` |
| მიგრაციები | `backend/Obd360.Infrastructure/Migrations/` |
| DTC seeder | `backend/Obd360.Infrastructure/Services/DtcCatalogSeeder.cs` |
| ვიზუალი | `docs/report/assets/data-model.png` |

> `ScanSession.cs` ერთ ფაილში აერთიანებს `ScanSession`, `LiveReading`, `DtcRecord` და `DtcCatalogEntry` კლასებს.

## გაშვება

### მოთხოვნები

- .NET 10 SDK
- Node.js 22+ და npm
- SQL Server (LocalDB ან სრული ინსტანსი)
- n8n 2.47.4 (სურვილისამებრ, AI ფუნქციისთვის)

### 1. მონაცემთა ბაზა

`backend/Obd360.Api/appsettings.Development.json`-ში ან user secrets-ში მიუთითე connection string:

```json
"ConnectionStrings": {
  "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=GeorgianCarScannerWeb;Trusted_Connection=True;TrustServerCertificate=True"
}
```

API გაშვებისას ავტომატურად უშვებს EF Core მიგრაციებს და DTC კატალოგის seeder-ს.

სუფთა ბაზისთვის შეგიძლია გამოიყენო:

```powershell
sqlcmd -S localhost -E -d GeorgianCarScannerWeb -i database/schema.sql
sqlcmd -S localhost -E -d GeorgianCarScannerWeb -i database/seed.sql
```

### 2. Backend

```powershell
cd backend/Obd360.Api
dotnet run
```

- API: http://localhost:5269
- Swagger: http://localhost:5269/swagger
- Health: http://localhost:5269/health/live

JWT გასაღები user secrets-ში:

```powershell
dotnet user-secrets set "Jwt:SigningKey" "REPLACE_WITH_A_LONG_RANDOM_SECRET"
```

### 3. Frontend

```powershell
cd frontend
npm install
npm start
```

- Frontend: http://localhost:4200
- პირველად გახსენი `Register`, შემდეგ `Login`.

### 4. n8n

```powershell
n8n\start-n8n.cmd
```

n8n: http://localhost:5678

workflow-ების იმპორტი:

```powershell
n8n import:workflow --input="n8n\obd360-scan-report.workflow.json"
n8n import:workflow --input="n8n\obd360-assistant-ask.workflow.json"
n8n import:workflow --input="n8n\obd360-critical-dtc.workflow.json"
```

AI workflow-ები იყენებს n8n-ში შენახულ `googlePalmApi` credential-ს. დეტალები: [n8n/README.md](n8n/README.md).

#### Telegram alert

`OBD360 Critical DTC Alert` workflow აგზავნის Telegram შეტყობინებას, თუ გაშვებამდე დააყენე:

```powershell
$env:OBD360_TELEGRAM_BOT_TOKEN = "123456:ABC..."
$env:OBD360_TELEGRAM_CHAT_ID = "123456789"
```

Bot token: `@BotFather` → `/newbot`. Chat ID: `@userinfobot` ან `getUpdates`.
თუ env ცვლადები არ არის დაყენებული, workflow იღებს მოთხოვნას, მაგრამ Telegram-ში არ აგზავნის.

## პაროლის აღდგენა

მომხმარებელი ჰკითხულობს ელფოსტას, იღებს **6-ნიშნა კოდს** და აყენებს ახალ პაროლს.

```text
POST /api/v1/auth/forgot-password   { email }
POST /api/v1/auth/reset-password    { email, code, newPassword }
POST /api/v1/auth/change-password   { currentPassword, newPassword }  (ავტორიზებული)
```

უსაფრთხოება:

- კოდი მოქმედებს **10 წუთი**, გამოიყენება **მხოლოდ ერთხელ** და აქვს **5 მცდელობა**.
- არ არსებობს user enumeration — უცნობ ელფოსტაზეც იგივე პასუხი ბრუნდება.
- პაროლის შეცვლის/აღდგენის შემდეგ ყველა refresh session უქმდება.

### SMTP კონფიგურაცია

`appsettings.json`-ში ან environment variables-ით:

```json
"Smtp": {
  "Host": "smtp.gmail.com",
  "Port": 587,
  "UserName": "your@gmail.com",
  "Password": "APP_PASSWORD",
  "FromAddress": "your@gmail.com",
  "FromName": "OBD360",
  "EnableSsl": true
}
```

ან environment variables:

```powershell
$env:Smtp__Host = "smtp.gmail.com"
$env:Smtp__Port = "587"
$env:Smtp__UserName = "your@gmail.com"
$env:Smtp__Password = "APP_PASSWORD"
$env:Smtp__FromAddress = "your@gmail.com"
```

Gmail-ისთვის გამოიყენე **App Password**, არა ჩვეულებრივი პაროლი.
SMTP-ის გარეშე (Development) API კოდს ლოგში წერს და `/auth/forgot-password`-ის პასუხში აბრუნებს
`devCode`-ს, რომ ლოკალურად დემონსტრირება შეიძლებოდეს.

## Reminder email notifications

რემაინდერები ავტომატურად ეგზავნება ელფოსტაზე. ფონური სერვისი:

- მუშაობს API-ის გაშვებისას და შემდეგ ყოველ **6 საათში**.
- ამოწმებს მხოლოდ **თარიღით** ვადაგასულ/დღევანდელ რემაინდერებს (`DueAtDate <= today`).
- ერთ მომხმარებელზე აგზავნის **ერთ digest მეილს** დღეში.
- შედეგი ინახება `NotificationLogs`-ში (`MaintenanceReminder` + `Email`), რომ დუბლიკატი არ გაიგზავნოს.

კონფიგურაცია `appsettings.json`-ში:

```json
"Reminders": {
  "Enabled": true,
  "CheckIntervalMinutes": 360
}
```

> კმ-ით რემაინდერები ჯერ არ იგზავნება, რადგან მანქანის მიმდინარე გარბენი არ ინახება.
> ტესტისთვის შექმენი რემაინდერი დღევანდელი ან გასული თარიღით და გადაუშვი API.

## Admin API

`/api/v1/admin` — მხოლოდ **Admin** როლისთვის. Frontend: `/app/admin`.

- `GET /overview` — users / vehicles / scans / DTC რაოდენობები
- `GET /users?search=` — მომხმარებლები, როლები და აქტივობა
- `DELETE /users/{id}` — მომხმარებლის წაშლა (საკუთარი თავის და ბოლო Admin-ის გარდა)
- `POST /users/{id}/toggle-role` — Admin როლის დამატება/მოხსნა
- `GET /scans?search=` — ყველა მომხმარებლის ბოლო სკანირებები

## ლოგირება და Swagger

- HTTP request logging: method, path, status, duration.
- Auth ლოგები: register, login success/failure, password reset/change.
- Reminder email ლოგები: გაგზავნა/შეცდომა.
- Swagger: `http://localhost:5269/swagger` — API info, JWT Authorize, XML summaries (Admin/Auth).

## API

| მეთოდი | მისამართი | აღწერა |
|---|---|---|
| POST | `/api/v1/auth/register` | რეგისტრაცია |
| POST | `/api/v1/auth/login` | ავტორიზაცია |
| POST | `/api/v1/auth/refresh` | token-ის განახლება |
| POST | `/api/v1/auth/logout` | გასვლა |
| POST | `/api/v1/auth/forgot-password` | აღდგენის კოდის გაგზავნა |
| POST | `/api/v1/auth/reset-password` | კოდით ახალი პაროლის დაყენება |
| POST | `/api/v1/auth/change-password` | პაროლის შეცვლა (ავტორიზებული) |
| GET/PUT | `/api/v1/preferences` | პარამეტრები |
| GET/POST | `/api/v1/vehicles` | მანქანების სია / დამატება |
| GET/PUT/DELETE | `/api/v1/vehicles/{id}` | მანქანის ნახვა / რედაქტირება / წაშლა |
| GET/POST | `/api/v1/reminders` | შეხსენებები |
| PUT/DELETE | `/api/v1/reminders/{id}` | შეხსენების რედაქტირება / წაშლა |
| POST | `/api/v1/reminders/{id}/complete` | შეხსენების დასრულება |
| GET/POST | `/api/v1/scans` | სკანირების ისტორია / ახალი სკანირება |
| GET | `/api/v1/dtc-catalog?search=&page=&pageSize=` | DTC კატალოგი |
| GET | `/api/v1/dtc-catalog/{code}` | კოდის დეტალები |
| GET | `/api/v1/ai/status` | AI ინტეგრაციის სტატუსი |
| POST | `/api/v1/ai/latest-scan-report` | ბოლო სკანირების AI რეპორტი |
| POST | `/api/v1/ai/ask` | AI ასისტენტის კითხვა |
| GET | `/api/v1/ai/conversation` | საუბრის ისტორია |
| GET | `/api/v1/admin/overview` | ადმინის სტატისტიკა |
| GET | `/api/v1/admin/users?search=` | მომხმარებლების სია |
| DELETE | `/api/v1/admin/users/{id}` | მომხმარებლის წაშლა |
| POST | `/api/v1/admin/users/{id}/toggle-role` | Admin როლის გადართვა |
| GET | `/api/v1/admin/scans?search=` | ყველა სკანირება |

## პრეზენტაცია

- `docs/slides/OBD360-Web-Presentation.pptx` — 18 სლაიდი (სრული ვერსია)
- `docs/slides/OBD360-Web-Presentation.pdf` — PDF ვერსია
- სლაიდებში: OBD-II/ECU დიაგრამა, DTC კატალოგი (13,629), კოდის ნაკადი, არქიტექტურა და დემო.

### გამარტივებული ვერსია — OBD2

- `docs/slides/OBD2-Web-Presentation-Simple.pptx` — 13 სლაიდი
- `docs/slides/OBD2-Web-Presentation-Simple.pdf` — PDF ვერსია
- ყველა წარწერა **OBD2**-ია; ტექსტი შემცირებულია და გამარტივებულია.

## დოკუმენტაცია

- `docs/report/OBD360-Web-Documentation.docx` — სრული პროექტის დოკუმენტაცია (36 გვერდი)
- `docs/report/OBD360-Web-Documentation.pdf` — PDF ვერსია
- მოიცავს: OBD-II თეორია, არქიტექტურა, მონაცემთა მოდელი, API, OBD-II კოდი, უსაფრთხოება, ტესტირება, გაშვება და მომხმარებლის გზამკვლევი.

## სწავლისა და დაცვის გზამკვლევი

- `docs/CODE-GUIDE.md` — კოდის რუკა: სად არის რა, 30 კითხვა-პასუხი, 5 სცენარი.
- `docs/report/OBD360-Defense-Guide.docx` / `.pdf` — 9-გვერდიანი დაცვის შეკვრა მარტივი ქართული ენით.

## ტესტები

```powershell
cd backend
dotnet test
```

მიმდინარე შედეგი: **29/29 backend** და **19/19 frontend** ტესტი passed.

## პროექტის სტრუქტურა

```
backend/
  Obd360.Api/            Web API, controllers, n8n integration
  Obd360.Core/           entities, enums
  Obd360.Infrastructure/ EF Core DbContext, migrations, seeding
  Obd360.Tests/          xUnit tests
frontend/
  src/app/core/          services, guards, interceptors
  src/app/features/      dashboard, garage, reminders, bluetooth, ...
  src/app/layout/        sidebar, topbar
n8n/                     n8n workflows and start/stop scripts
database/                schema.sql, seed.sql
docs/c4/                 C4 diagrams (PDF)
```

## Docker

```powershell
docker compose up --build
```

სერვისები:

- Frontend: http://localhost:4200
- API: http://localhost:5269
- Swagger: http://localhost:5269/swagger
- n8n: http://localhost:5678
- SQL Server: localhost:1433

Docker გარემოში connection string, JWT, CORS და Telegram ცვლადები გადაეცემა `docker-compose.yml`-იდან. საჭიროების შემთხვევაში შეცვალე `SQL_PASSWORD`, `JWT_SIGNING_KEY` და `PUBLIC_ORIGIN`.

### DigitalOcean (production)

Droplet-ზე გაშვების ინსტრუქცია: [`docs/deployment/DIGITALOCEAN.md`](docs/deployment/DIGITALOCEAN.md).

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Production override მალავს SQL Server/API/n8n პორტებს და web-ს აკავშირებს მხოლოდ `127.0.0.1:4200`-ზე; TLS-ს ამთავრებს host Nginx.

## შეზღუდვები / Future work

- ყოველკვირეული PDF რეპორტები (Reports) — მოდელი არსებობს, UI/API ჯერ არა.
- Email confirmation — ჯერ არ არის.
- GitHub Actions CI/CD — ჯერ არ არის.
- სრული ინტეგრაციული ტესტები რეალურ SQL Server-ზე.
- DigitalOcean-ის რეალური deployment ჯერ არ გაშვებულა; საჭიროა Droplet/დომენი.

## ავტორი

ზურაბ ლაზაშვილი — OBD360 Web, 2026.
