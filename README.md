# Grundstücksfinder NRW

Findet Grundstücke in NRW nach Ort, Fläche und Nutzung. Nutzt die LIKA OGC API des Landes NRW.

## Deployment auf Ubuntu (Hetzner)

### 1. Server vorbereiten

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv git
```

### 2. Repository klonen

```bash
cd /opt
sudo git clone https://github.com/jukkler/adressfinder.git
cd adressfinder
```

### 3. Venv erstellen & Dependencies installieren

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Testen (optional)

```bash
streamlit run src/grundstuecksfinder/app.py
```

Die App läuft auf `http://<server-ip>:8501`.

### 5. Systemd-Service einrichten

```bash
sudo tee /etc/systemd/system/grundstuecksfinder.service > /dev/null <<'EOF'
[Unit]
Description=Grundstücksfinder NRW
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/adressfinder
ExecStart=/opt/adressfinder/.venv/bin/streamlit run src/grundstuecksfinder/app.py --server.port 8501 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now grundstuecksfinder
```

### 6. Nginx Reverse-Proxy (optional, für Domain + HTTPS)

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

```bash
sudo tee /etc/nginx/sites-available/grundstuecksfinder > /dev/null <<'EOF'
server {
    listen 80;
    server_name deine-domain.de;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF
```

```bash
sudo ln -sf /etc/nginx/sites-available/grundstuecksfinder /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

HTTPS mit Let's Encrypt:

```bash
sudo certbot --nginx -d deine-domain.de
```

### 7. Updates deployen

```bash
cd /opt/adressfinder
sudo git pull
sudo systemctl restart grundstuecksfinder
```
