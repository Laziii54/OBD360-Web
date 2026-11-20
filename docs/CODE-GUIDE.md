# OBD360 — კოდის რუკა და ლექტორის კითხვები

> ეს გზამკვლევი კოდს **არ ცვლის**. ის მხოლოდ გიჩვენებს, სად არის რა და როგორ უპასუხო ლექტორს მარტივი ენით.

---

## 1. 30-წამიანი პასუხი: „მითხარი, რას აკეთებს პროექტი“

OBD360 Web არის ვებ-აპლიკაცია, რომელიც:

1. ბრაუზერიდან უკავშირდება OBD-II ადაპტერს **Web Bluetooth**-ით.
2. ადაპტერის მეშვეობით კითხულობს მანქანის **ECU**-დან DTC კოდებს და Live Data-ს.
3. აგზავნის შედეგებს **ASP.NET Core API**-ში.
4. ინახავს მონაცემებს **SQL Server**-ში.
5. აჩვენებს კოდების ახსნას ქართულად, ინახავს ისტორიას და უგზავნის შეხსენებებს.
6. AI ასისტენტი **n8n + Gemini**-ით ეხმარება მომხმარებელს კოდების გაგებაში.

**მოკლე ფორმულა:**

```text
Angular (ეკრანი) → ASP.NET API (ლოგიკა) → SQL Server (მონაცემები)
        ↑
OBD-II ადაპტერი → ECU (მანქანა)
```

---

## 2. სად არის რა — 10-წამიანი ცხრილი

| რას ეძებ ლექტორი | სად არის | რა უნდა თქვა |
|---|---|---|
| აპლიკაციის დაწყება (Angular) | `frontend/src/main.ts`, `frontend/src/app/app.config.ts` | „აქ იწყება Angular და უკავშირდება routing-სა და HttpClient-ს.“ |
| მარშრუტები | `frontend/src/app/app.routes.ts` | „აქ განსაზღვრულია ყველა გვერდი და რომელი გვერდია დაცული.“ |
| Login-ის გვერდი | `frontend/src/app/features/auth/login/login.ts` + `login.html` | „ეს არის login-ის ეკრანი; იძახებს Auth სერვისს.“ |
| Login-ის API | `backend/Obd360.Api/Controllers/AuthController.cs:95` | „Login მეთოდი ამოწმებს პაროლს და აბრუნებს token-ებს.“ |
| რეგისტრაცია | `frontend/.../auth/register/register.ts`, `AuthController.cs:53` | „Register ქმნის მომხმარებელს.“ |
| პაროლის აღდგენა | `frontend/.../auth/forgot-password/forgot-password.ts`, `AuthController.cs:157` | „6-ციფრიანი კოდი მიდის ელფოსტაზე.“ |
| JWT token-ის შექმნა | `backend/Obd360.Infrastructure/Services/TokenService.cs:20` | „აქ იქმნება ხელმოწერილი JWT.“ |
| Token-ის დამატება request-ზე | `frontend/src/app/core/interceptors/auth-interceptor.ts:8` | „Interceptor ამატებს Authorization header-ს.“ |
| 401-ის დამუშავება | `auth-interceptor.ts:22` | „401-ისას ცდილობს refresh-ს და request-ს იმეორებს.“ |
| Route guard | `frontend/src/app/core/guards/auth-guard.ts`, `admin-guard.ts` | „Guard ამოწმებს, შეუძლია თუ არა მომხმარებელს გვერდზე შესვლა.“ |
| Sidebar / burger menu | `frontend/src/app/layout/main-layout/main-layout.ts`, `.html`, `.scss` | „მობილურზე 720px-ზე sidebar იხსნება მარცხენა drawer-ად.“ |
| Dashboard | `frontend/src/app/features/dashboard/dashboard/dashboard.ts` | „მთავარი ეკრანი.“ |
| Garage | `frontend/src/app/features/garage/garage.ts`, `backend/.../VehiclesController.cs` | „მანქანების CRUD.“ |
| Reminders | `frontend/.../reminders/reminders.ts`, `backend/.../RemindersController.cs` | „შეხსენებების CRUD.“ |
| Bluetooth | `frontend/.../bluetooth/bluetooth.ts`, `core/services/obd-bluetooth.service.ts:97` | „აქ ხდება ადაპტერთან დაკავშირება.“ |
| Live Data | `frontend/.../live-data/live-data.ts`, `obd-decoder.ts:57` | „PID-ების კითხვა და გაშიფვრა.“ |
| DTC სკანირება | `frontend/.../dtc-scanner/dtc-scanner.ts`, `dtc-scan.service.ts:34` | „03/07/0A კოდების კითხვა.“ |
| DTC პარსერი | `frontend/src/app/core/services/obd-decoder.ts:62` | „hex პასუხის გადაქცევა P0300 ტიპის კოდად.“ |
| DTC კატალოგი | `frontend/.../dtc-catalog/dtc-catalog.ts`, `backend/.../DtcCatalogController.cs` | „13 629 კოდის ძებნა.“ |
| სკანირების ისტორია | `frontend/.../scan-history/scan-history.ts`, `backend/.../ScansController.cs` | „შენახული სკანირებები.“ |
| AI ასისტენტი | `frontend/.../ai-assistant/ai-assistant.ts`, `backend/.../AiController.cs` | „კითხვა მიდის API-ზე და n8n-ში.“ |
| n8n workflow | `n8n/*.workflow.json`, `backend/.../Integrations/N8n/` | „n8n იძახებს Gemini-ს.“ |
| Admin პანელი | `frontend/.../admin/admin.ts`, `backend/.../AdminController.cs` | „users, roles, scans.“ |
| მონაცემთა ბაზა | `backend/Obd360.Infrastructure/Data/ApplicationDbContext.cs` | „EF Core-ის DbContext.“ |
| მოდელები | `backend/Obd360.Core/Entities/` | „15 მოდელი; ზოგიერთი ერთ ფაილშია დაჯგუფებული.“ |
| მიგრაციები | `backend/Obd360.Infrastructure/Migrations/` | „ბაზის სქემის ვერსიები.“ |
| DTC 13 629-ის ჩატვირთვა | `DtcCatalogSeeder.cs`, `Data/dtc-catalog.json.gz` | „პირველ გაშვებაზე იტვირთება.“ |
| JWT კონფიგურაცია | `backend/Obd360.Api/Program.cs:93` | „AddJwtBearer.“ |
| ლოგირება | `Program.cs:154`, `appsettings.json` | „HTTP request logging.“ |
| Swagger | `Program.cs:29`, `/swagger` | „API-ის ინტერაქტიული დოკუმენტაცია.“ |
| ტესტები | `backend/Obd360.Tests/`, `frontend/**/*.spec.ts` | „29 backend + 19 frontend.“ |
| C4 დიაგრამები | `docs/c4/OBD360 C4.pdf` | „Context, Container, Component.“ |
| დოკუმენტაცია | `docs/report/OBD360-Web-Documentation.docx` | „სრული ახსნა.“ |
| პრეზენტაცია | `docs/slides/OBD360-Web-Presentation.pptx` | „18 სლაიდი.“ |

---

## 3. პროექტის ფოლდერები — მარტივად

```text
OBD2 WEB/
├── frontend/                 Angular — ეკრანი
│   └── src/app/
│       ├── core/             სერვისები, guard-ები, interceptor
│       ├── features/         გვერდები (login, garage, admin...)
│       └── layout/           sidebar, header
├── backend/
│   ├── Obd360.Api/           controllers, Program.cs, n8n
│   ├── Obd360.Core/          მოდელები (entities)
│   ├── Obd360.Infrastructure/ ბაზა, Identity, migrations
│   └── Obd360.Tests/         ტესტები
├── database/                 schema.sql, seed.sql
├── n8n/                      workflow-ები
└── docs/                     C4, report, slides
```

**დამახსოვრე 3 წესი:**

1. **ეკრანი** → `frontend/features/`
2. **ლოგიკა** → `backend/Obd360.Api/Controllers/`
3. **მონაცემები** → `backend/Obd360.Core/Entities/` + `Infrastructure/Data/`

---

## 4. „მაჩვენე, სად არის…“ — 5 მზა სცენარი

### სცენარი 1: „მაჩვენე login“

1. გახსენი `frontend/src/app/features/auth/login/login.ts`.
2. თქვი: „ეს არის login-ის კომპონენტი; ფორმა იძახებს `Auth.login()`-ს.“
3. გახსენი `frontend/src/app/core/services/auth.ts:43`.
4. თქვი: „აქ იგზავნება POST `/auth/login`.“
5. გახსენი `backend/Obd360.Api/Controllers/AuthController.cs:95`.
6. თქვი: „აქ მოწმდება პაროლი და გაიცემა JWT + refresh cookie.“

### სცენარი 2: „მაჩვენე, სად ინახება მანქანები“

1. `frontend/src/app/features/garage/garage.ts` — ეკრანი.
2. `frontend/src/app/core/services/vehicles.service.ts` — API გამოძახება.
3. `backend/Obd360.Api/Controllers/VehiclesController.cs` — CRUD.
4. `backend/Obd360.Core/Entities/Vehicle.cs` — მოდელი.
5. `ApplicationDbContext.cs` — ცხრილი `Vehicles`.

### სცენარი 3: „მაჩვენე, როგორ კითხულობს მანქანას“

1. `frontend/.../bluetooth/bluetooth.ts` — ღილაკი.
2. `core/services/obd-bluetooth.service.ts:97` — `connect()`.
3. `:192` — `initializeAdapter()`; აქ არის `ATZ`, `ATE0`, `ATSP0`, `0100`.
4. `dtc-scan.service.ts:34` — `scan()`; აქ `03`, `07`, `0A`.
5. `obd-decoder.ts:68` — `parseDtcResponse()`.

### სცენარი 4: „მაჩვენე, სად არის 13 629 კოდი“

1. `backend/Obd360.Api/Data/dtc-catalog.json.gz` — მონაცემები.
2. `DtcCatalogSeeder.cs:12` — ჩატვირთვა.
3. `Program.cs:127` — გაშვებისას იძახება.
4. `DtcCatalogController.cs` — API.
5. `frontend/.../dtc-catalog/dtc-catalog.ts` — ეკრანი.

### სცენარი 5: „მაჩვენე AI“

1. `frontend/.../ai-assistant/ai-assistant.ts` — კითხვის ფორმა.
2. `backend/.../AiController.cs:96` — `/ai/ask`.
3. `Integrations/N8n/N8nClient.cs` — n8n-თან კავშირი.
4. `Integrations/N8n/ScanPromptBuilder.cs` — prompt-ის აწყობა.
5. `n8n/obd360-assistant-ask.workflow.json` — workflow.

---

## 5. 30 კითხვა-პასუხი

### არქიტექტურა

**1. რა ტექნოლოგიები გამოიყენე?**  
Angular 22, ASP.NET Core 10, EF Core, SQL Server, JWT, n8n, Gemini.

**2. რატომ გაყავი frontend და backend?**  
რომ ეკრანი და ლოგიკა დამოუკიდებლად შეიცვალოს; API-ს სხვა კლიენტიც შეიძლება დაუკავშირდეს.

**3. რა არის REST API?**  
HTTP მისამართების ნაკრები, სადაც ერთი მისამართი ერთ მოქმედებას აკეთებს (`GET`, `POST`, `PUT`, `DELETE`).

**4. რატომ არის 32 endpoint?**  
7 auth + 2 preferences + 5 vehicles + 5 reminders + 2 scans + 2 DTC + 4 AI + 5 admin = 32.

### ავტორიზაცია

**5. სად ინახება access token?**  
`sessionStorage`-ში და Angular `signal`-ში — `auth.ts:109`.

**6. სად ინახება refresh token?**  
HttpOnly cookie-ში; ბაზაში მხოლოდ მისი hash — `RefreshSessions`.

**7. რა ხდება, როცა token ვადაგასულია?**  
Interceptor იღებს 401-ს, აკეთებს refresh-ს და request-ს იმეორებს — `auth-interceptor.ts:22`.

**8. რატომ არის access token მოკლე?**  
15 წუთი — მოპარული token-ის რისკი მცირდება.

**9. როგორ იცის სისტემამ, ვინ არის Admin?**  
JWT-ში role claim + `[Authorize(Roles="Admin")]` + `adminGuard`.

**10. სად არის პაროლის აღდგენა?**  
`AuthController.cs:157` (forgot), `:204` (reset), `PasswordResetCodeService.cs`, `SmtpEmailSender.cs`.

### მონაცემები

**11. სად არის ბაზა?**  
`ApplicationDbContext.cs`; connection string `appsettings.Development.json`.

**12. რამდენი მოდელია?**  
15 მოდელი, 21 ფიზიკური ცხრილი.

**13. სად არის `DtcRecord`?**  
`Obd360.Core/Entities/ScanSession.cs`-ში — `ScanSession`, `LiveReading`, `DtcRecord`, `DtcCatalogEntry` ერთ ფაილშია.

**14. სად ინახება სკანირება?**  
`ScanSessions` + `DtcRecords` + `LiveReadings`.

**15. რატომ იყენებ EF Core-ს?**  
SQL-ის ნაცვლად C# ობიექტებით ვმუშაობ; მიგრაციები სქემას აახლებს.

### OBD-II

**16. რა არის OBD-II?**  
მანქანის დიაგნოსტიკის სტანდარტი; 16-pin პორტი, რომლითაც ECU-ს ვკითხულობთ.

**17. რა არის ECU?**  
მანქანის ელექტრონული მართვის ბლოკი; ინახავს და ამუშავებს DTC-ებს.

**18. რა არის PID?**  
პარამეტრის ID; მაგ. `010C` — ბრუნი, `010D` — სიჩქარე.

**19. რა ბრძანებებს აგზავნის აპლიკაცია?**  
`ATZ`, `ATE0`, `ATL0`, `ATS0`, `ATH0`, `ATSP0`, `0100`, `03`, `07`, `0A`, `0902`, `04`.

**20. რას ნიშნავს `43` პასუხში?**  
`0x40 + 0x03` — რეჟიმ 03-ის პასუხი.

**21. როგორ იშიფრება `01 33`?**  
პირველი nibble → P/C/B/U, დანარჩენი → კოდი; გამოდის `P0133`.

**22. რატომ არის 13 629 კოდი?**  
კატალოგი ფარავს სტანდარტულ და მწარმოებლის კოდებს; იტვირთება `DtcCatalogSeeder`-ით.

### ფუნქციები

**23. სად არის მანქანების CRUD?**  
`VehiclesController.cs` + `garage.ts` + `vehicles.service.ts`.

**24. სად არის შეხსენებები?**  
`RemindersController.cs`, `reminders.ts`, `ReminderNotificationService.cs`.

**25. სად იგზავნება ელფოსტა?**  
`SmtpEmailSender.cs`; SMTP პარამეტრები user-secrets-ში.

**26. სად არის AI?**  
`AiController.cs` → `N8nClient.cs` → n8n workflow → Gemini.

**27. სად არის ადმინი?**  
`AdminController.cs` + `admin.ts` + `admin.service.ts`.

**28. სად არის რესპონსიული მენიუ?**  
`main-layout.ts` (`sidebarOpen`), `.html` (burger), `.scss` (`@media max-width:720px`).

### ხარისხი

**29. სად არის ტესტები?**  
`backend/Obd360.Tests/` და `frontend/**/*.spec.ts`; 29 + 19.

**30. სად არის Swagger, ლოგები, C4?**  
Swagger — `Program.cs:29`; ლოგები — `Program.cs:154`; C4 — `docs/c4/OBD360 C4.pdf`.

---

## 6. რთული სიტყვები მარტივად

| ტერმინი | მარტივი ახსნა |
|---|---|
| API | „მიმტანი“, რომელიც ეკრანსა და ბაზას შორის დგას |
| DTO | ყუთი, რომლითაც მონაცემები API-სა და ეკრანს შორის გადადის |
| JWT | ხელმოწერილი ბარათი, რომელიც ამბობს „ეს მომხმარებელია“ |
| Refresh token | გრძელვადიანი გასაღები ახალი ბარათის ასაღებად |
| Interceptor | „გამშვები“, რომელიც ყოველ request-ს token-ს ამატებს |
| Guard | „მცველი“, რომელიც გვერდზე შესვლას ამოწმებს |
| Signal | Angular-ის ცოცხალი ცვლადი; იცვლება — ეკრანიც იცვლება |
| EF Core | C#-იდან ბაზასთან მუშაობის ხიდი |
| Migration | ბაზის სქემის „ვერსია“ |
| PID | მანქანის პარამეტრის ID |
| DTC | ხარვეზის კოდი |
| n8n | ავტომატიზაციის პროგრამა, რომელიც AI-ს იძახებს |

---

## 7. 2-წუთიანი პრეზენტაცია (დასაწყისი)

> „პროექტი OBD360 Web არის ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა. მომხმარებელი ბრაუზერიდან უკავშირდება OBD-II ადაპტერს Web Bluetooth-ით. ადაპტერი მანქანის ECU-ს უგზავნის AT და PID ბრძანებებს, ხოლო პასუხს Angular ამუშავებს. DTC კოდები ინახება SQL Server-ში და აჩვენებს ქართულ ახსნას 13 629-კოდიანი კატალოგიდან. ავტორიზაცია JWT-ითაა, AI ასისტენტი — n8n და Gemini-ით. სისტემას აქვს 32 REST endpoint, 15 მოდელი და 48 ტესტი.“

---

## 8. სწავლის 3-დღიანი გეგმა

### დღე 1 — დიდი სურათი
- წაიკითხე ეს გზამკვლევი.
- დახაზე 3 ყუთი: Angular → API → SQL.
- იპოვე 5 ფაილი: `app.routes.ts`, `AuthController.cs`, `ApplicationDbContext.cs`, `obd-bluetooth.service.ts`, `dtc-scan.service.ts`.

### დღე 2 — ერთი ფუნქცია ბოლომდე
- აირჩიე „login“ ან „scan“.
- გაიარე გზა: ეკრანი → service → API → controller → ბაზა.
- ყოველ ფაილზე დაწერე 1 წინადადება: „ეს აკეთებს…“.

### დღე 3 — კითხვები
- გამოიყენე 30 კითხვა-პასუხი.
- ითამაშე ლექტორის როლი: სთხოვე საკუთარ თავს „მაჩვენე…“.
- გახსენი `docs/report/OBD360-Web-Documentation.pdf` და გადახედე შესაბამის თავს.

---

## 9. ოქროს წესი პასუხისთვის

როცა ლექტორი კითხულობს „სად არის ეს?“, უპასუხე 4 ნაბიჯით:

1. **ეკრანი** — რომელი გვერდია.
2. **ფაილი** — ზუსტი გზა.
3. **მეთოდი** — რომელი ფუნქცია.
4. **მონაცემი** — რომელ ცხრილში ინახება.

მაგალითი:

> „მანქანების დამატება ეკრანზე იწყება `garage.ts`-ში, იძახებს `vehicles.service.ts`-ს, მიდის `VehiclesController.Create`-ში და ინახება `Vehicles` ცხრილში.“
