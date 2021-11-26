from io import BytesIO
import requests, time, json
import hashlib

from colormap.colors import rgb2hex
from currency_converter import CurrencyConverter
from django.core.management.base import BaseCommand
from PIL import Image

from View1C.models import Materials, InvGroups, InvItems, Products, Hash

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


class Command(BaseCommand):
    help = 'Start restore database'

    def handle(self, *args, **options):

        curr = CurrencyConverter()
        usd = curr.convert(1, 'RUB', 'USD')
        eur = curr.convert(1, 'RUB', 'EUR')

        # ADD MATERIALS IN DATABASE ###
        materials_in_db = Materials.objects.all()

        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/Materials', data={}, auth=('', ''))
        if resp.status_code == 200:
            hash_object, created = Hash.objects.get_or_create(name = 'materials_hash')
            hash_val = hashlib.md5(resp.text.encode('utf-8')).hexdigest()

            if not created:
                if hash_object.value == hash_val:
                    pass
                else:
                    hash_object.value = hash_val
                    hash_object.save()
                    json_data = json.loads(resp.text)
                    materials = []
                    
                    for mts in json_data['mts']:
                        material, created = Materials.objects.get_or_create(ps = mts['ps'])
                        material.mt = mts['mt']
                        material.ph = mts['ph']
                        if mts['photo_material']:
                            material.photo_material = mts['photo_material']
                        material.sku = mts['sku']
                        material.kw = mts['kw']
                        material.save()
                        materials.append(material.ps)

                    for material_db in materials_in_db:
                        if (material_db.ps not in materials):
                            material_db.delete()

            else:
                hash_object.value = hash_val
                hash_object.save()
                json_data = json.loads(resp.text)
                materials = []
                for mts in json_data['mts']:
                    material, created = Materials.objects.get_or_create(ps = mts['ps'])
                    material.mt = mts['mt']
                    material.ph = mts['ph']
                    if mts['photo_material']:
                        material.photo_material = mts['photo_material']
                    material.sku = mts['sku']
                    material.kw = mts['kw']
                    material.save()
                    materials.append(material.ps)
                
                for material_db in materials_in_db:
                        if (material_db.ps not in materials):
                            material_db.delete()

        # ADD GROUPS IN DATABASE ###
        groups_in_db = InvGroups.objects.all()

        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/getInvGroups', data={}, auth=('VeneziaMegafon', 'gbDHrKy9'))
        if resp.status_code == 200:
            hash_object, created = Hash.objects.get_or_create(name = 'inv_groups_hash')
            hash_val = hashlib.md5(resp.text.encode('utf-8')).hexdigest()

            if not created:
                if hash_object.value == hash_val:
                    pass
                else:
                    hash_object.value = hash_val
                    hash_object.save()
                    json_data = json.loads(resp.text)
                    groups = []
                    colors = {}

                    for mts in json_data['mts']:
                        material_group = Materials.objects.get(ps = mts['ps'])
                        colors[material_group.ps] = {}
                        colors_material = dict()

                        for grp in mts['grs']:
                            group, created = InvGroups.objects.get_or_create(ps = grp['id'])
                            group.gr = grp['gr']
                            group.co = grp['co']
                            group.cl = grp['cl']
                            group.nam = grp['nam']
                            group.sku = grp['sku']

                            if grp['pr']:
                                price = float(grp['pr'])
                                group.prRUB = price
                                group.prUSD = round(price*usd,3)
                                group.prEUR = round(price*eur,3)

                            group.kw = grp['kw']
                            group.typeFoto = grp['typeFoto']
                            group.photo_groups = grp['file']
                            try:
                                colors_material[group.ps] = get_colors(group.photo_groups,1)
                            except:
                                colors_material[group.ps] = "#FFFFFF"

                            group.materials = material_group
                            group.save()
                            groups.append(group.ps)
                        colors[material_group.ps] = sorted(colors_material.items(), key=lambda x: x[1])

                    for group_db in groups_in_db:
                        if (group_db.ps not in groups):
                            group_db.delete() 

                    for material_id, inv_groups_colors in colors.items():
                        counter = 1
                        for object in inv_groups_colors:
                            inv_group = InvGroups.objects.get(ps = object[0])
                            inv_group.id_color_sort = counter
                            inv_group.save()
                            counter += 1
            
            else:
                hash_object.value = hash_val
                hash_object.save()
                json_data = json.loads(resp.text)
                groups = []
                colors = {}
                
                for mts in json_data['mts']:
                    material_group = Materials.objects.get(ps = mts['ps'])
                    colors[material_group.ps] = {}
                    colors_material = dict()
                    
                    for grp in mts['grs']:
                        group, created = InvGroups.objects.get_or_create(ps = grp['id'])
                        group.gr = grp['gr']
                        group.co = grp['co']
                        group.cl = grp['cl']
                        group.nam = grp['nam']
                        group.sku = grp['sku']
                        
                        if grp['pr']:
                            price = float(grp['pr'])
                            group.prRUB = price
                            group.prUSD = round(price*usd,3)
                            group.prEUR = round(price*eur,3)
                        
                        group.kw = grp['kw']
                        group.typeFoto = grp['typeFoto']
                        group.photo_groups = grp['file']
                        
                        try:
                            colors_material[group.ps] = get_colors(group.photo_groups,1)
                        except:
                            colors_material[group.ps] = "#FFFFFF"
                        group.materials = material_group
                        group.save()
                        groups.append(group.ps)
                    
                    colors[material_group.ps] = sorted(colors_material.items(), key=lambda x: x[1])
                
                for group_db in groups_in_db:
                    if (group_db.ps not in groups):
                        group_db.delete() 
                
                for material_id, inv_groups_colors in colors.items():
                    counter = 1
                    for object in inv_groups_colors:
                        inv_group = InvGroups.objects.get(ps = object[0])
                        inv_group.id_color_sort = counter
                        inv_group.save()
                        counter += 1

        # # ADD ITEMS IN DATABASE ###
        items_in_db = InvItems.objects.all()

        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/getInvItems', data={}, auth=('VeneziaMegafon', 'gbDHrKy9'))
        if resp.status_code == 200:
            hash_object, created = Hash.objects.get_or_create(name = 'inv_items_hash')
            hash_val = hashlib.md5(resp.text.encode('utf-8')).hexdigest()
            if not created:
                if hash_object.value == hash_val:
                    pass
                else:
                    hash_object.value = hash_val
                    hash_object.save()
                    json_data = json.loads(resp.text)
                    items = []
                    colors = {}
                    
                    for grs in json_data['grs']:
                        groups_item = InvGroups.objects.get(ps = grs['id'])
                        colors[groups_item.ps] = {}
                        colors_inv_groups= {}
                    
                        for itm in grs['itms']:
                            item, created = InvItems.objects.get_or_create(ps = itm['id'])
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
                    
                            if itm['pr']:
                                price = float(itm['pr'])
                                item.prRUB = price
                                item.prUSD = round(price*usd,3)
                                item.prEUR = round(price*eur,3)
                    
                            item.sku = itm['sku']
                            item.typeFoto = itm['phototp']
                    
                            if itm['photo']:
                                item.photo_item = itm['photo']
                                try:
                                    colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                                except:
                                    item.photo_item = item.groups.photo_groups
                                    try:
                                        colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                                    except:
                                        colors_inv_groups[item.ps] = "#FFFFFF"
                            else:
                                item.photo_item = item.groups.photo_groups
                                try:
                                    colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                                except:
                                    colors_inv_groups[item.ps] = "#FFFFFF"
                            item.groups = groups_item
                            item.save()
                            items.append(item.ps)
                    
                        colors[groups_item.ps] = sorted(colors_inv_groups.items(), key=lambda x: x[1])
                    
                    for item_db in items_in_db:
                        if (item_db.ps not in items):
                            item_db.delete()

                    for inv_gr_id, inv_items_colors in colors.items():
                        counter = 1
                        for object in inv_items_colors:
                            inv_item = InvItems.objects.get(ps = object[0])
                            inv_item.id_color_sort = counter
                            inv_item.save()
                            counter += 1
            
            else:
                hash_object.value = hash_val
                hash_object.save()
                json_data = json.loads(resp.text)
                items = []
                colors = {}
            
                for grs in json_data['grs']:
                    groups_item = InvGroups.objects.get(ps = grs['id'])
                    colors[groups_item.ps] = {}
                    colors_inv_groups= {}
            
                    for itm in grs['itms']:
                        item, created = InvItems.objects.get_or_create(ps = itm['id'])
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
                        if itm['pr']:
                            price = float(itm['pr'])
                            item.prRUB = price
                            item.prUSD = round(price*usd,3)
                            item.prEUR = round(price*eur,3)
            
                        item.sku = itm['sku']
                        item.typeFoto = itm['phototp']
                        item.groups = groups_item
                        if itm['photo']:
                            item.photo_item = itm['photo']
                            try:
                                colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                            except:
                                item.photo_item = item.groups.photo_groups
                                try:
                                    colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                                except:
                                    colors_inv_groups[item.ps] = "#FFFFFF"
                        else:
                            item.photo_item = item.groups.photo_groups
                            try:
                                colors_inv_groups[item.ps] = get_colors(item.photo_item, 1)
                            except:
                                colors_inv_groups[item.ps] = "#FFFFFF"
                        item.save()
                        items.append(item.ps)

                    colors[groups_item.ps] = sorted(colors_inv_groups.items(), key=lambda x: x[1])

                for item_db in items_in_db:
                    if (item_db.ps not in items):
                        item_db.delete()

                for inv_gr_id, inv_items_colors in colors.items():
                    counter = 1
                    for object in inv_items_colors:
                        inv_item = InvItems.objects.get(ps = object[0])
                        inv_item.id_color_sort = counter
                        inv_item.save()
                        counter += 1

        ## ADD PRODUCTS IN DATABASE ###
        products_in_db = Products.objects.all()

        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/getProducts', data={}, auth=('', ''))
        if resp.status_code == 200:
            hash_object, created = Hash.objects.get_or_create(name = 'products_hash')
            hash_val = hashlib.md5(resp.text.encode('utf-8')).hexdigest()
            if not created:
                if hash_object.value == hash_val:
                    pass
                else:
                    hash_object.value = hash_val
                    hash_object.save()
                    json_data = json.loads(resp.text)
                    products = []

                    for itms in json_data['itms']:
                        items_product = InvItems.objects.get(ps = itms['id'])
                        for prod in itms['prs']:
                            product, created = Products.objects.get_or_create(ps = prod['id'])
                            product.bl = prod['bl']
                            product.photobl = prod['photobl']
                            product.photobltp = prod['photobltp']
                            product.bty = prod['bty']
                            product.le = prod['le']
                            product.he = prod['he']
                            product.sco = prod['sco']
                            product.skl = prod['skl']
                            product.os = prod['os']
                            product.kolvo = prod['kolvo']
                            product.obos = prod['obos']
                            product.ossht = prod['ossht']
                            product.komment = prod['komment']
                            product.video = prod['video']
                            product.country = prod['country']

                            if prod['cnt']:
                                price = float(prod['cnt'])
                                product.cntRUB = price
                                product.cntUSD = round(price*usd,3)
                                product.cntEUR = round(price*eur,3)

                            if prod['photo']:
                                product.photo_product = prod['photo']
                                try:
                                    product.color_range = get_colors(product.photo_product,9)
                                except:
                                    product.photo_product = product.items.photo_item
                                    try:
                                        product.color_range = get_colors(product.photo_product,9)
                                    except:
                                        product.photo_product = product.items.groups.photo_groups
                                        try:
                                            product.color_range = get_colors(product.photo_product,9)
                                        except:
                                            product.color_range = ["#FFFFFF", "#FFFFFF", \
                                            "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                            "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                                        product.color_range = ["#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF"]

                            else:
                                product.photo_product = product.items.photo_item
                                try:
                                    product.color_range = get_colors(product.photo_product,9)
                                except:
                                    product.photo_product = product.items.groups.photo_groups
                                    try:
                                        product.color_range = get_colors(product.photo_product,9)
                                    except:
                                        product.color_range = ["#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                                    product.color_range = ["#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF"]

                            product.items = items_product
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
                            products.append(product.ps)

                    for product_db in products_in_db:
                        if (product_db.ps not in products):
                            product_db.delete()

            else:
                hash_object.value = hash_val
                hash_object.save()
                json_data = json.loads(resp.text)

                products = []
                for itms in json_data['itms']:
                    items_product = InvItems.objects.get(ps = itms['id'])
                    
                    for prod in itms['prs']:
                        product, created = Products.objects.get_or_create(ps = prod['id'])
                        product.bl = prod['bl']
                        product.photobl = prod['photobl']
                        product.photobltp = prod['photobltp']
                        product.bty = prod['bty']
                        product.le = prod['le']
                        product.he = prod['he']
                        product.sco = prod['sco']
                        product.skl = prod['skl']
                        product.os = prod['os']
                        product.kolvo = prod['kolvo']
                        product.obos = prod['obos']
                        product.ossht = prod['ossht']
                        product.komment = prod['komment']
                        product.video = prod['video']
                        product.country = prod['country']
                        product.items = items_product
                    
                        if prod['cnt']:
                            price = float(prod['cnt'])
                            product.cntRUB = price
                            product.cntUSD = round(price*usd,3)
                            product.cntEUR = round(price*eur,3)
                        
                        if prod['photo']:
                            product.photo_product = prod['photo']
                            try:
                                product.color_range = get_colors(product.photo_product,9)
                            except:
                                product.photo_product = product.items.photo_item
                                try:
                                    product.color_range = get_colors(product.photo_product,9)
                                except:
                                    product.photo_product = product.items.groups.photo_groups
                                    try:
                                        product.color_range = get_colors(product.photo_product,9)
                                    except:
                                        product.color_range = ["#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                        "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                                    product.color_range = ["#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                        
                        else:
                            product.photo_product = product.items.photo_item
                            try:
                                product.color_range = get_colors(product.photo_product,9)
                            except:
                                product.photo_product = product.items.groups.photo_groups
                                try:
                                    product.color_range = get_colors(product.photo_product,9)
                                except:
                                    product.color_range = ["#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                    "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                                product.color_range = ["#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", \
                                "#FFFFFF", "#FFFFFF", "#FFFFFF"]
                        
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
                        products.append(product.ps)

                for product_db in products_in_db:
                    if (product_db.ps not in products):
                        product_db.delete()