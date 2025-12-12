from requests_html import HTMLSession
import os

session = HTMLSession()
domain = "https://tpackss.globaltobaccocontrol.org"
url = f"{domain}/index.php/pack-search?countries=12&years=2179&orderBy=packs_brand_name&productTypes=6.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}
r = session.get(url, headers=headers)
r.html.render(sleep=8)

page = 1
total_packs = 0


def next_page():
    global page
    page += 1
    print(f"Navigating to next page\t\t-> {page}")
    next_page = "document.querySelector('nav.apollo__pager li.pager-text:nth-last-child(2)').click()"
    r.html.render(script=next_page, sleep=8)
    scrape_page()


def scrape_page():
    global total_packs
    entries = r.html.find("div.apollo__item")
    for entry in entries:
        title = entry.find("div.node--type-cigarette-pack__title", first=True).text
        idx = title.index("China")
        brand = title[: idx - 1]  # -1/+1 to account slice for whitespace
        pack = title[idx + 6 :]

        # path = f"Packs/{brand}/{pack}"  # create folders
        # if not os.path.exists(path):
        #     os.makedirs(path)

        img_src = entry.find("img", first=True).attrs["src"]
        img_url = (
            domain + img_src.replace("278x248", "500x500")[: img_src.index("1.jpg")]
        )
        i = 1
        while i <= 20:
            url = f"{img_url}{i}.jpg"
            r_img = session.get(url, headers=headers)

            status = r_img.status_code
            if status == 200:
                # open(f"{path}/{brand} {pack} ({i}).jpg", "wb").write(r_img.content)
                print(f"{brand} {pack} ({i}) \t\t saved")
            elif not status == 404:
                print(f"{brand} {pack} ({i}) \t\t Error {status}")
            i += 1

        total_packs += 1

    if r.html.find("span", containing="next"):
        next_page()
    else:
        print(
            f"Scraping complete.\nPages scraped:\t{page}\t\tPacks collected:\t{total_packs}"
        )
        exit()


scrape_page()
