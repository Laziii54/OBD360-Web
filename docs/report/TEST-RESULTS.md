# ტესტების შედეგები

თარიღი: **2026-11-21**

## Backend — xUnit

```powershell
cd backend
dotnet test
```

```text
Passed! - Failed: 0, Passed: 29, Skipped: 0, Total: 29
Duration: 1 s
```

## Frontend — Vitest (Angular)

```powershell
cd frontend
npm test -- --watch=false
```

```text
Test Files  18 passed (18)
Tests       19 passed (19)
Duration    15.07s
```

## ჯამი

| დონე | რაოდენობა | სტატუსი |
|---|---:|---|
| Backend | 29 | ✅ |
| Frontend | 19 | ✅ |
| **სულ** | **48** | ✅ |

## რას ფარავს

- backend: ავტორიზაცია, vehicles, reminders, scans, DTC, AI, n8n parser/prompt.
- frontend: OBD decoder, auth service, guards, ძირითადი კომპონენტები.

## Coverage

Coverage პროცენტი ცალკე არ არის გაზომილი. თუ ლექტორს კონკრეტული % სჭირდება:

```powershell
cd backend
dotnet test --collect:"XPlat Code Coverage"

cd frontend
npm test -- --watch=false --coverage
```
