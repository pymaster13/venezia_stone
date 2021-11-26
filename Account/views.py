import random
import json
import datetime

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import *
from django.core.mail import send_mail
from django.db import *
from django.http import HttpResponseRedirect
from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from templated_mail.mail import BaseEmailMessage

from VeneziaStone.settings import EMAIL_HOST_USER
from .serializers import *
from .tasks import *
from .models import *
from View1C.models import *

class Order(APIView):

    # На вход email, items, products, slabs
    def post(self, request):
        data = request.data
        keys = data.keys()
        order = {}
        if 'email' in keys:
            try:
                user = User.objects.get(email = data['email'])
                venezia = user.Venezia
                charme = user.Charme
                quartz = user.Quartz
                not_in_1c = False
                order["user"] = data['email']
            except:
                order["user"] = ""
                not_in_1c = True

        else:
            return Response({'error':'email field is blank'},status=status.HTTP_400_BAD_REQUEST)


        if 'products' in keys:
            slabs = []
            order["products"] = {}

            products_dict = data['products']
            for ps, kw in products_dict.items():
                product = Products.objects.get(ps = ps)
                project = product.items.pro
                if project == 'Venezia':

                    if not_in_1c:
                        if product.items.izd != 'Слэбы':
                            order["products"][product.ps] = {}
                            order["products"][product.ps][product.skl] = kw
                        else:
                            slabs.append(product.ps)

                    else:
                        if venezia:
                            if venezia.stock:
                                if product.items.izd != 'Слэбы':
                                    order["products"][product.ps] = {}
                                    order["products"][product.ps][product.skl] = kw
                                else:
                                    slabs.append(product.ps)
                        else:
                            if product.items.izd != 'Слэбы':
                                order["products"][product.ps] = {}
                                order["products"][product.ps][product.skl] = kw
                            else:
                                slabs.append(product.ps)

                elif project == 'Charme':
                    if not_in_1c:
                        if product.items.izd != 'Слэбы':
                            order["products"][product.ps] = {}
                            order["products"][product.ps][product.skl] = kw
                        else:
                            slabs.append(product.ps)
                    else:
                        if charme:
                            if charme.stock:
                                if product.items.izd != 'Слэбы':
                                    order["products"][product.ps] = {}
                                    order["products"][product.ps][product.skl] = kw
                                else:
                                    slabs.append(product.ps)
                        else:
                            if product.items.izd != 'Слэбы':
                                order["products"][product.ps] = {}
                                order["products"][product.ps][product.skl] = kw
                            else:
                                slabs.append(product.ps)

                elif project == 'Quartz':
                    if not not_in_1c:
                        if quartz:
                            if quartz.stock:
                                if product.items.izd != 'Слэбы':
                                    order["products"][product.ps] = {}
                                    order["products"][product.ps][product.skl] = kw
                                else:
                                    slabs.append(product.ps)
        else:
            order["products"] = ""

        order['slabs'] = slabs

        if 'items' in keys:
            items = []
            [items.append(item) for item in data['items']]
        else:
            items = []

        order["invItems"] = items

        if 'items' not in keys and 'products' not in keys:
            return Response({'error':'products and items are blank'},status=status.HTTP_400_BAD_REQUEST)

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            resp = requests.post('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnlineZakaz/createCustomerOrderSite',
                auth=('', ''), data=json.dumps(order), headers=headers)
            
            if resp.status_code == 200:
                return Response({'order':'sended'}, status=status.HTTP_200_OK)
            else:
                return Response({'order':'not sended'}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({'order':'not sended'}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmationEmail(BaseEmailMessage):
    template_name = "../templates/confirmation.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["site_name"] = "catalog-veneziastone.ru"
        return context


class ActivateUserView(APIView):
    serializer_class = ActivationUserSerializer

    def get(self,request,uid, token):
        dict = {}
        dict['uid'] = uid
        dict['token'] = token
        serializer = self.serializer_class(data=dict,
        context={'request': request})
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data
        user = User.objects.get(pk = id)
        if not user.is_active:
            user.is_active = True
            user.save()
            signals.user_activated.send(
                sender=self.__class__, user=user, request=self.request
            )

            context = {"user": user}
            to = [get_user_email(user)]
            ConfirmationEmail(self.request, context).send(to)

            head_mail = "Новый пользователь на сайте https://catalog-veneziastone.ru"
            body_mail = "Внимание, на сайте https://catalog-veneziastone.ru зарегистровался новый пользователь - {} {} {}." + \
                "Необходимо внести электронную почту данного пользователя в базу 1С.".format(user.last_name,user.first_name, user.middle_name)

            from_mail = EMAIL_HOST_USER
            to_mail = list()
            to_mail.append(EMAIL_HOST_USER)

            send_mail(head_mail, body_mail, from_mail, to_mail)

            return HttpResponseRedirect(redirect_to='https://catalog-veneziastone.ru')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ConfirmationResetPasswordView(APIView):
    serializer_class = ActivationUserSerializer

    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = datetime.datetime.now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GetFIOView(APIView):
    """
    APIVIEW for first,last and middle names by token
    """

    serializer_class = TokenToUserSerializer

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            user_mail = user_data.validated_data['token']
            user = User.objects.get(email = user_mail)

            return Response(
                {'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name,
                },
                status=status.HTTP_200_OK)
        
        else:
            return Response({'error': user_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetUserInfoView(APIView):
    """
    APIVIEW for get data (exclude password) about user by token
    """

    serializer_class = TokenToUserSerializer

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            user_mail = user_data.validated_data['token']
            user = User.objects.get(email = user_mail)

            return Response(
                {'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name,
                'email' : user.email,
                'phone' : str(user.phone)
                },
                status=status.HTTP_200_OK)
        else:
            return Response({'error': user_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserDataView(APIView):
    """
    APIVIEW for changing user's data
    """

    queryset = User.objects.all()
    serializer_class = TokenForChangeUserDataSerializer

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            user_mail = user_data.validated_data['token']
            user = User.objects.get(email = user_mail)
            
            try:
                if valid_user_data['email'] != "":
                    user.email = valid_user_data['email']
            except:
                pass
            try:
                if valid_user_data['phone']:
                    user.phone = valid_user_data['phone']
            except:
                pass
            try:
                if valid_user_data['first_name']:
                    user.first_name = valid_user_data['first_name']
            except:
                pass
            try:
                if valid_user_data['last_name']:
                    user.last_name = valid_user_data['last_name']
            except:
                pass
            try:
                if valid_user_data['middle_name']:
                    user.middle_name = valid_user_data['middle_name']
            except:
                pass
            try:
                if valid_user_data['password']:
                    user.set_password(valid_user_data['password'])
            except:
                pass
            
            if len(valid_user_data) > 1:
                user.save()
                return Response({user.email:'Data is changed successfully'},
                                        status=status.HTTP_200_OK)
            else:
                return Response({user.email:'Data is not changed'},
                                        status=status.HTTP_200_OK)
        else:
            return Response({'error': user_data.errors},
                                        status=status.HTTP_400_BAD_REQUEST)


class PasswordResetEmail(BaseEmailMessage):
    """
    VIEW for password reseting by email
    """
    
    template_name = "../templates/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["site_name"] = "catalog-veneziastone.ru"
        context["protocol"] = "https"
        context["domain"] = "catalog-veneziastone.ru"
        context["token"] = default_token_generator.make_token(user)
        context["url"] = '#/account/password/reset/confirm/{uid}/{token}'.format(**context)
        
        return context


class ActivationEmail(BaseEmailMessage):
    """
    VIEW for activation of registration
    """

    template_name = "../templates/activation.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["site_name"] = "catalog-veneziastone.ru"
        context["protocol"] = "https"
        context["domain"] = "catalog-veneziastone.ru"
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = 'account/activate/{uid}/{token}'.format(**context)
        
        return context


class PasswordResetPhoneView(APIView):
    """
    APIVIEW for password reseting by phone
    """

    queryset = User.objects.all()
    serializer_class = PasswordResetPhoneSerializer

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            phone = valid_user_data['phone']
            
            try:
                user = User.objects.get(phone=phone)
            
            except ObjectDoesNotExist:
                return Response({'error':'Сheck that entered phone number is correct!'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({'error':'Some error!'}, status=status.HTTP_400_BAD_REQUEST)

            code_value = random.randint(111111,999999)
            
            try:
                code = Code(user=user,code=code_value)
                code.save()
            except IntegrityError:
                return Response({'error':'New sms-code could send only throw 60 sec!'},status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'error':'This code is not exist or expired!'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({'error':'Some error!'}, status=status.HTTP_400_BAD_REQUEST)

            body = "Восстановления пароля на сайте catalog-veneziastone.ru. Код: %s." % code.code + \
                "Действителен в течение 60 секунд. Никому не сообщайте код." 
            
            code_id = str(code.id)

            sms_send.delay(code_id, body)
            delete_sms.s(code_id).apply_async(countdown=60)

            return Response({'phone':str(user.phone), 'sms':'sended'}, status=status.HTTP_200_OK)
        
        return Response({'error': user_data.errors}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetPhoneConfirmView(APIView):
    """
    APIVIEW for confirming of password reseting by phone
    """
    
    queryset = User.objects.all()
    serializer_class = PasswordResetPhoneConfirmSerializer

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data,
                                          context={'request': request})

        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            code_received = valid_user_data['code']
            new_password = valid_user_data['new_password']
            re_new_password = valid_user_data['re_new_password']
    
            try:
                code = Code.objects.get(code=code_received)
                user = code.user
            except ObjectDoesNotExist:
                return Response({'error':'Сheck that entered code is correct or 60 secs expired!'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({'error':'Some error!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password == re_new_password:
                try:
                    user.set_password(new_password)
                    user.save()
                    return Response({'user':user.email, 'password':'Successfully changed'}, status=status.HTTP_200_OK)
                except Exception:
                    return Response({'error':'Some error during setting of new password!'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': user_data.errors}, status=status.HTTP_400_BAD_REQUEST)
