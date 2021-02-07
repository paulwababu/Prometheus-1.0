from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import requests
import datetime
import emoji
import random
import json
import dns
import dns.resolver
import phonenumbers
from phonenumbers import geocoder
from requests.auth import HTTPBasicAuth
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment

cash = ""
number_yake = ""


@csrf_exempt
def index(request):
    if request.method == 'POST':
        # retrieve incoming message from POST request in lowercase
        incoming_msg = request.POST['Body'].lower()

        # create Twilio XML response
        resp = MessagingResponse()
        msg = resp.message()

        responded = False

        if incoming_msg == 'hello' or incoming_msg == 'hi':
            response = emoji.emojize("""
*Wagwan! I am the Prometheus, an AI created by PaulWababu* :wave:
Let's be friends :wink:
You can give me the following commands: ALSO NOTE THAT YOU CAN CHAT WITH ME, IF YOU DO NOT WANT TO USE THE COMMANDS BELOW!
:black_small_square: *'quote':* Hear an inspirational quote to start your day! :rocket:
:black_small_square: *'paul'*: See a picture of my creator? :superhero:
:black_small_square: *'resolve <domain name>'*: Find the IP address of the Domain name eg "resolve tutorialspoint.com" :alien:
:black_small_square: *'trace <phonenumber>'*: Trace origin of phone number eg "trace +254797584194" :handshake:
:black_small_square: *'instagram <username>'*: Retrieve publicly-available Instagram Profile. That includes name, bio, followers information along with profile pictures eg "instagram xtiandela":winking face:
:black_small_square: *'meme'*: The top memes of today, fresh from r/memes. :hankey:
:black_small_square: *'news'*: Latest news from around the world. :newspaper:
:black_small_square: *'donate'*: Donate via MPESA eg "donate 200 254797584194" where (200) is the amount and (254...) is your MPESA number :superhero:
""", use_aliases=True)
            msg.body(response)
            responded = True

        elif incoming_msg == 'quote':
            # returns a quote
            r = requests.get('https://api.quotable.io/random')

            if r.status_code == 200:
                data = r.json()
                quote = f'{data["content"]} ({data["author"]})'

            else:
                quote = 'I could not retrieve a quote at this time, sorry.'

            msg.body(quote)
            responded = True
        
        elif incoming_msg == 'paul':
            # return his pic
            msg.media('https://icomnalt.sirv.com/Images/paul.jpg')
            msg.body("Connect on Linked in: https://www.linkedin.com/in/paul-wababu-660b511a7/")
            responded = True   

        elif incoming_msg.startswith('resolve'):
            search_textt = incoming_msg.replace('resolve', '')
            search_textt = search_textt.strip()
            result = dns.resolver.query(search_textt, 'A')
            for ipval in result:
                ip = ipval.to_text()
                #print("IP", ipval.to_text())
                msg.body(ip)
                msg.body("Happy Hacking!")
            #msg.body("Enter Domain name to resolve: eg tutorialspoint.com")
            # return a cat pic
            #msg.media('https://cataas.com/cat')
            
            responded = True


        elif incoming_msg.startswith('donate'):
            word_list = incoming_msg.split()
            global cash
            global number_yake
            cash = word_list[1]
            number_yake = word_list[-1]
            stk = requests.get("https://0fea66d94d75.ngrok.io/api/v1/online/lipa")
            msg.body("Enter MPESA PIN to complete transcation")
            responded = True


        elif incoming_msg.startswith('instagram'):
            search_textt = incoming_msg.replace('instagram', '')
            search_textt = search_textt.strip()
            username = search_textt
            url = "https://easy-instagramapi.p.rapidapi.com/v1/profile/"+username
            headers = {
                'x-rapidapi-key': "43628cd680msh1812b1660500eb7p182976jsn5dda2f77f08f",
                'x-rapidapi-host': "easy-instagramapi.p.rapidapi.com"
     
            }
            response = requests.request("GET", url, headers=headers)
            a = response.json()
            dp = a['profilePhotoHd']
            followers = str(a['followersCount'])
            following = str(a['followingCount'])
            msg.media(dp)
            msg.body("Instagram User: " +username)
            msg.body("Total Followers: " +followers)
            msg.body("Total Following: " +following)
            msg.body("Bio: " +a['biography'])
            responded = True    

        elif incoming_msg.startswith('trace'):
            search_textt = incoming_msg.replace('trace', '')
            search_textt = search_textt.strip()
            phone_number1 = phonenumbers.parse(search_textt)
            location = geocoder.description_for_number(phone_number1,'en')
            msg.body("Phone number originates from: ")
            msg.body(location)
            responded = True
    

        elif incoming_msg == 'cat':
            # return a cat pic
            msg.media('https://cataas.com/cat')
            responded = True    

        elif incoming_msg == 'dog':
            # return a dog pic
            r = requests.get('https://dog.ceo/api/breeds/image/random')
            data = r.json()
            msg.media(data['message'])
            responded = True

        elif incoming_msg == 'news':
            r = requests.get('https://newsapi.org/v2/top-headlines?sources=bbc-news,the-washington-post,the-wall-street-journal,cnn,fox-news,cnbc,abc-news,business-insider-uk,google-news-uk,independent&apiKey=3ff5909978da49b68997fd2a1e21fae8')
            
            if r.status_code == 200:
                data = r.json()
                articles = data['articles'][:5]
                result = ''
                
                for article in articles:
                    title = article['title']
                    url = article['url']
                    if 'Z' in article['publishedAt']:
                        published_at = datetime.datetime.strptime(article['publishedAt'][:19], "%Y-%m-%dT%H:%M:%S")
                    else:
                        published_at = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%S%z")
                    result += """
*{}*
Read more: {}
_Published at {:02}/{:02}/{:02} {:02}:{:02}:{:02} UTC_
""".format(
    title,
    url, 
    published_at.day, 
    published_at.month, 
    published_at.year, 
    published_at.hour, 
    published_at.minute, 
    published_at.second
    )

            else:
                result = 'I cannot fetch news at this time. Sorry!'

            msg.body(result)
            responded = True

        elif incoming_msg.startswith('meme'):
            r = requests.get('https://www.reddit.com/r/memes/top.json?limit=20?t=day', headers = {'User-agent': 'your bot 0.1'})
            
            if r.status_code == 200:
                data = r.json()
                memes = data['data']['children']
                random_meme = random.choice(memes)
                meme_data = random_meme['data']
                title = meme_data['title']
                image = meme_data['url']

                msg.body(title)
                msg.media(image)
            
            else:
                msg.body('Sorry, I cannot retrieve memes at this time.')

            responded = True

        if not responded:
            url = "https://smalltalk-nlu.p.rapidapi.com/api/v1/smalltalk"
            text = incoming_msg
            payload = "languageCode=en-US&query="+text
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'x-rapidapi-key': "43628cd680msh1812b1660500eb7p182976jsn5dda2f77f08f",
                'x-rapidapi-host': "smalltalk-nlu.p.rapidapi.com"
                }
            
            response = requests.request("POST", url, data=payload, headers=headers)
            a = response.json()
            b = a['fulfillmentMessages']['text']
            msg.body(str(b))
             

        return HttpResponse(str(resp))


#############################################################
def getAccessToken(request):
    consumer_key = 'qaB31tWrbH4psywuGIfGnvekxMganto4'
    consumer_secret = 'YlH4kc0RqJrkmQJy'
    api_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)
def lipa_na_mpesa_online(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    global cash
    global number_yake
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": cash,
        "PartyA": int(number_yake), # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": int(number_yake),# replace with your phone number to get stk push
        "CallBackURL": "https://api.safaricom.co.ke/mpesa/",
        "AccountReference": "PaulWababu",
        "TransactionDesc": "Donate to PaulWababu!"
    }
    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('success')
@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://0fea66d94d75.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://0fea66d94d75.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)



@csrf_exempt
def call_back(request):
    pass




@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],
    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
