import requests
import base64

from django.conf import settings
from django.db import models
from io import BytesIO

sity = {'spb': 'Санкт-Петербург',
    'spbPrs': 'Санкт-Петербург, Парнас',
    'msc': 'Москва','kzn': 'Казань',
    'krd': 'Краснодар',
    'fdr': 'ЛО, Федоровское',
    'ekb': 'Екатеринбург',
    'bzl':'МО, Бузланово'}


class Image(models.Model):
    img = models.ImageField(upload_to='images')


class Project(models.Model):
    name = models.CharField(max_length = 64, blank = True, null = True)
    reserve = models.BooleanField(blank = False, null = False, default = False)
    prices = models.BooleanField(blank = False, null = False, default = False)
    stock = models.BooleanField(blank = False, null = False, default = False)

    def __str__(self):
        return '{}: {}, {}, {}'.format(self.name, self.reserve, self.prices, self.stock)


class Hash(models.Model):
    name = models.CharField(max_length = 64, blank = True, null = True)
    value = models.CharField(max_length = 64, blank = True, null = True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.value)


class Materials(models.Model):
    ps = models.CharField(max_length = 16,blank = True, null = True) # id
    mt = models.CharField(max_length = 32,  blank = True, null = True) # название на русском
    ph = models.CharField(max_length = 32,  blank = True, null = True) # название на английском
    photo_material = models.CharField(max_length = 256,  blank = True, null = True) # ссылка на картинку
    sku = models.CharField(max_length = 8,  blank = True, null = True) # sku количество
    kw = models.CharField(max_length = 16,  blank = True, null = True) # объем
    nw = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    onSale = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    pz = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    po = models.CharField(max_length = 32,  blank = True, null = True) # название на русском
    photo_type = models.CharField(max_length = 128,  blank = True, null = True) # название на русском

    @property
    def url(self):
        material = self.ph
        return '/{}/'.format(material)

    def __str__(self):
        return '{}'.format(self.ph)


class InvGroups(models.Model):
    ps = models.CharField(max_length = 16, unique = True, db_index=True, default = '') # id
    id_color_sort = models.IntegerField(blank = True, null = True, default=1)
    gr = models.CharField(max_length = 64,  blank = True, null = True) # название группы
    co = models.CharField(max_length = 32,  blank = True, null = True) # страна
    cl = models.CharField(max_length = 16,  blank = True, null = True) # цвет
    nam = models.CharField(max_length = 512,  blank = True, null = True) # непонятно что
    sku = models.CharField(max_length = 8,  blank = True, null = True) # sku количество
    prRUB = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    prUSD = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    prEUR = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    typeFoto = models.CharField(max_length = 32,  blank = True, null = True) # тип картинки
    kw = models.CharField(max_length = 16,  blank = True, null = True) # объем
    photo_groups = models.CharField(max_length = 256,  blank = True, null = True) # ссылка на картинку
    materials = models.ForeignKey(Materials, on_delete=models.CASCADE, blank = True, null = True) # группы материала
    photo_type = models.CharField(max_length = 128,  blank = True, null = True) # название на русском
    nw = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    onSale = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    pz = models.CharField(max_length = 8,  blank = True, null = True) # АМ

    @property
    def url(self):
        material = self.materials.ph
        group = self.ps
        return '/{}/{}/'.format(material, group)

    @property
    def cur(self):
        return '₽'

    def __str__(self):
        return '{}'.format(self.gr)


class InvItems(models.Model):
    ps = models.CharField(max_length = 16, unique = True, db_index=True, default = '') # id
    id_color_sort = models.IntegerField(blank = True, null = True, default=1)
    name = models.CharField(max_length = 128,  blank = True, null = True) # название объектов
    izd = models.CharField(max_length = 32,  blank = True, null = True) # тип
    pro = models.CharField(max_length = 16,  blank = True, null = True) # Venezia
    thn = models.CharField(max_length = 32,  blank = True, null = True) # 30
    obr = models.CharField(max_length = 32,  blank = True, null = True) # Honed
    kat = models.CharField(max_length = 128,  blank = True, null = True) #
    qua = models.CharField(max_length = 32,  blank = True, null = True) #
    cp = models.CharField(max_length = 32,  blank = True, null = True) # 3
    cs = models.CharField(max_length = 32,  blank = True, null = True) # 3
    kw = models.CharField(max_length = 16,  blank = True, null = True) # объем
    prRUB = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    prUSD = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    prEUR = models.CharField(max_length = 32,  blank = True, null = True) # цена от
    sku = models.CharField(max_length = 8,  blank = True, null = True) # sku количество
    typeFoto = models.CharField(max_length = 32,  blank = True, null = True) # тип картинки
    photo_item = models.CharField(max_length = 256,  blank = True, null = True) # ссылка на картинку
    groups = models.ForeignKey(InvGroups, on_delete=models.CASCADE, blank = True, null = True) # элементы группы
    photo_type = models.CharField(max_length = 128,  blank = True, null = True) # название объектов
    nw = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    onSale = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    pz = models.CharField(max_length = 8,  blank = True, null = True) # АМ

    @property
    def url(self):
        material = self.groups.materials.ph
        group = self.groups.ps
        item = self.ps
        return '/{}/{}/{}/'.format(material, group, item)

    @property
    def cur(self):
        return '₽'

    def __str__(self):
        return '{}'.format(self.name)


class Products(models.Model):
    ps = models.CharField(max_length = 16, default = '') # id
    bl = models.CharField(max_length = 64,  blank = True, null = True) #
    color_range = models.CharField(max_length = 128,  blank = True, null = True , 
        default= ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF'])
    photobl = models.CharField(max_length = 128,  blank = True, null = True) #
    photobltp = models.CharField(max_length = 32,  blank = True, null = True) # bundle
    bty = models.CharField(max_length = 32,  blank = True, null = True) #
    le = models.CharField(max_length = 32,  blank = True, null = True) # 0
    he = models.CharField(max_length = 32,  blank = True, null = True) # 0
    sco = models.CharField(max_length = 32,  blank = True, null = True) # 0
    skl = models.CharField(max_length = 32,  blank = True, null = True) # fdr
    os = models.CharField(max_length = 32,  blank = True, null = True) # 0.54
    kw = models.CharField(max_length = 32,  blank = True, null = True) # 0.54
    cntRUB = models.CharField(max_length = 32,  blank = True, null = True) 
    cntUSD = models.CharField(max_length = 32,  blank = True, null = True)  
    cntEUR = models.CharField(max_length = 32,  blank = True, null = True)
    nw = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    onSale = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    pz = models.CharField(max_length = 8,  blank = True, null = True) # АМ
    kolvo = models.CharField(max_length = 32,  blank = True, null = True) # АМ
    obos = models.CharField(max_length = 32,  blank = True, null = True) # АМ
    ossht = models.CharField(max_length = 32,  blank = True, null = True) # АМ
    komment = models.CharField(max_length = 512,  blank = True, null = True) # АМ
    video = models.CharField(max_length = 128,  blank = True, null = True) # АМ
    country = models.CharField(max_length = 32,  blank = True, null = True) # АМ
    typeFoto = models.CharField(max_length = 64,  blank = True, null = True) # тип картинки
    photo_product = models.CharField(max_length = 256,  blank = True, null = True) # ссылка на картинку
    items = models.ForeignKey(InvItems, on_delete=models.CASCADE, blank = True, null = True) # продукты элемента

    @property
    def url(self):
        material = self.items.groups.materials.ph
        group = self.items.groups.ps
        item = self.items.ps
        izd = self.items.izd
        product = self.pk
        if izd == 'Слэбы' or izd == 'Полоса':
            return '/{}/{}/{}/{}/'.format(material, group, item, product)
        else:
            return '/{}/{}/{}/'.format(material, group, item)

    @property
    def itms_name(self):
        return self.items.name

    @property
    def itms_izd(self):
        return self.items.izd

    @property
    def sklad(self):
        try:
            return sity[self.skl]
        except:
            return self.skl

    def __str__(self):
        return '{}'.format(self.ps)

    @property
    def photo_bytes(self):
        if self.photo_product:
            response = requests.get(self.photo_product)
            image = BytesIO(response.content)
            bytes_image = image.read()
            image_64_encode = str(base64.b64encode(bytes_image))
            return image_64_encode[2:-1]
        else:
            if self.items.photo_item:
                response = requests.get(self.items.photo_item)
                image = BytesIO(response.content)
                bytes_image = image.read()
                image_64_encode = str(base64.b64encode(bytes_image))
                return image_64_encode[2:-1]
            else:
                response = requests.get(self.items.groups.photo_groups)
                image = BytesIO(response.content)
                bytes_image = image.read()
                image_64_encode = str(base64.b64encode(bytes_image))
                return image_64_encode[2:-1]
