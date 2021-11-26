import base64
import time
from io import BytesIO

from django.db.models import Max, Min, Sum, Count, F
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.http import JsonResponse
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from urllib.request import urlopen

from .models import *
from Account.models import *
from View1C.models import Materials
from View1C.serializers import *


sity = {'spb': 'Санкт-Петербург',
    'spbPrs': 'Санкт-Петербург, Парнас',
    'msc': 'Москва','kzn': 'Казань',
    'krd': 'Краснодар',
    'fdr': 'ЛО, Федоровское',
    'ekb': 'Екатеринбург',
    'bzl':'МО, Бузланово'}


def get_colors(url, numcolors, resize=150):
    img = Image.open(urlopen(url))
    img = img.copy()

    #Уменьшаем масштаб картинки для увеличения скорости обработки
    img.thumbnail((resize, resize))

    #Извлекаем цвета из картинки
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    colors = list()

    for i in range(numcolors):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index*3:palette_index*3+3]

        #Преобразование dominant_color rgb в hex и заполнение словаря, отсортированного по доминантным цветам
        rgb = []
        rgb = tuple(dominant_color)
        if numcolors != 1:
            colors.append(rgb2hex(rgb[0],rgb[1],rgb[2]))
        else:
            colors = rgb2hex(rgb[0],rgb[1],rgb[2])
    
    #7-самый преобладающий
    return colors


class getPhotoBytes(APIView):

    def post(self, request):
        data = request.data
        pk = data['pk']
        product = Products.objects.get(pk = pk)
        dictionary = {}
        dictionary['bytes'] = product.photo_bytes
        dictionary['le'] = product.le
        dictionary['he'] = product.he

        try:
            return JsonResponse(dictionary, safe=False)
        except:
            return JsonResponse('error', safe=False)

class get_Photo_for_PDF(APIView):

    def post(self, request):
        data = request.data
        product = Products.objects.get(pk = data['pk'])
        try:
            return JsonResponse(product.photo_bytes, safe=False)
        except:
            return JsonResponse('error', safe=False)

class Bookmatch(APIView):

    def post(self, request):
        start_time = time.time()
        data = request.data
        modes = request.data['sides'].items()
        image_decode = base64.b64decode(data['image'].split(',')[1])
        stream = BytesIO(image_decode)
        image = Image.open(stream)

        if request.data['sides']:
            sorted_list = sorted(request.data['sides'].keys())
            for item in sorted_list:
                weight = image.size[0]
                height = image.size[1]
                side = request.data['sides'][item]
                image1 = image.copy()
                image2 = image.copy()

                if side == 'right':
                    image2 = image2.transpose(method=Image.FLIP_LEFT_RIGHT)
                    image = Image.new('RGB',(weight*2,height))
                    image.paste(image1,(0,0))
                    image.paste(image2,(weight,0))

                elif side == 'left':
                    image2 = image2.transpose(method=Image.ROTATE_180)
                    image2 = image2.transpose(method=Image.FLIP_LEFT_RIGHT)
                    image2 = image2.transpose(method=Image.ROTATE_180)
                    image = Image.new('RGB',(weight*2,height))
                    image.paste(image1,(weight,0))
                    image.paste(image2,(0,0))

                elif side == 'up':
                    image2 = image2.transpose(method=Image.ROTATE_180)
                    image2 = image2.transpose(method=Image.FLIP_TOP_BOTTOM)
                    image2 = image2.transpose(method=Image.ROTATE_180)
                    image = Image.new('RGB',(weight,height*2))
                    image.paste(image1,(0,height))
                    image.paste(image2,(0,0))

                elif side == 'down':
                    image2 = image2.transpose(method=Image.FLIP_TOP_BOTTOM)
                    image = Image.new('RGB',(weight,height*2))
                    image.paste(image1,(0,0))
                    image.paste(image2,(0,height))

                else:
                    return JsonResponse({'error':'Not correct format (sides:left,right,up,down)'})

        else:
            return JsonResponse({'error':'No sides'})

        byte_in = BytesIO()
        image.save(byte_in, format='JPEG')
        byte_out = byte_in.getvalue()
        enc_bytes = base64.b64encode(byte_out)

        return JsonResponse(str(enc_bytes)[2:-1], safe=False)


class getMaterials(APIView):

    def get(self, request):
        materials = Materials.objects.all()
        materials_new = Materials.objects.filter(nw = 1)
        materials_sale = Materials.objects.filter(onSale = 1)
        serializer = MaterialsSerializer(materials, many=True)
        serializer_sale = MaterialsSerializer(materials_sale, many=True)
        serializer_new = MaterialsSerializer(materials_new, many=True)

        context = {}
        context['mts'] = serializer.data
        context['sale'] = serializer_sale.data
        context['new'] = serializer_new.data

        return JsonResponse(context, safe=False)


class getGroups(APIView):

    def get(self, request, material):
        material_group = Materials.objects.get(ph = material)
        context = {'mts': [{'mt': material_group.mt, 'ps': material_group.ps, 'ph': material_group.ph}]}
        inv_groups = InvGroups.objects.filter(materials = material_group)
        serializer = InvGroupsSerializer(inv_groups, many=True)
        context['mts'][0].update({'grs': serializer.data})

        return JsonResponse(context, safe=False)

class getGroupsNew(APIView):

    def get(self, request, material):
        material_group = Materials.objects.get(ph = material, nw =1)
        context = {'mts': [{'mt': material_group.mt, 'ps': material_group.ps, 'ph': material_group.ph}]}
        inv_groups = InvGroups.objects.filter(materials = material_group, nw = 1)
        serializer = InvGroupsSerializer(inv_groups, many=True)
        context['mts'][0].update({'grs': serializer.data})

        return JsonResponse(context, safe=False)


class getGroupsSale(APIView):

    def get(self, request, material):
        material_group = Materials.objects.get(ph = material, onSale = 1)
        context = {'mts': [{'mt': material_group.mt, 'ps': material_group.ps, 'ph': material_group.ph}]}
        inv_groups = InvGroups.objects.filter(materials = material_group, onSale = 1)
        serializer = InvGroupsSerializer(inv_groups, many=True)
        context['mts'][0].update({'grs': serializer.data})

        return JsonResponse(context, safe=False)


class getGroupsElement(APIView):

    def get(self, request, material, group):
        material = Materials.objects.get(ph = material)
        group_item = InvGroups.objects.get(ps = group, materials = material)
        inv_items = InvItems.objects.filter(groups = group_item)
        context = {'grs': [{'id': group_item.ps}]}
        serializer = InvItemsSerializer(inv_items, many=True)
        context['grs'][0].update({'itms': serializer.data})

        return JsonResponse(context, safe=False)


class getGroupsElementNew(APIView):

    def get(self, request, material, group):
        material = Materials.objects.get(ph = material, nw = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, nw = 1)
        inv_items = InvItems.objects.filter(groups = group_item, nw = 1)
        context = {'grs': [{'id': group_item.ps}]}
        serializer = InvItemsSerializer(inv_items, many=True)
        context['grs'][0].update({'itms': serializer.data})

        return JsonResponse(context, safe=False)


class getGroupsElementSale(APIView):

    def get(self, request, material, group):
        material = Materials.objects.get(ph = material, onSale = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, onSale = 1)
        inv_items = InvItems.objects.filter(groups = group_item, onSale = 1)
        context = {'grs': [{'id': group_item.ps}]}
        serializer = InvItemsSerializer(inv_items, many=True)
        context['grs'][0].update({'itms': serializer.data})

        return JsonResponse(context, safe=False)


class getProducts(APIView):

    def get(self, request, material, group, item):
        material = Materials.objects.get(ph = material)
        group_item = InvGroups.objects.get(ps = group, materials = material)
        inv_item = InvItems.objects.get(ps = item, groups = group_item)

        products = Products.objects.filter(items = inv_item)
        products = Products.objects.filter(items = inv_item)
        products = Products.objects.filter(items = inv_item)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductsSerializer(products, many=True)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class getProductsNew(APIView):

    def get(self, request, material, group, item):
        material = Materials.objects.get(ph = material, nw = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, nw = 1)
        inv_item = InvItems.objects.get(ps = item, groups = group_item, nw = 1)
        products = Products.objects.filter(items = inv_item, nw = 1)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductsSerializer(products, many=True)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class getProductsSale(APIView):

    def get(self, request, material, group, item):
        material = Materials.objects.get(ph = material, onSale = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, onSale = 1)
        inv_item = InvItems.objects.get(ps = item, groups = group_item, onSale = 1)
        products = Products.objects.filter(items = inv_item, onSale = 1)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductsSerializer(products, many=True)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class getProduct(APIView):

    def get(self, request, material, group, item, product):
        material = Materials.objects.get(ph = material)
        group_item = InvGroups.objects.get(ps = group, materials = material)
        inv_item = InvItems.objects.get(ps = item, groups = group_item)
        product = Products.objects.get(ps = product, items = inv_item)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductSerializer(product)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class getProductNew(APIView):

    def get(self, request, material, group, item, product):
        material = Materials.objects.get(ph = material, nw = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, nw = 1)
        inv_item = InvItems.objects.get(ps = item, groups = group_item, nw = 1)
        product = Products.objects.get(ps = product, items = inv_item, nw = 1)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductSerializer(product)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class getProductSale(APIView):

    def get(self, request, material, group, item, product):
        material = Materials.objects.get(ph = material, onSale = 1)
        group_item = InvGroups.objects.get(ps = group, materials = material, onSale = 1)
        inv_item = InvItems.objects.get(ps = item, groups = group_item, onSale = 1)
        product = Products.objects.get(ps = product, items = inv_item, onSale = 1)
        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductSerializer(product)
        context['itms'][0].update({'prs': serializer.data})

        return JsonResponse(context, safe=False)


class Product(APIView):

    def post(self, request):
        material = request.data['material'][0]
        group = request.data['group'][0]
        item = request.data['item'][0]
        product = request.data['product'][0]
        token = request.data['token']

        material = Materials.objects.get(ph = material)
        group_item = InvGroups.objects.get(ps = group, materials = material)
        inv_item = InvItems.objects.get(ps = item, groups = group_item)
        product = Products.objects.get(pk = product, items = inv_item)

        context = {'itms': [{'id': inv_item.ps, 'izd': inv_item.izd, 'name': inv_item.name}]}
        serializer = ProductSerializer(product)
        context['itms'][0].update({'prs': serializer.data})

        if token != []:
            user = User.objects.get(id = Token.objects.get(key = token[0]).user_id)

            try:
                venezia_prices = user.Venezia.prices
                venezia_stock = user.Venezia.stock
            except:
                venezia_prices = True
                venezia_stock = True

            try:
                quartz_prices = user.Quartz.prices
                quartz_stock = user.Quartz.stock
            except:
                quartz_prices = False
                quartz_stock = False

            try:
                charme_prices = user.Charme.prices
                charme_stock = user.Charme.stock
            except:
                charme_prices = False
                charme_stock = True

        else:
            venezia_prices = True
            venezia_stock = True
            quartz_prices = False
            quartz_stock = False
            charme_prices = False
            charme_stock = True

        if inv_item.pro == 'Venezia':
            if venezia_prices == False or venezia_stock == False:
                context['itms'][0]['prs']['cntRUB'] = 'По запросу'
                context['itms'][0]['prs']['cntUSD'] = 'По запросу'
                context['itms'][0]['prs']['cntEUR'] = 'По запросу'
            if venezia_stock == False:
                context['itms'][0]['prs']['sklad'] = "В наличии"
                context['itms'][0]['prs']['ps'] = "-"
                context['itms'][0]['prs']['bl'] = "-"

        if inv_item.pro == 'Quartz':
            if quartz_prices == False or quartz_stock == False:
                context['itms'][0]['prs']['cntRUB'] = 'По запросу'
                context['itms'][0]['prs']['cntUSD'] = 'По запросу'
                context['itms'][0]['prs']['cntEUR'] = 'По запросу'
            if quartz_stock == False:
                context['itms'][0]['prs']['sklad'] = "В наличии"
                context['itms'][0]['prs']['ps'] = "-"
                context['itms'][0]['prs']['bl'] = "-"
        
        if inv_item.pro == 'Charme':
            if charme_prices == False or charme_stock == False:
                context['itms'][0]['prs']['cntRUB'] = 'По запросу'
                context['itms'][0]['prs']['cntUSD'] = 'По запросу'
                context['itms'][0]['prs']['cntEUR'] = 'По запросу'
            if charme_stock == False:
                context['itms'][0]['prs']['sklad'] = "В наличии"
                context['itms'][0]['prs']['ps'] = "-"
                context['itms'][0]['prs']['bl'] = "-"

        context['path'] = {'material' : material.mt, 'group' : group_item.gr, 'item' : inv_item.name, 'product': product.ps}

        return JsonResponse(context, safe=False)


class getFilters(APIView):

    def get(self, request):
        material_filter_mt = sorted(list(Materials.objects.values_list('mt', flat=True).exclude(mt__isnull=True).distinct()))
        group_filter_co = sorted(list(InvGroups.objects.values_list('co', flat=True).exclude(co__isnull=True).distinct()))
        group_filter_cl = sorted(list(InvGroups.objects.values_list('cl', flat=True).exclude(cl__isnull=True).distinct()))
        item_filter_izd = sorted(list(InvItems.objects.values_list('izd', flat=True).exclude(izd__isnull=True).distinct()))
        item_filter_thn = sorted(list(InvItems.objects.values_list('thn', flat=True).exclude(thn__isnull=True).distinct()))
        item_filter_obr = sorted(list(InvItems.objects.values_list('obr', flat=True).exclude(obr__isnull=True).distinct()))

        try:
            product_filter_skl = [sity[sklad] for sklad in Products.objects.values_list('skl', flat=True).exclude(skl__isnull=True).distinct()]
            product_filter_skl.sort()
        except:
            pass
        
        min_max_price_RUB_product_filter = Products.objects.exclude(cntRUB = '') \
            .annotate(rub = Cast('cntRUB', output_field=FloatField())).aggregate(Max('rub'), Min('rub'))
        min_max_price_USD_product_filter = Products.objects.exclude(cntUSD = '') \
            .annotate(usd = Cast('cntUSD', output_field=FloatField())).aggregate(Max('usd'), Min('usd'))
        min_max_price_EUR_product_filter = Products.objects.exclude(cntEUR = '') \
            .annotate(eur = Cast('cntEUR', output_field=FloatField())).aggregate(Max('eur'), Min('eur'))
        min_max_le_product_filter = Products.objects.exclude(le = '') \
            .annotate(length = Cast('le', output_field=FloatField())).aggregate(Max('length'), Min('length'))
        min_max_he_product_filter = Products.objects.exclude(he = '') \
            .annotate(height = Cast('he', output_field=FloatField())).aggregate(Max('height'), Min('height'))
        
        context = {'filters': {'materials': material_filter_mt, 'izdelie': item_filter_izd, \
            'colors': group_filter_cl, 'countries': group_filter_co, 'obrabotka': item_filter_obr, \
            'thickness': item_filter_thn, 'sklad': product_filter_skl, 'sizas': {'le': min_max_le_product_filter, \
            'he': min_max_he_product_filter}, 'prices': {'price_RUB': min_max_price_RUB_product_filter, \
            'price_USD': min_max_price_USD_product_filter, 'price_EUR': min_max_price_EUR_product_filter}}}
        
        return JsonResponse(context, safe=False)


class getUpperFilters(APIView):

    def get(self, request):
        izd_upper_filter = list(InvItems.objects.values_list('izd', flat=True).exclude(izd__isnull=True).distinct())
        context = {'izd': izd_upper_filter}

        return JsonResponse(context, safe=False)


class upperFilter(APIView):

    def get(self, request, izd):
        context = {}
        materials_list = list(InvItems.objects.filter(izd = izd).values_list('groups__materials__mt', flat=True).distinct())

        for mnt in materials_list:
            mnt_ph = Materials.objects.get(mt = mnt).ph
            context.update({mnt: []})
            groups = list(InvItems.objects.filter(izd = izd, groups__materials__mt = mnt).values_list('groups__gr', flat=True).distinct())
            for group in groups:
                group_ps = InvGroups.objects.get(gr = group, materials__mt = mnt).ps
                context[mnt].append({'gr' : group, 'route': '/'+mnt_ph+'/'+group_ps+'/'})
        
        return JsonResponse(context, safe=False)


def GetFilterMaterial(material, nw, on_sale):
    if material == []:
        material_group = Materials.objects.all()
    else:
        material_group = Materials.objects.filter(mt__in = material)
    if nw == 1:
        material_group = material_group.filter(nw = 1)
    if on_sale == 1:
        material_group = material_group.filter(onSale = 1)

    return material_group


def GetFilterGroup(material_group, countries, colors, nw, on_sale):
    inv_groups = InvGroups.objects.filter(materials__in = material_group)
    if countries != []:
        inv_groups = inv_groups.filter(co__in = countries)
    if colors != []:
        inv_groups = inv_groups.filter(cl__in = colors)
    if nw == 1:
        inv_groups = inv_groups.filter(nw = 1)
    if on_sale == 1:
        inv_groups = inv_groups.filter(onSale = 1)

    return inv_groups


def GetFilterItem(group_filter, izdelie, thickness, obrabotka, nw, on_sale):
    item_filter = InvItems.objects.filter(groups__in = group_filter)
    if izdelie != []:
        item_filter = item_filter.filter(izd__in = izdelie)
    if thickness != []:
        item_filter = item_filter.filter(thn__in = thickness)
    if obrabotka != []:
        item_filter = item_filter.filter(obr__in = obrabotka)
    if nw == 1:
        item_filter = item_filter.filter(nw = 1)
    if on_sale == 1:
        item_filter = item_filter.filter(onSale = 1)

    return item_filter


def GetFilterProduct(inv_item, sklad, le_min, le_max, he_min, he_max, cnt, cnt_min, cnt_max, nw, on_sale):
    product_filter = Products.objects.filter(items__in = inv_item)
    if sklad != []:
        skl = []
        for k, v in sity.items():
            for i in sklad:
                if v == i:
                    skl.append(k)
        product_filter = product_filter.filter(skl__in = skl)

    if nw == 1:
        product_filter = product_filter.filter(nw = 1)
    if on_sale == 1:
        product_filter = product_filter.filter(onSale = 1)
    if le_min != []:
        product_filter = product_filter.annotate(length = Cast('le', output_field=FloatField())).filter(length__gte = le_min[0])
    if le_max != []:
        product_filter = product_filter.annotate(length = Cast('le', output_field=FloatField())).filter(length__lte = le_max[0])
    if he_min != []:
        product_filter = product_filter.annotate(height = Cast('he', output_field=FloatField())).filter(height__gte = he_min[0])
    if he_max != []:
        product_filter = product_filter.annotate(height = Cast('he', output_field=FloatField())).filter(height__lte = he_max[0])

    if cnt_min != [] or cnt_max != []:
        if cnt[0] == 'rub':
            if cnt_min != []:
                product_filter = product_filter.annotate(rub = Cast('cntRUB', output_field=FloatField())).filter(rub__gte = cnt_min[0])
            if cnt_max != []:
                product_filter = product_filter.annotate(rub = Cast('cntRUB', output_field=FloatField())).filter(rub__lte = cnt_max[0])
        if cnt[0] == 'usd':
            if cnt_min != []:
                product_filter = product_filter.annotate(usd = Cast('cntUSD', output_field=FloatField())).filter(usd__gte = cnt_min[0])
            if cnt_max != []:
                product_filter = product_filter.annotate(usd = Cast('cntUSD', output_field=FloatField())).filter(usd__lte = cnt_max[0])
        if cnt[0] == 'eur':
            if cnt_min != []:
                product_filter = product_filter.annotate(eur = Cast('cntEUR', output_field=FloatField())).filter(eur__gte = cnt_min[0])
            if cnt_max != []:
                product_filter = product_filter.annotate(eur = Cast('cntEUR', output_field=FloatField())).filter(eur__lte = cnt_max[0])

    return product_filter


def FilterPrices3lvl(item_queryset, venezia_prices, quartz_prices, charme_prices, venezia_stock, quartz_stock, charme_stock):
    prices = {}
    context = {}
    item_queryset_venezia = item_queryset.filter(pro = "Venezia")
    item_queryset_quartz = item_queryset.filter(pro = "Quartz")
    item_queryset_charme = item_queryset.filter(pro = "Charme")

    if venezia_prices == False or venezia_stock == False:
        serializer = InvItemsSerializer(item_queryset_venezia, many=True)
        prices['itms_venezia'] = serializer.data
        for it in prices['itms_venezia']:
            it["prEUR"] = "По запросу"
            it["prUSD"] = "По запросу"
            it["prRUB"] = "По запросу"
    else:
        serializer = InvItemsSerializer(item_queryset_venezia, many=True)
        prices['itms_venezia'] = serializer.data

    if quartz_prices == False or quartz_stock == False:
        serializer = InvItemsSerializer(item_queryset_quartz, many=True)
        prices['itms_quartz'] = serializer.data
        for it in prices['itms_quartz']:
            it["prEUR"] = "По запросу"
            it["prUSD"] = "По запросу"
            it["prRUB"] = "По запросу"
    else:
        serializer = InvItemsSerializer(item_queryset_quartz, many=True)
        prices['itms_quartz'] = serializer.data

    if charme_prices == False or charme_stock == False:
        serializer = InvItemsSerializer(item_queryset_charme, many=True)
        prices['itms_charme'] = serializer.data
        for it in prices['itms_charme']:
            it["prEUR"] = "По запросу"
            it["prUSD"] = "По запросу"
            it["prRUB"] = "По запросу"
    else:
        serializer = InvItemsSerializer(item_queryset_charme, many=True)
        prices['itms_charme'] = serializer.data
    context.update({'itms' : prices['itms_venezia']})
    for itm_q in prices['itms_quartz']:
        context['itms'].append(itm_q)
    for itm_c in prices['itms_charme']:
        context['itms'].append(itm_c)
    return context


def FilterPrices4lvl(prod_filter, venezia_prices, quartz_prices, charme_prices, venezia_stock, quartz_stock, charme_stock):
    prices = {}
    context = {}
    product_venezia = prod_filter.filter(items__pro = "Venezia")
    product_quartz = prod_filter.filter(items__pro = "Quartz")
    product_charme = prod_filter.filter(items__pro = "Charme")

    if len(product_venezia) != 0:
        if venezia_prices == False or venezia_stock == False:
            if venezia_stock == False:
                product_venezia = product_venezia.last()
                serializer = ProductsSerializer(product_venezia)
                prices['prod_venezia'] = []
                prices['prod_venezia'].append(serializer.data)
            else:
                serializer = ProductsSerializer(product_venezia, many=True)
                prices['prod_venezia'] = serializer.data
            for it in prices['prod_venezia']:
                it["cntRUB"] = "По запросу"
                it["cntUSD"] = "По запросу"
                it["cntEUR"] = "По запросу"
                if venezia_stock == False:
                    it["sklad"] = "В наличии"
                    it["ps"] = "-"
                    it["bl"] = "-"
        else:
            serializer = ProductsSerializer(product_venezia, many=True)
            prices['prod_venezia'] = serializer.data
    else: prices['prod_venezia'] = []

    if len(product_quartz) != 0:
        if quartz_prices == False or quartz_stock == False:
            if quartz_stock == False:
                product_quartz = product_quartz.last()
                serializer = ProductsSerializer(product_quartz)
                prices['prod_quartz'] = []
                prices['prod_quartz'].append(serializer.data)
            else:
                serializer = ProductsSerializer(product_quartz, many=True)
                prices['prod_quartz'] = serializer.data
            for it in prices['prod_quartz']:
                it["cntRUB"] = "По запросу"
                it["cntUSD"] = "По запросу"
                it["cntEUR"] = "По запросу"
                if quartz_stock == False:
                    it["skl"] = "В наличии"
                    it["ps"] = "-"
                    it["bl"] = "-"
        else:
            serializer = ProductsSerializer(product_quartz, many=True)
            prices['prod_quartz'] = serializer.data

    else:
        prices['prod_quartz'] = []

    if len(product_charme) != 0:
        if charme_prices == False or charme_stock == False:
            if charme_stock == False:
                product_charme = product_charme.last()
                serializer = ProductsSerializer(product_charme)
                prices['prod_charme'] = []
                prices['prod_charme'].append(serializer.data)
            else:
                serializer = ProductsSerializer(product_charme, many=True)
                prices['prod_charme'] = serializer.data
            for it in prices['prod_charme']:
                it["cntRUB"] = "По запросу"
                it["cntUSD"] = "По запросу"
                it["cntEUR"] = "По запросу"
                if charme_stock == False:
                    it["skl"] = "В наличии"
                    it["ps"] = "-"
                    it["bl"] = "-"
        else:
            serializer = ProductsSerializer(product_charme, many=True)
            prices['prod_charme'] = serializer.data
    else:
        prices['prod_charme'] = []

    context.update({'prs' : prices['prod_venezia']})
    
    for prod_q in prices['prod_quartz']:
        context['prs'].append(prod_q)
    for prod_c in prices['prod_charme']:
        context['prs'].append(prod_c)
    
    return context


def Count_SKU_and_KW(prod_filter, level):
    products_count = {}

    if level == 1:
        materials_count = prod_filter.values(material_ps=F('items__groups__materials__ps')).annotate(kw = Sum('kw'))
        for material in materials_count:
            sku = len(list(prod_filter.filter(items__groups__materials__ps = material['material_ps']).values_list('items__groups', flat=True).distinct()))
            products_count.update({material['material_ps']: {'kw': material['kw'], 'sku': sku}})
        return products_count

    if level == 2:
        groups_count = prod_filter.values(group_ps=F('items__groups__ps')).annotate(kw = Sum('kw'))
        for group in groups_count:
            sku = len(list(prod_filter.filter(items__groups__ps = group['group_ps']).values_list('items', flat=True).distinct()))
            products_count.update({group['group_ps']: {'kw': group['kw'], 'sku': sku}})
        return products_count

    if level == 3:
        items_count = prod_filter.values(item_ps=F('items__ps')).annotate(kw = Sum('kw'), sku = Count('ps'))
        for item in items_count:
            products_count.update({item['item_ps']: {'kw': item['kw'], 'sku': item['sku']}})
        return products_count


class Filter(APIView):

    def post(self, request):
        level = int(request.data['level'][0])
        material = request.data['materials']
        token = request.data['token']

        if token != []:
            user = User.objects.get(id = Token.objects.get(key = token[0]).user_id)

            try:
                venezia_prices = user.Venezia.prices
                venezia_stock = user.Venezia.stock
            except:
                venezia_prices = True
                venezia_stock = True

            try:
                quartz_prices = user.Quartz.prices
                quartz_stock = user.Quartz.stock
            except:
                quartz_prices = False
                quartz_stock = False

            try:
                charme_prices = user.Charme.prices
                charme_stock = user.Charme.stock
            except:
                charme_prices = False
                charme_stock = True

        else:
            venezia_prices = True
            venezia_stock = True
            quartz_prices = False
            quartz_stock = False
            charme_prices = False
            charme_stock = True

        if request.data['nw'] == []:
            nw = 0
        else: nw = 1
        if request.data['on_sale'] == []:
            on_sale = 0
        else: on_sale = 1

        ''' Filter 2 lvl '''
        countries = request.data['countries']
        colors = request.data['colors']

        ''' Filter 3 lvl '''
        izdelie = request.data['izdelie']
        thickness = request.data['thickness']
        obrabotka = request.data['obrabotka']
        group = request.data['groups']

        ''' Filter 4 lvl '''
        sklad = request.data['sklad']
        le_min = request.data['le_min']
        le_max = request.data['le_max']
        he_min = request.data['he_min']
        he_max = request.data['he_max']
        cnt = request.data['cnt']
        cnt_min = request.data['cnt_min']
        cnt_max = request.data['cnt_max']
        item = request.data['items']

        context = {}

        material_filter = GetFilterMaterial(material, nw, on_sale)

        group_filter = GetFilterGroup(material_filter, countries, colors, nw, on_sale)

        if group == []:
            inv_items = GetFilterItem(group_filter, izdelie, thickness, obrabotka, nw, on_sale)
        else:
            group_filter_f = InvGroups.objects.filter(ps = group[0])
            inv_items = GetFilterItem(group_filter_f, izdelie, thickness, obrabotka, nw, on_sale)

        if item == []:
            prod_filter = GetFilterProduct(inv_items, sklad, le_min, le_max, he_min, he_max, cnt, cnt_min, cnt_max, nw, on_sale)
        else:
            inv_items_f = InvItems.objects.filter(ps = item[0])
            prod_filter = GetFilterProduct(inv_items_f, sklad, le_min, le_max, he_min, he_max, cnt, cnt_min, cnt_max, nw, on_sale)

        if level == 1:
            count_sku_kw = Count_SKU_and_KW(prod_filter, level)
            material_queryset = Materials.objects.filter(
                id__in=list(prod_filter.values_list('items__groups__materials__id', flat=True).distinct()))
            serializer = MaterialsSerializer(material_queryset.extra(
                select={'po_int': 'CAST(po AS UNSIGNED)'}).order_by('po_int'), many=True)
            context['mts'] = serializer.data
            for material_data in context['mts']:
                info = count_sku_kw[material_data['ps']]
                material_data["kw"] = float('{:.2f}'.format(info['kw']))
                material_data["sku"] = info['sku']
            
            return JsonResponse(context, safe=False)

        if level == 2:
            count_sku_kw = Count_SKU_and_KW(prod_filter, level)
            group_queryset = InvGroups.objects.filter(
                id__in=list(prod_filter.values_list('items__groups__id', flat=True).distinct()))
            serializer = InvGroupsSerializer(group_queryset, many=True)
            context['grs'] = serializer.data
            for group_data in context['grs']:
                info = count_sku_kw[group_data['ps']]
                group_data["kw"] = float('{:.2f}'.format(info['kw']))
                group_data["sku"] = info['sku']
            
            return JsonResponse(context, safe=False)

        if level == 3:
            count_sku_kw = Count_SKU_and_KW(prod_filter, level)
            item_queryset = InvItems.objects.filter(id__in=list(prod_filter.values_list('items__id', flat=True).distinct()))
            context = FilterPrices3lvl(item_queryset, venezia_prices, quartz_prices, charme_prices, venezia_stock, quartz_stock, charme_stock)
            try:
                element = item_queryset.last()
                context['path'] = {'material' : element.groups.materials.mt, 'group' : element.groups.gr}
            except:
                context['path'] = {'material' : material[0], 'group' : InvGroups.objects.get(ps = group[0]).gr}

            for item_data in context['itms']:
                info = count_sku_kw[item_data['ps']]
                item_data["kw"] = float('{:.2f}'.format(info['kw']))
                item_data["sku"] = info['sku']
            
            return JsonResponse(context, safe=False)

        if level == 4:
            context = FilterPrices4lvl(prod_filter, venezia_prices, quartz_prices, charme_prices, venezia_stock, quartz_stock, charme_stock)
            try:
                element = prod_filter.last()
                context['path'] = {'material' : element.items.groups.materials.mt, 'group' : element.items.groups.gr, 'item' : element.items.name}
            except:
                context['path'] = {'material' : material[0], 'group' : InvGroups.objects.get(ps = group[0]).gr, 'item' : InvItems.objects.get(ps = item[0]).name}
            
            return JsonResponse(context, safe=False)


class addFavourite(APIView):

    serializer_class = UserAndProduct

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            product = Products.objects.get(ps = valid_user_data['id_product'])
            token = Token.objects.get(key = valid_user_data['token'])
            user = token.user
            user.favourites.add(product)
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)


class deleteFavourite(APIView):

    serializer_class = UserAndProduct

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})

        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            product = Products.objects.get(ps = valid_user_data['id_product'])
            token = Token.objects.get(key = valid_user_data['token'])
            user = token.user
            try:
                user.favourites.remove(product)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_204_NO_CONTENT)

class addViewed(APIView):
    serializer_class = UserAndProduct

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})
        
        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            product = Products.objects.get(ps = valid_user_data['id_product'])
            token = Token.objects.get(key = valid_user_data['token'])
            user = token.user
            if user.viewed.count() > 10 :
                user.viewed.remove(user.viewed.first())
                user.viewed.add(product)
            else:
                user.viewed.add(product)
            user.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return JsonResponse({'error':'data is not valid'}, safe=False)


class deleteViewed(APIView):

    serializer_class = UserAndProduct

    def post(self, request, format=None):

        user_data = self.serializer_class(data=request.data, context={'request': request})
        
        if user_data.is_valid():
            valid_user_data = user_data.validated_data
            product = Products.objects.get(ps = valid_user_data['id_product'])
            token = Token.objects.get(key = valid_user_data['token'])
            user = token.user
            try:
                user.viewed.remove(product)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_204_NO_CONTENT)


class showSelectedFavourite(APIView):

    def post(self, request):
        request_token = request.data['token']
        token = Token.objects.get(key = request_token)
        products = list()
        for product in token.user.favourites.all():
            products.append(product.ps)
        return Response({'products':products})


class showSelectedViewed(APIView):

    def post(self, request):
        request_token = request.data['token']
        token = Token.objects.get(key = request_token)
        products = list()
        for product in token.user.viewed.all():
            products.append(product.ps)
        return Response({'products':products})


class showFavourite(APIView):

    def post(self, request):
        request_token = request.data['token']
        token = Token.objects.get(key = request_token)
        products = token.user.favourites.all()
        context = {}

        for product in products:
            context[product.ps] = {}
            context[product.ps]['ps'] = product.ps
            context[product.ps]['name'] = product.items.name
            if product.items.izd == 'Слэбы':
                context[product.ps]['izd'] = 'Слэб'
            else:
                context[product.ps]['izd'] = product.items.izd

            context[product.ps]['bl'] = product.bl
            context[product.ps]['sklad'] = product.sklad
            context[product.ps]['price'] = product.cntRUB
            context[product.ps]['le'] = product.le
            context[product.ps]['he'] = product.he
            context[product.ps]['ostkw'] = product.os
            context[product.ps]['ostsh'] = product.ossht
            context[product.ps]['photo'] = product.photo_product

            if product.items.izd == 'Слэбы' or product.items.izd == 'Полоса':
                context[product.ps]['route'] = 'https://catalog-veneziastone.ru/#/{}/{}/{}/{}/'.\
                format(product.items.groups.materials.ph, product.items.groups.ps, product.items.ps, product.ps)
            else:
                context[product.ps]['route'] = 'https://catalog-veneziastone.ru/#/{}/{}/{}/'.\
                format(product.items.groups.materials.ph, product.items.groups.ps, product.items.ps)

            if product.le and product.he:
                context[product.ps]['kw'] = "0.0"

        return JsonResponse(context, safe=False)


class showViewed(APIView):

    def post(self, request):
        request_token = request.data['token']
        token = Token.objects.get(key = request_token)
        products = token.user.viewed.all()
        context = {}
        for product in products:
            context[product.ps] = {}
            context[product.ps]['ps'] = product.ps
            context[product.ps]['name'] = product.items.name
            if product.items.izd == 'Слэбы':
                context[product.ps]['izd'] = 'Слэб'
            else:
                context[product.ps]['izd'] = product.items.izd

            context[product.ps]['bl'] = product.bl
            context[product.ps]['sklad'] = product.sklad
            context[product.ps]['price'] = product.cntRUB
            context[product.ps]['le'] = product.le
            context[product.ps]['he'] = product.he
            context[product.ps]['ostkw'] = product.os
            context[product.ps]['ostsh'] = product.ossht
            context[product.ps]['photo'] = product.photo_product

            if product.items.izd == 'Слэбы' or product.items.izd == 'Полоса':
                context[product.ps]['route'] = 'https://catalog-veneziastone.ru/#/{}/{}/{}/{}/'.\
                format(product.items.groups.materials.ph, product.items.groups.ps, product.items.ps, product.ps)
            else:
                context[product.ps]['route'] = 'https://catalog-veneziastone.ru/#/{}/{}/{}/'.\
                format(product.items.groups.materials.ph, product.items.groups.ps, product.items.ps)

            context[product.ps]['kw'] = "0.0"

        return JsonResponse(context, safe=False)


class Search(APIView):

    def get(self, request, nm):

        if ord(nm[0]) < 123:
            searched_materials = Materials.objects.filter(ph__icontains = nm)
        else:
            searched_materials = Materials.objects.filter(mt__icontains = nm)

        serializer_m = MaterialsSerializer(searched_materials, many=True)
        searched_groups = InvGroups.objects.filter(gr__icontains = nm)
        serializer_g = InvGroupsSerializer(searched_groups, many=True)
        searched_items = InvItems.objects.filter(name__icontains = nm)
        serializer_i = InvItemsSerializer(searched_items, many=True)
        searched_products = Products.objects.filter(ps__icontains = nm)
        serializer_p = ProductsSerializer(searched_products, many=True)
        context = {'mts': serializer_m.data, 'grs': serializer_g.data, 'itms': serializer_i.data, 'prs': serializer_p.data}

        return JsonResponse(context, safe=False)
