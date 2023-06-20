import http.client
import json
import datetime
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as tkfont
import matplotlib.pyplot as plt
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


ana = tk.Tk()
ana.title("Altın ve Döviz Uygulaması")
ana.state("zoomed")
baglanti = sqlite3.connect("doviz.db")
cursor = baglanti.cursor()


class Database:
     def __init__(self):
          # tabloların oluşturulması
          cursor.execute("CREATE TABLE IF NOT EXISTS tarih(id INTEGER PRIMARY KEY AUTOINCREMENT, tarih varchar(255), saat varchar(255))")
          cursor.execute("CREATE TABLE IF NOT EXISTS durum(id INTEGER PRIMARY KEY AUTOINCREMENT, tarih_id varchar(255), doviz varchar(255), deger varchar(255), alis varchar(255))")
          cursor.execute("CREATE TABLE IF NOT EXISTS kayit(id INTEGER PRIMARY KEY AUTOINCREMENT, tarih_id varchar(255),doviz varchar(255), miktar varchar(255))")
          self.baglanti = baglanti
          self.cursor = cursor
          
         # tarih tablosundaki id sütunu ile durum tablosundaki tarih_id sütunu arasında foreign key ilişkisi var.
         # tarih tablosundaki id sütunu ile kayit tablosundaki tarih_id sütunu arasında foreign key ilişkisi var.

          tarih = datetime.datetime.today()
          # tarih kayıtlı değilse veritabanına eklenmesi
          cek = cursor.execute("SELECT * FROM tarih where tarih=?",(tarih.strftime("%d.%m.%y"),))
          if(not cek.fetchall()):
               cursor.execute("INSERT INTO tarih(tarih,saat) VALUES (?,?)",(tarih.strftime("%d.%m.%y"),tarih.strftime("%H:%M:%S")))
               baglanti.commit()

          # ilgili tarihe ait döviz ve altın bilgilerinin kaydı yoksa eklenmesi  
          id = Database.tarihidcek(tarih.strftime("%d.%m.%y")) # tarih tablosundan id çek
          cursor.execute("SELECT * FROM durum where tarih_id=?",(id,))
          if(not cursor.fetchall()):
               liste = []

               # ALTIN ÇEK
               conn = http.client.HTTPSConnection("api.collectapi.com")
               headers = {
               'content-type': "application/json",
               'authorization': "apikey 0Hd64hqR05AeVORNZiLX3S:21lFv0x7d7j7PF78FLwnVX"
               }
               conn.request("GET", "/economy/goldPrice", headers=headers)
               res = conn.getresponse()
               data = json.loads(res.read())
               
               for i in range(3):
                    liste.append((id,data["result"][i]["name"],data["result"][i]["buying"],data["result"][i]["selling"]))
               
               
               # DÖVİZ ÇEK
               conn = http.client.HTTPSConnection("finans.truncgil.com")
               conn.request("GET", "/today.json")
               res = conn.getresponse()
               data = json.loads(res.read()) 

               usd = (id,"USD",data["USD"]["Alış"],data["USD"]["Satış"])
               liste.append(usd)
               eur = (id,"EUR",data["EUR"]["Alış"],data["EUR"]["Satış"])
               liste.append(eur)
               gbp = (id,"GBP",data["GBP"]["Alış"],data["GBP"]["Satış"])
               liste.append(gbp)

               cursor.executemany("INSERT INTO durum(tarih_id,doviz,deger,alis) VALUES (?,?,?,?)",liste) # altın ve döviz bilgilerini aynı anda ekle
               baglanti.commit()

     @staticmethod
     def tarihidcek(date=""): #verilen tarihin idsini getirir (tarih verilmezse bugünün tarihini getir)
               if date=="":
                    tarih = datetime.datetime.today()
                    date = (tarih.strftime("%d.%m.%y")) 
               cursor.execute("SELECT * FROM tarih where tarih=?",(date,))
               idcek = cursor.fetchall()
               return idcek[0][0]   
     
     @staticmethod
     def boxguncelle(tarih=""):        # döviz kurlarının bulunduğu boxu günceller
         if tarih=="":
               id = Database.tarihidcek() # bugünkü tarihin idsini al
         else:
               id = Database.tarihidcek(tarih) # ilgili tarihin idsini al
         cursor.execute("SELECT * FROM durum where tarih_id=?",(id,))
         veri = cursor.fetchall()
         return veri

     @staticmethod
     def tarihlerigetir(): #Combobox için seçenekleri getir
          cursor.execute("SELECT * FROM tarih")
          tarihler = cursor.fetchall()
          geriyolla = []
          for tarih in tarihler:
               geriyolla.append(tarih[1])
          return tuple(geriyolla)     
     
     @staticmethod
     def varlikarttir(birim,miktar): # database varlıkları güncelle
          try:
               int(miktar) # girilen değer sayı mı kontrol
               cursor.execute("INSERT INTO kayit(tarih_id,doviz,miktar) VALUES (?,?,?)",(Database.tarihidcek(),birim,miktar))
               try:
                    baglanti.commit()
                    messagebox.showinfo("Başarıyla Eklendi !", "Mevcut varlığınız başarıyla artırıldı !")
                    SolFrame.uzaktanguncelle() #varlık tablosunu anlık güncelle
               except:
                    messagebox.showerror("Hata Oluştu!", "Veritabanı bağlantısında hata var.")
          except:
               messagebox.showerror("Hata Oluştu!", "Girilen miktar tam sayı olmalı.")

     @staticmethod
     def varlikcek(birim): # ilgile birime ait varlık miktarını getirir
          cursor.execute("SELECT * FROM kayit where doviz=?",(birim,))
          veriler = cursor.fetchall()
          miktar = 0
          for i in veriler:
                miktar += int(i[3])
          return miktar     
          
     @staticmethod
     def varliktlhesapla(birim,miktar,ozel=""): # birim ve ilgili birime ait miktarı alarak güncel kura göre TL değeri hesaplar
          cursor.execute("SELECT * FROM durum where doviz=? and tarih_id=?",(birim,Database.tarihidcek()))
          veri = cursor.fetchone()
          kur = veri[3]
          kur = kur.replace(",",".")
          if ozel=="":
               return str(float(kur) * float(miktar)) + " TL" #solframedeki miktarguncelle fonksiyonu için
          else:
               return str(float(kur) * float(miktar)) + "||" + kur #karzararhesapla fonksiyonu için

     
     @staticmethod
     def karzararhesapla(): # KAR - ZARAR HESAPLAMA
          cursor.execute("SELECT * FROM kayit")
          kayitlar = cursor.fetchall()
          dondur = []
          for i in kayitlar:
               tarih,birim,miktar = i[1],i[2],i[3] # kayıttan ilgili bilgileri çek

               cursor.execute("SELECT * FROM durum where tarih_id=? and doviz=?",(tarih,birim))
               tekil = cursor.fetchone()  
               kullanicialiskur = float(tekil[4].replace(",","."))
               kullanicialis = kullanicialiskur * float(miktar) # aldığı tarihteki kura göre tl değeri
               bilgial = Database.varliktlhesapla(birim,miktar,5)
               bilgial = bilgial.split("||")
               kullanicisatis = float(bilgial[0]) # bugünkü satış kuruna göre tl değeri
               kullanicisatiskur = float(bilgial[1])

               ifade = Database.karzararifade(kullanicisatis,kullanicialis,kullanicialiskur,kullanicisatiskur)
               dondur.append([birim,miktar,ifade])
          return dondur     
 

     @staticmethod # kar zarar için yüzde hesabı ve geri dönüş ifadesi
     def karzararifade(kullanicisatis,kullanicialis,kullanicialiskur,kullanicisatiskur):
          sonuc = round(kullanicisatis-kullanicialis,4)
          yuzde = abs(round(100*(kullanicisatiskur-kullanicialiskur)/kullanicialiskur,4)) # yüzde hesabı
          ifade = ""
          if(sonuc>0):
               ifade = str(sonuc)+ " TL KAR ---> %"+str(yuzde)
          elif(sonuc==0):
               ifade = str(sonuc)+ " TL ---> %"+str(yuzde)
          else:
               ifade = str(sonuc)+ " TL ZARAR ---> %" +str(yuzde)
          return ifade 
     
     @staticmethod
     def grafiktlhesapla(miktar,birim): # grafik için ilgili tarihlere ait döviz bilgilerini çekerek TL değerini alır.
          tarihler = Database.tarihlerigetir()
          tldeger = []
          for i in list(tarihler):
               cursor.execute("SELECT * FROM durum where tarih_id=? and doviz=?",(Database.tarihidcek(i),birim))
               veriler = cursor.fetchone()
               kur = float(veriler[3].replace(",","."))
               tldeger.append(kur*float(miktar))               
          return tldeger     



     @staticmethod
     def grafiktl(birim): # grafik için ana fonksiyon
          miktar = float(Database.varlikcek(birim))   
          tliste = Database.grafiktlhesapla(miktar,birim)  
          return tliste

     


class SagFrame:
     ekself = 0
     def __init__(self):
          global ekself
          ekself = self
          self.bolge1 = tk.Frame(ana,width=800,relief="raised",bd=5,border=2,padx=375,pady=20)
          self.bolge1.pack(fill="y",anchor="ne",side="right")
          self.varlikekle = tk.Label(self.bolge1,text="Varlık Ekle : ",font="Calibri 30 bold",fg="orange",padx=10)
          self.varlikekle.grid(row=0, column=0)
          self.birims = ttk.Combobox(self.bolge1,width=16,state="readonly",font="Verdana 15 roman")
          self.birims["values"] = ("USD","EUR","GBP","Gram Altın","Çeyrek Altın","Yarım Altın")
          self.birims.grid(row=0,column=1,padx=5,pady=2,ipady=4)    
          self.birims.current("0")

          self.miktarekle = tk.Label(self.bolge1,text="Miktar : ",font="Calibri 30 bold",fg="orange",padx=10)
          self.miktarekle.grid(row=1,column=0)
          self.miktar = tk.Entry(self.bolge1,width=23,font="Calibri 15 bold")
          self.miktar.grid(row=1,column=1,ipady=5)

          self.ekle = tk.Button(self.bolge1,text="Ekle",font="Verdana 15 bold", command=lambda : Database.varlikarttir(self.birims.get(),self.miktar.get()), bg='orange',fg='#ffffff',bd=0)
          self.ekle.grid(row=2,column=0,padx=5,pady=10,columnspan=2,ipadx=50,ipady=8)

          self.grafikekle = tk.Label(self.bolge1,text="Grafik",font="Calibri 40 bold",fg="orange",padx=10,pady=50)
          self.grafikekle.grid(row=3,column=0,columnspan=2)
          SagFrame.uzaktancagir()

     @staticmethod
     def uzaktancagir(birim="USD"):
          global ekself
          tarihler = list(Database.tarihlerigetir())
          tl = Database.grafiktl(birim)
          ekself.grafikolustur(tarihler,tl,birim)
          
     def grafikolustur(self,tarihler,tl,birim):
          grafik_frame = tk.Frame(self.bolge1)
          grafik_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
          fig = plt.figure(figsize=(6, 6)) 
          ayarla = fig.add_subplot(1,1,1)
          ayarla.plot(tarihler, tl)
          ayarla.set_xlabel("Tarih")
          ayarla.set_ylabel("TL Değer")
          ayarla.set_title(birim + "- TL Değişim Grafiği")
          canvas = FigureCanvasTkAgg(fig,grafik_frame)
          canvas.draw()
          canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
          canvas._tkcanvas.pack(side="top", fill="both", expand=True)





          



class SolFrame:
    selfim = 0
    def __init__(self):
        global selfim
        selfim = self #static methodta kullanmak için tanımlandı
        self.frame1 = tk.Frame(ana,width=400,relief="raised",bd=5,border=2,padx=75,pady=30)
        self.frame1.pack(fill="y",anchor="nw",side="top")
        self.frame2 = tk.Frame(ana,width=400,relief="raised",bd=5,border=2,padx=35,pady=20)
        self.frame2.pack(fill="y",anchor="nw",side="top")
        self.frame3 = tk.Frame(ana,width=400,relief="raised",bd=5,border=2,padx=50,pady=10)
        self.frame3.pack(fill="y",anchor="nw",side="top")
        self.frame4 = tk.Frame(ana,width=400,relief="raised",bd=5,border=2,padx=15,pady=10)
        self.frame4.pack(fill="y",anchor="nw",side="top")        

        self.varlik = tk.Label(self.frame1,text="Toplam Varlık :",font="Calibri 28 bold",fg="orange")
        self.varlik.grid(row=0, column=0, columnspan=1)
        self.varlikmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.varlikmiktar.grid(row=0,column=1,padx=15,pady=15)

        self.usd = tk.Label(self.frame1,text=" USD ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.usd.grid(row=1, column=0)
        self.usdmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.usdmiktar.grid(row=1,column=1,columnspan=2,padx=15)

        self.eur = tk.Label(self.frame1,text=" EUR ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.eur.grid(row=2, column=0)
        self.eurmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.eurmiktar.grid(row=2,column=1,columnspan=2,padx=15)

        self.gbp = tk.Label(self.frame1,text=" GBP ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.gbp.grid(row=3, column=0)
        self.gbpmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.gbpmiktar.grid(row=3,column=1,columnspan=2,padx=15)

        self.galtin = tk.Label(self.frame1,text=" Gram Altın ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.galtin.grid(row=4, column=0)
        self.galtinmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.galtinmiktar.grid(row=4,column=1,columnspan=2,padx=15)

        self.caltin = tk.Label(self.frame1,text=" Çeyrek Altın ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.caltin.grid(row=5, column=0)
        self.caltinmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.caltinmiktar.grid(row=5,column=1,columnspan=2,padx=15)

        self.yaltin = tk.Label(self.frame1,text=" Yarım Altın ",font="Calibri 18 bold",pady=5,padx=20,height=1,anchor="w")
        self.yaltin.grid(row=6, column=0)
        self.yaltinmiktar = tk.Entry(self.frame1,width=14,font=("Calibri", 18))
        self.yaltinmiktar.grid(row=6,column=1,columnspan=2,padx=15)
        self.miktarguncelle()

        self.veriler = tk.Label(self.frame2,text="Tarihler :",font="Calibri 28 bold",fg="orange").grid(row=7,column=0,sticky="w")
        self.tarih = ttk.Combobox(self.frame2,width=14,state="readonly",font="Verdana 15 roman")
        self.tarih["values"] = Database.tarihlerigetir()      
        self.tarih.current("end")
        self.tarih.grid(row=7,column=1,padx=4,pady=2,sticky="w")               
        self.cek = tk.Button(self.frame2,text="Göster",font="Verdana 12 bold",command=lambda:self.cekbilgi(self.tarih.get()),bg='orange',fg='#ffffff',bd=0)
        self.cek.grid(row=7,column=2,pady=2,ipadx=4,sticky="w")
        self.lboxfont1 = tkfont.Font(size=14) 
        self.bilgi = tk.Listbox(self.frame2,width=40,height=7,font=self.lboxfont1)
        self.bilgi.grid(row=9,column=0,columnspan=2,sticky="w")
        self.cekbilgi()

        self.grafik = tk.Label(self.frame3,text="Grafik :",font="Calibri 28 bold",fg="orange").grid(row=9,column=0,sticky="w")
        self.birim = ttk.Combobox(self.frame3,width=16,state="readonly",font="Verdana 15 roman")
        self.birim["values"] = ("USD","EUR","GBP","Gram Altın","Çeyrek Altın","Yarım Altın")
        self.birim.grid(row=9,column=1,padx=10,pady=2)               
        self.cek2 = tk.Button(self.frame3,text="Göster",font="Verdana 12 bold",command=lambda:self.grafikolustur(self.birim.get()),bg='orange',fg='#ffffff',bd=0)
        self.cek2.grid(row=9,column=2,padx=10,pady=2,ipadx=4,sticky="w")
        
        self.yazi = tk.StringVar()
        self.yazi.set("")
        self.durum = tk.Label(self.frame4,textvariable=self.yazi,font="Calibri 22 bold",fg="orange").grid(row=10,column=0,columnspan=1)
        self.lboxfont2 = tkfont.Font(size=12)
        self.karzarar = tk.Listbox(self.frame4,width=80,height=9,font=self.lboxfont2)
        self.karzarar.grid(row=11,column=0,columnspan=2,padx=10,pady=(0,20))
        self.scrollbar = tk.Scrollbar(self.frame4,bd=2,width=20)
        self.scrollbar.grid(row=11,column=1,ipady=50,sticky="w")
        self.karzarar.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.karzarar.yview)
        self.karzararcek()

      
    def cekbilgi(self,tarih=""):
         self.bilgi.delete("0", "end")
         gelenveri = Database.boxguncelle(tarih)   
         for i in gelenveri:
              self.bilgi.insert("end",i[2]+" | Satış : "+i[3]+" Alış : "+i[4] )
         
        
    def grafikolustur(self,birim):
         SagFrame.uzaktancagir(birim)
     
    def karzararcek(self):
         self.karzarar.delete("0","end")
         data = Database.karzararhesapla()
         toplam = 0
         for i in data:
              self.karzarar.insert("end",str(i[1]) + " " + i[0] + " ---> Durum : " + i[2])
              i[2] = i[2].split()
              toplam += float(i[2][0])
         self.yazi.set("Toplam Kâr/Zarar Durumu :\n"+str(round(toplam,4))+ " TL")    
              
    
    @staticmethod
    def uzaktanguncelle(): # Database sınıfından, bu sınıftaki miktarguncelle ve karzararcek fonksiyonuna erişebilmek için aracı fonksiyon
         selfim.miktarguncelle()
         selfim.karzararcek()

    def miktarguncelle(self):

        self.usdmiktar.config(state= "normal") #entryin değerini güncelleyebilmek için statesini değiştiriyoruz
        self.usdmiktar.delete("0","end")
        self.usdmiktar.insert("end", Database.varliktlhesapla("USD",Database.varlikcek("USD")))
        self.usdmiktar.config(state="readonly") # daha iyi bir görünüm için stateyi sadece okunabilir yapıyoruz

        self.eurmiktar.config(state="normal") 
        self.eurmiktar.delete("0","end")
        self.eurmiktar.insert("end", Database.varliktlhesapla("EUR",Database.varlikcek("EUR")))
        self.eurmiktar.config(state="readonly") 

        self.gbpmiktar.config(state="normal") 
        self.gbpmiktar.delete("0","end")
        self.gbpmiktar.insert("end", Database.varliktlhesapla("GBP",Database.varlikcek("GBP")))
        self.gbpmiktar.config(state="readonly") 

        self.galtinmiktar.config(state="normal") 
        self.galtinmiktar.delete("0","end") 
        self.galtinmiktar.insert("end", Database.varliktlhesapla("Gram Altın",Database.varlikcek("Gram Altın")))
        self.galtinmiktar.config(state="readonly") 

        self.caltinmiktar.config(state="normal") 
        self.caltinmiktar.delete("0","end") 
        self.caltinmiktar.insert("end", Database.varliktlhesapla("Çeyrek Altın",Database.varlikcek("Çeyrek Altın")))
        self.caltinmiktar.config(state="readonly") 

        self.yaltinmiktar.config(state="normal") 
        self.yaltinmiktar.delete("0","end") 
        self.yaltinmiktar.insert("end", Database.varliktlhesapla("Yarım Altın",Database.varlikcek("Yarım Altın")))
        self.yaltinmiktar.config(state="readonly") 

        self.varlikmiktar.config(state="normal") 
        self.varlikmiktar.delete("0","end")
        self.varlikmiktar.insert("end", str(round(float(self.usdmiktar.get()[0:-3])+ float(self.eurmiktar.get()[0:-3]) + float(self.gbpmiktar.get()[0:-3]) + float(self.galtinmiktar.get()[0:-3]) + float(self.caltinmiktar.get()[0:-3]) + float(self.yaltinmiktar.get()[0:-3]),3))+ " TL")
        self.varlikmiktar.config(state="readonly") 

        


         



Database()
SagFrame()
SolFrame()



ana.mainloop()

