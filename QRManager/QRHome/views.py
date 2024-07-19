import base64
import json
import random
from io import BytesIO

import rsa
from Crypto.Cipher import AES
from django.contrib import auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rsa import PrivateKey

import QRToken
from QR import QR
from QRToken.models import AuthToken

PRIVATE_KEY = PrivateKey(
    7986291780433942702581136058302074301869943192822634967674988332655544673562834902209971777236281808177806213336709918483629434748245227209063301345541661,
    65537,
    4936032086580973848524520456804306295246104017096810229345912650907815315953492056322152603750728817786591437602611599892261751761804372392019730431025985,
    4584312980377402143750832148916217154446726651722338745420592101845914862723241449,
    1742091304546242763214587551800604991391242834066373977744134043884282389)


# Create your views here.
def login_page(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
    return render(request, 'QRHome/login.html')


def logout_page(request):
    logout(request)
    return redirect("/")


@login_required()
def home(request):
    user = request.user
    tokens = AuthToken.objects.filter(user=user, active=True, prev=None)
    return render(request, 'QRHome/index.html', context={"user": user, "tokens": tokens})


@login_required()
def deactivate_code(request):
    id = request.GET["id"]
    if not AuthToken.objects.filter(pk=id, user=request.user).exists():
        response = JsonResponse({"error": ""})
        response.code = 400
        return response

    token = AuthToken.objects.get(pk=id, user=request.user)
    while token is not None:
        token.active = False
        token.save()
        token = token.next

    response = JsonResponse({"success": ""})
    response.code = 200
    return response


@login_required()
def generate(request):
    return render(request, 'QRHome/generate.html')


@login_required()
def generate_multi(request):
    return render(request, 'QRHome/generate_multi_newUI.html')


@login_required()
def scanner(request):
    return render(request, 'QRHome/scanner.html')


@login_required()
def debug_get(request):
    qr = request.GET["qr"]
    id = QR.getID(qr)
    tok = None
    if not AuthToken.objects.filter(qr_id=id).exists():
        active = None
        hash = None
    else:
        token = AuthToken.objects.get(qr_id=id)
        tok = token.token
        active = token.active == True
        hash = QR.get_hashed_token(qr)
    return JsonResponse({"id": id, "token": tok, "active": active, "hash": hash})


@login_required()
def gen_2fa_code(request):
    temp = QR()
    buffered = BytesIO()
    temp.qr.save(buffered)
    img_str = base64.b64encode(buffered.getvalue())
    if request.GET["hide"] == "true":
        save_str = ""
    else:
        save_str = temp.qr_string
    AuthToken.objects.create(user=request.user, qr_id=temp.id, token=save_str,
                             hashed_token=QR.get_hashed_token(temp.qr_string), name=request.GET["name"])
    return HttpResponse(img_str)


@login_required()
def gen_multi_2fa_codes(request):
    # Get number of codes
    amount = int(request.GET["amount"])
    name = request.GET["name"].strip()
    phrase = request.GET['keyphrase'].split()
    if not phrase or amount == 1:
        phrase = [""]
    hide = request.GET["hide"] == "true"

    if name == "" or amount < 1 or (len(phrase) != amount and amount != 1):
        response = JsonResponse({"error": "error"})
        response.code = 400
        return response

    if amount > 1:
        if len(set(phrase)) != len(phrase):
            response = JsonResponse({"error": "error"})
            response.code = 400
            return response

    # Store codes
    codes = []
    images = []

    for i in range(amount):
        temp = QR()
        buffered = BytesIO()
        temp.qr.save(buffered)
        img_str = base64.b64encode(buffered.getvalue())
        images.append((img_str, phrase[i]))
        if hide:
            save_str = ""
        else:
            save_str = temp.qr_string

        codes.append(temp)
        current = codes[i]
        save_str = codes[i].qr_string if not hide else ""

        AuthToken.objects.create(user=request.user, qr_id=current.id, token=save_str,
                                 hashed_token=QR.get_hashed_token(current.qr_string), name=name,
                                 hint=phrase[i])

    for i in range(amount):
        current = codes[i]
        if i == 0:
            prev = None
        else:
            prev = AuthToken.objects.get(qr_id=codes[i - 1].id)

        if i == amount - 1:
            nxt = None
        else:
            nxt = AuthToken.objects.get(qr_id=codes[i + 1].id)

        AuthToken.objects.filter(qr_id=current.id).update(prev=prev, next=nxt)

    if amount > 1:
        before = [x[1] for x in images]
        after = before
        while before == after:
            random.shuffle(images)
            after = [x[1] for x in images]

    dict = {}
    for i in range(len(images)):
        dict[i] = images[i][0].decode("utf-8"), images[i][1]

    return JsonResponse(dict)


@login_required()
def retrieve_2fa_code_image(request):
    id = request.GET["id"]
    if not AuthToken.objects.filter(pk=id, user=request.user, active=True).exists():
        response = JsonResponse({"error": ""})
        response.code = 400
        return response

    token = AuthToken.objects.get(pk=id, user=request.user)
    imgs = []
    keyphrase = []
    while token is not None:
        if token.token == "":
            response = JsonResponse({"error": "error"})
            response.code = 400
            return response

        temp = QR.get_image(token.token)
        buffered = BytesIO()
        temp.save(buffered)
        img_str = base64.b64encode(buffered.getvalue())
        imgs.append((img_str.decode("utf-8"), token.hint))
        keyphrase.append(token.hint)
        token = token.next

    random.shuffle(imgs)

    dict = {}
    for i in range(len(imgs)):
        dict[i] = imgs[i]
    dict["key-phrase"] = keyphrase
    return JsonResponse(dict)


@csrf_exempt
def validate(request):
    qr_data = request.POST["qr"]

    qr_data = base64.b64decode(qr_data)

    key = request.POST["key"]
    nonce = request.POST["nonce"]
    tag = request.POST["tag"]

    key = rsa.decrypt(base64.b64decode(key), PRIVATE_KEY)
    nonce = rsa.decrypt(base64.b64decode(nonce), PRIVATE_KEY)
    tag = rsa.decrypt(base64.b64decode(tag), PRIVATE_KEY)

    cipher = AES.new(key, AES.MODE_OCB, nonce=nonce)
    qr_data = cipher.decrypt_and_verify(qr_data, tag)

    qr_data = qr_data.decode()

    try:
        if QR.validate(qr_data):
            qr_id = QR.getID(qr_data)
            qr = AuthToken.objects.get(qr_id=qr_id)
            if qr.prev is None:
                return JsonResponse({"valid": "true", "qr_id": qr_id})
    except Exception as e:
        pass

    return JsonResponse({"valid": "false"})


@csrf_exempt
def authenticate(request):
    # TODO We should see if we can send a list of rsa encrypted items to clean up code a little and aes encrypted items
    # Then we could do for each aes_item, key,tag,nonce in zip(aes,keys,tags,nonces) decrypt.

    # The data that makes up the qr code
    qr_data_list = request.POST["qr"]
    # The QRUser ID that the remote site has stores
    qr_id = request.POST["id"]
    # The AES Keys for the qr code and ID
    qr_key = request.POST["qr_key"]
    id_key = request.POST["id_key"]
    # The AES Nonces for the qr code and ID
    qr_nonce = request.POST["qr_nonce"]
    id_nonce = request.POST["id_nonce"]
    # The AES Tags for the qr code and ID
    id_tag = request.POST["id_tag"]
    qr_tag = request.POST["qr_tag"]

    # TODO maybe a batch decrypt function. Takes in all 10 values and returns it all?
    qr_key = rsa.decrypt(base64.b64decode(qr_key), PRIVATE_KEY)
    id_key = rsa.decrypt(base64.b64decode(id_key), PRIVATE_KEY)

    qr_nonce = rsa.decrypt(base64.b64decode(qr_nonce), PRIVATE_KEY)
    id_nonce = rsa.decrypt(base64.b64decode(id_nonce), PRIVATE_KEY)

    id_tag = rsa.decrypt(base64.b64decode(id_tag), PRIVATE_KEY)
    qr_tag = rsa.decrypt(base64.b64decode(qr_tag), PRIVATE_KEY)

    cipher = AES.new(qr_key, AES.MODE_OCB, nonce=qr_nonce)
    qr_data_list = cipher.decrypt_and_verify(base64.b64decode(qr_data_list), qr_tag)

    cipher = AES.new(id_key, AES.MODE_OCB, nonce=id_nonce)
    qr_id = cipher.decrypt_and_verify(base64.b64decode(qr_id), id_tag)

    # Convert the list of qr codes from <class 'str'> back into <class 'list'>
    qr_data_list=json.loads(qr_data_list)

    # Check the first code, return if bad
    counter = 0
    qr_data = qr_data_list[0]
    qr_id = qr_id.decode()
    next = None
    if QR.validate(qr_data) and AuthToken.objects.filter(qr_id=qr_id).exists():
        qr = AuthToken.objects.get(qr_id=qr_id)
        hashed = QR.get_hashed_token(qr_data)
        next = qr.next
        counter += 1
        if not qr.active or not (hashed == qr.hashed_token):
            return JsonResponse({"auth": "false"})

    while next is not None:
        qr = next
        hashed = QR.get_hashed_token(qr_data_list[counter])
        next = qr.next
        counter += 1
        if not qr.active or not (hashed == qr.hashed_token):
            return JsonResponse({"auth": "false"})

    return JsonResponse({"auth": "true"})


@csrf_exempt
def check_key_count(request):
    qr_id = request.POST["id"]
    qr_id = base64.b64decode(qr_id)

    key = request.POST["key"]
    nonce = request.POST["nonce"]
    tag = request.POST["tag"]
    key = rsa.decrypt(base64.b64decode(key), PRIVATE_KEY)
    nonce = rsa.decrypt(base64.b64decode(nonce), PRIVATE_KEY)
    tag = rsa.decrypt(base64.b64decode(tag), PRIVATE_KEY)

    cipher = AES.new(key, AES.MODE_OCB, nonce=nonce)
    qr_id = cipher.decrypt_and_verify(qr_id, tag)

    qr_id = qr_id.decode()
    if AuthToken.objects.filter(qr_id=qr_id).exists():
        qr = AuthToken.objects.get(qr_id=qr_id)
        if qr.active:
            count = 1
            temp = qr
            while (temp.next is not None):
                count += 1
                temp = temp.next
            return JsonResponse({"count": count})
        else:
            return JsonResponse({"count": -1})
