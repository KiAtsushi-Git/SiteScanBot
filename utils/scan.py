import asyncio
import aiohttp
import dns.resolver

async def get_ip(domain: str):
    loop = asyncio.get_event_loop()
    try:
        infos = await loop.getaddrinfo(domain, None)
        ips = list({info[4][0] for info in infos})
        return ips
    except Exception as e:
        return f"Ошибка получения IP: {e}"

def get_dns_records_sync(domain: str):
    records = {}
    try:
        answers = dns.resolver.resolve(domain, 'A')
        records['A'] = [r.to_text() for r in answers]
    except Exception as e:
        records['A'] = []
        print(f"A record error: {e}")

    try:
        answers = dns.resolver.resolve(domain, 'AAAA')
        records['AAAA'] = [r.to_text() for r in answers]
    except Exception as e:
        records['AAAA'] = []
        print(f"AAAA record error: {e}")

    try:
        answers = dns.resolver.resolve(domain, 'MX')
        records['MX'] = [r.exchange.to_text() for r in answers]
    except Exception as e:
        records['MX'] = []
        print(f"MX record error: {e}")

    try:
        answers = dns.resolver.resolve(domain, 'NS')
        records['NS'] = [r.to_text() for r in answers]
    except Exception as e:
        records['NS'] = []
        print(f"NS record error: {e}")

    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        records['TXT'] = [''.join([txt.decode('utf-8') if isinstance(txt, bytes) else txt for txt in r.strings]) for r in answers]
    except Exception as e:
        records['TXT'] = []
        print(f"TXT record error: {e}")

    return records

async def get_dns_records(domain: str):
    loop = asyncio.get_event_loop()
    records = await loop.run_in_executor(None, get_dns_records_sync, domain)
    return records

async def check_port(ip: str, port: int, timeout=1):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def scan_ports(ip: str, ports=None):
    if ports is None:
        ports = [
            20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 137, 138, 139,
            143, 161, 162, 389, 443, 445, 465, 514, 515, 587, 993, 995, 1080, 1194, 1433,
            1521, 1723, 2049, 2082, 2083, 2086, 2087, 2095, 2096, 3306, 3389, 5432, 5900,
            6000, 8080, 8443, 8888
        ]
    open_ports = []
    tasks = [check_port(ip, port) for port in ports]
    results = await asyncio.gather(*tasks)
    for port, is_open in zip(ports, results):
        if is_open:
            open_ports.append(port)
    return open_ports

async def get_server_info(ip: str):
    url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,query"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
                if data['status'] == 'success':
                    return {
                        "<b>IP</b>": data.get('query'),
                        "<b>Country</b>": data.get('country'),
                        "<b>Region</b>": data.get('regionName'),
                        "<b>City</b>": data.get('city'),
                        "<b>ISP</b>": data.get('isp'),
                        "<b>Org</b>": data.get('org'),
                    }
                else:
                    return {"error": "Информация недоступна"}
    except Exception as e:
        return {"error": f"Ошибка запроса: {e}"}

async def scan_domain(domain: str) -> str:
    ips = await get_ip(domain)
    if isinstance(ips, str):
        return ips

    dns = await get_dns_records(domain)

    open_ports_result = {}
    server_info_result = {}

    for ip in ips:
        open_ports = await scan_ports(ip)
        open_ports_result[ip] = open_ports

        info = await get_server_info(ip)
        server_info_result[ip] = info

    text = f"Результаты сканирования для {domain}:\n\n"

    text += "IP адреса:\n" + "\n".join(ips) + "\n\n"

    for rtype, recs in dns.items():
        text += f"{rtype}: {', '.join(recs) if recs else 'нет данных'}\n"

    text += "\nОткрытые порты:\n"
    for ip, ports in open_ports_result.items():
        if ports:
            text += f"{ip}: {', '.join(str(p) for p in ports)}\n"
        else:
            text += f"{ip}: нет открытых популярных портов\n"

    text += "\nИнформация о сервере:\n"
    for ip, info in server_info_result.items():
        text += f"{ip}:\n"
        if "error" in info:
            text += f"  Ошибка: {info['error']}\n"
        else:
            for k, v in info.items():
                text += f"  {k}: {v}\n"
        text += "\n"

    return text

async def scan_domain_data(domain: str):
    ips = await get_ip(domain)
    if isinstance(ips, str):
        return None, None, None  # ошибка

    dns = await get_dns_records(domain)

    open_ports_result = {}
    server_info_result = {}

    for ip in ips:
        open_ports = await scan_ports(ip)
        open_ports_result[ip] = open_ports

        info = await get_server_info(ip)
        server_info_result[ip] = info

    return ips, open_ports_result, server_info_result, dns
