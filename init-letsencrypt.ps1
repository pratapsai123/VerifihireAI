$ErrorActionPreference = "Stop"

$domains = @("verifihireai.com", "www.verifihireai.com")
$rsa_key_size = 4096
$data_path = "./certbot"
$email = "saipratap65@gmail.com" # Updated to your email
$staging = 0 # Set to 1 if you're testing your setup to avoid hitting request limits

if (Test-Path "$data_path/conf/live/$($domains[0])") {
    Write-Host "Existing certificates found for $domains. If you want to force renewal, delete the certbot folder first." -ForegroundColor Cyan
    # Exit if they already exist to prevent accidental deletion
    # return
}

if (-not (Test-Path "$data_path/conf/options-ssl-nginx.conf")) {
    Write-Host "### Downloading options-ssl-nginx.conf ..."
    New-Item -ItemType Directory -Force -Path "$data_path/conf"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf" -OutFile "$data_path/conf/options-ssl-nginx.conf"
}

if (-not (Test-Path "$data_path/conf/ssl-dhparams.pem")) {
    Write-Host "### Downloading ssl-dhparams.pem ..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem" -OutFile "$data_path/conf/ssl-dhparams.pem"
}

Write-Host "### Creating dummy certificate for $domains ..."
$path = "/etc/letsencrypt/live/$($domains[0])"
mkdir -Force "$data_path/conf/live/$($domains[0])"

docker compose run --rm --entrypoint "openssl" certbot req -x509 -nodes -newkey rsa:4096 -days 1 -keyout "$path/privkey.pem" -out "$path/fullchain.pem" -subj "/CN=localhost"

Write-Host "### Starting nginx..."
docker compose up --force-recreate -d nginx

Write-Host "### Deleting dummy certificate for $domains ..."
docker compose run --rm --entrypoint "rm" certbot -rf "/etc/letsencrypt/live/$($domains[0])" "/etc/letsencrypt/archive/$($domains[0])" "/etc/letsencrypt/renewal/$($domains[0]).conf"

Write-Host "### Requesting Let's Encrypt certificate for $domains ..."
$domain_args = @()
foreach ($domain in $domains) {
    $domain_args += "-d"
    $domain_args += $domain
}

$email_args = if ($email) { @("--email", $email) } else { @("--register-unsafely-without-email") }
$staging_args = if ($staging -ne 0) { @("--staging") } else { @() }

docker compose run --rm --entrypoint "certbot" certbot certonly --webroot -w /var/www/certbot $staging_args $email_args $domain_args --rsa-key-size $rsa_key_size --agree-tos --force-renewal --non-interactive

Write-Host "### Reloading nginx ..."
docker compose exec nginx nginx -s reload

Write-Host "✅ SSL Setup Complete!" -ForegroundColor Green
