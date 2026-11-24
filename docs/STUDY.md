# OBD360 — სწავლის ფურცელი

> ერთი გვერდი დაცვისთვის. დეტალები: `README.md` (ტექნიკური) და
> `docs/report/OBD360-Web-Documentation.pdf` (36 გვერდი).

## 1. ერთი წინადადებით

OBD360 არის ვებ-პლატფორმა, რომელიც ბრაუზერიდან უერთდება მანქანის OBD-II ადაპტერს,
კითხულობს ცოცხალ მონაცემებსა და შეცდომის კოდებს, ხსნის მათ ქართულად (13 629 კოდი + AI)
და ინახავს ისტორიას მომხმარებლის ანგარიშზე.

## 2. სად არის რა

| რას ეძებ | სად |
|---|---|
| მოდელები (15) | `backend/Obd360.Core/Entities/`, `backend/Obd360.Infrastructure/Identity/` |
| ბაზის კონფიგურაცია | `backend/Obd360.Infrastructure/Data/ApplicationDbContext.cs` |
| მიგრაციები | `backend/Obd360.Infrastructure/Migrations/` |
| SQL სკრიპტები | `database/schema.sql`, `database/seed.sql` |
| ენდპოინტები (32) | `backend/Obd360.Api/Controllers/` |
| ავტორიზაცია | `Controllers/AuthController.cs`, `Infrastructure/Services/TokenService.cs`, `Program.cs:88` |
| პაროლის აღდგენა | `Controllers/AuthController.cs:157, :204`, `Services/PasswordResetCodeService.cs` |
| ეკრანები (Angular) | `frontend/src/app/features/`, მარშრუტები — `src/app/app.routes.ts` |
| State (Signals) | `core/services/auth.ts`, `features/admin/admin.ts:32` |
| ტესტები | `backend/Obd360.Tests/`, `frontend/src/app/**/*.spec.ts` |

## 3. დემო — 6 ნაბიჯი

1. **README** — გახსენი და აჩვენე გაშვების ინსტრუქცია.
2. **Swagger** (`http://localhost:5269/swagger`) — login → Authorize → `GET /vehicles` 200.
3. **UI** — Dashboard → Garage (მანქანის დამატება) → Reminders.
4. **მობილური** — ეკრანის დაპატარავება → burger მენიუ.
5. **ბაზა** — `schema.sql` (21 ცხრილი), ER დიაგრამა `docs/report/assets/er-diagram.png`.
6. **ტესტები** — `dotnet test`, `npm test`.

## 4. 10 კითხვა-პასუხი

1. **ეს MVC-ა?** არა — REST API + Angular SPA. `AddControllers()` (`Program.cs:19`), `Views/` არ არსებობს, პასუხი JSON-ია.
2. **როგორ მუშაობს ავტორიზაცია?** JWT 15 წუთი + refresh token 30 დღე (HttpOnly cookie, ბაზაში ჰეშად, rotation-ით).
3. **რატომ Signals და არა NgRx?** 3 გლობალური service + component state — Signals საკმარისია და მარტივია.
4. **სად ინახება მომხმარებლის მონაცემები?** SQL Server, 21 ცხრილი; ყველა query ფილტრდება `UserId`-ით.
5. **რას აკეთებს Web Bluetooth?** ბრაუზერი პირდაპირ უერთდება BLE ადაპტერს, აგზავნის AT/PID ბრძანებებს.
6. **რა არის DTC?** დიაგნოსტიკური კოდი (P/C/B/U); 03 — stored, 07 — pending, 0A — permanent, 04 — clear.
7. **რას აკეთებს AI?** n8n workflow აგზავნის კოდებს Gemini-ს და აბრუნებს ქართულ ახსნას.
8. **როგორ იცავთ სხვის მონაცემებს?** token-ის `sub` claim → `UserId` → ყველა SELECT-ში ფილტრი; ტესტი ამოწმებს.
9. **ტესტები რას ფარავს?** 29 backend (CRUD, იზოლაცია, n8n, prompt) + 47 frontend (decoder, smoke).
10. **რა არის C4?** არქიტექტურის 3 დონე: Context (ვინ იყენებს), Container (SPA/API/DB/n8n), Component (კონტროლერები).

## 5. რიცხვები, რომლებიც უნდა ახსოვდეს

| 15 მოდელი | 21 ცხრილი | 32 endpoint | 8 კონტროლერი |
|---|---|---|---|
| 13 629 DTC | 29 + 47 ტესტი | 16 სლაიდი | C4: 3 დონე |

## 6. სად ვეძებ დეტალებს

- ტექნიკური ახსნა, გაშვება, API ცხრილი → `README.md`
- აკადემიური დოკუმენტი (თეორია, დიზაინი, ტესტირება) → `docs/report/OBD360-Web-Documentation.pdf`
- არქიტექტურა → `docs/c4/OBD360 C4.pdf`
- პრეზენტაცია → `docs/პრეზენტაცია/პრეზენტაცია.pptx`
