#     a,  8a
#     `8, `8)                            ,adPPRg,
#      8)  ]8                        ,ad888888888b
#     ,8' ,8'                    ,gPPR888888888888
#    ,8' ,8'                 ,ad8""   `Y888888888P
#    8)  8)              ,ad8""        (8888888""
#    8,  8,          ,ad8""            d888""
#    `8, `8,     ,ad8""            ,ad8""
#     `8, `" ,ad8""            ,ad8""
#        ,gPPR8b           ,ad8""
#       dP:::::Yb      ,ad8""
#       8):::::(8  ,ad8""
#       Yb:;;;:d888""
#        "8ggg8P"

from bs4 import BeautifulSoup
import requests, re, os

domain = "https://tpackss.globaltobaccocontrol.org"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}


def html_scrape(entries, total):
    i = 1
    for entry in entries:
        title = entry["packs_title"].strip()  # "Mevius China W3 03"
        brand = re.search("(.*) China", title).group(1)  # anything preceding " China"
        pack = re.search("China (.*)", title).group(1)  # anything following "China "
        print(f"Collecting Pack {brand} {pack} ({i}/{total})...")

        # create folder
        dir = f"Packs/{brand}/{pack}"
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Folder {dir}\t\t created")

        # extract path from attr
        path = re.search('about="(.*?)"', str(entry["rendered_item"])).group(1)
        r = requests.post(f"{domain}/{path}", headers=headers)

        soup = BeautifulSoup(r.content, "html.parser")
        # find pack images
        images = soup.find("div", {"class": "thumbnails"}).find_all("img")
        for image in images:
            # resize image
            path = image["src"].replace("75x84", "500x500")
            r = requests.get(f"{domain}/{path}", headers=headers)

            # extract filename from path
            slug = re.search("([A-Za-z0-9]+(_[A-Za-z0-9]+)+.jpg)", path).group(0)
            open(f"{dir}/{slug}", "wb").write(r.content)
            print(f"{slug}\t\t saved")

        i += 1
        print("\n")


def json_scrape():
    query = """
        query packsQuery($search: [String]!, $offset: Int!, $limit: Int!, $conditions: [ConditionInput], $conditionGroup: ConditionGroupInput, $sort: [SortInput]) {
            searchAPISearch(
                index_id: \"packs_db\"
                range: {offset: $offset, limit: $limit}
                fulltext: {keys: $search}
                conditions: $conditions
                condition_group: $conditionGroup
                sort: $sort
            ) {
                documents {
                    ... on PacksDbDoc {
                        packs_title
                        packs_nid
                        rendered_item
                    }
                }
                result_count
            }
        }
    """
    json_data = {
        "operationName": "packsQuery",
        "variables": {
            "search": "",
            "limit": 500,
            "offset": 263,
            "conditions": [],
            "conditionGroup": {
                "conjunction": "AND",
                "groups": [
                    {
                        "conjunction": "OR",
                        "conditions": [
                            {
                                "operator": "=",
                                "name": "packs_product_type_tid",
                                "value": "6",  # Type: Cigarettes
                            }
                        ],
                    },
                    {
                        "conjunction": "OR",
                        "conditions": [
                            {
                                "operator": "=",
                                "name": "packs_country_tid",
                                "value": "12",  # Country: China
                            }
                        ],
                    },
                    {
                        "conjunction": "OR",
                        "conditions": [
                            {
                                "operator": "=",
                                "name": "packs_collection_year_name",
                                "value": "2023",  # Year: 2023
                            }
                        ],
                    },
                ],
            },
            "sort": {"sort": {"field": "packs_brand_name", "value": "asc"}},
        },
        "query": query,
    }

    r = requests.post(f"{domain}/graphql", headers=headers, json=json_data)
    entries = r.json()["data"]["searchAPISearch"]["documents"]
    total = r.json()["data"]["searchAPISearch"]["result_count"]
    html_scrape(entries, total)


json_scrape()
