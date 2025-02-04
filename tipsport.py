from playwright.sync_api import sync_playwright
import time
from datetime import datetime

# Selektory
tipsport_match_name_selector = "#contentColumn > div:nth-child(2) > div.LiveOverviewstyled__LiveContainer-sc-1c991wm-0.fPSuZD > div > div:nth-child(3) > a > div > div > div.LiveOverviewMatchstyled__MatchInfo-sc-oy8wyv-3.kDPGFY > div.LiveOverviewMatchstyled__MatchName-sc-oy8wyv-4.lfNCzg > span"
tipsport_odd_one_selector = "#contentColumn > div:nth-child(2) > div.LiveOverviewstyled__LiveContainer-sc-1c991wm-0.fPSuZD > div > div:nth-child(3) > a > div > div > div:nth-child(4) > div > div:nth-child(1) > span:nth-child(2)"
tipsport_odd_two_selector = "#contentColumn > div:nth-child(2) > div.LiveOverviewstyled__LiveContainer-sc-1c991wm-0.fPSuZD > div > div:nth-child(3) > a > div > div > div:nth-child(4) > div > div:nth-child(2) > span:nth-child(2)"
fortuna_match_player1_name_selector = "#app > div.app__container > div.app__main_panel > div > div.live-container > div.live-container__main > div.live-container__content > div > div.sport--TENNIS > div:nth-child(2) > div > div:nth-child(4) > div:nth-child(2) > div > a > div.live-match-info__team.live-match-info__team--1"
fortuna_match_player2_name_selector = "#app > div.app__container > div.app__main_panel > div > div.live-container > div.live-container__main > div.live-container__content > div > div.sport--TENNIS > div:nth-child(2) > div > div:nth-child(4) > div:nth-child(2) > div > a > div.live-match-info__team.live-match-info__team--2"
fortuna_odd_one_selector = "#app > div.app__container > div.app__main_panel > div > div.live-container > div.live-container__main > div.live-container__content > div > div.sport--TENNIS > div:nth-child(2) > div > div:nth-child(4) > div:nth-child(2) > div > div.live-match__markets > div.live-match__top-market.live-match__top-market--1 > div > div > div:nth-child(1) > span.odds_button__value"
fortuna_odd_two_selector = "#app > div.app__container > div.app__main_panel > div > div.live-container > div.live-container__main > div.live-container__content > div > div.sport--TENNIS > div:nth-child(2) > div > div:nth-child(4) > div:nth-child(2) > div > div.live-match__markets > div.live-match__top-market.live-match__top-market--1 > div > div > div:nth-child(2) > span.odds_button__value"


def monitor_tennis_live_odds():
    with sync_playwright() as p:
        # Spustíme prohlížeč
        browser = p.chromium.launch(headless=False)  # Nastav headless=True pro skrytý režim
        context = browser.new_context()
        page = context.new_page()

        # URL live sázkové stránky
        url_tipsport = "https://www.tipsport.cz/live/tenis-43"
        url_fortuna = "https://live.ifortuna.cz/sport/LCZTENNIS"
        page.goto(url_tipsport)

        # Načteme jméno zápasu
        try:
            match_name_element = page.query_selector(tipsport_match_name_selector)
            if match_name_element:
                match_name = match_name_element.text_content()
            else:
                match_name = "Neznámý zápas"
        except Exception as e:
            print(f"Chyba při načítání jména zápasu: {e}")
            match_name = "Neznámý zápas"

        print(f"Zápas: {match_name}")

        last_odd_one = None
        last_odd_two = None

        # Smyčka pro sledování kurzů
        while True:
            try:
                # Načteme kurzy
                odd_one_element = page.query_selector(tipsport_odd_one_selector)
                odd_two_element = page.query_selector(tipsport_odd_two_selector)

                odd_one = odd_one_element.text_content() if odd_one_element else "N/A"
                odd_two = odd_two_element.text_content() if odd_two_element else "N/A"

                # Vypíšeme pouze, pokud se něco změnilo
                if odd_one != last_odd_one or odd_two != last_odd_two:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] kurz 1: {odd_one} ||| kurz 2: {odd_two}")
                    last_odd_one = odd_one
                    last_odd_two = odd_two

            except Exception as e:
                print(f"Chyba při načítání kurzů: {e}")

            # Čekáme 3 sekundy
            time.sleep(3)

        browser.close()

# Spustíme funkci
monitor_tennis_live_odds()
