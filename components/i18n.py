"""Text in English (en), Kinyarwanda (rw) and French (fr) for the farmer-facing parts of the app.

Kinyarwanda and French wording should be checked by native speakers before each release.
"""

LANGS = {"en": "English", "rw": "Kinyarwanda", "fr": "Français"}

MONTHS_FULL = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "rw": ["Mutarama", "Gashyantare", "Werurwe", "Mata", "Gicurasi", "Kamena", "Nyakanga", "Kanama", "Nzeri", "Ukwakira", "Ugushyingo", "Ukuboza"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
}
MONTHS_SHORT = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "rw": MONTHS_FULL["rw"],
    "fr": ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"],
}
BEFORE_AFTER = {"en": ("Before", "After"), "rw": ("Mbere ya", "Nyuma ya"), "fr": ("Avant", "Après")}

SEASONS = {
    "en": {"Season A": "Season A (plant Sep, harvest Dec to Feb)",
           "Season B": "Season B (plant Feb to Mar, harvest May to Aug)",
           "Season C": "Season C (plant Jun to Jul, harvest Aug to Sep)"},
    "rw": {"Season A": "Igihembwe A (Nzeri kugeza Gashyantare)",
           "Season B": "Igihembwe B (Gashyantare kugeza Kanama)",
           "Season C": "Igihembwe C (Kamena kugeza Nzeri)"},
    "fr": {"Season A": "Saison A (semis en sept., récolte de déc. à févr.)",
           "Season B": "Saison B (semis de févr. à mars, récolte de mai à août)",
           "Season C": "Saison C (semis de juin à juil., récolte d'août à sept.)"},
}

CROPS = {
    "rw": {"Amaranth": "Dodo", "Banana for beer": "Ibitoki by'inzoga", "Bush bean": "Ibishyimbo by'ibihuru", "Cabbage": "Amashu",
           "Carrot": "Karoti", "Cassava": "Imyumbati", "Climbing bean": "Ibishyimbo bishorera", "Coffee": "Ikawa",
           "Cooking banana": "Ibitoki bitetse", "Dessert banana": "Imineke", "Eggplant": "Intoryi", "Groundnut": "Ubunyobwa",
           "Irish potato": "Ibirayi", "Maize": "Ibigori", "Millet": "Uburo", "Napia grass for fodder": "Ubwatsi bw'amatungo (Napier)",
           "Onion": "Ibitunguru", "Paddy rice": "Umuceri", "Pea": "Amashaza", "Sorghum": "Amasaka", "Soybean": "Soya",
           "Sugar cane": "Ibisheke", "Sun flower": "Ururabyo", "Sweet potato": "Ibijumba", "Taro": "Amateke",
           "Tomato": "Inyanya", "Wheat": "Ingano"},
    "fr": {"Amaranth": "Amarante", "Banana for beer": "Banane à bière", "Bush bean": "Haricot nain", "Cabbage": "Chou",
           "Carrot": "Carotte", "Cassava": "Manioc", "Climbing bean": "Haricot volubile", "Coffee": "Café",
           "Cooking banana": "Banane à cuire", "Dessert banana": "Banane dessert", "Eggplant": "Aubergine", "Groundnut": "Arachide",
           "Irish potato": "Pomme de terre", "Maize": "Maïs", "Millet": "Millet", "Napia grass for fodder": "Herbe de Napier (fourrage)",
           "Onion": "Oignon", "Paddy rice": "Riz paddy", "Pea": "Pois", "Sorghum": "Sorgho", "Soybean": "Soja",
           "Sugar cane": "Canne à sucre", "Sun flower": "Tournesol", "Sweet potato": "Patate douce", "Taro": "Taro",
           "Tomato": "Tomate", "Wheat": "Blé"},
}

GROUPS = {
    "en": {"Bread and cereals": "cereal and bread prices", "Vegetables": "vegetable prices", "Food (all)": "overall food prices",
           "Meat": "meat prices", "Milk, cheese and eggs": "milk and egg prices"},
    "rw": {"Bread and cereals": "ibiciro by'ibinyampeke n'imigati", "Vegetables": "ibiciro by'imboga", "Food (all)": "ibiciro by'ibiribwa muri rusange",
           "Meat": "ibiciro by'inyama", "Milk, cheese and eggs": "ibiciro by'amata n'amagi"},
    "fr": {"Bread and cereals": "les prix des céréales et du pain", "Vegetables": "les prix des légumes", "Food (all)": "les prix alimentaires en général",
           "Meat": "les prix de la viande", "Milk, cheese and eggs": "les prix du lait et des œufs"},
}

T = {
 "language": {"en": "Language", "rw": "Ururimi", "fr": "Langue"},
 "tagline": {"en": "When to plant, harvest and sell.", "rw": "Igihe cyo gutera, gusarura no kugurisha.", "fr": "Quand semer, récolter et vendre."},
 "src_title": {"en": "Where the numbers come from", "rw": "Aho imibare ikomoka", "fr": "D'où viennent les chiffres"},
 "src_survey": {"en": "Farm survey: NISR Agricultural Household Survey 2024", "rw": "Ubushakashatsi ku bahinzi: NISR, Agricultural Household Survey 2024",
                "fr": "Enquête agricole : NISR, Agricultural Household Survey 2024"},
 "src_prices": {"en": "Prices: NISR consumer price index, up to {d}", "rw": "Ibiciro: NISR, indangagaciro y'ibiciro ku baguzi, kugeza {d}",
                "fr": "Prix : indice des prix à la consommation du NISR, jusqu'à {d}"},
 "disclaimer": {"en": "Guidance, not advice: prices are national averages, not offers from buyers.",
                "rw": "Ni ubuyobozi bwa rusange, si inama yihariye: ibiciro ni impuzandengo y'igihugu, si ibyo abaguzi batanze.",
                "fr": "Repères, pas des conseils : les prix sont des moyennes nationales, pas des offres d'acheteurs."},
 "nav_0": {"en": "My crop", "rw": "Igihingwa cyanjye", "fr": "Ma culture"},
 "nav_1": {"en": "Crop details", "rw": "Ibisobanuro by'igihingwa", "fr": "Détails de la culture"},
 "nav_2": {"en": "Compare crops", "rw": "Gereranya ibihingwa", "fr": "Comparer les cultures"},
 "nav_3": {"en": "Where it grows", "rw": "Aho gihingwa", "fr": "Où elle pousse"},
 "nav_4": {"en": "Price forecast", "rw": "Iteganya ry'ibiciro", "fr": "Prévision des prix"},
 "english_only": {"en": "", "rw": "Uru rupapuro ruboneka mu Cyongereza gusa.", "fr": "Cette page n'est disponible qu'en anglais."},
 "title": {"en": "My crop", "rw": "Igihingwa cyanjye", "fr": "Ma culture"},
 "intro": {"en": "Choose what you grow and when you plant. You will see when farmers usually harvest it, when prices are best, and where it is most common.",
           "rw": "Hitamo icyo uhinga n'igihembwe uhingiramo. Uzabona igihe abahinzi basarura akenshi, igihe ibiciro biba byiza, n'aho gihingwa cyane.",
           "fr": "Choisissez ce que vous cultivez et la saison. Vous verrez quand les agriculteurs récoltent en général, quand les prix sont les meilleurs et où cette culture est la plus courante."},
 "q_crop": {"en": "What do you grow?", "rw": "Uhinga iki?", "fr": "Que cultivez-vous ?"},
 "q_season": {"en": "Which growing season?", "rw": "Ni mu gihembwe cy'ihinga kihe?", "fr": "Quelle saison de culture ?"},
 "c_info": {"en": "Season C has few survey records, so take these answers as a rough guide.",
            "rw": "Igihembwe C gifite amakuru make mu bushakashatsi, bityo ibisubizo ni igereranya gusa.",
            "fr": "La saison C compte peu de réponses à l'enquête : prenez ces réponses comme une indication approximative."},
 "plant_title": {"en": "When to plant", "rw": "Igihe cyo gutera", "fr": "Quand semer"},
 "plant_yes": {"en": "Most farmers plant **{crop}** in this period: **{w}**.", "rw": "Abenshi mu bahinzi batera **{crop}** muri iki gihe: **{w}**.",
               "fr": "La plupart des agriculteurs sèment **{crop}** à cette période : **{w}**."},
 "plant_no": {"en": "Farmers did not report one clear planting time for this crop.", "rw": "Abahinzi ntibagaragaje igihe kimwe gisobanutse cyo gutera iki gihingwa.",
              "fr": "Les agriculteurs n'ont pas indiqué de période de semis claire pour cette culture."},
 "harvest_title": {"en": "When to harvest", "rw": "Igihe cyo gusarura", "fr": "Quand récolter"},
 "harvest_yes": {"en": "The most common harvest time is **{w}**.", "rw": "Igihe abenshi basaruramo ni **{w}**.", "fr": "La période de récolte la plus courante est **{w}**."},
 "harvest_share": {"en": "About {p} of farmers who gave a harvest time chose this one.", "rw": "Hafi {p} by'abahinzi batanze igihe cyo gusarura bahisemo iki.",
                   "fr": "Environ {p} des agriculteurs ayant indiqué une période de récolte ont choisi celle-ci."},
 "harvest_no": {"en": "Farmers did not report one clear harvest time for this crop.", "rw": "Abahinzi ntibagaragaje igihe kimwe gisobanutse cyo gusarura iki gihingwa.",
                "fr": "Les agriculteurs n'ont pas indiqué de période de récolte claire pour cette culture."},
 "sell_title": {"en": "When to sell", "rw": "Igihe cyo kugurisha", "fr": "Quand vendre"},
 "sell_wait": {"en": "**Prices are usually lowest around harvest. If you can store {crop} safely, waiting until {m} usually pays better.**",
               "rw": "**Ibiciro akenshi biba biri hasi mu gihe cyo gusarura. Niba ushobora kubika {crop} neza, gutegereza kugeza muri {m} akenshi bigira inyungu.**",
               "fr": "**Les prix sont généralement au plus bas autour de la récolte. Si vous pouvez stocker {crop} sans risque, attendre {m} rapporte en général davantage.**"},
 "sell_wait_cap": {"en": "{g} are typically about {x}% higher in {m} than in the harvest month.",
                   "rw": "{g} akenshi biba biri hejuru hafi ya {x}% muri {m} ugereranyije n'ukwezi gusarurirwamo.",
                   "fr": "{g} sont en général supérieurs d'environ {x} % en {m} par rapport au mois de récolte."},
 "sell_now": {"en": "**Sell soon after harvest.**", "rw": "**Gurisha vuba nyuma yo gusarura.**", "fr": "**Vendez peu après la récolte.**"},
 "sell_now_cap": {"en": "{g} are already at their best in the harvest month, so waiting is unlikely to pay.",
                  "rw": "{g} biba biri ku rwego rwiza mu kwezi gusarurirwamo, bityo gutegereza ntibyunguka cyane.",
                  "fr": "{g} sont déjà à leur meilleur niveau pendant le mois de récolte : attendre a peu de chances de rapporter."},
 "sell_disc": {"en": "This is the normal market pattern across Rwanda. It is not a price quote from a buyer, and it does not count storage costs or crop losses.",
               "rw": "Iyi ni imiterere isanzwe y'isoko mu Rwanda hose. Si igiciro watangiwe n'umuguzi, kandi ntabwo harimo ikiguzi cyo kubika cyangwa igihombo cy'umusaruro.",
               "fr": "C'est l'évolution habituelle du marché dans tout le Rwanda. Ce n'est pas une offre d'acheteur, et elle ne tient pas compte des coûts de stockage ni des pertes de récolte."},
 "sell_guess": {"en": "Note: we assume {crop} prices move like vegetable prices. This is our best estimate and has not been confirmed.",
                "rw": "Icyitonderwa: dutekereza ko ibiciro bya {crop} bigenda nk'iby'imboga. Ni igereranya ryacu kandi ntiriremezwa.",
                "fr": "Remarque : nous supposons que les prix de {crop} évoluent comme ceux des légumes. C'est notre meilleure estimation, non confirmée."},
 "sell_none": {"en": "**No price guide for this crop.**", "rw": "**Nta nama ku biciro by'iki gihingwa.**", "fr": "**Pas de repère de prix pour cette culture.**"},
 "sell_none_cap": {"en": "The national price statistics do not track a group that matches this crop.",
                   "rw": "Imibare y'igihugu y'ibiciro ntigaragaza itsinda rihuye n'iki gihingwa.",
                   "fr": "Les statistiques nationales de prix n'ont pas de groupe correspondant à cette culture."},
 "where_title": {"en": "Where it is most common", "rw": "Aho gihingwa cyane", "fr": "Où elle est la plus courante"},
 "where_none": {"en": "Not enough survey records to say.", "rw": "Nta makuru ahagije y'ubushakashatsi yo kubivuga.", "fr": "Pas assez de réponses à l'enquête pour le dire."},
 "where_cap": {"en": "These districts grow the most {crop} compared with their other crops. The percentage is its share of what surveyed farmers there grow. It is not total harvest size.",
               "rw": "Utu turere dutera {crop} nyinshi ugereranyije n'ibindi bihingwa byatwo. Ijanisha ni umugabane waryo mu byo abahinzi babajijwe bahinga. Si ingano y'umusaruro wose.",
               "fr": "Ces districts cultivent le plus de {crop} par rapport à leurs autres cultures. Le pourcentage est sa part dans ce que cultivent les agriculteurs enquêtés. Ce n'est pas la taille de la récolte totale."},
}


def t(key, lang, **kw):
    s = T[key].get(lang) or T[key]["en"]
    return s.format(**kw) if kw else s
