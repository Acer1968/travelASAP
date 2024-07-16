import sqlite3
from travelasap import Hotel
import math

def create_sitemap(hotels, sitemap_number):
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for hotel in hotels:
        hotel_desc = Hotel(hotel[0])
        hotel_url_frag1, hotel_url_frag2 = hotel_desc.generate_url_fragments()
        if hotel_url_frag2:
            url_record = f"""<url>
    <loc>https://www.travelasap.cz/{hotel_url_frag2}/</loc>
    <lastmod>2024-07-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    </url>"""
            sitemap_content += url_record + '\n'
    
    sitemap_content += '</urlset>'
    
    with open(f'sitemap_{sitemap_number}.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

conn = sqlite3.connect('travelasap.db')

sql_query = "SELECT Hotel_ID, Hotel_name, Country_and_Destination FROM hotels WHERE Hotel_Picture IS NOT NULL AND Hotel_Picture != ''"

hotels = conn.execute(sql_query).fetchall()

# Rozdělení hotelů do bloků po 50 000
block_size = 50000
num_sitemaps = math.ceil(len(hotels) / block_size)

for i in range(num_sitemaps):
    start = i * block_size
    end = (i + 1) * block_size
    hotels_block = hotels[start:end]
    create_sitemap(hotels_block, i + 1)

conn.close()

print(f"Vytvořeno {num_sitemaps} sitemap souborů.")