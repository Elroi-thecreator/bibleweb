"""
Bible Quiz / Trivia Game Dataset
Bilingual Questions (Tamil & English) with categories, difficulty, scripture references, and explanations.
"""

QUIZ_CATEGORIES = {
    "all": {"name_en": "All Categories", "name_ta": "அனைத்து பிரிவுகள்", "icon": "📖"},
    "gospels": {"name_en": "Gospels & Jesus", "name_ta": "சுவிசேஷங்கள் & இயேசு", "icon": "✝️"},
    "old_testament": {"name_en": "Old Testament", "name_ta": "பழைய ஏற்பாடு", "icon": "📜"},
    "heroes": {"name_en": "Heroes & Prophets", "name_ta": "விசுவாச வீரர்கள் & தீர்க்கதரிசிகள்", "icon": "🛡️"},
    "miracles_parables": {"name_en": "Miracles & Parables", "name_ta": "அற்புதங்கள் & உவமைகள்", "icon": "✨"},
    "general": {"name_en": "General Bible Trivia", "name_ta": "பொதுவான வேதாகம வினாடி வினா", "icon": "💡"},
}

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "Where was Jesus born?",
        "question_ta": "இயேசு எங்கே பிறந்தார்?",
        "options_en": ["Nazareth", "Bethlehem", "Jerusalem", "Capernaum"],
        "options_ta": ["நாசரேத்து", "பெத்லகேம்", "எருசலேம்", "கப்பர்நகூம்"],
        "correct_index": 1,
        "reference": "Matthew 2:1 / மத்தேயு 2:1",
        "explanation_en": "Jesus was born in Bethlehem of Judea in the days of Herod the king.",
        "explanation_ta": "ஏரோது ராஜாவின் நாட்களில் யூதேயாவிலுள்ள பெத்லகேமிலே இயேசு பிறந்தார்."
    },
    {
        "id": 2,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "Who built the ark to survive the great flood?",
        "question_ta": "பெருவெள்ளத்திலிருந்து தப்பிக்க பேழையைக் கட்டியவர் யார்?",
        "options_en": ["Abraham", "Moses", "Noah", "David"],
        "options_ta": ["ஆபிரகாம்", "மோசே", "நோவா", "தாவீது"],
        "correct_index": 2,
        "reference": "Genesis 6:13-14 / ஆதியாகமம் 6:13-14",
        "explanation_en": "God commanded Noah to build an ark of gopher wood.",
        "explanation_ta": "தேவன் நோவாவிடம் கொப்பேர் மரத்தால் ஒரு பேழையை உண்டுபண்ணக் கட்டளையிட்டார்."
    },
    {
        "id": 3,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who defeated the Philistine giant Goliath with a sling and stone?",
        "question_ta": "கவணும் கல்லும் கொண்டு பெலிஸ்திய அரக்கன் கோலியாத்தை வென்றவர் யார்?",
        "options_en": ["Saul", "Samson", "David", "Jonathan"],
        "options_ta": ["சவுல்", "சிம்சோன்", "தாவீது", "யோனத்தான்"],
        "correct_index": 2,
        "reference": "1 Samuel 17:49-50 / 1 சாமுவேல் 17:49-50",
        "explanation_en": "David prevailed over the Philistine with a sling and with a stone.",
        "explanation_ta": "தாவீது ஒரு கவணினாலும் ஒரு கல்லினாலும் அந்தப் பெலிஸ்தனை மேற்கொண்டான்."
    },
    {
        "id": 4,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "What was Jesus' first miracle recorded in the Gospel of John?",
        "question_ta": "யோவான் சுவிசேஷத்தில் பதிவு செய்யப்பட்டுள்ள இயேசுவின் முதல் அற்புதம் எது?",
        "options_en": [
            "Walking on water",
            "Healing the blind man",
            "Turning water into wine",
            "Feeding the 5,000"
        ],
        "options_ta": [
            "கடலின் மேல் நடப்பது",
            "பார்வையற்றவனை குணமாக்குவது",
            "தண்ணீரை திராட்சரசமாக மாற்றியது",
            "5,000 பேருக்கு உணவளித்தது"
        ],
        "correct_index": 2,
        "reference": "John 2:11 / யோவான் 2:11",
        "explanation_en": "Jesus performed His first miracle at the wedding in Cana of Galilee by turning water into wine.",
        "explanation_ta": "இயேசு கலிலேயாவிலுள்ள கானாவூர் திருமண விருந்தில் தண்ணீரை திராட்சரசமாக மாற்றினார்."
    },
    {
        "id": 5,
        "category": "general",
        "difficulty": "easy",
        "question_en": "How many books are there in the standard Protestant Bible?",
        "question_ta": "வேதாகமத்தில் மொத்தம் எத்தனை புத்தகங்கள் உள்ளன?",
        "options_en": ["60", "66", "72", "70"],
        "options_ta": ["60", "66", "72", "70"],
        "correct_index": 1,
        "reference": "Bible Canon (39 Old Testament + 27 New Testament)",
        "explanation_en": "The Bible has 66 books: 39 in the Old Testament and 27 in the New Testament.",
        "explanation_ta": "வேதாகமத்தில் மொத்தம் 66 புத்தகங்கள் உள்ளன: பழைய ஏற்பாட்டில் 39, புதிய ஏற்பாட்டில் 27."
    },
    {
        "id": 6,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "Which sea did God part through Moses for the Israelites to cross?",
        "question_ta": "இஸ்ரவேலர் கடந்து செல்ல மோசே மூலமாக தேவன் பிளந்த கடல் எது?",
        "options_en": ["Dead Sea", "Red Sea", "Sea of Galilee", "Mediterranean Sea"],
        "options_ta": ["உப்புக் கடல்", "செங்கடல்", "கலிலேயா கடல்", "மத்திய தரைக்கடல்"],
        "correct_index": 1,
        "reference": "Exodus 14:21 / யாத்திராகமம் 14:21",
        "explanation_en": "Moses stretched out his hand over the sea, and the Lord drove the sea back by a strong east wind.",
        "explanation_ta": "மோசே தன் கையைச் சமுத்திரத்தின்மேல் நீட்டினான்; கர்த்தர் செங்கடலை இரண்டாகப் பிளந்தார்."
    },
    {
        "id": 7,
        "category": "gospels",
        "difficulty": "medium",
        "question_en": "Who baptized Jesus in the Jordan River?",
        "question_ta": "யோர்தான் நதியில் இயேசுவுக்கு ஞானஸ்நானம் கொடுத்தவர் யார்?",
        "options_en": ["Peter", "John the Baptist", "James", "Andrew"],
        "options_ta": ["பேதுரு", "யோவான் ஸ்நானகன்", "யாக்கோபு", "அந்திரேயா"],
        "correct_index": 1,
        "reference": "Matthew 3:13-17 / மத்தேயு 3:13-17",
        "explanation_en": "Jesus came from Galilee to John at the Jordan to be baptized by him.",
        "explanation_ta": "இயேசு யோவானால் ஞானஸ்நானம் பெறுவதற்கு கலிலேயாவை விட்டு யோர்தானுக்கு வந்தார்."
    },
    {
        "id": 8,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who was swallowed by a great fish when running away from God's calling?",
        "question_ta": "தேவனின் கட்டளையை விட்டு தப்பியோடும் போது பெரிய மீனால் விழுங்கப்பட்டவர் யார்?",
        "options_en": ["Elijah", "Jonah", "Daniel", "Jeremiah"],
        "options_ta": ["எலியா", "யோனா", "தானியேல்", "எரேமியா"],
        "correct_index": 1,
        "reference": "Jonah 1:17 / யோனா 1:17",
        "explanation_en": "Now the Lord had prepared a great fish to swallow up Jonah. And Jonah was in the belly of the fish three days and three nights.",
        "explanation_ta": "யோனாவை விழுங்கும்படி ஒரு பெரிய மீனைக் கர்த்தர் கட்டளையிட்டிருந்தார்; யோனா மூன்று இரவும் மூன்று பகலும் மீனின் வயிற்றில் இருந்தான்."
    },
    {
        "id": 9,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who was thrown into the lions' den for praying to God?",
        "question_ta": "தேவனிடத்தில் ஜெபம் பண்ணினதற்காக சிங்கங்களின் கெபியில் போடப்பட்டவர் யார்?",
        "options_en": ["Shadrach", "Daniel", "Joseph", "Nehemiah"],
        "options_ta": ["சாத்ராக்", "தானியேல்", "யோசேப்பு", "நெகேமியா"],
        "correct_index": 1,
        "reference": "Daniel 6:16 / தானியேல் 6:16",
        "explanation_en": "The king commanded, and they brought Daniel and cast him into the den of lions. God shut the lions' mouths.",
        "explanation_ta": "ராஜா கட்டளையிட்டபடி தானியேலைக் கொண்டுவந்து சிங்கங்களின் கெபியிலே போட்டார்கள்; தேவன் சிங்கங்களின் வாயைக் கட்டினார்."
    },
    {
        "id": 10,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "With how many loaves of bread and fish did Jesus feed the 5,000?",
        "question_ta": "இயேசு எத்தனை அப்பங்கள் மற்றும் மீன்களைக் கொண்டு 5,000 பேருக்கு உணவளித்தார்?",
        "options_en": [
            "5 loaves and 2 fish",
            "7 loaves and 3 fish",
            "3 loaves and 2 fish",
            "12 loaves and 5 fish"
        ],
        "options_ta": [
            "5 அப்பங்கள் மற்றும் 2 மீன்கள்",
            "7 அப்பங்கள் மற்றும் 3 மீன்கள்",
            "3 அப்பங்கள் மற்றும் 2 மீன்கள்",
            "12 அப்பங்கள் மற்றும் 5 மீன்கள்"
        ],
        "correct_index": 0,
        "reference": "Matthew 14:17-21 / மத்தேயு 14:17-21",
        "explanation_en": "Jesus multiplied five loaves and two fish to feed five thousand men, besides women and children.",
        "explanation_ta": "இயேசு ஐந்து அப்பங்களையும் இரண்டு மீன்களையும் எடுத்து ஸ்தோத்திரித்து ஐயாயிரம் பேருக்குப் பரிமாறினார்."
    },
    {
        "id": 11,
        "category": "old_testament",
        "difficulty": "hard",
        "question_en": "How many days and nights did rain pour upon the earth during Noah's flood?",
        "question_ta": "நோவாவின் பெருவெள்ளத்தின் போது பூமியின்மேல் எத்தனை நாட்கள் இரவும் பகலும் மழை பெய்தது?",
        "options_en": ["7 days", "40 days", "100 days", "150 days"],
        "options_ta": ["7 நாட்கள்", "40 நாட்கள்", "100 நாட்கள்", "150 நாட்கள்"],
        "correct_index": 1,
        "reference": "Genesis 7:12 / ஆதியாகமம் 7:12",
        "explanation_en": "And the rain was upon the earth forty days and forty nights.",
        "explanation_ta": "மழை நாற்பது நாள் இரவும் பகலும் பூமியின்மேல் பெய்தது."
    },
    {
        "id": 12,
        "category": "gospels",
        "difficulty": "medium",
        "question_en": "Which disciple denied Jesus three times before the rooster crowed?",
        "question_ta": "சேவல் கூவுவதற்கு முன்னே இயேசுவை மூன்று முறை மறுதலித்த சீடர் யார்?",
        "options_en": ["Judas", "Thomas", "Peter", "John"],
        "options_ta": ["யூதாஸ்", "தோமா", "பேதுரு", "யோவான்"],
        "correct_index": 2,
        "reference": "Luke 22:60-61 / லூக்கா 22:60-61",
        "explanation_en": "Immediately, while he was still speaking, the rooster crowed, and Peter remembered the Lord's words.",
        "explanation_ta": "பேதுரு பேசிக்கொண்டிருக்கையிலேயே சேவல் கூவிற்று; கர்த்தர் சொன்ன வார்த்தையை பேதுரு நினைவுகூர்ந்தான்."
    },
    {
        "id": 13,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who received the Ten Commandments from God on Mount Sinai?",
        "question_ta": "சீனாய் மலையில் தேவனிடமிருந்து பத்து கற்பனைகளைப் பெற்றவர் யார்?",
        "options_en": ["Aaron", "Joshua", "Moses", "Samuel"],
        "options_ta": ["ஆரோன்", "யோசுவா", "மோசே", "சாமுவேல்"],
        "correct_index": 2,
        "reference": "Exodus 20:1-17 / யாத்திராகமம் 20:1-17",
        "explanation_en": "Moses went up to Mount Sinai, and God gave him the tablets of the covenant.",
        "explanation_ta": "மோசே சீனாய் மலையில் ஏறி தேவனிடமிருந்து கற்பனைகளின் கற்பலகைகளைப் பெற்றார்."
    },
    {
        "id": 14,
        "category": "general",
        "difficulty": "easy",
        "question_en": "Which is the longest chapter in the Bible?",
        "question_ta": "வேதாகமத்தில் மிக நீளமான அதிகாரம் எது?",
        "options_en": ["Psalm 23", "Psalm 119", "Isaiah 53", "Matthew 1"],
        "options_ta": ["சங்கீதம் 23", "சங்கீதம் 119", "ஏசாயா 53", "மத்தேயு 1"],
        "correct_index": 1,
        "reference": "Psalm 119 (176 verses) / சங்கீதம் 119 (176 வசனங்கள்)",
        "explanation_en": "Psalm 119 is the longest chapter in the Bible with 176 verses, celebrating God's Word.",
        "explanation_ta": "சங்கீதம் 119 மொத்தம் 176 வசனங்களைக் கொண்ட வேதாகமத்தின் மிக நீளமான அதிகாரமாகும்."
    },
    {
        "id": 15,
        "category": "general",
        "difficulty": "easy",
        "question_en": "Which is the shortest verse in the Bible?",
        "question_ta": "வேதாகமத்தில் மிகச் சிறிய வசனம் எது?",
        "options_en": [
            "Jesus wept (John 11:35)",
            "Pray without ceasing (1 Thess 5:17)",
            "Rejoice evermore (1 Thess 5:16)",
            "God is love (1 John 4:8)"
        ],
        "options_ta": [
            "இயேசு கண்ணீர்விட்டார் (யோவான் 11:35)",
            "இடைவிடாமல் ஜெபம்பண்ணுங்கள் (1 தெச 5:17)",
            "எப்பொழுதும் சந்தோஷமாயிருங்கள் (1 தெச 5:16)",
            "தேவன் அன்பாகவே இருக்கிறார் (1 யோவான் 4:8)"
        ],
        "correct_index": 0,
        "reference": "John 11:35 / யோவான் 11:35",
        "explanation_en": "John 11:35 contains just two words: 'Jesus wept.'",
        "explanation_ta": "யோவான் 11:35 'இயேசு கண்ணீர்விட்டார்' என்பது வேதாகமத்தின் மிகக் குறுகிய வசனமாகும்."
    },
    {
        "id": 16,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "Whom did Jesus raise from the dead after he had been in the tomb four days?",
        "question_ta": "கல்லறையில் நான்கு நாட்கள் இருந்த பின் இயேசு யாரை உயிரோடு எழுப்பினார்?",
        "options_en": ["Jairus' daughter", "Lazarus", "Widow's son at Nain", "Tabitha"],
        "options_ta": ["யவீருவின் மகள்", "லாசரு", "நாயீன் ஊர் விதவையின் மகன்", "தபீத்தாள்"],
        "correct_index": 1,
        "reference": "John 11:43-44 / யோவான் 11:43-44",
        "explanation_en": "Jesus called out with a loud voice, 'Lazarus, come forth!' and he who had died came out.",
        "explanation_ta": "இயேசு 'லாசருவே, வெளியே வா' என்று உரத்த சத்தமாய்க் கூப்பிட்டார்; மரித்தவன் வெளியே வந்தான்."
    },
    {
        "id": 17,
        "category": "old_testament",
        "difficulty": "hard",
        "question_en": "Who was the oldest recorded person in the Bible, living 969 years?",
        "question_ta": "வேதாகமத்தில் 969 ஆண்டுகள் வாழ்ந்த மிக அதிக வயதுடைய மனிதர் யார்?",
        "options_en": ["Adam", "Enoch", "Methuselah", "Noah"],
        "options_ta": ["ஆதாம்", "ஏனோக்கு", "மெத்தூசலா", "நோவா"],
        "correct_index": 2,
        "reference": "Genesis 5:27 / ஆதியாகமம் 5:27",
        "explanation_en": "All the days of Methuselah were nine hundred and sixty-nine years, and he died.",
        "explanation_ta": "மெத்தூசலாவின் நாளெல்லாம் தொள்ளாயிரத்து அறுபத்தொன்பது வருஷம்; அவன் மரித்தான்."
    },
    {
        "id": 18,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who interpreted Pharaoh's dreams of seven fat cows and seven thin cows?",
        "question_ta": "பார்வோனின் ஏழு கொழுத்த பசுக்களையும் ஏழு மெலிந்த பசுக்களையும் குறித்த சொப்பனத்திற்கு அர்த்தம் சொன்னவர் யார்?",
        "options_en": ["Joseph", "Daniel", "Moses", "Jacob"],
        "options_ta": ["யோசேப்பு", "தானியேல்", "மோசே", "யாக்கோபு"],
        "correct_index": 0,
        "reference": "Genesis 41:25-30 / ஆதியாகமம் 41:25-30",
        "explanation_en": "Joseph told Pharaoh that seven years of great abundance would be followed by seven years of severe famine.",
        "explanation_ta": "யோசேப்பு பார்வோனிடம் ஏழு வருஷம் மிகுந்த விளைச்சல் உண்டாகும், அதன்பின் ஏழு வருஷம் கடும் பஞ்சம் உண்டாகும் என்று விளக்கினார்."
    },
    {
        "id": 19,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "In what city did Jesus ride in triumph on a donkey on Palm Sunday?",
        "question_ta": "குருத்தோலை ஞாயிறன்று இயேசு கழுதைக்குட்டியின் மேல் ஏறி வெற்றி பவனியாகச் சென்ற நகரம் எது?",
        "options_en": ["Jericho", "Jerusalem", "Nazareth", "Bethany"],
        "options_ta": ["எரிகோ", "எருசலேம்", "நாசரேத்து", "பெத்தானியா"],
        "correct_index": 1,
        "reference": "Matthew 21:1-11 / மத்தேயு 21:1-11",
        "explanation_en": "The multitude spread their garments and cried, 'Hosanna to the Son of David!' as Jesus entered Jerusalem.",
        "explanation_ta": "இயேசு எருசலேமுக்குள் பிரவேசித்தபோது, ஜனங்கள் தங்கள் வஸ்திரங்களை வழியிலே விரித்து 'தாவீதின் குமாரனுக்கு ஓசன்னா!' என்று ஆர்ப்பரித்தனர்."
    },
    {
        "id": 20,
        "category": "general",
        "difficulty": "medium",
        "question_en": "What is the final book of the New Testament?",
        "question_ta": "புதிய ஏற்பாட்டின் இறுதி புத்தகம் எது?",
        "options_en": ["Jude", "Hebrews", "Revelation", "Acts"],
        "options_ta": ["யூதா", "எபிரெயர்", "வெளிப்படுத்தின விசேஷம்", "அப்போஸ்தலர்"],
        "correct_index": 2,
        "reference": "Revelation / வெளிப்படுத்தின விசேஷம்",
        "explanation_en": "The Revelation of Jesus Christ written by the Apostle John is the 66th and concluding book of Scripture.",
        "explanation_ta": "அப்போஸ்தலனாகிய யோவானால் எழுதப்பட்ட வெளிப்படுத்தின விசேஷம் வேதாகமத்தின் 66வது மற்றும் இறுதிப் புத்தகமாகும்."
    }
]
