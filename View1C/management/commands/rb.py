import kronos
from io import BytesIO
import requests
import time

from colormap.colors import rgb2hex
from django.core.management.base import BaseCommand
from PIL import Image

from View1C.models import Materials, InvGroups, InvItems, Products

def get_colors(url, numcolors, resize=150):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.copy()

    #Уменьшаем масштаб картинки для увеличения скорости обработки
    img.thumbnail((resize, resize))

    #Извлекаем цвета из картинки
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    colors = []

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

@kronos.register('0 0,4,8,12,16,20 * * *')
class Command(BaseCommand):
    help = 'Start restore database'

    def handle(self, *args, **options):
        start_time = time.time()

        # ADD MATERIALS IN DATABASE ###
        materials_in_db = Materials.objects.all().only('ph')
        groups_in_db = InvGroups.objects.all().only('ps')
        items_in_db = InvItems.objects.all().only('ps')
        products_in_db = Products.objects.all().only('pk')
        json_data = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/getProductsAll',
            data={}, auth=('', '')).json()
        
        currencies_list = json_data['ExchangeRate']
        usd = float(currencies_list[0]['USD'])
        eur = float(currencies_list[0]['EUR'])
        
        materials = []
        groups = []
        items = []
        products = []
        colors_group_by_material = dict()
        colors_items_by_group = dict()
        
        for mts in json_data['mts']:
            material = Materials.objects.get_or_create(ph = mts['ph'])[0]
            material.mt = mts['mt']
            if mts['photo_material']:
                material.photo_material = mts['photo_material']
            else:
                material.photo_material = 'https://catalog-veneziastone.ru/media/photo.gif'
            material.sku = mts['sku']
            material.kw = mts['kw']
            material.po = mts['po']
            material.photo_type = "Фото текстуры"
            material.save()
            materials.append(material.ph)
            colors_material = {}
        
            for grp in mts['grs']:
                group = InvGroups.objects.get_or_create(ps = grp['id'])[0]
                start_time2 = time.time()
                group.gr = grp['gr']
                group.co = grp['co']
                group.cl = grp['cl']
                try:
                    group.nam = str(grp['nam'])
                except:
                    pass
                group.sku = grp['sku']
                group.materials = material

                if grp['pr']:
                    price = float(grp['pr'])
                    group.prRUB = round(price)
                    group.prUSD = round(price/usd)
                    group.prEUR = round(price/eur)
                else:
                    try:
                        group.prRUB = round(group.prRUB)
                        group.prUSD = round(group.prUSD)
                        group.prEUR = round(group.prEUR)
                    except:
                        pass

                group.kw = grp['kw']

                if grp['file']:
                    group.photo_groups = grp['file']
                else:
                    group.photo_groups = 'https://catalog-veneziastone.ru/media/photo.gif'

                group.photo_type = "Фото текстуры"
                group.save()
                groups.append(group.ps)
        
                try:
                    colors_material[group.ps] = get_colors(group.photo_groups,1)
                except:
                    colors_material[group.ps] = "#FFFFFF"
                colors_group_by_material[material.ph] = sorted(colors_material.items(), key=lambda x: x[1])

                colors_group = {}

                for itm in grp['itms']:
                    item = InvItems.objects.get_or_create(ps = itm['id'])[0]
                    item.name = itm['name']
                    item.izd = itm['izd']
                    item.pro = itm['pro']
                    item.thn = itm['thn']
                    item.obr = itm['obr']
                    item.kat = itm['kat']
                    item.qua = itm['qua']
                    item.cp = itm['cp']
                    item.cs = itm['cs']
                    item.kw = itm['kw']
                    item.sku = itm['sku']
                    item.groups = group
        
                    if itm['pr']:
                        price = float(itm['pr'])
                        item.prRUB = round(price)
                        item.prUSD = round(price/usd)
                        item.prEUR = round(price/eur)
                    else:
                        try:
                            item.prRUB = round(item.prRUB)
                            item.prUSD = round(item.prUSD)
                            item.prEUR = round(item.prEUR)
                        except:
                            pass

                    if itm['photo']:
                        item.photo_item = itm['photo']
                        item.photo_type = "Фото текстуры"
                        try:
                            colors_group[item.ps] = get_colors(item.photo_item,1)
                        except:
                            colors_group[item.ps] = "#FFFFFF"
                    else:
                        item.photo_item = item.groups.photo_groups
                        item.photo_type = item.groups.photo_type
                        if item.photo_item == 'https://catalog-veneziastone.ru/media/photo.gif':
                            colors_group[item.ps] = "#FFFFFF"
                        else:
                            try:
                                colors_group[item.ps] = get_colors(item.photo_item,1)
                            except:
                                colors_group[item.ps] = "#FFFFFF"
                    item.save()
                    items.append(item.ps)

                    colors_items_by_group[group.ps] = sorted(colors_group.items(), key=lambda x: x[1])

                    colors_item = {}

                    for prod in itm['prs']:
                        product = Products.objects.get_or_create(ps = prod['id'], skl = prod['skl'])[0]
                        product.bl = prod['bl']
                        product.bty = prod['bty']
                        product.le = prod['le']
                        product.he = prod['he']
                        product.sco = prod['sco'] if prod['sco'] else 0
                        product.kw = prod['kw'] if prod['kw'] else 0
                        product.kolvo = prod['kolvo'] if prod['kolvo'] else 0
                        product.skl = prod['skl']
                        product.os = prod['os']
                        product.obos = prod['obos']
                        product.ossht = prod['ossht']
                        product.items = item

                        if prod['cnt']:
                            price = float(prod['cnt'])
                            product.cntRUB = round(price)
                            product.cntUSD = round(price/usd)
                            product.cntEUR = round(price/eur)
                        else:
                            try:
                                product.cntRUB = round(product.cntRUB)
                                product.cntUSD = round(product.cntUSD)
                                product.cntEUR = round(product.cntEUR)
                            except:
                                pass

                        if prod['photo']:
                            product.photo_product = prod['photo']
                            product.typeFoto = "Фото слэба"
                            try:
                                product.color_range = get_colors(product.photo_product,9)
                            except:
                                product.color_range = ["#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF"]

                        elif prod['photobl']:
                            product.photo_product = prod['photobl']
                            product.typeFoto = "Фото пачки"
                            try:
                                product.color_range = get_colors(product.photo_product,9)
                            except:
                                product.color_range = ["#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF"]

                        else:
                            product.photo_product = product.items.photo_item
                            product.typeFoto = product.items.photo_type
                            if product.photo_product == 'https://catalog-veneziastone.ru/media/photo.gif':
                                product.color_range = ["#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                            else:
                                try:
                                    product.color_range = get_colors(product.photo_product,9)
                                except:
                                    product.color_range = ["#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF"]

                        if prod['photobl']:
                            product.photobl = prod['photobl']
                        else:
                            product.photobl = product.items.photo_item

                        product.nw = prod['nw']
                        if product.nw:
                            product.items.nw = 1
                            product.items.save()
                            product.items.groups.nw = 1
                            product.items.groups.save()
                            product.items.groups.materials.nw= 1
                            product.items.groups.materials.save()
                        product.onSale = prod['onSale']
                        if product.onSale:
                            product.items.onSale = 1
                            product.items.save()
                            product.items.groups.onSale = 1
                            product.items.groups.save()
                            product.items.groups.materials.onSale= 1
                            product.items.groups.materials.save()
                        product.pz = prod['pz']
                        if product.pz:
                            product.items.pz = 1
                            product.items.save()
                            product.items.groups.pz = 1
                            product.items.groups.save()
                            product.items.groups.materials.pz= 1
                            product.items.groups.materials.save()

                        product.save()
                        products.append(product.pk)

        if materials_in_db:
            [material_db.delete() for material_db in materials_in_db if (material_db.ph not in materials)]
        if groups_in_db:
            [group_db.delete() for group_db in groups_in_db if (group_db.ps not in groups)]
        if items_in_db:
            [item_db.delete() for item_db in items_in_db if (item_db.ps not in items)]
        if products_in_db:
            [product_db.delete() for product_db in products_in_db if (product_db.pk not in products)]

        for mat, group_dict in colors_group_by_material.items():
            material = Materials.objects.get(ph = mat)
            count = 1
            for group_ps, id_color in group_dict:
                group = InvGroups.objects.get(ps = group_ps)
                group.id_color_sort = count
                group.save()
                count += 1

        for group_ps, item_dict in colors_items_by_group.items():
            group = InvGroups.objects.get(ps = group_ps)
            count = 1
            for item_ps, id_color in item_dict:
                item = InvItems.objects.get(ps = item_ps)
                item.id_color_sort = count
                item.save()
                count += 1
