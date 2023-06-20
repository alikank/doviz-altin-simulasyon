
# Python Altın&Döviz Simülasyonu


Bu proje, altın ve döviz verilerini apiden elde ederek; sınırsız varlık ekleme, varlıkların TL karşılıklarını listeleme, eski ve yeni döviz/altın bilgilerini görme, eklenen varlıkların ayrı ayrı kar-zarar durumunu ve yüzdeliğini görme, altın ve döviz birimlerinin TL değerine göre grafiksel değişimini gösterme özelliklerine sahip bir simülasyondur.




![Logo](https://i.ibb.co/27hc8CR/Black-Clean-and-Minimalist-Project-Overview-Docs-Banner.png)

    
İlgili proje, TÜ | programlama dillerine giriş dersi dönem sonu ödevidir.


## Kullanılan Araçlar

- Python (OOP)
- Tkinter (Grafik Arayüz Tasarımı)
- Datetime
- sqlite3
- json
- http.client

  
## Ekran Görüntüleri

![Uygulama Ekran Görüntüsü](https://i.ibb.co/FYdLFgQ/githubdoviz.png)

  
## API Kaynağı

#### Altın Verileri

```http
  GET api.collectapi.com
```

| Parametre | Tip     | Açıklama                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Gerekli**. API anahtarınız. |

#### Döviz Verileri

```http
  GET finans.truncgil.com
```

| Açıklama |
| :- |
| **Gereksiz**. API anahtarınız  |



  
## Proje Bilgi

Altın ve Döviz verilerini bir API'den alarak kullanıcının sahip olduğu altın ve döviz miktarlarının TL karşılığını gösteren bir tkinter uygulaması geliştirilmiştir.

 Kullanıcının farklı döviz ve altın miktarlarını kaydedebilmesi için bu bilgilerin saklanacağı bir veritabanı kullanılacaktır.

Kullanıcı, miktarları farklı tarihlerde güncelleyebilecek ve güncellenen miktarlar kaydedilecektir. 

Uygulama her açıldığında, kullanıcının tüm altın ve döviz varlıklarının TL karşılıkları ayrı ayrı gösterilecek ve toplam varlık miktarı da görüntülenecektir. 

Uygulama, aldığı verileri kaydederek kullanıcıya eski tarihlerdeki bilgileri görüntüleme imkanı sunacak. Ayrıca, seçilen altın veya dövizin değişimi ile kullanıcının varlığının TL karşılığının değişimi grafiksel olarak gösterilebilecektir. 

Kullanıcı, her döviz veya altın miktarı üzerinden yaptığı kâr/zararın hem TL bazında hem de yüzde olarak listesini görebilecektir. Tarihler arasındaki miktar güncellemeleri de dikkate alınarak kâr/zarar hesaplanacak ve toplamı verilecektir.

  
## Bilgisayarınızda Çalıştırın

Projeyi çalıştırmak için komut satırına :


```bash
  python main.py
```

  
## Planlanan Güncellemeler

- Veritabanından döviz veya altın kayıtlarını silme

- API'den günlük tek veri çekimi yerine her girişte anlık olarak döviz ve altın bilgilerini güncelleme

  
