# OBD360 — დაცვის მზადყოფნის ჩეკლისტი

> ეს არის პასუხი კითხვაზე: **„სად ვანახო ეს და როგორ ავხსნა?“**  
> სტატუსი: ✅ მზადაა · ⚠️ ნაწილობრივ · ❌ ჯერ არ არის

---

## 0. 20-წუთიანი დემო — სწორი თანმიმდევრობა

1. **README** — გახსენი და აჩვენე გაშვების ინსტრუქცია (2 წთ).
2. **Swagger** — `http://localhost:5269/swagger` (2 წთ).
3. **Login + JWT** — login, token, Authorize (3 წთ).
4. **Frontend** — dashboard, garage, reminders, mobile menu (5 წთ).
5. **OBD კოდი** — `obd-bluetooth.service.ts` + `dtc-scan.service.ts` (3 წთ).
6. **DB** — `schema.sql`, migrations, 15 მოდელი (3 წთ).
7. **ტესტები + ლოგები** — ტერმინალში (2 წთ).
8. **დოკუმენტაცია/სლაიდები** — 1 წთ.

---

## 1. Backend

### 1.1 ბაზის სტრუქტურა და დიზაინი — ✅

| რას აჩვენებ | სად |
|---|---|
| სრული SQL სქემა (21 ცხრილი) | `database/schema.sql` |
| საწყისი მონაცემები | `database/seed.sql` |
| EF Core კონფიგურაცია | `backend/Obd360.Infrastructure/Data/ApplicationDbContext.cs` |
| მოდელების სქემა | `docs/report/assets/data-model.png` |
| ახსნა დოკუმენტში | `docs/report/OBD360-Web-Documentation.pdf`, თავი 5 |

**რა უნდა თქვა:**  
„ბაზა SQL Server-ზეა. 15 ბიზნეს მოდელი 21 ფიზიკურ ცხრილად იშლება Identity-ის ცხრილების ჩათვლით. სქემა აღწერილია `schema.sql`-ში, ხოლო EF Core-ის კონფიგურაცია — `ApplicationDbContext.cs`-ში.“

### 1.2 მიგრაციები — ✅

| რას აჩვენებ | სად |
|---|---|
| მიგრაციები | `backend/Obd360.Infrastructure/Migrations/` |
| InitialCreate | `20261028152609_InitialCreate.cs` |
| DTC გაფართოება | `20261106120000_ExpandDtcCatalog.cs` |
| ავტომატური გამოყენება | `Program.cs:125` — `db.Database.MigrateAsync()` |

**რა უნდა თქვა:**  
„API-ის გაშვებისას Development გარემოში ავტომატურად გამოიყენება მიგრაციები. ცალკე `dotnet ef database update` არ გვჭირდება.“

### 1.3 მოდელები — ✅

| მოდელი | ფაილი |
|---|---|
| ApplicationUser / ApplicationRole | `backend/Obd360.Infrastructure/Identity/` |
| Vehicle | `Obd360.Core/Entities/Vehicle.cs` |
| Adapter | `Obd360.Core/Entities/Adapter.cs` |
| ScanSession, LiveReading, DtcRecord, DtcCatalogEntry | `Obd360.Core/Entities/ScanSession.cs` |
| MaintenanceReminder | `Obd360.Core/Entities/MaintenanceReminder.cs` |
| AiConversation, AiMessage | `Obd360.Core/Entities/AiConversation.cs` |
| Report, NotificationLog | `Obd360.Core/Entities/Report.cs` |
| UserPreference, RefreshSession | `Obd360.Core/Entities/UserPreference.cs` |

> მნიშვნელოვანია: რამდენიმე კლასი ერთ ფაილშია დაჯგუფებული. მაგალითად, `ScanSession.cs` შეიცავს `ScanSession`, `LiveReading`, `DtcRecord`, `DtcCatalogEntry`-ს.

### 1.4 API endpoint-ები — ✅

| რას აჩვენებ | სად |
|---|---|
| კონტროლერები | `backend/Obd360.Api/Controllers/` |
| Swagger | `http://localhost:5269/swagger` |
| სრული ცხრილი | `docs/CODE-GUIDE.md` + დოკუმენტაციის დანართი A |

**32 endpoint:** Auth 7, Preferences 2, Vehicles 5, Reminders 5, Scans 2, DTC 2, AI 4, Admin 5.

### 1.5 REST vs MVC — ✅ ეს არის REST API, არა server-side MVC

**როგორ დაამტკიცო:**

1. `Program.cs:18` — `builder.Services.AddControllers();`  
   **არა** `AddControllersWithViews()`.
2. პროექტში **არ არის** `Views/` საქაღალდე და `.cshtml` ფაილები.
3. კონტროლერებს აქვთ `[ApiController]` და აბრუნებენ `ActionResult<T>` / JSON-ს.
4. UI არის ცალკე Angular აპლიკაცია; API მხოლოდ JSON-ს აბრუნებს.
5. DevTools → Network → response არის JSON.

**რა უნდა თქვა:**  
„ეს არის REST API ASP.NET Core-ზე. MVC-ის Controllers გამოიყენება როგორც routing, მაგრამ არ არის server-rendered MVC — არ არის Views, არის JSON და ცალკე Angular SPA. ამიტომ ვამბობ, რომ პროექტი REST API + SPA არქიტექტურაა.“

### 1.6 Swagger — ✅

- გაშვება: `cd backend/Obd360.Api` → `dotnet run`
- URL: `http://localhost:5269/swagger`
- დააჭირე **Authorize** → ჩასვი access token (Bearer-ის გარეშე).
- Swagger აჩვენებს ყველა კონტროლერს და endpoint-ს.
- ეკრანის სურათი: `docs/report/assets/swagger.png`.

### 1.7 ავტორიზაცია, JWT, პაროლის განახლება — ✅

| რას აჩვენებ | სად |
|---|---|
| Login / Register | `AuthController.cs:53`, `:95` |
| JWT შექმნა | `TokenService.cs:20` |
| JWT კონფიგურაცია | `Program.cs:93` |
| Refresh token | `AuthController.cs:110`; `RefreshSession` |
| პაროლის შეცვლა | `AuthController.cs:236` |
| პაროლის აღდგენა | `AuthController.cs:157` და `:204` |
| 6-ციფრიანი კოდი | `PasswordResetCodeService.cs` |
| Frontend token | `auth.ts:43` / `auth-interceptor.ts:8` |
| Refresh 401-ზე | `auth-interceptor.ts:22` |

**დემო Swagger-ში:**
1. `POST /api/v1/auth/login` → copy `accessToken`.
2. Authorize → paste token.
3. `GET /api/v1/vehicles` → 200.
4. `POST /api/v1/auth/change-password` → 204.
5. `POST /api/v1/auth/forgot-password` → email code (Development-ში `devCode`).
6. `POST /api/v1/auth/reset-password` → 204.

---

## 2. Frontend

### 2.1 UI ფუნქციონალობა — ✅

| გვერდი | URL | რას აჩვენებ |
|---|---|---|
| Login | `/login` | ავტორიზაცია |
| Register | `/register` | რეგისტრაცია |
| Dashboard | `/app/dashboard` | Live Data, DTC, აქტივობა |
| Garage | `/app/garage` | მანქანების CRUD |
| Reminders | `/app/reminders` | ვადები, Overdue |
| Bluetooth | `/app/bluetooth` | ადაპტერი |
| DTC Scanner | `/app/dtc-scanner` | 03/07/0A |
| Scan History | `/app/scan-history` | ისტორია |
| AI Assistant | `/app/ai-assistant` | კითხვა |
| Admin | `/app/admin` | users/roles/scans |

**დემო 5 წუთში:**
1. Login.
2. Garage → დაამატე მანქანა.
3. Dashboard → ნახე ბარათები.
4. Reminders → დაამატე შეხსენება.
5. გააპატარავე ეკრანი → burger menu.
6. Admin → users/roles.

### 2.2 State management — ✅

- **State management** ნიშნავს: სად ინახება ეკრანის მონაცემები და როგორ ახლდება.
- პროექტში არ არის NgRx; გამოყენებულია **Angular Signals**.
- `Auth` — token/user.
- `UserSettings` — theme/units/refresh.
- `Admin` — users/scans/filter.
- `Garage`, `Reminders`, `ScanHistory` — local signals.

**სად ვანახო:**
- `frontend/src/app/core/services/auth.ts:29` — `signal`.
- `frontend/src/app/core/services/user-settings.service.ts` — signals + `effect`.
- `frontend/src/app/features/admin/admin.ts` — `signal`/`computed`.
- `frontend/src/app/layout/main-layout/main-layout.ts` — `sidebarOpen`.

### 2.3 Signals — ✅

მაგალითი (`admin.ts`):

```ts
readonly userSearch = signal('');
readonly filteredUsers = computed(() => {
  const term = this.userSearch().trim().toLowerCase();
  return this.users().filter(user => user.email.includes(term));
});
```

**რა უნდა თქვა:**  
„Signal არის ცოცხალი ცვლადი. როცა `userSearch` იცვლება, `computed` ავტომატურად ითვლის ახალ სიას და ეკრანი თავისით ახლდება — manual change detection არ გვჭირდება.“

---

## 3. ტესტები — ✅ 29 + 19

| ტესტი | რაოდენობა | ბრძანება |
|---|---:|---|
| Backend | 29 | `cd backend` → `dotnet test` |
| Frontend | 19 | `cd frontend` → `npm test -- --watch=false` |
| სულ | 48 | — |

**შედეგი (2026-11-21):**
```text
Passed! - Failed: 0, Passed: 29, Skipped: 0, Total: 29
Test Files 18 passed (18)
Tests 19 passed (19)
```

> Coverage პროცენტი არ არის გაზომილი; თუ ლექტორს კონკრეტული % სჭირდება, ცალკე უნდა გავუშვათ `--collect:"XPlat Code Coverage"`.

---

## 4. Error handling და logging — ✅

### Error handling — რა არის

- ვალიდაცია → `ValidationProblemDetails` (400).
- არაავტორიზებული → 401.
- აკრძალული → 403.
- ვერ მოიძებნა → 404.
- unhandled exception → გლობალური handler → 500 JSON + ლოგი (`Program.cs`).
- Frontend აჩვენებს შეცდომის ტექსტს.

**სად ვანახო:**
- `Program.cs` — `UseExceptionHandler` (500).
- `AuthController.cs` — login/register/reset errors.
- `AdminController.cs` — self-delete/last-admin 400.
- `auth-interceptor.ts` — 401 refresh.
- `forgot-password.ts` — backend validation error.

### Logging — ✅

- HTTP logging: `Program.cs` (`UseHttpLogging`).
- Auth ლოგები: `AuthController.cs`.
- Reminder ლოგები: `ReminderNotificationService.cs`.
- unhandled exception ლოგი: `Program.cs`.
- ნახვა: API-ის კონსოლში.

```text
Request: GET /api/v1/admin/overview
Response: StatusCode: 200
Duration: 42.7ms
```

---

## 5. README, პრეზენტაცია, დოკუმენტაცია — ✅

| რას აჩვენებ | სად |
|---|---|
| README + გაშვება | `README.md` |
| სრული დოკუმენტაცია | `docs/report/OBD360-Web-Documentation.pdf` |
| დაცვის გზამკვლევი | `docs/report/OBD360-Defense-Guide.pdf` |
| კოდის რუკა | `docs/CODE-GUIDE.md` |
| პრეზენტაცია | `docs/slides/OBD360-Web-Presentation.pptx` |
| C4 | `docs/c4/OBD360 C4.pdf` |

---

## 6. მონაცემთა მოდელები სრულად — ✅

- **15 მოდელი**, **21 ცხრილი**.
- სრული სვეტები: `database/schema.sql`.
- მოდელების კოდი: `backend/Obd360.Core/Entities/`.
- ახსნა: დოკუმენტაციის თავი 5.
- ვიზუალი: `docs/report/assets/data-model.png`.

---

## 7. DigitalOcean — ⚠️ კონფიგურაცია მზადაა, deployment ჯერ არა

**მიმდინარე სტატუსი:** აპლიკაცია მუშაობს ლოკალურად (`localhost`), ხოლო production Docker/Nginx კონფიგურაცია მომზადებულია, მაგრამ **DigitalOcean-ზე ჯერ არ არის გაშვებული**.

**მზადაა:**
- `docker-compose.prod.yml` — SQL/API/n8n პორტები დახურულია, web მხოლოდ `127.0.0.1:4200`.
- `frontend/nginx.conf` — `/api` და `/swagger` proxy.
- `frontend` ახლა იძახებს ფარდობით `/api/v1`-ს (არა `localhost:5269`).
- API ავტომატურად უშვებს მიგრაციებს Production-შიც.
- გიდი: `docs/deployment/DIGITALOCEAN.md`.

**რატომ ჯერ არა:** საჭიროა DigitalOcean ანგარიში, Droplet, დომენი და SSH/Deploy Key. ტოკენები ჩატში არ უნდა გაიგზავნოს.

**რა უნდა გაკეთდეს:** Droplet 4GB+, Docker Compose, host Nginx + Certbot, DNS. ნაბიჯები გიდშია.

---

## 8. „Lvl2 ან Lvl3 პროექტის აღწერა 4 ფაილში“ — გასარკვევია

ეს შეიძლება ნიშნავდეს ორ რამეს:

1. **C4 Level 2 / Level 3** — გვაქვს Container და Component დიაგრამები ✅.
2. **კურსის პროექტის დონე (Level 2/3)** — აქ საჭიროა ლექტორის ზუსტი მოთხოვნა: რომელი 4 ფაილი?

**თუ პირველია:** უკვე გვაქვს.  
**თუ მეორეა:** მაჩვენე მოთხოვნა — 4 ფაილს იმ ფორმატში მოვამზადებ.

---

## 9. სწრაფი ბრძანებები დაცვის წინ

```powershell
# API
cd "C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\backend\Obd360.Api"
dotnet run

# Frontend (ახალი ტერმინალი)
cd "C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\frontend"
npm start

# Tests
cd "C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\backend"
dotnet test
cd "C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\frontend"
npm test -- --watch=false
```

- Frontend: `http://localhost:4200`
- Swagger: `http://localhost:5269/swagger`
- API health: `http://localhost:5269/health/live`
