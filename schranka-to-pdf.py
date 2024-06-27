# %%
import pandas as pd
import numpy as np
import pprint
import html5lib

link = r"https://c4-10912.cesys.info//schranka/298839495;298839509;299734554;299744062;299747335;304706693;304715281;306304547"

# %%
import requests
from bs4 import BeautifulSoup

response = requests.get(link)
soup = BeautifulSoup(response.text)
offers = []
for article in soup.find_all(
    name="article", attrs={"class": ["offer", "offer--favourites"]}
):
    hotel = article.a.text
    stars = "*" * int(article.find("span", {"title": True})["title"].replace("*", ""))
    destination_tree = (
        article.find("p", class_="offer__country")
        .text.replace("\n", "")
        .replace("\xa0", "")
    )
    offer__date = (
        article.find("p", class_="offer__date")
        .text.split(" ")[1]
        .replace("\t", "")
        .replace("\n", "")
        .replace("\xa0", "")
    )
    offer__duration = (
        article.find("p", class_="offer__duration")
        .text.split(" ")[1]
        .replace("\t", "")
        .replace("\n", "")
        .replace("\xa0", "")
    )
    offer__boarding = (
        "".join(str(article.find("p", class_="offer__boarding").text))
        .replace("Strava: ", "")
        .replace("\n", "")
        .replace("\xa0", "")
        .replace("\t", "")
    )
    offer__price = int(
        article.find("span", class_="offer__price--current")
        .text.replace("\n", "")
        .replace("\xa0", "")
        .replace("Kč", "")
    )
    offers.append(
        [
            hotel,
            stars,
            destination_tree,
            offer__date,
            offer__duration,
            offer__boarding,
            offer__price,
        ]
    )
print(offers)

# %%
from fpdf import FPDF
import pandas as pd
import unicodedata


class PDF(FPDF):
    def __init__(
        self,
        orientation="P",
        unit="mm",
        format="A4",
        font_cache_dir=None,
        background=r"D:\PetrVavrinec\Dokumenty\www\www.travelasap.cz\grafika\A4-letaky-vyloha\umbrella-tips-white-orange.png",
    ):
        super().__init__(
            orientation=orientation,
            unit=unit,
            format=format,
            font_cache_dir=font_cache_dir,
        )
        self.background = background
        self.add_font("segoeui", "", r"C:\Windows\Fonts\segoeui.ttf", uni=True)

    def add_page(self):
        super().add_page()
        self.image(self.background, x=0, y=0, w=self.w, h=self.h)

    # def header(self, image):
    #     self.image(image, x=0, y=0, w=self.w, h=self.h)

    # def footer(self) -> None:
    #     self.set_y(-15)
    #     self.set_font("segoeui", size=60)
    #     self.cell(0, 10, "www.travelasap.cz", align="C")
    #     return super().footer()

    def hotel_row(self, index, data):
        y_offset = 119
        row_height = 17.5

        self.title_big = "VYBÍRÁME SRDCEM"

        self.title_small = "a hledáme to nejlepší pro Vás"

        hotel_and_stars = str(f"{data[0]} {data[1]}")
        extended_info = str(f"{data[2]}, {data[3]}, {data[4]}, {data[5]}")
        tisice = str(f" {str(data[6])[:-3]}.")
        stovky = str(f"{str(data[6])[-3:]}Kč")

        self.set_font("segoeui", "", size=48)
        self.title_big_w = self.get_string_width(self.title_big) + 6
        self.set_xy((self.w - self.title_big_w) / 2, 90)
        self.cell(
            self.title_big_w,
            10,
            txt=self.title_big,
            border=myborder,
            align="C",
        )
        self.set_font("segoeui", "", size=32)
        self.title_small_w = self.get_string_width(self.title_small) + 6
        self.set_xy((self.w - self.title_small_w) / 2, 105)
        self.cell(
            self.title_small_w,
            10,
            txt=self.title_small,
            border=myborder,
            align="C",
        )

        self.set_font("segoeui", "", size=18)
        self.set_xy(10, index * row_height + y_offset)
        self.cell(
            140,
            10,
            txt=hotel_and_stars,
            border=myborder,
            align="L",
        )
        self.set_xy(self.get_x() + 13, self.get_y() + 4)
        self.set_font("segoeui", "", size=45)
        self.cell(15, 10, txt=tisice, border=myborder, align="R")
        self.set_xy(self.get_x(), self.get_y() + 2)
        self.set_font("segoeui", "", size=20)
        self.cell(20, 10, txt=stovky, border=myborder, align="L")

        self.set_font("segoeui", size=12)
        self.set_xy(10, index * row_height + y_offset + 10)
        self.cell(135, 6, txt=extended_info, border=myborder, align="L")


image_file = r"D:\PetrVavrinec\Dokumenty\www\www.travelasap.cz\grafika\A4-letaky-vyloha\umbrella-tips-white-orange.png"
pdf = PDF("P", "mm", "A4", background=image_file)
pdf.add_page()

# iterace přes seznam dat a vytvoření řádků pro tabulku
text = ""
myborder = False

for index, row in enumerate(offers):
    pdf.hotel_row(index, row)


# table = Table(table_data, 185 * mm, 8 * 17 * mm)

print(f"Vytvořený text:\n{text}")


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


pdf_name = strip_accents((pdf.title_big + ".pdf").replace(" ", "_").lower())
# Create PDF document
pdf.output(pdf_name)

# %%
