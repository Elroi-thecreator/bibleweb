# -*- coding: utf-8 -*-
"""
Curated Contemporary Worship Song Datasets
Pastor John Jebaraj, Dr. Joseph Aldrin, Pastor Benny Joshua
Compliant with PROD-SONGS-001 v1.5.1
"""

def make_stanza(st_type, label, lines_ta, lines_en):
    return {
        "type": st_type,
        "label": label,
        "ta": "\n".join(lines_ta),
        "en": "\n".join(lines_en),
        "lines_ta": lines_ta,
        "lines_en": lines_en,
    }

# =========================================================================
# 1. PASTOR JOHN JEBARAJ (LEVI SERIES & BELOVED WORSHIP HITS)
# =========================================================================
JOHN_JEBARAJ_EXTRA_SONGS = [
    {
        "title_ta": "இஸ்ரவேலின் துதிகளில்",
        "title_en": "Isravelin Thuthigalil",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=MuiSYOWWVAY",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "இஸ்ரவேலின் துதிகளில் வாசம் செய்யும் தேவனே",
                "எங்கள் துதியின் மத்தியிலே இறங்கி வாருமே",
                "அல்லேலூயா அல்லேலூயா அல்லேலூயா ஆமென்",
                "அல்லேலூயா அல்லேலூயா அல்லேலூயா ஆமென்"
            ], [
                "Isravelin thudhigalil vaasam seiyum Dhevanae",
                "Engal thudhiyin madhiyilay irangi vaarumae",
                "Hallelujah Hallelujah Hallelujah Amen",
                "Hallelujah Hallelujah Hallelujah Amen"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "சேராபீம்கள் போற்றிடும் பரிசுத்த தெய்வமே",
                "கேரூபீம்கள் பாடிடும் சர்வ வல்லவரே",
                "தூயவரே துதிக்கு பாத்திரரே",
                "முழு உள்ளத்தோடு உம்மை பணிகின்றோம்"
            ], [
                "Seraphim-gal potridum parisutha Deivamae",
                "Cherubim-gal paadidum sarva vallavarae",
                "Thooyavarae thudhiku paathirarae",
                "Muzhu ullathodu ummai panigindrom"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "ஜீவனுள்ள நாளெல்லாம் உம்மைப் பாடுவேன்",
                "என்னுயிரும் மூச்சும் உள்ள வரை போற்றுவேன்",
                "துதிகளின் நடுவே அசைவாடிடும்",
                "உந்தன் பிரசன்னத்தால் எங்களை நிரப்பிடும்"
            ], [
                "Jeevanulla naalellaam ummaip paaduvaen",
                "Ennuyirum moochum ulla varai potruvaen",
                "Thudhigalin naduvae asaivaadidum",
                "Undhan prasannathaal engalai nirappidum"
            ])
        ]
    },
    {
        "title_ta": "எபனேசரே என் எபனேசரே",
        "title_en": "Ebenesarae En Ebenesarae",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=4wIYopgrDMI",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "எபனேசரே என் எபனேசரே",
                "இதுவரை உதவி செய்தீரே",
                "என்னை மறவா என் நேசரே",
                "இனிமேலும் நடத்திச் செல்வீரே"
            ], [
                "Ebenesarae en Ebenesarae",
                "Idhuvarai udhavi seidheerae",
                "Ennai maravaa en Naesarae",
                "Inimaelum nadathich chelveerae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "தனிமையில் நான் அழுதபோது",
                "கண்ணீரைத் துடைத்த என் தகப்பனே",
                "மனிதர்கள் கைவிட்ட நேரத்திலே",
                "மார்போடு அணைத்த என் நேசரே"
            ], [
                "Thanimaiyil naan azhudhapodhu",
                "Kanneerath thudaitha en thagappanae",
                "Manidhargal kaivitta naerathilae",
                "Maarbodu anaitha en Naesarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "காத்திருந்தேன் உம் பாதத்திலே",
                "புது பெலன் தந்து என்னை உயர்த்தினீர்",
                "கழுகு போல சிறகடித்து",
                "உயரே எழும்பச் செய்தீரையா"
            ], [
                "Kaathirundhaen um paadhathilae",
                "Pudhu belan thandhu ennai uyarthineer",
                "Kazhugu pola siragadithu",
                "Uyarae ezhumbach cheidheeraiyaa"
            ])
        ]
    },
    {
        "title_ta": "உயர் மலையோ சமவெளியோ",
        "title_en": "Uyar Malaiyo Samaveliyo",
        "alternate_title": "Uyarmalaiyo Samavelio",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=3h_2tJfz19s",
        "stanzas": [
            make_stanza("stanza", "அனுபல்லவி (Intro)", [
                "எந்தப்பக்கம் வந்தாலும் நீங்க என் கூடாரம்",
                "தீங்கு என்னை அணுகாது",
                "துர்ச்சனப்பிரவாகம் சூழ்ந்திட நின்றாலும்",
                "துளியும் என்னை நெருங்காது",
                "சிறு வெள்ளாட்டு கிடை போல் கிடந்தேன்",
                "உம் நிழலில் என் தஞ்சம் கொண்டேன்"
            ], [
                "Endhappakkam vandhaalum neenga en koodaaram",
                "Theengu ennai anugaadhu",
                "Thurchanappiravaagam soozhndhida nindraalum",
                "Thuliyum ennai nerungaadhu",
                "Siru vellaattu kidai pol kidandhaen",
                "Um nizhalil en thanjam kondaen"
            ]),
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உயர் மலையோ சமவெளியோ",
                "இரண்டிலும் நீரே என் தேவன்",
                "எந்த நிலையிலும் ஆராதித்திடுவேன்",
                "என் இயேசுவை முழு மனதோடு ஆராதித்திடுவேன்"
            ], [
                "Uyar malaiyo samaveliyo",
                "Irandilum Neerae en Dhevan",
                "Endha nilaiyilum aaraadhithiduvaen",
                "En Yesuvai muzhu manadhodu aaraadhithiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "ஏற்றமாய் தோன்றும் பாதைகளிலெல்லாம்",
                "பின்னிலே தாங்கிடும் உள்ளங்கை அழகு",
                "சருக்கலாய் தோன்றும் பாதைகளிலெல்லாம்",
                "பின்னலாய் தாங்கிடும் உம் விரல்கள் அழகு",
                "நான் எந்த நிலை என்றாலும்",
                "என்னை விட்டு போகாமல்",
                "நிற்பதல்லோ உம் அழகு",
                "விட்டு கொடுக்காத பேரழகு"
            ], [
                "Eattramaai thondrum paadhaigalilellaam",
                "Pinnilae thaangidum ullangai azhagu",
                "Sarukkalaai thondrum paadhaigalilellaam",
                "Pinnalaai thaangidum um viralgai azhagu",
                "Naan endha nilai endraalum",
                "Ennai vittu pogaamal",
                "Nirpadhallo um azhagu",
                "Vittu kodukkaadha paerazhagu"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உலகத்தின் கண்ணில் பெரும்பான்மை என்றால்",
                "அதிகம்பேர் நிற்பதே அவர் சொல்லும் கணக்கு",
                "அப்பா உம் கண்ணில் தனிமனிதனாயினும்",
                "நீர் துணை நிற்பதால் பெரும்பான்மை எனக்கு",
                "அட ஊர் என்ன சொன்னாலும்",
                "பார் எதிர் நின்னாலும்",
                "பிள்ளையல்லோ நான் உமக்கு",
                "நிகர் இல்லாத தகப்பனுக்கு"
            ], [
                "Ulagaththin kannil perumbaanmai endraal",
                "Adhigambaer nirpadhae avar sollum kanakku",
                "Appa um kannil thanimanidhanaayinum",
                "Neer thunai nirpadhaal perumbaanmai enakku",
                "Ada oor enna sonnaalum",
                "Paar edhir ninnaalum",
                "Pillaiyallo naan umakku",
                "Nigar illaadha thagappanukku"
            ])
        ]
    },
    {
        "title_ta": "எனக்கா இத்தனை கிருபை",
        "title_en": "Enakka Ithana Kirubai",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=7vu_4gTb33M",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "எனக்கா இத்தனை கிருபை நாதா",
                "எனக்கா இத்தனை தயவு ஐயா",
                "தகுதியே இல்லாத எனக்காய்",
                "உம் ஜீவனையே தந்தீரையா"
            ], [
                "Enakkaa ithanai kirubai Naadhaa",
                "Enakkaa ithanai dhayavu aiyaa",
                "Thagudhiyae illaadha enakkaai",
                "Um jeevanaiyae thandheeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "தூசியில் கிடந்த என்னையுமே",
                "தூக்கி எடுத்து நிறுத்தினீரே",
                "பிரபுக்களோடு அமர வைத்தீர்",
                "ராஜரீக ஆசீர்வாதம் தந்தீர்"
            ], [
                "Dhoosiyil kidandha ennaiyumae",
                "Thookki eduthu niruthineerae",
                "Prabukkalodu amara vaiththeer",
                "Raajareega aaseervaadham thandheer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "என் குற்றங்கள் நீர் எண்ணவில்லை",
                "இரத்தத்தினால் கழுவி விட்டீர்",
                "புது சிருஷ்டியாய் என்னை மாற்றி",
                "உந்தன் அன்பினால் முடிசூட்டினீர்"
            ], [
                "En kuttrangal neer ennavillai",
                "Irathathinaal kazhuvi vitteer",
                "Pudhu sirushtiyaai ennai maatri",
                "Undhan anbinaal mudisoottineer"
            ])
        ]
    },
    {
        "title_ta": "துதிகள் ஓயாது என் துதி நாயகனே",
        "title_en": "Thudhigal Oayaadhu",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=LJKoFkjhFWk",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "துதிகள் ஓயாது என் துதி நாயகனே",
                "வாழ்நாளெல்லாம் உம்மைப் பாடுவேன்",
                "என் ஜீவன் உள்ளவரை போற்றுவேன்",
                "இயேசுவே உம்மை ஆராதிப்பேன்"
            ], [
                "Thudhigal oyaadhu en thudhi Naayakanae",
                "Vaazhnaalellaam ummaip paaduvaen",
                "En jeevan ullavarai potruvaen",
                "Yesuvae ummai aaraadhippaen"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "காலைதோறும் உம் கிருபைகள் புதிதாய்",
                "என் மேல் பொழிந்து மகிழச் செய்தீர்",
                "மாறாத உம் உண்மை பெரியது",
                "மண்ணான என்னைத் தேடி வந்தீர்"
            ], [
                "Kaalaidhorum um kirubaigal pudhidhaai",
                "En mael pozhindhu magizha seidheer",
                "Maaraadha um unmai periyadhu",
                "Mannaana ennaith thaedi vandheer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "பாவ இருளில் தவித்த என்னை",
                "ஆச்சரியமான ஒளியினில் அழைத்தீர்",
                "உந்தன் நன்மைகளை சொல்லிச் சொல்லி",
                "ஓயாமல் துதித்துப் பாடிடுவேன்"
            ], [
                "Paava irulil thavitha ennai",
                "Aachariyamaana oliyinil azhaitheer",
                "Undhan nanmaigalai sollich cholli",
                "Oyaamal thudhithup paadiduvaen"
            ])
        ]
    },
    {
        "title_ta": "பரன் இயேசையா என் பாவம் போக்க",
        "title_en": "Paran Yesaiya",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=pFQTxky9wmM",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "பரன் இயேசையா என் பாவம் போக்க",
                "கல்வாரி சிலுவை சுமந்தீரே",
                "விலையேறப்பெற்ற இரத்தத்தாலே",
                "என்னை சொந்தமாய் மீட்டுக் கொண்டீரே"
            ], [
                "Paran Yesaiya en paavam pokka",
                "Kalvaari siluvai sumandheerae",
                "Vilaiyaerappettra irathaththaalae",
                "Ennai sondhamaai meettuk kondirae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "முள்முடி சூடி காயங்கள் தாங்கி",
                "எனக்காக நொறுக்கப்பட்டீரே",
                "உம் தழும்புகளால் சுகமானேனே",
                "உம் அன்பிற்கு இணையில்லையே"
            ], [
                "Mulmudi soodi kaayangal thaangi",
                "Enakkaaga norukkappatteerae",
                "Um thazhumbugalaal sugamaanaenae",
                "Um anbirku inaiyillaiyae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உலகத்தின் பாசங்கள் மறைந்து போயிடும்",
                "உந்தன் தூய அன்பு என்றும் மாறாதது",
                "என்னை விட்டு பிரியாத நேசரே",
                "உம்மை மட்டுமே நேசிப்பேன்"
            ], [
                "Ulagathin paasangal maraindhu poyidum",
                "Undhan thooya anbu endrum maaraadhadhu",
                "Ennai vittu piriyaadha Naesarae",
                "Ummai mattumae naesippaen"
            ])
        ]
    },
    {
        "title_ta": "கலங்கின நேரங்களில்",
        "title_en": "Kalangina Nerangalil",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=gRX7YqVC728",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "கலங்கின நேரங்களில் என் கரம் பிடித்தீர்",
                "தனிமையில் கண்ணீரைத் துடைத்தீரையா",
                "கைவிடாத நேசரே என் அடைக்கலமே",
                "உம்மையன்றி பூமியில் யாருமில்லையே"
            ], [
                "Kalangina naerangalil en karam piditheer",
                "Thanimaiyil kanneeraith thudaiththeeraiyaa",
                "Kaividaadha Naesarae en adaikkalamae",
                "Ummaiyandri boomiyil yaarumillaiyae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "சோதனைகள் பெரு வெள்ளமாய் வந்தாலும்",
                "நீரே என் கேடகமாய் நின்றீரையா",
                "அக்கினியின் நடுவே உடன் நடந்தீர்",
                "ஒரு சேதமும் அணுகாமல் காத்தீரையா"
            ], [
                "Sodhanaigal peru vellamaai vandhaalum",
                "Neerae en kaedagamaai nindreeraiyaa",
                "Akkiniyin naduvae udan nadantheer",
                "Oru saedhamum anugaamal kaaththeeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வார்த்தையினால் என் வாழ்வை மாற்றிடுவீர்",
                "சொன்னதை நிறைவேற்றும் உண்மையுள்ளவரே",
                "உம் வாக்குத்தத்தம் என்றும் மாறாதையா",
                "என் நம்பிக்கையின் கன்மலையே"
            ], [
                "Vaarthaiyinaal en vaazhvai maatriduveer",
                "Sonnadhai niraivaettrum unmaiyullavarae",
                "Um vaakkuthatham endrum maaraadhaiyaa",
                "En nambikkaiyin kanmalaiyae"
            ])
        ]
    },
    {
        "title_ta": "நீர் சொன்னால் போதும்",
        "title_en": "Neer Sonnal Podhum",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=iwuzWtZAXsE",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "நீர் சொன்னால் போதும் செய்வேன்",
                "நீர் காட்டினால் போதும் செல்வேன்",
                "என் வாழ்வின் வழிகாட்டி நீர்தானையா",
                "என் பாதையின் தீபமும் நீர்தானையா"
            ], [
                "Neer sonnaal podhum seivaen",
                "Neer kaattinaal podhum selvaen",
                "En vaazhvin vazhikaatti Neerdhaanaiyaa",
                "En paadhaiyin dheebamum Neerdhaanaiyaa"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மனிதர்களின் குரல்கள் அடங்கிடட்டும்",
                "உந்தன் மெல்லிய சத்தம் கேட்டிடட்டும்",
                "உம் சித்தமே என் உணவாகட்டும்",
                "உம் பிரியமே என் வாழ்வாகட்டும்"
            ], [
                "Manidhargalin kuralkal adangidattum",
                "Undhan melliya saththam kaettidattum",
                "Um siththamae en unavaagattum",
                "Um piriyamae en vaazhvaagattum"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வலைகளை வீசிட சொன்னவரே",
                "வெற்றியை பரிசாக தந்தவரே",
                "உம் வார்த்தைக்கு கீழ்ப்படிந்து வாழ்ந்திடுவேன்",
                "முடிவு வரை உம் பின்னே தொடர்ந்திடுவேன்"
            ], [
                "Valaigalai veesida sonnavarae",
                "Vettriyai parisaaga thandhavarae",
                "Um vaarthaikku keezhpadindhu vaazhndhiduvaen",
                "Mudivu varai um pinnae thodarndhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "ஓசே பாலா (அதிசயம் செய்பவரே)",
        "title_en": "Oseh Pele",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=sYv_lpuQKQk",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "ஓசே பாலா ஓசே பாலா",
                "அதிசயம் செய்கின்றவரே",
                "வார்த்தையினால் நீர் சொன்னதெல்லாம்",
                "செய்து முடிப்பவரே"
            ], [
                "Oseh pele Oseh pele",
                "Adhisayam seigindravarae",
                "Vaarthaiyinaal neer sonnadhellaam",
                "Seidhu mudippavarae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "பார்க்கின்ற கண்கள் வியந்திடவே",
                "ஆச்சரியங்கள் செய்திடுவீர்",
                "நம்பின மனிதர் திகைத்திடவே",
                "நன்மைகளை நீர் தந்திடுவீர்"
            ], [
                "Paarkkindra kangal viyandhidavae",
                "Aachariyangal seithiduveer",
                "Nambina manidhar thigaithidavae",
                "Nanmaigalai neer thandhiduveer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வழிகள் இல்லாத வனாந்தரத்திலே",
                "புது வழிகளை திறப்பவரே",
                "வறண்ட நிலத்தில் ஆறுகளை",
                "உண்டாக்கும் வல்லவரே"
            ], [
                "Vazhigal illaadha vanaandharathilae",
                "Pudhu vazhigalai thirappavarae",
                "Varanda nilathil aarugalai",
                "Undaakkum vallavarae"
            ])
        ]
    },
    {
        "title_ta": "ஒருவனாய் இருக்கையில் அழைத்தீரையா",
        "title_en": "Oruvanaai Irukkayil",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=v8ABFQvB4CU",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "ஒருவனாய் இருக்கையில் அழைத்தீரையா",
                "திரளான கூட்டமாய் மாற்றினீரே",
                "என் இயேசையா என் தகப்பனே",
                "உம் கிருபை என்னை உயர்த்தியதே"
            ], [
                "Oruvanaai irukkayil azhaitheeraiyaa",
                "Thiralaana koottamaai maatrineerae",
                "En Yesaiyaa en thagappanae",
                "Um kirubai ennai uyarthiyadhae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "ஒன்றுமில்லா என்னை கண்டீரையா",
                "உயிரூட்டி என்னை நிறுத்தினீரே",
                "தனிமையில் கண்ணீர் வடித்தபோது",
                "தோளோடு அணைத்த என் நேசரே"
            ], [
                "Ondrumillaa ennai kandeeraiyaa",
                "Uyirootti ennai niruthineerae",
                "Thanimaiyil kanneer vadithapodhu",
                "Tholodu anaitha en Naesarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "ஆபிரகாமை ஆசீர்வதித்தது போல",
                "ஆயிரம் மடங்காய் பெருக்கினீரே",
                "உம் வாக்குத்தத்தம் உண்மை உள்ளது",
                "உம் மாறா கிருபை பெரியது"
            ], [
                "Aabiragaamai aaseervadhithadhu pola",
                "Aayiram madangaai perukkineerae",
                "Um vaakkuthatham unmai ulladhu",
                "Um maaraa kirubai periyadhu"
            ])
        ]
    },
    {
        "title_ta": "விவரிக்க முடியாத அன்பு",
        "title_en": "Vivarikka Mudiyatha",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=i1_NmBcLN-Q",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "விவரிக்க முடியாத அன்பு இது",
                "வார்த்தையில் அடங்காத பாசம் இது",
                "என்னைக் கண்டுகொண்ட என் நேசரே",
                "என்னை மீட்டுக் கொண்ட என் இரட்சகரே"
            ], [
                "Vivarikka mudiyadha anbu idhu",
                "Vaarthaiyil adangaadha paasam idhu",
                "Ennaik kandukonda en Naesarae",
                "Ennai meettuk konda en Iratchagarae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "அளவிட முடியாத கருணை உம்மோடு",
                "எல்லையில்லாத தயவு என்னோடு",
                "மன்னிக்கும் உள்ளம் கொண்ட தெய்வமே",
                "என்னை உயர்த்திய சர்வ வல்லவரே"
            ], [
                "Alavida mudiyadha karunai ummodu",
                "Ellaiyillaadha dhayavu ennodu",
                "Mannikkum ullam konda Deivamae",
                "Ennai uyarthiya sarva vallavarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உம் அன்பை எண்ணி தினம் பாடுவேன்",
                "உம் நாமத்தை உயர்த்தி கொண்டாடுவேன்",
                "வாழும் நாளெல்லாம் உம் மகிமை சொல்வேன்",
                "இயேசுவே உம்மை ஆராதிப்பேன்"
            ], [
                "Um anbai enni dhinam paaduvaen",
                "Um naamathai uyarthi kondaaduvaen",
                "Vaazhum naalellaam um magimai solvaen",
                "Yesuvae ummai aaraadhippaen"
            ])
        ]
    },
    {
        "title_ta": "கைவிட மாட்டார் என் நேசர்",
        "title_en": "Kaivida Maatar",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=fx8ZTaVuvpM",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "கைவிட மாட்டார் என் நேசர் கர்த்தர்",
                "என்றும் கைவிட மாட்டார்",
                "அழைத்தவர் உண்மையுள்ளவர்",
                "முழுமையாய் காத்துக் கொள்வார்"
            ], [
                "Kaivida maattar en Naesar Karthar",
                "Endrum kaivida maattar",
                "Azhaiththavar unmaiyullavar",
                "Muzhumaiyaai kaathuk kolvaar"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மனிதர்கள் வாக்கு மாறினாலும்",
                "அவர் வாக்குத்தத்தம் ஒருபோதும் மாறாது",
                "சொன்னதைச் செய்து முடிப்பவரே",
                "நன்மையை அருளிச் செய்பவரே"
            ], [
                "Manidhargal vaakku maarinaalum",
                "Avar vaakkuthatham orupodhum maaraadhu",
                "Sonnadhaich seidhu mudippavarae",
                "Nanmaiyai arulich cheipavarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "காரிருள் போன்ற பாதையிலும்",
                "வெளிச்சமாய் முன் சென்றிடுவார்",
                "கண்ணீர் யாவையும் துடைத்திடுவார்",
                "ஆனந்தக் களிப்பால் நிரப்பிடுவார்"
            ], [
                "Kaarirul pondra paadhaiyilum",
                "Velichamaai mun sendriduvaar",
                "Kanneer yaavaiyum thudaithiduvaar",
                "Aanandhak kalippaal nirappiduvaar"
            ])
        ]
    },
    {
        "title_ta": "அழகே என் இயேசுவே",
        "title_en": "Azhagae",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=1Uh2qBiiObA",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "அழகே என் இயேசுவே",
                "அளவில்லா அன்பே",
                "உம்மைப் போல அழகு இவ்வுலகில் இல்லையே",
                "உம்மைப் போல அன்பு எங்குமே காணோமே"
            ], [
                "Azhagae en Yesuvae",
                "Alavillaa anbae",
                "Ummai pola azhagu ivvulagil illaiyae",
                "Ummai pola anbu engumae kaanomae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "பதினாயிரங்களில் சிறந்தவரே",
                "சாரோனின் ரோஜா நீர்தானையா",
                "பள்ளத்தாக்கின் லீலி புஷ்பமே",
                "என் நேசரே உம்மைப் பாடுவேன்"
            ], [
                "Padhinaayirangalil sirandhavarae",
                "Saaronin roja Neerdhaanaiyaa",
                "Pallathaakkin leeli pushpamae",
                "En Naesarae ummaip paaduvaen"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "கல்வாரி மேட்டினில் என் அழகே",
                "காயங்கள் எனக்காய் சுமந்தீரே",
                "அழகற்றுப் போனீர் என் அழகுக்காய்",
                "உம்மை என்றென்றும் துதித்திடுவேன்"
            ], [
                "Kalvaari maettinil en azhagae",
                "Kaayangal enakkaai sumandheerae",
                "Azhagattrup poneer en azhagukkaai",
                "Ummai endrendrum thudhithiduvaen"
            ])
        ]
    },
    {
        "title_ta": "துதி உமக்கே கனம் உமக்கே",
        "title_en": "Thuthi Umakkae",
        "author": "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}",
        "youtube_url": "https://www.youtube.com/watch?v=eHDoAzvrtwU",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "துதி உமக்கே கனம் உமக்கே",
                "புகழ்ச்சி உமக்கே என் ராஜாவே",
                "ஆராதனை உமக்கே அல்லேலூயா",
                "என்றென்றும் உமக்கே ஆராதனை"
            ], [
                "Thuthi Umakkae ganam Umakkae",
                "Pugazhchi Umakkae en Raajaavae",
                "Aaraadhanai Umakkae Hallelujah",
                "Endrendrum Umakkae aaraadhanai"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "ஜீவனுள்ள தேவன் நீரே",
                "ஜீவன் தந்து மீட்டீரே",
                "மரணத்தை ஜெயித்த ஜெயவேந்தரே",
                "மகிமையின் ராஜா நீர்தானே"
            ], [
                "Jeevanulla Dhevan Neerae",
                "Jeevan thandhu meetteerae",
                "Maranathai jeyitha jeyavaendharae",
                "Magimaiyin Raajaa Neerdhaanae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "இரவும் பகலும் ஓயாமல்",
                "தூதர்கள் போற்றும் தூயவரே",
                "பூமியின் எல்லைகள் யாவும் உம்மை",
                "பணிந்து போற்றி வணங்கிடுதே"
            ], [
                "Iravum pagalum oyaamal",
                "Thoodhargal potrum thooyavarae",
                "Boomiyin ellaigal yaavum Ummai",
                "Panindhu potri vanangidudhae"
            ])
        ]
    }
]

# =========================================================================
# 2. DR. JOSEPH ALDRIN (CONTEMPORARY WORSHIP HITS)
# =========================================================================
ALDRIN_NEW_SONGS = [
    {
        "title_ta": "ஏன் ஹக்கோரே (ஜீவதண்ணீர் தந்தீர்)",
        "title_en": "En Hakkore",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=rznrvTlprYw",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "ஏன் ஹக்கோரே ஏன் ஹக்கோரே",
                "கூப்பிட்டேன் ஜீவதண்ணீர் தந்தீரையா",
                "தாகத்தால் சோர்ந்து மடிந்த வேளையில்",
                "கன்மலையைத் திறந்து ஜீவ ஊற்று தந்தீர்"
            ], [
                "En Hakkore En Hakkore",
                "Kooppittaen jeevathanneer thandheeraiyaa",
                "Dhaagaththaal sorndhu madindha vaelaiyil",
                "Kanmalaiyaith thirandhu jeeva oottru thandheer"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "சாம்பலில் கிடந்த சிம்சோனின் குரல் கேட்டு",
                "கன்மலையை பிளந்து தண்ணீர் சுரக்கச் செய்தீர்",
                "அப்படியே என் கண்ணீரின் விண்ணப்பம் கேட்டு",
                "தாகம் தீர்த்து உயிர்ப்பித்தீரையா"
            ], [
                "Saambalil kidandha Simsonin kural kaettu",
                "Kanmalaiyai pilandhu thanneer surakkach cheidheer",
                "Appadiyae en kanneerin vinnappam kaettu",
                "Dhaagam theerthu uyirpiththeeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வறண்ட நிலத்தில் ஆறுகளை உருவாக்குவீர்",
                "பாலைவனத்தில் பாதைகளை திறந்திடுவீர்",
                "நீர் செய்யும் அற்புதங்கள் பெரிதானவை",
                "உம்மை நம்பும் எவரும் வெட்கப்படுவதில்லை"
            ], [
                "Varandha nilaththil aarugalai uruvaakkuveer",
                "Paalaivanathil paadhaigalai thirandhiduveer",
                "Neer seiyum arpudhangal peridhaanavai",
                "Ummai nambum evarum vetkappaduvadhillai"
            ])
        ]
    },
    {
        "title_ta": "உண்மையுள்ளவரே உத்தமரே",
        "title_en": "Unmai Ullavarae",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=9hQ_aIjedpk",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உண்மையுள்ளவரே உத்தமரே",
                "என்றும் மாறாத என் நேசரே",
                "சொன்னதை செய்திடும் சர்வ வல்லவரே",
                "உம்மைப் போல தெய்வமில்லை பூமியிலே"
            ], [
                "Unmaiyullavarae uththamarae",
                "Endrum maaraadha en Naesarae",
                "Sonnadhaich cheidhidum sarva vallavarae",
                "Ummaip pola Deivamillai boomiyilae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மனிதர்கள் மறந்தாலும் நீர் மறப்பதில்லை",
                "சொந்தங்கள் வெறுத்தாலும் தள்ளுவதில்லை",
                "உள்ளங்கையில் என்னைப் பொறித்து வைத்தீர்",
                "உம் கண்மணி போலப் பாதுகாத்தீர்"
            ], [
                "Manidhargal marandhaalum Neer marappadhillai",
                "Sondhangal veruththaalum thalluvadhillai",
                "Ullangaiyil ennaip porithu vaiththeer",
                "Um kanmani pola paadhukaaththeer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "ஆயிரம் தலைமுறைகள் ஆனாலும்",
                "உம் உடன்படிக்கை ஒருபோதும் மறையாது",
                "நம்பினோரை கைவிடாத நல்ல தகப்பனே",
                "உம்மையே என்றும் தொழுதிடுவேன்"
            ], [
                "Aayiram thalaimuraigal aanaalum",
                "Um udanpadikkai orupodhum maraiyaadhu",
                "Nambinorai kaividaadha nalla thagappanae",
                "Ummaiyae endrum thozhdhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "அபிஷேக ஒலிவ மரம் நான்",
        "title_en": "Abishega Oliva Maram",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=iyYtYSBrdQ4",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "அபிஷேக ஒலிவ மரம் நான்",
                "தேவாலயத்தில் செழித்திருப்பேன்",
                "தேவனின் கிருபையை என்றென்றைக்கும்",
                "நம்பி வாழ்ந்திடுவேன்"
            ], [
                "Abishega oliva maram naan",
                "Dhevaalayathil sezhiththiruppaen",
                "Dhevanin kirubaiyai endrendraikkum",
                "Nambi vaazhndhiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "நீரூற்றின் ஓரமாய் நடப்பட்டு",
                "தக்க காலத்தில் கனிகளைத் தந்திடுவேன்",
                "இலைகள் உதிராமல் பசுமையாய் இருப்பேன்",
                "செய்வதெல்லாம் வாய்க்கச் செய்வீர்"
            ], [
                "Neerootttrin oaramaai nadappattu",
                "Thakka kaalathil kanigalaith thandhiduvaen",
                "Ilaigal udhiraamal pasumaiyaai iruppaen",
                "Seivadhellaam vaaikkach cheiveer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "புதிய எண்ணெயால் என்னை அபிஷேகித்தீர்",
                "என் பாத்திரம் நிரம்பி வழியச் செய்தீர்",
                "நன்மையும் கிருபையும் என் வாழ்நாளெல்லாம்",
                "என்னைத் தொடரச் செய்தீரையா"
            ], [
                "Pudhiya ennaiyaal ennai abhishegitheer",
                "En paaththiram nirambi vazhiyach cheidheer",
                "Nanmaiyum kirubaiyum en vaazhnaalellaam",
                "Ennaith thodarach cheidheeraiyaa"
            ])
        ]
    },
    {
        "title_ta": "உம்மை நம்பும் நான் வெட்கப்படுவதில்லை",
        "title_en": "Ummai Nambum Naan",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=5P43M3aiuHE",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உம்மை நம்பும் நான் வெட்கப்படுவதில்லை",
                "ஒருபோதும் நான் வெட்கப்படுவதில்லை",
                "என் நம்பிக்கையின் நங்கூரமே",
                "என் வாழ்வின் கோட்டையும் நீர்தானே"
            ], [
                "Ummai nambum naan vetkappaduvadhillai",
                "Orupodhum naan vetkappaduvadhillai",
                "En nambikkaiyin nangooramae",
                "En vaazhvin kottaiyum Neerdhaanae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "எதிரிகள் என்னைச் சூழ்ந்து கொண்டாலும்",
                "என் தலைக்கு மேலாக நீர் நின்றீரையா",
                "பந்தி ஒன்றை எனக்காய் ஆயத்தம் செய்து",
                "அபிஷேகத்தால் என்னை உயர்த்தினீரே"
            ], [
                "Edhirigal ennaich choozhndhu kondaalum",
                "En thalaikku maelaaga Neer nindreeraiyaa",
                "Bandhi ondrai enakkaai aayaththam seidhu",
                "Abishegaththaal ennai uyarthineerae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "கர்த்தர் என் வெளிச்சமும் இரட்சிப்புமானார்",
                "யாருக்கு அஞ்சுவேன் என் பாதையிலே",
                "அவரே என் ஜீவனின் பெலனானவர்",
                "யாருக்கு பயப்படுவேன்"
            ], [
                "Karthar en velichamum iratchippumaanaar",
                "Yaarukku anjuvaen en paadhaiyilae",
                "Avarae en jeevanin belanaanavar",
                "Yaarukku bayappaduvaen"
            ])
        ]
    },
    {
        "title_ta": "கன்மலையானவர் உறைவிடமானவர்",
        "title_en": "Kanmalaiyanavar",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=X9y2DVykixM",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "கன்மலையானவர் உறைவிடமானவர்",
                "இரட்சணிய கன்மலையாம் இயேசுவே",
                "அசைக்கப்படுவதில்லை நான் அசைக்கப்படுவதில்லை",
                "என் கன்மலையின் மேல் நிற்கின்றேன்"
            ], [
                "Kanmalaiyaanavar uraividamaanavar",
                "Iratchaniya kanmalaiyaam Yesuvae",
                "Asaikkappaduvadhillai naan asaikkappaduvadhillai",
                "En kanmalaiyin mael nirkindroam"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "பெருங்காற்று அடித்தாலும் பெருவெள்ளம் வந்தாலும்",
                "என் வீடானது ஒருபோதும் விழாது",
                "கன்மலையாம் இயேசுவின் மேல் அஸ்திபாரம்",
                "என்றென்றும் நிலைத்து நிற்கும்"
            ], [
                "Perungkaattru adiththaalum peruvellam vandhaalum",
                "En veedaanadhu orupodhum vizhaadhu",
                "Kanmalaiyaam Yesuvin mael asthibaaram",
                "Endrendrum nilaithu nirkum"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "ஆபத்துக் காலத்தில் அனுகூலமான துணையே",
                "என் பலவீனத்தில் பூரண பெலனே",
                "உம் சிறகுகளின் நிழல்தனிலே தங்கி",
                "எப்போதும் பாடி மகிழ்ந்திடுவேன்"
            ], [
                "Aabathuk kaalathil anukoolamaana thunaiyae",
                "En balaveenathil poorana belanae",
                "Um siragugalin nizhaldhanilae thanggi",
                "Eppodhum paadi magizhndhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "எதிர்பார்த்த முடிவை தருபவரே",
        "title_en": "Ethirpaartha Mudivai",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=KNh00kWbi-Y",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "எதிர்பார்த்த முடிவை அருளிச் செய்பவர்",
                "சமாதானத்தின் தேவன் நீரே",
                "என் எதிர்காலம் உம் கரத்தில் உண்டு",
                "என் நம்பிக்கை ஒருபோதும் வீணாகாது"
            ], [
                "Edhirpaartha mudivai arulich cheipavar",
                "Samaadhaanaththin Dhevan Neerae",
                "En edhirkaalam um karathil undu",
                "En nambikkai orupodhum veenaagaadhu"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "நீங்கள் நினைப்பதற்கும் வேண்டுவதற்கும் மேலாக",
                "கிரியை செய்திடும் சர்வ வல்லவரே",
                "என் திட்டங்கள் யாவும் உடைந்த போதும்",
                "உன்னத திட்டம் வகுத்தீரையா"
            ], [
                "Neengal ninaippadharkum vaenduvadharkum maelaaga",
                "Kiriyai seidhidum sarva vallavarae",
                "En thittangal yaavum udaindha podhum",
                "Unnadha thittam vaguththeeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "குறைவுகள் யாவையும் நிறைவாக்கிடுவீர்",
                "கண்ணீரின் பாதையை களிப்பாக்கிடுவீர்",
                "முடிவு வரை என்னைக் காப்பவரே",
                "மகிமையில் கொண்டு சேர்ப்பவரே"
            ], [
                "Kuraivugal yaavaiyum niraivaakkiduveer",
                "Kanneerin paadhaiyai kalippaakkiduveer",
                "Mudivu varai ennaik kaappavarae",
                "Magimaiyil kondu saerppavarae"
            ])
        ]
    },
    {
        "title_ta": "உம்மேல் வாஞ்சையாய் இருக்கின்றேன்",
        "title_en": "Ummel Vaanjaiyai",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=E2wLBfTyCe8",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உம்மேல் வாஞ்சையாய் இருக்கின்றேன்",
                "உம் சித்தம் செய்யவே ஆசையாய் இருக்கின்றேன்",
                "இயேசையா உம் அன்பை ருசிக்கின்றேன்",
                "உம் பிரசன்னத்தில் மூழ்கித் திளைக்கின்றேன்"
            ], [
                "Ummel vaanjaiyaai irukkindroam",
                "Um siththam seiyavae aasaiyaai irukkindroam",
                "Yesaiyaa um anbai rusikkindroam",
                "Um prasannathil moozhgi thilaikkindroam"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மானானது நீரோடையை வாஞ்சிப்பது போல",
                "என் ஆத்துமா உம்மையே வாஞ்சிக்கின்றதே",
                "ஜீவனுள்ள தேவன் மேல் தாகமாயிருக்கின்றேன்",
                "எப்போது உம் சமூகம் வந்திடுவேன்"
            ], [
                "Maanaanadhu neeroadaiyai vaanjippadhu pola",
                "En aathumaa Ummaiyae vaanjikkindradhae",
                "Jeevanulla Dhevan mael dhaagamaayirukkindroam",
                "Eppodhu um samoogam vandhiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உலகத்தின் இச்சைகள் விலகிடட்டும்",
                "உந்தன் பரிசுத்தம் என்னில் விளங்கட்டும்",
                "என் வாழ்வின் ஒரே வாஞ்சை நீரே",
                "இயேசுவே உம்மை ஆராதிப்பேன்"
            ], [
                "Ulagaththin ichaigal vilagidattum",
                "Undhan parisuththam ennil vilangattum",
                "En vaazhvin orae vaanjai Neerae",
                "Yesuvae ummai aaraadhippaen"
            ])
        ]
    },
    {
        "title_ta": "என் ஆத்துமாவே கர்த்தரை ஸ்தோத்திரி",
        "title_en": "En Aathumave",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=E2W1WEhOX80",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "என் ஆத்துமாவே கர்த்தரை ஸ்தோத்திரி",
                "முழு உள்ளமே அவர் பரிசுத்த நாமம் போற்றிடு",
                "அவர் செய்த உபகாரங்கள் எதையும்",
                "ஒருபோதும் மறவாதே"
            ], [
                "En aathumaavae Kartharai sthothiri",
                "Muzhu ullamae avar parisutha naamam pottridu",
                "Avar seidha ubagaarangal edhaiyum",
                "Orupodhum maravaadhae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "அக்கிரமங்கள் யாவையும் மன்னித்தாரே",
                "வியாதிகள் யாவையும் குணமாக்கினாரே",
                "படுகுழிக்கு ஜீவனை மீட்டெடுத்தாரே",
                "கிருபை இரக்கத்தால் முடிசூட்டினாரே"
            ], [
                "Akkiramangal yaavaiyum manniththaarae",
                "Viyaadhigal yaavaiyum gunamaakkinaarae",
                "Paduguzhikku jeevanai meetteduththaarae",
                "Kirubai irakkaththaal mudisoottinaarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "கழுகு போல் இளமை திரும்பச் செய்தார்",
                "நன்மையினால் வாயை நிறைத்து விட்டார்",
                "எல்லா துதியும் உமக்கே செலுத்துகின்றேன்",
                "என்றென்றும் உம்மைப் புகழ்ந்திடுவேன்"
            ], [
                "Kazhugu pol ilamai thirumbach cheidhaar",
                "Nanmaiyinaal vaayai niraithu vittaar",
                "Ellaa thudhiyum Umakkae seluthugindroam",
                "Endrendrum ummaip pugazhndhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "நீரே என் தஞ்சம் நீரே என் கோட்டை",
        "title_en": "Neerae En Thanjam",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=ixD7QE5vUpo",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "நீரே என் தஞ்சம் நீரே என் கோட்டை",
                "நான் நம்பும் தேவனும் நீரே",
                "ஆபத்துக் காலத்தில் அனுகூல துணையே",
                "என் அடைக்கலமானவரே"
            ], [
                "Neerae en thanjam Neerae en kottai",
                "Naan nambum Dhevanum Neerae",
                "Aabathuk kaalathil anukoola thunaiyae",
                "En adaikkalamaanavarae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "இரவின் பயங்கரத்திற்கும் பகலில் பறக்கும் அம்புக்கும்",
                "இருளில் நடமாடும் கொள்ளைநோய்க்கும் பயப்படேன்",
                "உன்னதமானவரின் மறைவில் தங்கி",
                "சர்வ வல்லவரின் நிழலில் வாழ்ந்திடுவேன்"
            ], [
                "Iravin bayangarathirkum pagalil parakkum ambukkum",
                "Irulil nadamaadum kollainoikkum bayappadaen",
                "Unnadhamaanavarin maraivil thanggi",
                "Sarva vallavarin nizhalil vaazhndhiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "பாதைகளில் என்னை காப்பதற்கு",
                "தூதர்களைக் கட்டளையிடுவீரே",
                "என் பாதம் கல்லில் இடறாதபடிக்கு",
                "கரங்களில் தாங்கிக் கொள்வீர்"
            ], [
                "Paadhaigalil ennai kaappadharku",
                "Thoodhargalaik kattalaiyiduveerae",
                "En paadham kallil idaraadhabadikku",
                "Karangalil thaangik kolveer"
            ])
        ]
    },
    {
        "title_ta": "ஆட்டுக்குட்டியானவரே மகிமைக்குப் பாத்திரரே",
        "title_en": "Aattukkuttiyanavarae",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=4GThNlGcQkM",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "ஆட்டுக்குட்டியானவரே மகிமைக்குப் பாத்திரரே",
                "சிங்காசனத்தில் வீற்றிருக்கும் ராஜாவே",
                "துதியும் கனமும் மகிமையும் வல்லமையும்",
                "உமக்கே உண்டாவதாக"
            ], [
                "Aattukkuttiyaanavarae magimaikkup paathirarae",
                "Singaasanathil veetrirukkum Raajaavae",
                "Thudhiyum ganamum magimaiyum vallamaiyum",
                "Umakkae undaavadhaaga"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "எங்களுக்காக அடிக்கப்பட்டு",
                "உம் இரத்தத்தினால் எங்களை மீட்டுக் கொண்டீர்",
                "ராஜாக்களும் ஆசாரியர்களுமாய் மாற்றி",
                "சுதந்திரவாளிகளாய் நிறுத்தினீரே"
            ], [
                "Engalukkaaga adikkappaattu",
                "Um irathathinaal engalai meettuk kondeer",
                "Raajaakkalum aasariyargalumaai maatri",
                "Sudhandhiravaaligalaai niruthineerae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "பரலோக சேனைகள் போற்றிப் பணியும்",
                "பரிசுத்தரே எங்கள் இயேசு நாதா",
                "என்றென்றும் ஆளுகை செய்திடும் தேவா",
                "உம் பாதம் பணிந்து தொழுகின்றோம்"
            ], [
                "Paraloga saenaigal potrip paniyum",
                "Parisuththarae engal Yesu Naadhaa",
                "Endrendrum aalugai seidhidum Dhevaa",
                "Um paadham panindhu thozhugindroam"
            ])
        ]
    },
    {
        "title_ta": "அதிகாலையில் உம்மைத் தேடுவேன்",
        "title_en": "Athikalayil",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=e6JXTF7yw6U",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "அதிகாலையில் உம்மைத் தேடுவேன்",
                "ஆவலாய் உம் முகம் நோக்கிடுவேன்",
                "என் கர்த்தாவே காலையிலே என் சத்தம் கேட்பீர்",
                "உம் பாதத்தில் விண்ணப்பம் செய்திடுவேன்"
            ], [
                "Adhikaalaiyil ummaith thaeduvaen",
                "Aavalaai um mugam nokkiduvaen",
                "En Karththavae kaalaiyilae en saththam kaetpeer",
                "Um paadhathil vinnappam seidhiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "உம் கிருபை ஜீவனைப் பார்க்கிலும் மேலானது",
                "என் உதடுகள் உம்மைத் துதித்திடும்",
                "உயிருள்ள வரை உம்மை வாழ்த்திடுவேன்",
                "உம் நாமத்தினால் கைகளை உயர்த்திடுவேன்"
            ], [
                "Um kirubai jeevanaip paarkkilum maelaanadhu",
                "En udhadugal ummaith thudhithidum",
                "Uyirulla varai ummai vaazhthiduvaen",
                "Um naamathinaal kaigalai uyarthiduvaen"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "இரவு ஜாமங்களில் உம்மை தியானித்து",
                "என் படுக்கையிலும் உம்மை நினைந்திடுவேன்",
                "நீர் எனக்கு சகாயரானதினால்",
                "உம் சிறகுகளின் நிழலில் களிகூருவேன்"
            ], [
                "Iravu jaamangalil ummai dhiyaanithu",
                "En padukkaiyilum ummai ninaindhiduvaen",
                "Neer enakku sagaayar aanadhinaal",
                "Um siragugalin nizhalil kalikooruvaen"
            ])
        ]
    },
    {
        "title_ta": "என் கண்ணீரைக் கண்டீர்",
        "title_en": "En Kanneerai Kandeer",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=JGYAg2cULv4",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "என் கண்ணீரைக் கண்டீர் விண்ணப்பம் கேட்டீர்",
                "ஆறுதல் தந்தீரையா",
                "மரண இருளின் வேளையிலும்",
                "ஆயுளைக் கூட்டித் தந்தீரையா"
            ], [
                "En kanneeraik kandeer vinnappam kaetteer",
                "Aarudhal thandheeraiyaa",
                "Marana irulin vaelaiyilum",
                "Aayulaik koottith thandheeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "எசேக்கியாவின் கண்ணீருக்கு பதிலளித்த தேவன்",
                "இன்றும் ஜீவிக்கின்றீர் என் வாழ்வில்",
                "வியாதியின் படுக்கையை மாற்றிப் போட்டு",
                "பரிபூரண சுகம் தந்தீரையா"
            ], [
                "Ezekiyaavin kanneerukku badhilalitha Dhevan",
                "Indrum jeevikkindreer en vaazhvil",
                "Viyaadhiyin padukkaiyai maattrip pottu",
                "Paripoorana sugam thandheeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "துக்கத்தை ஆனந்தக் களிப்பாய் மாற்றி",
                "இரட்டை அத்தனை நன்மைகள் தந்தீர்",
                "ஜீவனுள்ள நாளெல்லாம் உம்மைப் பாடி",
                "சாட்சியாய் வாழ்ந்திடுவேன்"
            ], [
                "Dhookkathai aanandhak kalippaai maatri",
                "Irattai athanai nanmaigal thandheer",
                "Jeevanulla naalellaam ummaip paadi",
                "Saatchiyaai vaazhndhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "என்னை நினைத்தவரே எபனேசரே",
        "title_en": "Ennai Ninaithavarae",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=9hQ_aIjedpk",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "என்னை நினைத்தவரே எபனேசரே",
                "மறக்காமல் ஆசீர்வதித்தீரையா",
                "சிறுமைப்பட்ட என்னை கண்ணோக்கிப் பார்த்து",
                "உயர்ந்த அடைக்கலத்தில் வைத்தீரையா"
            ], [
                "Ennai ninaithavarae Ebenesarae",
                "Marakkaamal aaseervadhiththeeraiyaa",
                "Sirumaippatta ennai kannokkip paarthu",
                "Uyarndha adaikkalathil vaiththeeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "தள்ளப்பட்ட கல்லாக கிடந்த என்னை",
                "மூலைக்கு தலைக்கல்லாய் மாற்றினீரே",
                "இது கர்த்தரால் வந்த அதிசயமே",
                "எங்கள் கண்களுக்கு ஆச்சரியமே"
            ], [
                "Thallappatta kallaaga kidandha ennai",
                "Moolaikku thalaikkallaai maatrineerae",
                "Idhu Kartharaal vandha adhisayamae",
                "Engal kangalukku aachariyamae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "நாட்களை நன்மையால் நிரப்புகின்றீர்",
                "ஆண்டுகளை அழகாய் மாற்றுகின்றீர்",
                "ஜீவனுள்ள வரை உம் அன்பை எண்ணி",
                "என்றும் துதித்துப் பாடுவேன்"
            ], [
                "Naatkalai nanmaiyaal nirappukindreer",
                "Aandugalai azhagaai maatrugindreer",
                "Jeevanulla varai um anbai enni",
                "Endrum thudhithup paaduvaen"
            ])
        ]
    },
    {
        "title_ta": "ஆறுதலின் தேவன் நீரே அடைக்கலமே",
        "title_en": "Aaruthalin Devan",
        "author": "Dr. Joseph Aldrin {டாக்டர் ஜோசப் அல்ட்ரின்}",
        "youtube_url": "https://www.youtube.com/watch?v=X_MZI0lqfsQ",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "ஆறுதலின் தேவன் நீரே",
                "ஆதரவற்றோரின் அடைக்கலமே",
                "நொறுங்குண்ட இதயத்தைக் குணமாக்குவீர்",
                "உடைந்த உள்ளத்தைக் கட்டிடுவீர்"
            ], [
                "Aarudhalin Dhevan Neerae",
                "Aadharavatttrorin adaikkalamae",
                "Norungunda idhayathaik gunamaakkuveer",
                "Udaindha ullaththaik kattiduveer"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "கண்ணீரைக் காண்கின்ற கர்த்தர் நீரே",
                "பெருமூச்சை அறிகின்ற பரம பிதாவே",
                "என் துயரத்தை நாட்டியமாய் மாற்றிடுவீர்",
                "மகிழ்ச்சியின் ஆடையை உடுத்திடுவீர்"
            ], [
                "Kanneeraik kaangindra Karthar Neerae",
                "Perumoochai arigindra parama Pithaavae",
                "En thuyarathai naattiyamaai maatriduveer",
                "Magizhchiyin aadaiyai uduthiduveer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "அநாதி தேவனே என் அடைக்கலமே",
                "நித்திய புயங்கள் எனக்காதரவே",
                "பயமின்றி நான் சுகமாய் வாழ்வேன்",
                "உம் நாமத்தை என்றென்றும் துதிப்பேன்"
            ], [
                "Anaadhi Dhevanae en adaikkalamae",
                "Nithiya buyangal enakkaadharavae",
                "Bayamindri naan sugamaai vaazhvaen",
                "Um naamathai endrendrum thudhippaen"
            ])
        ]
    }
]

# =========================================================================
# 3. PASTOR BENNY JOSHUA (CONTEMPORARY WORSHIP HITS)
# =========================================================================
BENNY_NEW_SONGS = [
    {
        "title_ta": "சீர்படுத்துவார் ஸ்திரப்படுத்துவார்",
        "title_en": "Seerpaduthuvaar",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=VR5xeJLU9vo",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "சீர்படுத்துவார் ஸ்திரப்படுத்துவார்",
                "பலப்படுத்துவார் நிலைநிறுத்துவார்",
                "சிறிது காலம் பாடுபடும் நம்மை",
                "நித்திய மகிமையில் பங்கு பெறச் செய்வார்"
            ], [
                "Seerpaduthuvaar sthirapaduthuvaar",
                "Balapaduthuvaar nilainiruthuvaar",
                "Siridhu kaalam paadubadum nammai",
                "Nithiya magimaiyil pangu perach cheivaar"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "உடைந்த பாண்டத்தை உருக்கி வார்த்து",
                "மகிமையின் பாத்திரமாய் மாற்றிடுவார்",
                "குயவன் கையில் களிமண் போல",
                "ஒப்புக்கொடுத்து வாழ்ந்திடுவோம்"
            ], [
                "Udaindha paandathai urukki vaarthu",
                "Magimaiyin paathiramaai maatriduvaar",
                "Kuyavan kaiyil kaliman pola",
                "Oppukkoduthu vaazhndhiduvom"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "காற்றைக் காணோம் மழையைக் காணோம்",
                "ஆனாலும் வாய்க்கால்கள் நிரம்பி வழியும்",
                "தேவனின் வாக்குத்தத்தம் உண்மை உள்ளது",
                "காலத்தில் நன்மையை செய்திடுவார்"
            ], [
                "Kaattraik kaanom mazhaiyaik kaanom",
                "Aanaalum vaaikkaalgal nirambi vazhiyum",
                "Dhevanin vaakkuthatham unmai ulladhu",
                "Kaalathil nanmaiyai seidhiduvaar"
            ])
        ]
    },
    {
        "title_ta": "யூதாவின் ராஜாவே உம்மை ஆராதிக்கின்றோம்",
        "title_en": "Yudhavin Raja",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=vqKgOnDN7TY",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "யூதாவின் ராஜாவே உம்மை ஆராதிக்கின்றோம்",
                "சிங்காசனத்தில் வீற்றிருக்கும் இயேசுவே",
                "ஜெயம் பெற்ற சிங்கம் நீரே",
                "எங்கள் ஜெயக்கொடியும் நீரே"
            ], [
                "Yudhaavin Raajaavae ummai aaraadhikkindroam",
                "Singaasanathil veetrirukkum Yesuvae",
                "Jeyam pettra singam Neerae",
                "Engal jeyakkodiyum Neerae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "சத்துருவின் சேனைகளை முறியடித்தீர்",
                "மரணத்தை ஜெயமாய் விழுங்கி விட்டீர்",
                "பாதாளத்தின் திறவுகோல் உம் கையிலே",
                "என்றென்றும் உயிரோடு வாழ்பவரே"
            ], [
                "Sathuruvin saenaigalai muriyaditheer",
                "Maranathai jeyamaai vizhungi vitteer",
                "Paadhaalaththin thiravukol um kaiyilae",
                "Endrendrum uyirodu vaazhbavarae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "முழங்கால்கள் யாவும் உமக்கு முன்பாக முடங்கும்",
                "நாவுகள் யாவும் உம்மை ஆண்டவர் என்று அறிக்கை செய்யும்",
                "ராஜாதி ராஜாவே கர்த்தாதி கர்த்தரே",
                "என்றென்றும் ஆளுகை செய்திடுவீர்"
            ], [
                "Muzhangkaalgal yaavum umakku munbaaga mudangum",
                "Naavugal yaavum ummai Aandavar endru arikkai seiyum",
                "Raajaadhi Raajaavae Karththaadhi Karththarae",
                "Endrendrum aalugai seidhiduveer"
            ])
        ]
    },
    {
        "title_ta": "அற்புதங்கள் அடையாளங்கள் செய்கின்ற தேவன்",
        "title_en": "Arpudhangal Adayalangal",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=RSIC2bpHUoc",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "அற்புதங்கள் அடையாளங்கள் செய்கின்ற தேவன் நீரே",
                "வல்லமையின் ராஜாவே ஆராதிக்கின்றோம்",
                "நேற்றும் இன்றும் என்றும் மாறாதவரே",
                "எங்கள் நடுவில் கிரியை செய்திடுவீர்"
            ], [
                "Arpudhangal adayalangal seigindra Dhevan Neerae",
                "Vallamaiyin Raajaavae aaraadhikkindroam",
                "Naettrum indrum endrum maaraadhavarae",
                "Engal naduvil kiriyai seidhiduveer"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "செங்கடலை இரண்டாகப் பிளந்தவரே",
                "வழியில்லாத இடத்தில் வழி திறந்தீர்",
                "இன்றும் என் வாழ்வின் தடைகள் யாவையும்",
                "உடைத்து எறிந்து வழி செய்திடுவீர்"
            ], [
                "Sengadalai irandaagap pilandhavarae",
                "Vazhiyillaadha idathil vazhi thirantheer",
                "Indrum en vaazhvin thadaigal yaavaiyum",
                "Udaithu erindhu vazhi seidhiduveer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "குருடரின் கண்களைத் திறந்த தெய்வமே",
                "செவிடரின் காதுகளைக் கேட்கச் செய்தீர்",
                "சகல நோய்களையும் சுகமாக்கும் வல்லவரே",
                "உம் தழும்புகளால் நான் சுகமானேன்"
            ], [
                "Kurudarin kangalaith thirandha Deivamae",
                "Sevidarin kaadhugalaik kaetkach cheidheer",
                "Sagala noigalaiyum sugamaakkum vallavarae",
                "Um thazhumbugalaal naan sugamaanaen"
            ])
        ]
    },
    {
        "title_ta": "நீர் வாழ்கவே நீர் வாழ்கவே",
        "title_en": "Neer Vazhgavae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=S1NJL7KxQVY",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "நீர் வாழ்கவே நீர் வாழ்கவே",
                "இயேசுவே நீர் வாழ்கவே",
                "என்றென்றும் வாழ்கவே ராஜாதி ராஜாவே",
                "எங்கள் துதிகளின் மத்தியில் நீர் வாழ்கவே"
            ], [
                "Neer vaazhgavae Neer vaazhgavae",
                "Yesuvae Neer vaazhgavae",
                "Endrendrum vaazhgavae Raajaadhi Raajaavae",
                "Engal thudhigalin madhiyil Neer vaazhgavae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மண்ணுலகில் வந்து மாந்தரை மீட்டீர்",
                "மகிமையின் தேவன் தாழ்மையை ஏற்றீர்",
                "உம் தியாக அன்பிற்கு ஈடில்லையே",
                "உம்மைப் போல நேசர் யாருமில்லையே"
            ], [
                "Mannulagil vandhu maandharai meetteer",
                "Magimaiyin Dhevan thaazhmaiyai aettreeer",
                "Um thiyaaga anbirku eedillaiyae",
                "Ummaip pola Naesar yaarumillaiyae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உயிர்த்தெழுந்த ஜீவ அதிபதியே",
                "மரணத்தை ஜெயித்த மா மன்னரே",
                "எங்கள் புகழ்ச்சியின் பாத்திரரே",
                "என்றென்றும் வாழ்கவே"
            ], [
                "Uyirththezhundha jeeva adhipadhiyae",
                "Maranathai jeyiththa maa mannarae",
                "Engal pugazhchiyin paaththirarae",
                "Endrendrum vaazhgavae"
            ])
        ]
    },
    {
        "title_ta": "தகப்பனே என் தகப்பனே",
        "title_en": "Thagappanae En Thagappanae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=-HLSZy1cZt8",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "தகப்பனே என் தகப்பனே",
                "தாயினும் மேலானவரே",
                "உயிருள்ள நாளெல்லாம் பாடுவேன்",
                "உம் அன்பை விவரிக்க வார்த்தையில்லையே"
            ], [
                "Thagappanae en thagappanae",
                "Thaayinum maelaanavarae",
                "Uyirulla naalellaam paaduvaen",
                "Um anbai vivarikka vaarthaiyillaiyae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "கருவிலே என்னைக் கண்டீரையா",
                "பேர் சொல்லி என்னைக் கூப்பிட்டீரே",
                "தாயின் கருவில் உருவான நாள் முதல்",
                "கரங்களில் ஏந்தி சுமந்தீரையா"
            ], [
                "Karuvilae ennaik kandeeraiyaa",
                "Paer solli ennaik kooppitteerae",
                "Thaayin karuvil uruvaana naal mudhal",
                "Karangalil aendhi sumandheeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "தகப்பன் பிள்ளைக்கு இரங்குவது போல",
                "என் மேல் நீர் இரக்கம் கொண்டீர்",
                "என் பலவீனங்களை அறிந்தவரே",
                "உம் அன்பினால் என்னை அணைத்துக் கொண்டீர்"
            ], [
                "Thagappan pillaikku iranguvadhu pola",
                "En mael Neer irakkam kondeer",
                "En balaveenangalai arindhavarae",
                "Um anbinaal ennai anaithuk kondeer"
            ])
        ]
    },
    {
        "title_ta": "வழி தவறிப் போன என்னை",
        "title_en": "Vazhi Thavari Pona",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=dYbLVCaWNQQ",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "வழி தவறிப் போன என்னைத் தேடி வந்தீரே",
                "மார்போடு அணைத்துக் கொண்டீரே",
                "காணாமல் போன ஆட்டைப் போல அலைந்த என்னை",
                "தோளின் மேல் சுமந்து வந்தீரையா"
            ], [
                "Vazhi thavarip pona ennaith thaedi vandheerae",
                "Maarbodu anaithuk kondeerae",
                "Kaanaamal pona aattaip pola alaindha ennai",
                "Tholin mael sumandhu vandheeraiyaa"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "உலகத்தின் சேற்றில் மூழ்கிப் போனேன்",
                "பாவத்தின் பாரத்தால் நசுங்கி நின்றேன்",
                "தூக்கி எடுத்து கல்வாரி இரத்தத்தால்",
                "முழுமையாய் கழுவி சுத்திகரித்தீர்"
            ], [
                "Ulagaththin saettril moozhgip ponaen",
                "Paavaththin baaraththaal nasungki nindraen",
                "Thookki eduthu Kalvaari irathaththaal",
                "Muzhumaiyaai kazhuvi suthigaritheer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "மன்னிக்கும் தெய்வம் நீர்தானையா",
                "மறந்து போன நன்மைகளை மீண்டும் தந்தீர்",
                "புதிய வாழ்வை எனக்குத் தந்து",
                "உம் பிள்ளையாய் மாற்றி விட்டீரையா"
            ], [
                "Mannikkum Deivam Neerdhaanaiyaa",
                "Marandhu pona nanmaigalai meendum thandheer",
                "Pudhiya vaazhvai enakkuth thandhu",
                "Um pillaiyaai maatri vitteeraiyaa"
            ])
        ]
    },
    {
        "title_ta": "உம் நாமம் அற்புதமானது",
        "title_en": "Um Naamam",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=6BdB0_7AbDI",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உம் நாமம் அற்புதமானது அதிசயமானது",
                "எல்லா நாமத்திலும் மேலானது",
                "இயேசு என்னும் நாமம் இன்ப நாமம்",
                "எங்கள் நாவுகள் போற்றிடும் திவ்ய நாமம்"
            ], [
                "Um naamam arpudhamaanadhu adhisayamaanadhu",
                "Ellaa naamathilum maelaanadhu",
                "Yesu ennum naamam inba naamam",
                "Engal naavugal pottridum dhivya naamam"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "அந்த நாமத்தினால் பிணிகள் ஓடும்",
                "அந்த நாமத்தினால் பேய்கள் நடுங்கும்",
                "அந்த நாமத்தினால் இரட்சிப்பு உண்டு",
                "அந்த நாமத்தினால் ஜெயமும் உண்டு"
            ], [
                "Andha naamathinaal pinigal odum",
                "Andha naamathinaal paeigal nadungum",
                "Andha naamathinaal iratchippu undu",
                "Andha naamathinaal jeyamum undu"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வானிலும் பூவிலும் அந்த நாமம்",
                "உயர்ந்த அடைக்கல அரணான நாமம்",
                "நீதிமான் அதற்குள் ஓடிப் போகும்போது",
                "சுகமாய் தங்கி வாழ்ந்திடுவான்"
            ], [
                "Vaanilum boovilum andha naamam",
                "Uyarndha adaikkala aranaana naamam",
                "Needhimaan adharkkul odip pogumpodhu",
                "Sugamaai thanggi vaazhndhiduvaan"
            ])
        ]
    },
    {
        "title_ta": "யேகோவா யீரே எல்லாமே பார்த்துக் கொள்வீர்",
        "title_en": "Yegovah Yirae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=otavRKgH8lE",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "யேகோவா யீரே எல்லாமே பார்த்துக் கொள்வீர்",
                "குறைவுகள் ஒன்றும் எனக்கில்லையே",
                "தேவைப்படும் நேரத்தில் தேவைகளைச் சந்திப்பீர்",
                "என்னை நடத்தும் நல்ல மேய்ப்பரே"
            ], [
                "Yegovah Yirae ellaamae paarthuk kolveer",
                "Kuraivugal ondrum enakkillaiyae",
                "Thaevaippadum naerathil thaevaigalaich chandhippeer",
                "Ennai nadathum nalla Maeipparae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "புல்லுள்ள இடங்களில் என்னை மேய்க்கின்றீர்",
                "அமர்ந்த தண்ணீரண்டை நடத்துகின்றீர்",
                "ஆத்துமாவைத் தேற்றி புது பெலன் தந்து",
                "நீதியின் பாதையில் நடத்துகின்றீர்"
            ], [
                "Pullulla idangalil ennai meykkindreer",
                "Amarndha thanneerandai nadathukindreer",
                "Aathumaavaith thaetri pudhu belan thandhu",
                "Needhiyin paadhaiyil nadathukindreer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "எலியாவுக்கு அப்பம் காகத்தைக் கொண்டு தந்தீர்",
                "விதவையின் பாத்திரத்தை குறையாமல் காத்தீர்",
                "எனக்காய் யாவையும் செய்து முடிப்பவரே",
                "உம்மையே நான் சார்ந்திருப்பேன்"
            ], [
                "Eliyaavukku appam kaagathaik kondu thandheer",
                "Vidhavaiyin paathirathai kuraiyaamal kaaththeer",
                "Enakkaai yaavaiyum seidhu mudippavarae",
                "Ummaiyae naan saarndhiruppaen"
            ])
        ]
    },
    {
        "title_ta": "என் இயேசுவே உம் அன்பு போதுமையா",
        "title_en": "En Yesuvae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=fD4OIG37evo",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "என் இயேசுவே உம் அன்பு போதுமையா",
                "காலமெல்லாம் என்னை நடத்தும் ஐயா",
                "உம் பாதத்தில் நான் அமர்ந்திருக்கும் போது",
                "உலக கவலைகள் எல்லாம் பறந்து போகுதே"
            ], [
                "En Yesuvae um anbu podhumaiyaa",
                "Kaalamellaam ennai nadathum aiyaa",
                "Um paadhathil naan amarndhirukkum podhu",
                "Ulaga kavalaigal ellaam parandhu pogudhae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "நண்பர்கள் கைவிட்ட போதும் நீர் கைவிடவில்லை",
                "உலகமே எதிர்த்த போதும் விலகிப் போகவில்லை",
                "மார்போடு அணைத்துக் கொண்ட நேசரே",
                "உம் அன்பிற்கு இணையே இல்லையே"
            ], [
                "Nanbargal kaivitta podhum Neer kaividavillai",
                "Ulagamae edhirtha podhum vilagip pogavillai",
                "Maarbodu anaithuk konda Naesarae",
                "Um anbirku inaiyae illaiyae"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "வாழ்நாளெல்லாம் உம்மைப் பணிந்திடுவேன்",
                "உம் அன்பின் சுடராய் பிரகாசிப்பேன்",
                "இயேசுவே என் வாழ்வின் ஒளியானவரே",
                "என்றென்றும் உம்மைத் துதிப்பேன்"
            ], [
                "Vaazhnaalellaam ummaip panindhiduvaen",
                "Um anbin sudaraai piragaasippaen",
                "Yesuvae en vaazhvin oliyaanavarae",
                "Endrendrum ummaith thudhippaen"
            ])
        ]
    },
    {
        "title_ta": "என் மீட்பரான இயேசுவே",
        "title_en": "En Meetparaana Yesuvae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=cCSURn1aFSM",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "என் மீட்பரான இயேசுவே உம்மை ஆராதிக்கின்றேன்",
                "ஜீவனுள்ள நாளெல்லாம் உமக்காய் வாழ்வேன்",
                "பாவ சாபங்களை நீக்கி மீட்டெடுத்தீரே",
                "உம் சொந்த ஜனமாய் தெரிந்து கொண்டீரே"
            ], [
                "En meetparana Yesuvae ummai aaraadhikkindroam",
                "Jeevanulla naalellaam umakkaai vaazhvaen",
                "Paava saabangalai neekki meetteduththeerae",
                "Um sondha janamaai therindhu kondeerae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "மரண இருளின் கூண்டிலிருந்து தப்புவித்தீர்",
                "பாதாளத்தின் கட்டுகளை உடைத்தெறிந்தீர்",
                "சுதந்திர மனிதனாய் என்னை வாழ வைத்தீர்",
                "உந்தன் பரிசுத்த ஆவியால் முத்திரை போட்டீர்"
            ], [
                "Marana irulin koondilirundhu thappuvitheer",
                "Paadhaalaththin kattugalai udaittherintheer",
                "Sudhandhira manidhannaai ennai vaazha vaiththeer",
                "Undhan parisutha aaviyaal muththirai potteer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உம் இரத்தத்தின் வல்லமையால் வெற்றி சிறந்தீர்",
                "சாத்தானின் தலையை நசுக்கிப் போட்டீர்",
                "ஜெயம் கொடுக்கும் என் மீட்பரே",
                "என்றென்றும் உம்மை உயர்த்துவேன்"
            ], [
                "Um irathaththin vallamaiyaal vettri sirandheer",
                "Saaththaanin thalaiyai nasukkip potteer",
                "Jeyam kodukkum en Meetparae",
                "Endrendrum ummai uyarthuvaen"
            ])
        ]
    },
    {
        "title_ta": "உயிரோடிருப்பவரே என்றும் ஜீவிப்பவரே",
        "title_en": "Uyirodirupavarae",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=u6PT87wgDEY",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "உயிரோடிருப்பவரே என்றும் ஜீவிப்பவரே",
                "சர்வ வல்லவரே உம்மைப் போற்றுகின்றோம்",
                "மரித்தீரானாலும் உயிர்த்தெழுந்தீரே",
                "சதா காலங்களிலும் வாழ்பவரே"
            ], [
                "Uyirodu iruppavarae endrum jeevippavarae",
                "Sarva vallavarae ummaip potrugindroam",
                "Mariththeeraanaalum uyirththezhundheerae",
                "Sadhaa kaalangalilum vaazhbavarae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "கல்லறை உம்மை அடக்கி வைக்கவில்லை",
                "மரணத்தின் கட்டுகள் தாங்கவில்லை",
                "மகிமையின் தேவனாய் வெற்றி சிறந்தீர்",
                "எங்களுக்கும் நித்திய ஜீவன் தந்தீர்"
            ], [
                "Kallarai ummai adakki vaikkavillai",
                "Maranaththin kattugal thaangavillai",
                "Magimaiyin Dhevanaai vettri sirandheer",
                "Engalukkum nithiya jeevan thandheer"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "பரலோகத்தில் நமக்காய் பரிந்து பேசுகின்றீர்",
                "மறுபடியும் சீக்கிரமாய் வரப்போகின்றீர்",
                "மேகங்களின் மீது உம்மை சந்திப்போம்",
                "என்றென்றும் உம்மோடு வாழ்ந்திடுவோம்"
            ], [
                "Paralogathil namakkaai parindhu paesugindreer",
                "Marubadiyum seekkiramaai varappogindreer",
                "Maegangalin meedhu ummai sandhippom",
                "Endrendrum ummodu vaazhndhiduvom"
            ])
        ]
    },
    {
        "title_ta": "சிலுவையின் நிழலில் நான் தங்குவேன்",
        "title_en": "Siluvaiyin Nizhalil",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=JY7ixjP5bzg",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "சிலுவையின் நிழலில் நான் தங்குவேன்",
                "கல்வாரி அன்பை நான் பாடுவேன்",
                "எனக்காய் ஜீவன் தந்த என் நேசரே",
                "உம் இரத்தத்தால் என்னை மீட்டுக்கொண்டீரே"
            ], [
                "Siluvaiyin nizhalil naan thangguvaen",
                "Kalvaari anbai naan paaduvaen",
                "Enakkaai jeevan thandha en Naesarae",
                "Um irathaththaal ennai meettuk kondeerae"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "சிலுவை சுமந்த என் இயேசுவே",
                "முள்முடி சூடிய என் தெய்வமே",
                "உம் தியாக அன்பை நினைக்கையிலே",
                "கண்ணீர் பெருக்கெடுத்து ஓடுதையா"
            ], [
                "Siluvai sumandha en Yesuvae",
                "Mulmudi soodiya en Deivamae",
                "Um thiyaaga anbai ninaikkaiyilae",
                "Kanneer perukkeduthu odudhaiyaa"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "உலகத்தின் மேன்மைகள் வேண்டாமையா",
                "உம் சிலுவையை மட்டுமே மேன்மை பாராட்டுவேன்",
                "உம்மோடு சிலுவையில் அறையப்பட்டு",
                "உமக்காய் மட்டுமே வாழ்ந்திடுவேன்"
            ], [
                "Ulagaththin maenmaigal vaendaamaiyaa",
                "Um siluvaiyai mattumae maenmai paaraattuvaen",
                "Ummodu siluvaiyil araiyappattu",
                "Umakkaai mattumae vaazhndhiduvaen"
            ])
        ]
    },
    {
        "title_ta": "கர்த்தரை நம்பும் மனிதன் பாக்கியவான்",
        "title_en": "Kartharai Nambum Manithan",
        "author": "Pastor Benny Joshua {பாஸ்டர் பென்னி ஜோசுவா}",
        "youtube_url": "https://www.youtube.com/watch?v=6BdB0_7AbDI",
        "stanzas": [
            make_stanza("chorus", "பல்லவி (Chorus)", [
                "கர்த்தரை நம்பும் மனிதன் பாக்கியவான்",
                "அசைக்கப்படுவதில்லை அவன் என்றென்றும்",
                "சீயோன் பர்வதம் போல நிலைத்திருப்பான்",
                "தேவனின் சமாதானம் அவன் மேலிருக்கும்"
            ], [
                "Kartharai nambum manidhan baakkiyavaan",
                "Asaikkappaduvadhillai avan endrendrum",
                "Seeyon parvatham pola nilaiththiruppaan",
                "Dhevanin samaadhaanam avan maelirukkum"
            ]),
            make_stanza("stanza", "சரணம் 1 (Verse 1)", [
                "பர்வதங்கள் எருசலேமைச் சுற்றிலும் இருப்பது போல",
                "கர்த்தர் தம் ஜனத்தைச் சுற்றிலும் இருக்கிறார்",
                "இதுமுதல் என்றென்றைக்கும் காத்திடுவார்",
                "ஒரு பொல்லாப்பும் நம்மைத் தொடாது"
            ], [
                "Parvathangal Yerusalemaich chuttrilum iruppadhu pola",
                "Karthar tham janathaich chuttrilum irukkiraar",
                "Idhumudhal endrendraikkum kaathiduvaar",
                "Oru pollaappum nammaith thodaadhu"
            ]),
            make_stanza("stanza", "சரணம் 2 (Verse 2)", [
                "கர்த்தருக்குள் மனமகிழ்ச்சியாய் இருங்கள்",
                "அவர் உன் இருதயத்தின் வேண்டுதல்களைத் தருவார்",
                "உன் வழியைக் கர்த்தருக்கு ஒப்புவித்துவிடு",
                "அவரே யாவையும் வாய்க்கச் செய்வார்"
            ], [
                "Kartharukkul manamagizhchiyaai irungal",
                "Avar un irudhayaththin vaendudhalgalaith tharuvaar",
                "Un vazhiyaik Kartharukku oppuvithuvidu",
                "Avarae yaavaiyum vaaikkach cheivaar"
            ])
        ]
    }
]
