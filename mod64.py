import struct

class MOD64:
    def __init__(self):
        self.tur_sayisi = 8

    def _dairesel_sola_kaydir(self, x, n, bits=32):
        """Yardımcı Fonksiyon: Bitleri sola dairesel kaydırır"""
        return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)

    def _s_kutusu(self, deger):
        """Yardımcı Fonksiyon: (5x + 3) mod 16"""
        sonuc = 0
        for i in range(8):
            kaydirma = i * 4
            nibble = (deger >> kaydirma) & 0xF 
            donusum = (5 * nibble + 3) % 16
            sonuc |= (donusum << kaydirma)
        return sonuc

    def _f_fonksiyonu(self, sag_blok, tur_anahtari):
        """F-Fonksiyonu: XOR + S-Kutusu + Permütasyon"""
        t = sag_blok ^ tur_anahtari
        s_cikti = self._s_kutusu(t)
        return self._dairesel_sola_kaydir(s_cikti, 5)

    def Anahtar_Uret(self, parola):
        """
        İster 1: Paroladan 8 adet tur anahtarı üretir.
        """
        parola = parola.ljust(8)[:8] # 64-bite tamamla
        ana_anahtar = int.from_bytes(parola.encode('utf-8'), 'big')
        
        anahtarlar = []
        temp_key = ana_anahtar
        for i in range(8):
            tur_anahtari = temp_key & 0xFFFFFFFF 
            anahtarlar.append(tur_anahtari)
            # Anahtarı karıştır (Key Schedule)
            temp_key = ((temp_key << 7) | (temp_key >> (64 - 7))) & ((1 << 64) - 1)
        return anahtarlar

    def Sifrele(self, duz_metin, parola):
        """
        İster 2: Düz metni şifreler.
        """
        tur_anahtarlari = self.Anahtar_Uret(parola)
        
        duz_metin = duz_metin.ljust(8)[:8]
        blok = int.from_bytes(duz_metin.encode('utf-8'), 'big')
        
        sol = (blok >> 32) & 0xFFFFFFFF
        sag = blok & 0xFFFFFFFF
        
        for i in range(8):
            eski_sol = sol
            eski_sag = sag
            
            sol = eski_sag
            f_sonuc = self._f_fonksiyonu(eski_sag, tur_anahtarlari[i])
            sag = eski_sol ^ f_sonuc
            
        sifreli_blok = (sol << 32) | sag
        return sifreli_blok

    def Desifrele(self, sifreli_sayi, parola):
        """
        İster 3: Şifreli veriyi çözer.
        """
        tur_anahtarlari = self.Anahtar_Uret(parola)[::-1] # Anahtarları ters çevir
        
        sol = (sifreli_sayi >> 32) & 0xFFFFFFFF
        sag = sifreli_sayi & 0xFFFFFFFF
        
        for i in range(8):
            suanki_sol = sol
            suanki_sag = sag
            
            # Ters Feistel
            f_sonuc = self._f_fonksiyonu(suanki_sol, tur_anahtarlari[i])
            eski_sol = suanki_sag ^ f_sonuc
            eski_sag = suanki_sol
            
            sol = eski_sol
            sag = eski_sag
            
        son_blok = (sol << 32) | sag
        try:
            return son_blok.to_bytes(8, 'big').decode('utf-8').strip()
        except:
            return "[Anlamsız Veri]" # Decode edilemezse

# --- TEST SENARYOLARI ---
if __name__ == "__main__":
    algoritma = MOD64()
    
    print("--- TEST 1: BASİT DOĞRULAMA ---")
    metin = "KALE"
    anahtar_dogru = "AN"
    
    print(f"Giriş Metni: {metin}")
    print(f"Anahtar: {anahtar_dogru}")
    
    # Şifreleme
    sifreli = algoritma.Sifrele(metin, anahtar_dogru)
    print(f"Şifreli Veri (Hex): {hex(sifreli)}")
    
    # Deşifreleme
    cozulen = algoritma.Desifrele(sifreli, anahtar_dogru)
    print(f"Çözülen Metin: {cozulen}")
    
    if metin == cozulen:
        print("SONUÇ: ✅ Test 1 Başarılı (Metin geri döndürüldü)\n")
    
    print("--- TEST 2: ANAHTAR HASSASİYETİ (ÇIĞ ETKİSİ) ---")
    # Anahtarın sadece bir harfini değiştiriyoruz (N -> M)
    anahtar_yanlis = "AM" 
    print(f"Orijinal Şifreli Veri: {hex(sifreli)}")
    print(f"Yanlış Anahtar: {anahtar_yanlis} (Sadece 1 bit/harf farklı)")
    
    hatali_cozum = algoritma.Desifrele(sifreli, anahtar_yanlis)
    print(f"Yanlış Anahtarla Çözülen: {hatali_cozum}")
    
    if metin != hatali_cozum:
        print("SONUÇ: ✅ Test 2 Başarılı (Yanlış anahtar veriyi açamadı)")