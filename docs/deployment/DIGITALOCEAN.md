# DigitalOcean — Droplet-ზე გაშვება

> **სტატუსი:** კონფიგურაცია მზადაა, მაგრამ ეს გარემო DigitalOcean-ზე **ჯერ არ არის გაშვებული** — საჭიროა DigitalOcean ანგარიში, Droplet და დომენი.

## 1. რა დაგჭირდება

- DigitalOcean ანგარიში.
- **Ubuntu 24.04 Droplet**, მინიმუმ **4 GB RAM / 2 vCPU** (SQL Server + API + web).
- დომენი ან ქვედომენი, მაგ. `obd360.example.com`.
- GitHub-ზე წვდომა private repo-ზე (Deploy Key ან PAT).
- სურვილისამებრ: SMTP App Password, Telegram bot/chat, Gemini key (n8n).

## 2. DNS

DigitalOcean → **Networking → Domains**:

```text
A  obd360.example.com  ->  <Droplet public IPv4>
```

## 3. Droplet-ის მომზადება

SSH-ით შედი Droplet-ში და დააყენე Docker:

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
docker compose version
```

> `docker compose` უნდა იყოს **2.24+**, რადგან `docker-compose.prod.yml` იყენებს `!reset`-ს.

## 4. პროექტის ჩამოტვირთვა

```bash
sudo mkdir -p /opt/obd360
sudo chown $USER:$USER /opt/obd360
git clone https://github.com/Laziii54/OBD360-Web.git /opt/obd360
cd /opt/obd360
```

თუ repo private-ია, გამოიყენე **Deploy Key** ან GitHub PAT; ტოკენი `.env`-ში არ ჩაწერო.

## 5. `.env` ფაილი

```bash
cp .env.example .env
nano .env
```

შეავსე:

```dotenv
SQL_PASSWORD=<ძლიერი-პაროლი-მინიმუმ-8-სიმბოლო-დიდი-პატარა-ციფრი>
JWT_SIGNING_KEY=<მინიმუმ-32-სიმბოლო-რენდომ-გასაღები>
PUBLIC_ORIGIN=https://obd360.example.com

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=<gmail-app-password>
SMTP_FROM_ADDRESS=your@gmail.com

OBD360_TELEGRAM_BOT_TOKEN=
OBD360_TELEGRAM_CHAT_ID=
```

> `.env` **არასოდეს** არ უნდა მოხვდეს Git-ში.

## 6. გაშვება

```bash
cd /opt/obd360
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

შეამოწმე:

```bash
docker compose ps
docker compose logs -f api
curl -I http://127.0.0.1:4200
```

- API ავტომატურად უშვებს მიგრაციებს და DTC კატალოგს (29 → 13 629).
- SQL Server, API და n8n გარედან **დახურულია**.
- web მხოლოდ `127.0.0.1:4200`-ზეა მიბმული.

## 7. Host Nginx + HTTPS

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo nano /etc/nginx/sites-available/obd360
```

```nginx
server {
    listen 80;
    server_name obd360.example.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:4200;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/obd360 /etc/nginx/sites-enabled/obd360
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d obd360.example.com
```

Certbot ავტომატურად დაამატებს HTTPS-ს და გადაამისამართებს HTTP-ს.

## 8. რას უნდა გახსნა firewall-ზე

DigitalOcean Cloud Firewall:

| პორტი | დანიშნულება |
|---|---|
| 22 | SSH |
| 80 | HTTP (certbot redirect) |
| 443 | HTTPS |

**არ** გახსნა: `1433` (SQL), `5269` (API), `5678` (n8n).

## 9. შემოწმება

```text
https://obd360.example.com/            -> Angular
https://obd360.example.com/swagger     -> Swagger UI
https://obd360.example.com/api/v1/...  -> API
https://obd360.example.com/health/live -> {"status":"live"}
```

Swagger-ში login → Authorize → `GET /api/v1/vehicles`.

## 10. განახლება

```bash
cd /opt/obd360
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 11. შეზღუდვები

- DigitalOcean-ს **managed SQL Server არ აქვს**; ამიტომ SQL Server Docker კონტეინერშია.
- 4 GB RAM მინიმალურია; 8 GB უფრო სტაბილურია.
- Web Bluetooth მუშაობს მხოლოდ **HTTPS**-ზე (ან localhost).
- n8n/Gemini გარეშე AI ასისტენტი არ იმუშავებს, მაგრამ დანარჩენი აპლიკაცია მუშაობს.
- ბექაფი: DigitalOcean Droplet Snapshot ან `sql-data` volume-ის რეგულარული backup.

## 12. რა არის საჭირო ჩემგან, რომ რეალურად გავუშვა

1. Droplet-ის IP ან SSH წვდომა.
2. დომენი.
3. GitHub Deploy Key/PAT (თუ repo private).
4. SMTP/აუცილებელი საიდუმლოებები — **ჩატში არ გამოგზავნო**; `.env`-ში ჩაწერე Droplet-ზე.

> ტოკენები/პაროლები ჩატში არ უნდა გაიგზავნოს. გამოიყენე DigitalOcean Console ან SSH.
