# OBD360 Web

**ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა.** OBD360 უკავშირდება მანქანას OBD-II Bluetooth ადაპტერით
(ELM327), კითხულობს სენსორებს და შეცდომის კოდებს (DTC), ინახავს ისტორიას ბაზაში და AI ასისტენტით
ქართულად ხსნის, რას ნიშნავს ისინი.

სადიპლომო პროექტი · ზურაბ ლაზაშვილი · 2026

---

## რას აკეთებს

| ფუნქცია | მოკლედ |
|---|---|
| **რეგისტრაცია / შესვლა** | JWT + refresh token, პაროლის აღდგენა ელფოსტით (6-ნიშნა კოდი) |
| **Garage** | მანქანების დამატება, რედაქტირება, წაშლა, ძებნა |
| **Bluetooth** | ადაპტერთან დაკავშირება პირდაპირ ბრაუზერიდან (Web Bluetooth) |
| **Live Data** | ბრუნი, სიჩქარე, ტემპერატურა, ძაბვა და სხვა სენსორები რეალურ დროში |
| **DTC Scanner / Catalog** | შეცდომის კოდების წაკითხვა; 13 629 კოდის ქართული აღწერა |
| **Scan History** | წინა სკანირებები ბაზიდან |
| **Reminders** | ტექნიკური მომსახურების შეხსენებები თარიღით, ელფოსტის შეტყობინებით |
| **AI Assistant** | კითხვა-პასუხი და სკანირების ანგარიში ქართულად (n8n + Google Gemini) |
| **Admin** | მომხმარებლების და სკანირებების მართვა (მხოლოდ Admin როლისთვის) |

## ტექნოლოგიები

| ფენა | რას ვიყენებთ |
|---|---|
| Frontend | Angular 22, TypeScript, **Signals**, Web Bluetooth API |
| Backend | ASP.NET Core Web API (.NET 10), EF Core |
| ბაზა | SQL Server |
| ავტორიზაცია | ASP.NET Identity, JWT, refresh cookie (HttpOnly) |
| ავტომატიზაცია / AI | n8n (webhook workflows) + Google Gemini |
| ტესტები | xUnit (backend), Vitest (frontend) |

## როგორ მუშაობს

```
ბრაუზერი (Angular) ──HTTP/JSON──►  ASP.NET Core API  ──EF Core──►  SQL Server
      │                                    │
      │ Web Bluetooth                      └──webhook──► n8n ──► Google Gemini (AI)
      ▼
OBD-II ადაპტერი (ELM327) ◄──► მანქანის ECU
```

- ეს არის **REST API + Angular SPA** (სერვერი აბრუნებს JSON-ს და არა HTML გვერდებს, `Views/` არ არის).
- ადაპტერს ბრაუზერი კითხულობს პირდაპირ; API მხოლოდ მონაცემებს ინახავს და ამოწმებს უფლებებს.
- AI კითხვა გადის API → n8n → Gemini, პასუხი ინახება ბაზაში.

C4 დიაგრამები: [`docs/c4/OBD360 C4.pdf`](<docs/c4/OBD360 C4.pdf>) · ER დიაგრამა: [`docs/report/assets/er-diagram.png`](docs/report/assets/er-diagram.png)

---

## სწრაფი გაშვება

### რა გჭირდება

- .NET SDK 10
- Node.js 22+ და npm
- SQL Server (სრული ინსტანსი ან LocalDB)
- n8n — მხოლოდ AI ფუნქციისთვის (არასავალდებულო)

### 1. ბაზის მისამართი

გახსენი `backend/Obd360.Api/appsettings.Development.json` და მიუთითე `DefaultConnection`.
ბაზა `GeorgianCarScannerWeb` და ცხრილები **თავისით შეიქმნება** პირველ გაშვებაზე (მიგრაციები +
DTC კატალოგის ჩატვირთვა).

LocalDB-ით:

```json
"DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=GeorgianCarScannerWeb;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True"
```

> პაროლის შემცველი connection string **არ დააკომიტო** — გამოიყენე `dotnet user-secrets`:
> `dotnet user-secrets set "ConnectionStrings:DefaultConnection" "<შენი connection string>"`

### 2. Backend

```powershell
cd backend/Obd360.Api
dotnet run
```

API: http://localhost:5269 · Swagger: http://localhost:5269/swagger

### 3. Frontend (ახალ ტერმინალში)

```powershell
cd frontend
npm install
npm start
```

საიტი: http://localhost:4200 — ჯერ **Register** (პაროლში ერთი სპეცსიმბოლო მაინც უნდა იყოს), შემდეგ **Login**.

### 4. n8n და AI (არასავალდებულო)

```powershell
n8n\start-n8n.cmd
```

გახსენი http://localhost:5678, შემოიტანე და **ჩართე (Active)** workflow-ები საქაღალდიდან `n8n/`,
და მიუთითე Gemini credential. დეტალები: [`n8n/README.md`](n8n/README.md).
n8n-ის გარეშე ყველაფერი მუშაობს, გარდა AI გვერდისა.

### ყველაფრის ერთად გაშვება (Windows)

`START-DEMO.cmd` — ააქტიურებს API-ს და ფრონტს; გასაჩერებლად `STOP-ALL.cmd`.

---

## მონაცემთა ბაზა

**21 ცხრილი · 19 FK · 21 ინდექსი.** მთავარი ჯაჭვი:

```
მომხმარებელი ─1:N─► მანქანა ─1:N─► სკანირების სესია ─1:N─► DTC კოდები / Live მონაცემები
```

- 1:1 კავშირები: მომხმარებელი ↔ პარამეტრები, მანქანა ↔ ადაპტერი.
- მანქანის წაშლისას დაკავშირებული სკანირებები, შეხსენებები და ანგარიშები იშლება (cascade).
- ბაზა იქმნება **EF Core მიგრაციებით** (Code First): `InitialCreate`, `ExpandDtcCatalog`.

| რა | სად |
|---|---|
| მოდელები | `backend/Obd360.Core/Entities/` |
| DbContext (კავშირები, ინდექსები) | `backend/Obd360.Infrastructure/Data/ApplicationDbContext.cs` |
| მიგრაციები | `backend/Obd360.Infrastructure/Migrations/` |
| სრული SQL სქემა და საწყისი მონაცემები | `database/schema.sql`, `database/seed.sql` |

## API

8 კონტროლერი, 32 endpoint, ყველა `api/v1/...` ქვეშ. სრული სია და გამოსაცდელი ფორმა — **Swagger**
(`/swagger`). ჯგუფები: `auth`, `vehicles`, `scans`, `reminders`, `dtc-catalog`, `preferences`, `ai`, `admin`.

Swagger-ში JWT-ის გამოსაყენებლად: `auth/login` → შედეგის `accessToken` → **Authorize** (Bearer-ის გარეშე).

## ტესტები

```powershell
cd backend  ; dotnet test                      # xUnit — 29 ტესტი
cd frontend ; npm test -- --watch=false        # Vitest — 47 ტესტი
```

## პრობლემების მოგვარება

| პრობლემა | გამოსავალი |
|---|---|
| Swagger / საიტი `ERR_CONNECTION_REFUSED` | API არ მუშაობს — გაუშვი `dotnet run` (ან `START-DEMO.cmd`) |
| რეგისტრაციაზე `400` | პაროლს სჭირდება დიდი/პატარა ასო, ციფრი და სპეცსიმბოლო |
| API ვერ უკავშირდება SQL Server-ს | შეამოწმე `DefaultConnection`; სერვერზე ჩართული უნდა იყოს TCP (SQL Server Configuration Manager) |
| AI გვერდზე „n8n მიუწვდომელია“ | ჩართე `n8n\start-n8n.cmd` და გახადე workflow-ები Active |
| AI-ს ანგარიშში „ჯერ სკანირება არ არის“ | ჯერ გააკეთე სკანირება DTC Scanner-ზე |

## დოკუმენტაცია

| ფაილი | რა არის |
|---|---|
| [`docs/TECHNICAL-REFERENCE.md`](docs/TECHNICAL-REFERENCE.md) | დეტალური ტექნიკური მასალა: კრიტერიუმების რუკა, ავტორიზაცია, Swagger დემო, logging, state management, Docker |
| [`docs/STUDY.md`](docs/STUDY.md) | დაცვისთვის მოსამზადებელი: კოდის რუკა, კითხვა-პასუხი |
| [`docs/report/OBD360-Web-Documentation.pdf`](docs/report/OBD360-Web-Documentation.pdf) | სრული აკადემიური დოკუმენტაცია |
| [`docs/c4/OBD360 C4.pdf`](<docs/c4/OBD360 C4.pdf>) | C4 დიაგრამები |
| [`docs/პრეზენტაცია/`](docs/პრეზენტაცია/) | პრეზენტაცია (`.pptx`) |
| [`n8n/README.md`](n8n/README.md) | n8n და AI ინტეგრაცია |

## პროექტის სტრუქტურა

```
backend/
  Obd360.Api/             controllers, DTOs, n8n ინტეგრაცია
  Obd360.Core/            მოდელები (entities)
  Obd360.Infrastructure/  EF Core, მიგრაციები, Identity
  Obd360.Tests/           xUnit ტესტები
frontend/src/app/
  core/                   services, guards, interceptors
  features/               15 გვერდი (dashboard, garage, ...)
  layout/                 გვერდითი მენიუ, topbar
database/                 schema.sql, seed.sql
n8n/                      workflow-ები და გაშვების სკრიპტები
docs/                     C4, დოკუმენტაცია, პრეზენტაცია
```

## შეზღუდვები

- შეხსენებები გარბენით ჯერ არ მუშაობს (მხოლოდ თარიღით).
- Email confirmation და CI/CD ჯერ არ არის.
- ტესტების უმეტესობა in-memory ბაზაზეა; სრული ინტეგრაციული ტესტები SQL Server-ზე ჯერ არ არის.
- Login-ზე არ არის lockout/rate limiting; Swagger ჩართულია ყველა გარემოში.
- Production deployment (DigitalOcean) მომზადებულია, მაგრამ რეალურად ჯერ არ გაშვებულა.

## ავტორი

ზურაბ ლაზაშვილი — OBD360 Web, 2026.
