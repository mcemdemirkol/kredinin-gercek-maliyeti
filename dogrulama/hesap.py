"""Kredinin gerçek maliyeti — sayfadaki hesabın bağımsız Python karşılığı.

Sayfa (index.html) hesabı tarayıcıda JavaScript ile yapar. Bu betik aynı
formülleri sıfırdan uygular; dört senaryonun çıktısı sayfayla kuruşu kuruşuna
aynı olmalıdır. Ek paket gerekmez.

Çalıştırma:  python dogrulama/hesap.py
"""
import sys


def kredi(tutar, vade, aylik_faiz, kkdf=0.15, bsmv=0.15, tahsis_orani=0.005, sigorta=0.0):
    vergi = kkdf + bsmv
    i_vergili = aylik_faiz * (1 + vergi)                      # vergiler faize eklenir
    taksit = tutar / vade if i_vergili == 0 else tutar * i_vergili / (1 - (1 + i_vergili) ** -vade)

    kalan, faiz_toplam, odemeler = tutar, 0.0, []
    for ay in range(1, vade + 1):
        faiz = kalan * aylik_faiz
        anapara = kalan if ay == vade else taksit - faiz * (1 + vergi)
        kalan -= anapara
        faiz_toplam += faiz
        odemeler.append(anapara + faiz * (1 + vergi))

    tahsis = tutar * tahsis_orani
    ucret = tahsis * (1 + bsmv) + sigorta                     # tahsis ücretine de BSMV eklenir
    net = tutar - ucret                                       # ele geçen para

    # Aylık iç verim: net = Σ ödeme_k / (1 + r)^k  (ikiye bölme)
    f = lambda r: sum(p / (1 + r) ** k for k, p in enumerate(odemeler, 1)) - net
    lo, hi = -0.99, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    r = (lo + hi) / 2

    toplam = sum(odemeler)
    return {
        "taksit": taksit,
        "toplam geri ödeme": toplam,
        "faiz": faiz_toplam,
        "KKDF": faiz_toplam * kkdf,
        "BSMV": faiz_toplam * bsmv + tahsis * bsmv,
        "kredinin bedeli": toplam - tutar + ucret,
        "yıllık maliyet oranı %": ((1 + r) ** 12 - 1) * 100,
    }


SENARYOLAR = {
    "İhtiyaç · 100.000 TL · 24 ay · %3,29": dict(tutar=100_000, vade=24, aylik_faiz=0.0329),
    "İhtiyaç · 250.000 TL · 36 ay · %4,50 · 1.500 TL sigorta": dict(tutar=250_000, vade=36, aylik_faiz=0.045, sigorta=1500),
    "Konut · 2.000.000 TL · 120 ay · %2,79": dict(tutar=2_000_000, vade=120, aylik_faiz=0.0279, kkdf=0, bsmv=0),
    "İhtiyaç · 50.000 TL · 1 ay · %0": dict(tutar=50_000, vade=1, aylik_faiz=0.0),
}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for ad, girdi in SENARYOLAR.items():
        print(ad)
        for k, v in kredi(**girdi).items():
            print(f"  {k:<24}{v:>16,.2f}")
