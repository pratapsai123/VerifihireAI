$ErrorActionPreference = "Stop"

$domains = @("verifihireai.com", "www.verifihireai.com")
$rsa_key_size = 4096
$data_path = "./certbot"
$email = "edumala.rakesh@iit.org.in" # Updated email
$staging = 0 # Set to 1 if you're testing your setup to avoid hitting request limits

if (Test-Path "$data_path/conf/live/$($domains[0])") {
    Write-Host "Existing data found for $domains. Removing existing certificates..."
    Remove-Item -Recurse -Force "$data_path/conf/live/$($domains[0])"
    Remove-Item -Recurse -Force "$data_path/conf/archive/$($domains[0])" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$data_path/conf/renewal/$($domains[0]).conf" -ErrorAction SilentlyContinue
}

if (-not (Test-Path "$data_path/conf/options-ssl-nginx.conf")) {
    Write-Host "### Downloading options-ssl-nginx.conf ..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf" -OutFile "$data_path/conf/options-ssl-nginx.conf"
}

if (-not (Test-Path "$data_path/conf/ssl-dhparams.pem")) {
    Write-Host "### Downloading ssl-dhparams.pem ..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem" -OutFile "$data_path/conf/ssl-dhparams.pem"
}

if ($true) {
    Write-Host "### Creating dummy certificate for $domains ..."
    $path = "$data_path/conf/live/$($domains[0])"
    New-Item -ItemType Directory -Force -Path $path
    
    docker compose run --rm --entrypoint "openssl" certbot req -x509 -nodes -newkey rsa:4096 -days 1 -keyout "/etc/letsencrypt/live/$($domains[0])/privkey.pem" -out "/etc/letsencrypt/live/$($domains[0])/fullchain.pem" -subj "/CN=localhost"
    
    Write-Host "### Starting nginx ..."
    docker compose up --force-recreate -d nginx
    
    Write-Host "### Deleting dummy certificate for $domains ..."
    docker compose exec nginx rm -Rf /etc/letsencrypt/live/$($domains[0])
    docker compose exec nginx rm -Rf /etc/letsencrypt/archive/$($domains[0])
    docker compose exec nginx rm -Rf /etc/letsencrypt/renewal/$($domains[0]).conf
    
    Write-Host "### Requesting Let's Encrypt certificate for $domains ..."
    
    # Check if we should use staging
    $staging_arg = ""
    if ($staging -ne 0) {
        $staging_arg = "--staging"
    }

    $domain_args = ""
    foreach ($domain in $domains) {
        $domain_args += " -d $domain"
    }

    $email_arg = "--register-unsafely-without-email"
    if ($email -ne "") {
        $email_arg = "--email $email"
    }
    
    # Enable staging mode if needed
    if ($staging -ne 0) { $staging_arg = "--staging" }

    docker compose run --rm --entrypoint "certbot" certbot certonly --webroot -w /var/www/certbot $staging_arg $email_arg $domain_args --rsa-key-size $rsa_key_size --agree-tos --force-renewal
    
    Write-Host "### Reloading nginx ..."
    docker compose exec nginx nginx -s reload
}
