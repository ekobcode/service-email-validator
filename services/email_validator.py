import re
import dns.resolver
import socket
import time
import os


EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Contoh list disposable dan free provider sederhana
disposable_domains = {"10minutemail.com", "temp-mail.org", "mailinator.com"}
free_email_providers = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "mail.com"}
role_based_prefixes = {"admin", "info", "support", "sales", "contact"}


def get_public_ip_fallback():
    try:
        dns_ip = os.getenv("FALLBACK_DNS_IP")
        dns_port = int(os.getenv("FALLBACK_DNS_PORT"))

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((dns_ip, dns_port))
            return s.getsockname()[0]
    except Exception:
        return None

def validate_email_address(email: str) -> dict:
    result = {
        "email": email,
        "status": False,
        "message": "Email validation failed.",
        "data": {}
    }

    # Step 1: Validate format
    if not EMAIL_REGEX.fullmatch(email):
        result["message"] = "Invalid email format."
        return result

    # Step 2: Parse domain
    local_part, domain = email.lower().split('@')
    is_role_based = local_part in role_based_prefixes
    is_disposable = domain in disposable_domains
    is_free = domain in free_email_providers
    provider_info = {
        "provider": domain,
        "provider_type": "free" if is_free else "custom"
    }

    # Step 3: Resolve MX Records
    mx_start_time = time.time()
    mx_records = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 1.5
        resolver.lifetime = 2.5
        dns_nameservers = os.getenv("DNS_NAMESERVERS")
        resolver.nameservers = [ip.strip() for ip in dns_nameservers.split(",") if ip.strip()]
        answers = resolver.resolve(domain, 'MX')
        for r in answers:
            mx_server = str(r.exchange).rstrip('.')
            try:
                ip_list = list({
                    res[4][0]
                    for res in socket.getaddrinfo(mx_server, 25, proto=socket.IPPROTO_TCP)
                })
            except socket.gaierror:
                ip_list = []
            mx_records.append({
                "priority": r.preference,
                "server": mx_server,
                "ip_addresses": ip_list
            })
    except Exception:
        result.update({
            "message": "No MX records found.",
            "data": {
                "email": email,
                "valid_syntax": True,
                "valid_domain": False,
                "domain": domain,
                "mx_records": [],
                "is_disposable": is_disposable,
                "is_free_email_provider": is_free,
                "is_role_based": is_role_based,
                "is_catch_all": None,
                "smtp_check": None,
                "is_blacklisted": False,
                "provider_info": provider_info,
                "server_public_ip": get_public_ip_fallback()
            }
        })
        return result

    if not mx_records:
        result.update({
            "message": "No valid MX records.",
            "data": {
                "email": email,
                "valid_syntax": True,
                "valid_domain": False,
                "domain": domain,
                "mx_records": [],
                "is_disposable": is_disposable,
                "is_free_email_provider": is_free,
                "is_role_based": is_role_based,
                "is_catch_all": None,
                "smtp_check": None,
                "is_blacklisted": False,
                "provider_info": provider_info,
                "server_public_ip": get_public_ip_fallback()
            }
        })
        return result

    # Step 4: Build Success Response
    result.update({
        "status": True,
        "message": "Email syntax and MX check passed.",
        "data": {
            "email": email,
            "valid_syntax": True,
            "valid_domain": True,
            "domain": domain,
            "mx_records": mx_records,
            "is_disposable": is_disposable,
            "is_free_email_provider": is_free,
            "is_role_based": is_role_based,
            "is_catch_all": None,
            "smtp_check": None,
            "is_blacklisted": False,
            "provider_info": provider_info,
            "server_public_ip": get_public_ip_fallback()
        }
    })

    return result
