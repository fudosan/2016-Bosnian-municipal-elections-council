import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re


def create_driver():
    """Creates a simple webdriver with basic options

    :return: webdriver with configured options
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_path = "path-to-your-chrome-driver"
    return webdriver.Chrome(executable_path=chrome_path, options=chrome_options)


class Council2016Spider(scrapy.Spider):
    name = 'council2016'
    allowed_domains = ['www.izbori.ba']
    start_urls = ['https://www.izbori.ba/rezultati_izbora_2016/?resId=13&langId=1#/9/0/0/0']

    def __init__(self):
        driver = create_driver()
        driver.get("https://www.izbori.ba/rezultati_izbora_2016/?resId=13&langId=1#/9/0/0/0")
        time.sleep(3)
        self.html = driver.page_source
        driver.close()

    def parse(self, response):
        resp = Selector(text=self.html)
        for izborna_jedinica in resp.xpath("//div[@id='leftBar']/select[1]/option"):
            izborna_jedinica_name = izborna_jedinica.xpath(".//text()").get()
            if izborna_jedinica_name == '-':
                continue
            izborna_jedinica_value = int(re.search(r'\((\b\d+\b)\)', izborna_jedinica_name).group(1))
            driver = create_driver()
            driver.get(f"https://www.izbori.ba/rezultati_izbora_2016/?resId=13&langId=1#/9/{izborna_jedinica_value}/0/0")
            time.sleep(2)
            new_page = driver.page_source
            new_page_selectable = Selector(text=new_page)
            options = new_page_selectable.xpath("//div[@id='leftBar']/select[2]/option")
            for ind, option in enumerate(options):
                biracko_mjesto = option.xpath('.//text()').get()
                if biracko_mjesto == '-':
                    stranka_dict = {}
                    broj_obradjenih_listica = new_page_selectable.xpath("//div[@id='leftBar']/span/text()").get().split(':')[-1]
                    broj_vazecih_listica = new_page_selectable.xpath("//div[@id='leftBar']/div[3]/div/span/text()").get().split(':')[-1]
                    broj_vazecih_redovnih_listica = new_page_selectable.xpath("//div[@id='leftBar']/div[3]/div/div[1]/span/span/text()").get()
                    broj_vazecih_posta_listica = new_page_selectable.xpath("//div[@id='leftBar']/div[3]/div/div[2]/span/span/text()").get()
                    broj_vazecih_odsustvo_mobilni_tim_i_DKP_listica = new_page_selectable.xpath("//div[@id='leftBar']/div[3]/div/div[3]/span/span/text()").get()
                    broj_vazecih_potvrdjenih_listica = new_page_selectable.xpath("//div[@id='leftBar']/div[3]/div/div[4]/span/span/text()").get()
                    broj_redovnih_mandata = new_page_selectable.xpath("//tr[@class='data ng-scope']/td[3]/text()").get()
                    broj_nac_manjina_mandata = new_page_selectable.xpath("//tr[@class='data ng-scope']/td[4]/text()").get()
                    for stranka in new_page_selectable.xpath("//table[@class='kingTable ng-scope']/tbody/tr[@class='ng-scope']"):
                        stranka_kod = stranka.xpath(".//td[1]/a/text()").get()
                        stranka_broj_mandata = stranka.xpath(".//td[9]/text()").get()
                        if stranka_broj_mandata is None:
                            stranka_broj_mandata = '0'
                        stranka_dict[stranka_kod] = {
                            'broj glasova - biracko mjesto': stranka.xpath(".//td[3]/text()").get(),
                            'ukupan broj vazecih listica (redovni) - biracko mjesto': stranka.xpath(".//td[4]/text()").get(),
                            'ukupan broj vazecih listica (posta) - biracko mjesto': stranka.xpath(".//td[5]/text()").get(),
                            'ukupan broj vazecih listica (odsustvo, mobilni tim i DKP) - biracko mjesto': stranka.xpath(".//td[6]/text()").get(),
                            'ukupan broj vazecih listica (potvrdjeni) - biracko mjesto': stranka.xpath(".//td[7]/text()").get(),
                            'broj mandata': stranka_broj_mandata
                        }
                    for nac_manjina in new_page_selectable.xpath("//table[@class='kingTable']/tbody/tr[@class='ng-scope']"):
                        nac_manjina_kod = nac_manjina.xpath(".//td[1]/text()").get()
                        if nac_manjina_kod == 'Nema podataka za prikazivanje!':
                            continue
                        nac_manjina_mandat = nac_manjina.xpath(".//td[9]/i").get()
                        if nac_manjina_mandat is not None:
                            nac_manjina_mandat = '1'
                        else:
                            nac_manjina_mandat = '0'
                        stranka_dict[nac_manjina_kod] = {
                            'broj glasova - biracko mjesto': nac_manjina.xpath(".//td[3]/text()").get(),
                            'ukupan broj vazecih listica (redovni) - biracko mjesto': nac_manjina.xpath(".//td[4]/text()").get(),
                            'ukupan broj vazecih listica (posta) - biracko mjesto': nac_manjina.xpath(".//td[5]/text()").get(),
                            'ukupan broj vazecih listica (odsustvo, mobilni tim i DKP) - biracko mjesto': nac_manjina.xpath(".//td[6]/text()").get(),
                            'ukupan broj vazecih listica (potvrdjeni) - biracko mjesto': nac_manjina.xpath(".//td[7]/text()").get(),
                            'broj mandata': nac_manjina_mandat
                        }
                    continue
                driver.find_element_by_xpath(f"//div[@id='leftBar']/select[2]/option[{ind + 1}]").click()
                time.sleep(2)
                new_page_data = driver.page_source
                new_page_selectable_data = Selector(text=new_page_data)
                broj_biraca = new_page_selectable_data.xpath("//tr[@class='data']/td[1]/text()").get()
                broj_izaslih = new_page_selectable_data.xpath(
                    "//div[@class='pieChartDiv']/div[1]/div/table/tbody/tr[1]/td[2]/b/text()").get()
                broj_neizaslih = new_page_selectable_data.xpath(
                    "//div[@class='pieChartDiv']/div[1]/div/table/tbody/tr[3]/td[2]/b/text()").get()
                broj_vazecih_listica_bir_mjesto = new_page_selectable_data.xpath(
                    "//div[@class='pieChartDiv']/div[2]/div/table/tbody/tr[1]/td[2]/b/text()").get()
                broj_nevazecih_praznih_listica = new_page_selectable_data.xpath(
                    "//div[@class='pieChartDiv']/div[2]/div/table/tbody/tr[3]/td[2]/b/text()").get()
                broj_nevazecih_listica_drugi_krit = new_page_selectable_data.xpath(
                    "//div[@class='pieChartDiv']/div[2]/div/table/tbody/tr[5]/td[2]/b/text()").get()
                for stranka in new_page_selectable_data.xpath(
                        "//table[@class='kingTable']/tbody/tr[@class='ng-scope']"):
                    stranka_sifra = stranka.xpath(".//td[1]/a/text()").get()
                    if stranka_sifra is None:
                        continue
                    stranka_ime = stranka.xpath(".//td[2]/a/text()").get()
                    stranka_broj_glasova = stranka.xpath(".//td[3]/text()").get()
                    stranka_broj_glasova_procenti = stranka.xpath(".//td[4]/text()").get()
                    yield {
                        'izborna jedinica': izborna_jedinica_name,
                        'biracko mjesto': biracko_mjesto,
                        'broj biraca - biracko mjesto': broj_biraca,
                        'broj redovnih mandata': broj_redovnih_mandata,
                        'broj mandata nacionalnih manjina': broj_nac_manjina_mandata,
                        'stranka sifra': stranka_sifra,
                        'stranka ': stranka_ime,
                        'broj glasova stranka - biracko mjesto': stranka_broj_glasova,
                        'broj glasova stranka (procenti) - biracko mjesto': stranka_broj_glasova_procenti,
                        'izasli na izbore - biracko mjesto': broj_izaslih,
                        'nisu izasli na izbore - biracko mjesto': broj_neizaslih,
                        'broj vazecih listica - biracko mjesto': broj_vazecih_listica_bir_mjesto,
                        'broj nevazecih praznih listica - biracko mjesto': broj_nevazecih_praznih_listica,
                        'broj nevazecih praznih listica po drugim kriterijama - biracko mjesto': broj_nevazecih_listica_drugi_krit,
                        'ukupan broj obradjenih listica - izborna jedinica': broj_obradjenih_listica,
                        'ukupan broj vazecih listica - izborna jedinica': broj_vazecih_listica,
                        'ukupan broj vazecih listica (redovni) - izborna jedinica': broj_vazecih_redovnih_listica,
                        'ukupan broj vazecih listica (posta) - izborna jedinica': broj_vazecih_posta_listica,
                        'ukupan broj vazecih listica (odsustvo, mobilni tim i DKP) - izborna jedinica': broj_vazecih_odsustvo_mobilni_tim_i_DKP_listica,
                        'ukupan broj vazecih listica (potvrdjeni) - izborna jedinica': broj_vazecih_potvrdjenih_listica,
                        'broj glasova - biracko mjesto': stranka_dict[stranka_sifra]['broj glasova - biracko mjesto'],
                        'ukupan broj vazecih listica (redovni) - biracko mjesto': stranka_dict[stranka_sifra]['ukupan broj vazecih listica (redovni) - biracko mjesto'],
                        'ukupan broj vazecih listica (posta) - biracko mjesto': stranka_dict[stranka_sifra]['ukupan broj vazecih listica (posta) - biracko mjesto'],
                        'ukupan broj vazecih listica (odsustvo, mobilni tim i DKP) - biracko mjesto': stranka_dict[stranka_sifra]['ukupan broj vazecih listica (odsustvo, mobilni tim i DKP) - biracko mjesto'],
                        'ukupan broj vazecih listica (potvrdjeni) - biracko mjesto': stranka_dict[stranka_sifra]['ukupan broj vazecih listica (potvrdjeni) - biracko mjesto'],
                        'broj mandata': stranka_dict[stranka_sifra]['broj mandata']
                    }
            driver.close()