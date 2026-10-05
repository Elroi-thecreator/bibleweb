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
        "options_en": [
            "Nazareth",
            "Bethlehem",
            "Jerusalem",
            "Capernaum"
        ],
        "options_ta": [
            "நாசரேத்து",
            "பெத்லகேம்",
            "எருசலேம்",
            "கப்பர்நகூம்"
        ],
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
        "options_en": [
            "Abraham",
            "Moses",
            "Noah",
            "David"
        ],
        "options_ta": [
            "ஆபிரகாம்",
            "மோசே",
            "நோவா",
            "தாவீது"
        ],
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
        "options_en": [
            "Saul",
            "Samson",
            "David",
            "Jonathan"
        ],
        "options_ta": [
            "சவுல்",
            "சிம்சோன்",
            "தாவீது",
            "யோனத்தான்"
        ],
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
        "options_en": [
            "60",
            "66",
            "72",
            "70"
        ],
        "options_ta": [
            "60",
            "66",
            "72",
            "70"
        ],
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
        "options_en": [
            "Dead Sea",
            "Red Sea",
            "Sea of Galilee",
            "Mediterranean Sea"
        ],
        "options_ta": [
            "உப்புக் கடல்",
            "செங்கடல்",
            "கலிலேயா கடல்",
            "மத்திய தரைக்கடல்"
        ],
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
        "options_en": [
            "Peter",
            "John the Baptist",
            "James",
            "Andrew"
        ],
        "options_ta": [
            "பேதுரு",
            "யோவான் ஸ்நானகன்",
            "யாக்கோபு",
            "அந்திரேயா"
        ],
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
        "options_en": [
            "Elijah",
            "Jonah",
            "Daniel",
            "Jeremiah"
        ],
        "options_ta": [
            "எலியா",
            "யோனா",
            "தானியேல்",
            "எரேமியா"
        ],
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
        "options_en": [
            "Shadrach",
            "Daniel",
            "Joseph",
            "Nehemiah"
        ],
        "options_ta": [
            "சாத்ராக்",
            "தானியேல்",
            "யோசேப்பு",
            "நெகேமியா"
        ],
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
        "options_en": [
            "7 days",
            "40 days",
            "100 days",
            "150 days"
        ],
        "options_ta": [
            "7 நாட்கள்",
            "40 நாட்கள்",
            "100 நாட்கள்",
            "150 நாட்கள்"
        ],
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
        "options_en": [
            "Judas",
            "Thomas",
            "Peter",
            "John"
        ],
        "options_ta": [
            "யூதாஸ்",
            "தோமா",
            "பேதுரு",
            "யோவான்"
        ],
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
        "options_en": [
            "Aaron",
            "Joshua",
            "Moses",
            "Samuel"
        ],
        "options_ta": [
            "ஆரோன்",
            "யோசுவா",
            "மோசே",
            "சாமுவேல்"
        ],
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
        "options_en": [
            "Psalm 23",
            "Psalm 119",
            "Isaiah 53",
            "Matthew 1"
        ],
        "options_ta": [
            "சங்கீதம் 23",
            "சங்கீதம் 119",
            "ஏசாயா 53",
            "மத்தேயு 1"
        ],
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
        "options_en": [
            "Jairus' daughter",
            "Lazarus",
            "Widow's son at Nain",
            "Tabitha"
        ],
        "options_ta": [
            "யவீருவின் மகள்",
            "லாசரு",
            "நாயீன் ஊர் விதவையின் மகன்",
            "தபீத்தாள்"
        ],
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
        "options_en": [
            "Adam",
            "Enoch",
            "Methuselah",
            "Noah"
        ],
        "options_ta": [
            "ஆதாம்",
            "ஏனோக்கு",
            "மெத்தூசலா",
            "நோவா"
        ],
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
        "options_en": [
            "Joseph",
            "Daniel",
            "Moses",
            "Jacob"
        ],
        "options_ta": [
            "யோசேப்பு",
            "தானியேல்",
            "மோசே",
            "யாக்கோபு"
        ],
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
        "options_en": [
            "Jericho",
            "Jerusalem",
            "Nazareth",
            "Bethany"
        ],
        "options_ta": [
            "எரிகோ",
            "எருசலேம்",
            "நாசரேத்து",
            "பெத்தானியா"
        ],
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
        "options_en": [
            "Jude",
            "Hebrews",
            "Revelation",
            "Acts"
        ],
        "options_ta": [
            "யூதா",
            "எபிரெயர்",
            "வெளிப்படுத்தின விசேஷம்",
            "அப்போஸ்தலர்"
        ],
        "correct_index": 2,
        "reference": "Revelation / வெளிப்படுத்தின விசேஷம்",
        "explanation_en": "The Revelation of Jesus Christ written by the Apostle John is the 66th and concluding book of Scripture.",
        "explanation_ta": "அப்போஸ்தலனாகிய யோவானால் எழுதப்பட்ட வெளிப்படுத்தின விசேஷம் வேதாகமத்தின் 66வது மற்றும் இறுதிப் புத்தகமாகும்."
    },
    {
        "id": 21,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "In how many days did God complete the creation of the heavens and the earth before resting?",
        "question_ta": "தேவன் எத்தனை நாட்களில் வானத்தையும் பூமியையும் படைத்து முடித்து ஓய்ந்திருந்தார்?",
        "options_en": [
            "3 days",
            "6 days",
            "7 days",
            "10 days"
        ],
        "options_ta": [
            "3 நாட்கள்",
            "6 நாட்கள்",
            "7 நாட்கள்",
            "10 நாட்கள்"
        ],
        "correct_index": 1,
        "reference": "Genesis 1:31-2:2 / ஆதியாகமம் 1:31-2:2",
        "explanation_en": "God completed His work of creation in 6 days and rested on the seventh day.",
        "explanation_ta": "தேவன் ஆறு நாட்களில் சிருஷ்டிப்பின் கிரியைகளை முடித்து, ஏழாம் நாளிலே ஓய்ந்திருந்தார்."
    },
    {
        "id": 22,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "How many disciples did Jesus specifically choose as His primary apostles?",
        "question_ta": "இயேசு தமக்கு பிரதான அப்போஸ்தலர்களாக எத்தனை சீடர்களைத் தெரிந்துகொண்டார்?",
        "options_en": [
            "7",
            "10",
            "12",
            "70"
        ],
        "options_ta": [
            "7",
            "10",
            "12",
            "70"
        ],
        "correct_index": 2,
        "reference": "Luke 6:13 / லூக்கா 6:13",
        "explanation_en": "When morning came, Jesus called His disciples and chose twelve of them, whom He also designated apostles.",
        "explanation_ta": "விடிந்தபோது, அவர் தம்முடைய சீஷர்களை வரவழைத்து, அவர்களில் பன்னிரண்டு பேரைத் தெரிந்துகொண்டு, அவர்களுக்கு அப்போஸ்தலர் என்று பேரிட்டார்."
    },
    {
        "id": 23,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who in Scripture was specifically called the 'friend of God'?",
        "question_ta": "வேதாகமத்தில் 'தேவனுடைய சிநேகிதன்' என்று அழைக்கப்பட்டவர் யார்?",
        "options_en": [
            "Moses",
            "Abraham",
            "David",
            "Elijah"
        ],
        "options_ta": [
            "மோசே",
            "ஆபிரகாம்",
            "தாவீது",
            "எலியா"
        ],
        "correct_index": 1,
        "reference": "James 2:23 / யாக்கோபு 2:23",
        "explanation_en": "Abraham believed God, and it was imputed unto him for righteousness: and he was called the Friend of God.",
        "explanation_ta": "ஆபிரகாம் தேவனை விசுவாசித்தான், அது அவனுக்கு நீதியாக எண்ணப்பட்டது; அவன் தேவனுடைய சிநேகிதன் என்னப்பட்டான்."
    },
    {
        "id": 24,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "In the Parable of the Prodigal Son, what did the father instruct the servants to put on his returned son?",
        "question_ta": "காணாமற்போன குமாரனின் உவமையில், திரும்பி வந்த தன் மகனுக்கு எதை அணிவிக்கும்படி தகப்பன் வேலைக்காரருக்குக் கூறினார்?",
        "options_en": [
            "A crown of gold",
            "The best robe, a ring, and sandals",
            "A shepherd's cloak",
            "New linen garments only"
        ],
        "options_ta": [
            "பொன் கிரீடம்",
            "விசேஷித்த வஸ்திரம், மோதிரம், பாதரட்சை",
            "மேய்ப்பனின் சால்வை",
            "புதிய மெல்லிய வஸ்திரம் மட்டும்"
        ],
        "correct_index": 1,
        "reference": "Luke 15:22 / லூக்கா 15:22",
        "explanation_en": "The father said: Bring forth the best robe, and put it on him; and put a ring on his hand, and shoes on his feet.",
        "explanation_ta": "தகப்பன்: நீங்கள் சீக்கிரமாய் விசேஷித்த வஸ்திரத்தைக் கொண்டுவந்து இவனுக்கு உடுத்தி, இவன் கைக்கு மோதிரத்தையும் கால்களுக்குப் பாதரட்சைகளையும் போடுங்கள் என்றார்."
    },
    {
        "id": 25,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What are the opening four words of the Holy Bible in Genesis 1:1?",
        "question_ta": "ஆதியாகமம் 1:1 இல் பரிசுத்த வேதாகமத்தின் முதல் வார்த்தைகள் என்ன?",
        "options_en": [
            "God created the world",
            "In the beginning God",
            "The earth was empty",
            "Light came into darkness"
        ],
        "options_ta": [
            "தேவன் உலகைப் படைத்தார்",
            "ஆதியிலே தேவன் வானத்தையும் பூமியையும்",
            "பூமியானது ஒழுங்கின்மையாய் இருந்தது",
            "வெளிச்சம் உண்டாயிற்று"
        ],
        "correct_index": 1,
        "reference": "Genesis 1:1 / ஆதியாகமம் 1:1",
        "explanation_en": "Genesis 1:1 begins: 'In the beginning God created the heaven and the earth.'",
        "explanation_ta": "ஆதியாகமம் 1:1 'ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்' என்று தொடங்குகிறது."
    },
    {
        "id": 26,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "What was the name of Abraham's wife and the mother of Isaac?",
        "question_ta": "ஆபிரகாமின் மனைவியும் ஈசாக்கின் தாயுமானவர் பெயர் என்ன?",
        "options_en": [
            "Rebekah",
            "Rachel",
            "Sarah",
            "Leah"
        ],
        "options_ta": [
            "ரெபேக்காள்",
            "ராகேல்",
            "சாராள்",
            "லேயாள்"
        ],
        "correct_index": 2,
        "reference": "Genesis 17:15-19 / ஆதியாகமம் 17:15-19",
        "explanation_en": "God said to Abraham, 'As for Sarai your wife, you shall not call her name Sarai, but Sarah shall her name be.'",
        "explanation_ta": "தேவன் ஆபிரகாமை நோக்கி: உன் மனைவி சாராயை சாராய் என்று அழையாதிருப்பாயாக; சாராள் என்பது அவளுக்குப் பெயராய் இருக்கும் என்றார்."
    },
    {
        "id": 27,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Which brave queen risked her life before King Ahasuerus saying, 'If I perish, I perish'?",
        "question_ta": "'நான் செத்தாலும் சாகிறேன்' என்று கூறி ராஜா அகாஸ்வேருவின் முன் சென்று யூதர்களைக் காப்பாற்றிய ராணி யார்?",
        "options_en": [
            "Vashti",
            "Esther",
            "Deborah",
            "Jezebel"
        ],
        "options_ta": [
            "வஸ்தி",
            "எஸ்தர்",
            "தெபொராள்",
            "யேசபேல்"
        ],
        "correct_index": 1,
        "reference": "Esther 4:16 / எஸ்தர் 4:16",
        "explanation_en": "Queen Esther approached the king unsummoned to deliver her people from Haman's decree.",
        "explanation_ta": "ராணி எஸ்தர் ஆமானின் கொடிய திட்டத்திலிருந்து தன் ஜனங்களைக் காப்பாற்ற தன் ஜீவனையும் துச்சமாக எண்ணி ராஜாவிடம் சென்றாள்."
    },
    {
        "id": 28,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "In Jesus' parable, who stopped to bandage the beaten traveler on the road to Jericho?",
        "question_ta": "இயேசுவின் உவமையில், எரிகோ வழியில் கள்வரால் அடிபட்டுக் கிடந்த மனிதனுக்கு இரக்கப்பட்டு உதவி செய்தவர் யார்?",
        "options_en": [
            "A Priest",
            "A Levite",
            "A Good Samaritan",
            "A Roman Soldier"
        ],
        "options_ta": [
            "ஆசாரியன்",
            "லேவியன்",
            "நல்ல சமாரியன்",
            "ரோம போர்வீரன்"
        ],
        "correct_index": 2,
        "reference": "Luke 10:33-34 / லூக்கா 10:33-34",
        "explanation_en": "A certain Samaritan came where he was, and when he saw him, he had compassion and bound up his wounds.",
        "explanation_ta": "சமாரியன் ஒருவன் பிரயாணமாய் வருகையில், அவனைக் கண்டு, மனதுருகி, அவனுடைய காயங்களில் எண்ணெய் வார்த்து கட்டினான்."
    },
    {
        "id": 29,
        "category": "gospels",
        "difficulty": "medium",
        "question_en": "Which Old Testament figures appeared talking with Jesus at the Transfiguration?",
        "question_ta": "மறுரூப மலையில் இயேசுவோடு பேசிக்கொண்டிருந்த பழைய ஏற்பாட்டு நபர்கள் யார்?",
        "options_en": [
            "Abraham and David",
            "Moses and Elijah",
            "Noah and Daniel",
            "Samuel and Isaiah"
        ],
        "options_ta": [
            "ஆபிரகாம் மற்றும் தாவீது",
            "மோசே மற்றும் எலியா",
            "நோவா மற்றும் தானியேல்",
            "சாமுவேல் மற்றும் ஏசாயா"
        ],
        "correct_index": 1,
        "reference": "Matthew 17:3 / மத்தேயு 17:3",
        "explanation_en": "Behold, there appeared unto them Moses and Elijah talking with Jesus.",
        "explanation_ta": "அப்பொழுது மோசேயும் எலியாவும் அவர்களுடனே பேசுகிறவர்களாக அவர்களுக்குக் காணப்பட்டார்கள்."
    },
    {
        "id": 30,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "Which prophet was taken up into heaven by a whirlwind in a chariot of fire?",
        "question_ta": "அக்கினி இரதத்தினாலும் அக்கினிக் குதிரைகளினாலும் சுழல்காற்றிலே பரலோகத்திற்கு எடுத்துக்கொள்ளப்பட்ட தீர்க்கதரிசி யார்?",
        "options_en": [
            "Elisha",
            "Enoch",
            "Elijah",
            "Isaiah"
        ],
        "options_ta": [
            "எலிசா",
            "ஏனோக்கு",
            "எலியா",
            "ஏசாயா"
        ],
        "correct_index": 2,
        "reference": "2 Kings 2:11 / 2 இராஜாக்கள் 2:11",
        "explanation_en": "Behold, there appeared a chariot of fire, and horses of fire... and Elijah went up by a whirlwind into heaven.",
        "explanation_ta": "இதோ, ஒரு அக்கினி ரதமும் அக்கினிக் குதிரைகளும்... எலியா சுழல்காற்றிலே பரலோகத்திற்கு ஏறிப்போனான்."
    },
    {
        "id": 31,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who was anointed by Samuel as the very first king of the nation of Israel?",
        "question_ta": "இஸ்ரவேல் தேசத்தின் முதல் ராஜாவாக சாமுவேலால் அபிஷேகம் பண்ணப்பட்டவர் யார்?",
        "options_en": [
            "David",
            "Saul",
            "Solomon",
            "Rehoboam"
        ],
        "options_ta": [
            "தாவீது",
            "சவுல்",
            "சாலொமோன்",
            "ரெகொபெயாம்"
        ],
        "correct_index": 1,
        "reference": "1 Samuel 10:1 / 1 சாமுவேல் 10:1",
        "explanation_en": "Samuel took a vial of oil, and poured it upon Saul's head, and anointed him king over Israel.",
        "explanation_ta": "சாமுவேல் தைலக்குப்பியை எடுத்து, சவுலின் தலையின்மேல் ஊற்றி, அவனை முத்தமிட்டு ராஜாவாக அபிஷேகம் பண்ணினான்."
    },
    {
        "id": 32,
        "category": "general",
        "difficulty": "easy",
        "question_en": "Which New Testament book immediately follows the four Gospels?",
        "question_ta": "நான்கு சுவிசேஷங்களுக்குப் பிறகு உடனடியாக வரும் புதிய ஏற்பாட்டு புத்தகம் எது?",
        "options_en": [
            "Romans",
            "Acts of the Apostles",
            "Hebrews",
            "Galatians"
        ],
        "options_ta": [
            "ரோமர்",
            "அப்போஸ்தலருடைய நடபடிகள்",
            "எபிரெயர்",
            "கலாத்தியர்"
        ],
        "correct_index": 1,
        "reference": "New Testament Canon (Matthew, Mark, Luke, John, Acts)",
        "explanation_en": "The Acts of the Apostles, written by Luke, follows the Gospel of John and records the early Church history.",
        "explanation_ta": "யோவான் சுவிசேஷத்திற்குப் பின் அப்போஸ்தலருடைய நடபடிகள் புத்தகம் வருகிறது."
    },
    {
        "id": 33,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "What is the famous 'Golden Rule' proclaimed by Jesus in Matthew 7:12?",
        "question_ta": "மத்தேயு 7:12 இல் இயேசு அருளிய புகழ்பெற்ற 'பொன் விதி' என்ன?",
        "options_en": [
            "An eye for an eye",
            "Do unto others as you would have them do unto you",
            "Store up treasures on earth",
            "Love only those who love you"
        ],
        "options_ta": [
            "கண்ணுக்குக் கண், பல்லுக்குப் பல்",
            "மனுஷர் உங்களுக்கு எவைகளைச் செய்ய விரும்புகிறீர்களோ, அவைகளை நீங்களும் அவர்களுக்குச் செய்யுங்கள்",
            "பூமியிலே பொக்கிஷங்களைச் சேர்த்துவையுங்கள்",
            "உங்களைச் சிநேகிக்கிறவர்களை மாத்திரம் சிநேகியுங்கள்"
        ],
        "correct_index": 1,
        "reference": "Matthew 7:12 / மத்தேயு 7:12",
        "explanation_en": "Therefore all things whatsoever ye would that men should do to you, do ye even so to them.",
        "explanation_ta": "ஆதலால், மனுஷர் உங்களுக்கு எவைகளைச் செய்ய விரும்புகிறீர்களோ, அவைகளை நீங்களும் அவர்களுக்குச் செய்யுங்கள்; இதுவே நியாயப்பிரமாணமும் தீர்க்கதரிசனங்களுமாம்."
    },
    {
        "id": 34,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "For how many pieces of silver was Joseph sold into slavery by his brothers to the Ishmeelites?",
        "question_ta": "யோசேப்பை அவனுடைய சகோதரர்கள் இஸ்மவேலருக்கு எத்தனை வெள்ளிக்காசுக்கு அடிமையாக விற்றார்கள்?",
        "options_en": [
            "10 pieces",
            "20 pieces",
            "30 pieces",
            "50 pieces"
        ],
        "options_ta": [
            "10 வெள்ளிக்காசு",
            "20 வெள்ளிக்காசு",
            "30 வெள்ளிக்காசு",
            "50 வெள்ளிக்காசு"
        ],
        "correct_index": 1,
        "reference": "Genesis 37:28 / ஆதியாகமம் 37:28",
        "explanation_en": "The brothers lifted Joseph up out of the pit and sold him to the Ishmeelites for twenty pieces of silver.",
        "explanation_ta": "யோசேப்பைக் குழியிலிருந்து தூக்கியெடுத்து, இஸ்மவேலரிடத்தில் இருபது வெள்ளிக்காசுக்கு விற்றுப்போட்டார்கள்."
    },
    {
        "id": 35,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "What words did Jesus speak to calm the raging storm in Mark 4:39?",
        "question_ta": "மாற்கு 4:39 இல் சீறிப்பாய்ந்த புயலை அமைதிப்படுத்த இயேசு என்ன வார்த்தைகளைச் சொன்னார்?",
        "options_en": [
            "Be silent forever",
            "Peace, be still",
            "Depart from me",
            "Let there be rain"
        ],
        "options_ta": [
            "என்றென்றைக்கும் அமைதியாயிரு",
            "இரையாதே, அமைதலாயிரு",
            "என்னை விட்டு அகன்று போ",
            "மழை பெய்யக்கடவது"
        ],
        "correct_index": 1,
        "reference": "Mark 4:39 / மாற்கு 4:39",
        "explanation_en": "Jesus arose, and rebuked the wind, and said unto the sea, Peace, be still. And the wind ceased, and there was a great calm.",
        "explanation_ta": "அவர் எழுந்திருந்து, காற்றை அதட்டி, கடலைப்பார்த்து: இரையாதே, அமைதலாயிரு என்றார். அப்பொழுது காற்று நின்றுபோய், மிகுந்த அமைதல் உண்டாயிற்று."
    },
    {
        "id": 36,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Which Nazarite judge was endowed with miraculous strength through the Spirit of God?",
        "question_ta": "தேவனுடைய ஆவியினால் அற்புத பலத்தைப் பெற்று நாசரேயனாய் வாழ்ந்த இஸ்ரவேலின் நியாயாதிபதி யார்?",
        "options_en": [
            "Gideon",
            "Samson",
            "Barak",
            "Jephthah"
        ],
        "options_ta": [
            "கிதியோன்",
            "சிம்சோன்",
            "பாராக்",
            "யெப்தா"
        ],
        "correct_index": 1,
        "reference": "Judges 13:24-25 / நியாயாதிபதிகள் 13:24-25",
        "explanation_en": "The child Samson grew, and the Lord blessed him. And the Spirit of the Lord began to move him.",
        "explanation_ta": "பிள்ளை சிம்சோன் வளர்ந்தான்; கர்த்தர் அவனை ஆசீர்வதித்தார். கர்த்தருடைய ஆவியானவர் அவனை ஏவத் தொடங்கினார்."
    },
    {
        "id": 37,
        "category": "general",
        "difficulty": "medium",
        "question_en": "In what primary ancient language was the Old Testament originally penned?",
        "question_ta": "பழைய ஏற்பாடு ஆரம்பத்தில் பிரதானமாக எந்த பண்டைய மொழியில் எழுதப்பட்டது?",
        "options_en": [
            "Latin",
            "Greek",
            "Hebrew",
            "Aramaic"
        ],
        "options_ta": [
            "லத்தீன்",
            "கிரேக்கம்",
            "எபிரெயம்",
            "அரமேயம்"
        ],
        "correct_index": 2,
        "reference": "Biblical Languages (Hebrew with small portions in Aramaic)",
        "explanation_en": "The Old Testament was predominantly written in Biblical Hebrew, with a few sections in Aramaic (Daniel & Ezra).",
        "explanation_ta": "பழைய ஏற்பாடு பெரும்பாலும் எபிரெய மொழியிலும், சில பகுதிகள் அரமேய மொழியிலும் எழுதப்பட்டன."
    },
    {
        "id": 38,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "Who climbed a sycamore tree in Jericho just to catch a glimpse of Jesus passing by?",
        "question_ta": "எரிகோவில் இயேசுவைக் காணும் ஆசையினால் காட்டு அத்திமரத்தில் ஏறிக்கொண்ட மனிதர் யார்?",
        "options_en": [
            "Bartimaeus",
            "Nicodemus",
            "Zacchaeus",
            "Cornelius"
        ],
        "options_ta": [
            "பர்த்திமேயு",
            "நிக்கோதேமு",
            "சகேயு",
            "கொர்நேலியு"
        ],
        "correct_index": 2,
        "reference": "Luke 19:1-4 / லூக்கா 19:1-4",
        "explanation_en": "Zacchaeus was small in stature, so he ran ahead and climbed up into a sycamore tree to see Jesus.",
        "explanation_ta": "சகேயு குள்ளமானவனாயிருந்தபடியால், இயேசுவைக் காணும்படி முன்னே ஓடி, ஒரு காட்டு அத்திமரத்தின்மேல் ஏறினான்."
    },
    {
        "id": 39,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "Which king of Israel asked God for an understanding heart and constructed the First Temple in Jerusalem?",
        "question_ta": "தேவனிடத்தில் ஞானமுள்ள இருதயத்தைக் கேட்டு, எருசலேமில் முதல் ஆலயத்தைக் கட்டிய இஸ்ரவேலின் ராஜா யார்?",
        "options_en": [
            "David",
            "Solomon",
            "Hezekiah",
            "Josiah"
        ],
        "options_ta": [
            "தாவீது",
            "சாலொமோன்",
            "எசேக்கியா",
            "யோசியா"
        ],
        "correct_index": 1,
        "reference": "1 Kings 3:9-12, 6:1 / 1 இராஜாக்கள் 3:9-12, 6:1",
        "explanation_en": "God granted Solomon wisdom and discernment beyond measure, and Solomon built the house of the Lord.",
        "explanation_ta": "தேவன் சாலொமோனுக்கு அளவற்ற ஞானத்தையும் புத்தியையும் தந்தார்; சாலொமோன் கர்த்தரின் ஆலயத்தைக் கட்டினான்."
    },
    {
        "id": 40,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who was struck blind on the road to Damascus before becoming the apostle Paul?",
        "question_ta": "தமஸ்கு வழியில் பிரகாசமான ஒளியினால் குருடாகி, பின்னர் பவுல் அப்போஸ்தலனாக மாறியவர் யார்?",
        "options_en": [
            "Barnabas",
            "Silas",
            "Saul of Tarsus",
            "Apollos"
        ],
        "options_ta": [
            "பர்னபா",
            "சீலா",
            "தர்சு பட்டணத்து சவுல்",
            "அப்பொல்லோ"
        ],
        "correct_index": 2,
        "reference": "Acts 9:3-6 / அப்போஸ்தலர் 9:3-6",
        "explanation_en": "As Saul neared Damascus, suddenly a light from heaven flashed around him, and he heard the voice of Jesus.",
        "explanation_ta": "சவுல் தமஸ்குவுக்குச் சமீபத்தபோது, வானத்திலிருந்து ஒரு ஒளி அவனைச் சுற்றிப் பிரகாசித்தது; இயேசு அவனோடு பேசினார்."
    },
    {
        "id": 41,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "When Jesus walked on the Sea of Galilee, which disciple stepped out of the boat to walk to Him?",
        "question_ta": "இயேசு கலிலேயாக் கடலின் மேல் நடந்தபோது, படவிலிருந்து இறங்கி இயேசுவை நோக்கி தண்ணீரின் மேல் நடந்த சீடர் யார்?",
        "options_en": [
            "John",
            "Peter",
            "Thomas",
            "Andrew"
        ],
        "options_ta": [
            "யோவான்",
            "பேதுரு",
            "தோமா",
            "அந்திரேயா"
        ],
        "correct_index": 1,
        "reference": "Matthew 14:28-29 / மத்தேயு 14:28-29",
        "explanation_en": "Peter walked on the water to go to Jesus, but when he saw the wind boisterous, he was afraid and began to sink.",
        "explanation_ta": "பேதுரு படவை விட்டு இறங்கி, இயேசுவினிடத்தில் போகத் தண்ணீரின்மேல் நடந்தான்."
    },
    {
        "id": 42,
        "category": "general",
        "difficulty": "medium",
        "question_en": "Which Epistle contains the world-renowned 'Love Chapter' declaring: 'Love is patient, love is kind'?",
        "question_ta": "'அன்பு நீடிய சாந்தமும் தயவுமுள்ளது' என்று அன்பைக் குறித்து விவரிக்கும் 13-ம் அதிகாரம் எந்த நிருபத்தில் உள்ளது?",
        "options_en": [
            "Romans",
            "1 Corinthians",
            "Ephesians",
            "Philippians"
        ],
        "options_ta": [
            "ரோமர்",
            "1 கொரிந்தியர்",
            "எபேசியர்",
            "பிலிப்பியர்"
        ],
        "correct_index": 1,
        "reference": "1 Corinthians 13:4 / 1 கொரிந்தியர் 13:4",
        "explanation_en": "1 Corinthians 13 describes the supremacy of Christian agape love over all spiritual gifts.",
        "explanation_ta": "1 கொரிந்தியர் 13-ம் அதிகாரம் கிறிஸ்தவ அன்பின் மேன்மையை மிக அழகாக விவரிக்கிறது."
    },
    {
        "id": 43,
        "category": "gospels",
        "difficulty": "hard",
        "question_en": "Who was compelled by Roman soldiers to carry Jesus' cross on the path to Golgotha?",
        "question_ta": "கொல்கொதாவுக்குப் போகும் வழியில் இயேசுவின் சிலுவையைச் சுமக்கும்படி ரோம வீரர்களால் பலவந்தம் பண்ணப்பட்டவர் யார்?",
        "options_en": [
            "Joseph of Arimathaea",
            "Nicodemus",
            "Simon of Cyrene",
            "Barabbas"
        ],
        "options_ta": [
            "அரிமத்தியா ஊரானாகிய யோசேப்பு",
            "நிக்கோதேமு",
            "சீரேனே ஊரானாகிய சீமோன்",
            "பரபாஸ்"
        ],
        "correct_index": 2,
        "reference": "Matthew 27:32 / மத்தேயு 27:32",
        "explanation_en": "As they came out, they found a man of Cyrene, Simon by name: him they compelled to bear his cross.",
        "explanation_ta": "அவர்கள் புறப்பட்டுப் போகையில், சீரேனே ஊரானாகிய சீமோன் என்னும் பேருள்ள ஒரு மனுஷனைக் கண்டு, அவருடைய சிலுவையைச் சுமக்கும்படி அவனைப் பலவந்தம்பண்ணினார்கள்."
    },
    {
        "id": 44,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "What visual sign did God establish in the sky as an everlasting covenant with Noah and every living creature?",
        "question_ta": "இனி பூமியின்மேல் சகல ஜீவன்களையும் அழிக்கிற ஜலப்பிரளயம் உண்டாவதில்லை என்பதற்கு அடையாளமாக தேவன் ஆகாயத்தில் வைத்தது எது?",
        "options_en": [
            "A pillar of cloud",
            "The rainbow",
            "A burning bush",
            "A comet"
        ],
        "options_ta": [
            "மேக ஸ்தம்பம்",
            "வானவில்",
            "முட்செடி",
            "வால் நட்சத்திரம்"
        ],
        "correct_index": 1,
        "reference": "Genesis 9:13 / ஆதியாகமம் 9:13",
        "explanation_en": "I do set my bow in the cloud, and it shall be for a token of a covenant between me and the earth.",
        "explanation_ta": "என் வில்லை மேகத்தில் வைக்கிறேன்; அது எனக்கும் பூமிக்கும் நடுவே உடன்படிக்கைக்கு அடையாளமாயிருக்கும்."
    },
    {
        "id": 45,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Which faithful woman pledged to Naomi: 'Whither thou goest, I will go... thy people shall be my people, and thy God my God'?",
        "question_ta": "'நீர் போகும் இடத்திற்கு நானும் வருவேன்... உம்முடைய ஜனம் என் ஜனம், உம்முடைய தேவன் என் தேவன்' என்று நகோமியிடம் உறுதியாய் நின்ற பெண் யார்?",
        "options_en": [
            "Orpah",
            "Ruth",
            "Hannah",
            "Abigail"
        ],
        "options_ta": [
            "ஒர்பாள்",
            "ரூத்",
            "அன்னாள்",
            "அபிகாயில்"
        ],
        "correct_index": 1,
        "reference": "Ruth 1:16 / ரூத் 1:16",
        "explanation_en": "Ruth declared loyalty to Naomi and the God of Israel, and she became an ancestor of King David and Jesus Christ.",
        "explanation_ta": "ரூத் நகோமியைப் பற்றிக்கொண்டு இஸ்ரவேலின் தேவனைப் பின்பற்றினாள்; அவள் தாவீது ராஜா மற்றும் இயேசு கிறிஸ்துவின் வம்சாவளியில் இடம்பெற்றாள்."
    },
    {
        "id": 46,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "In the Parable of the Sower, what does Jesus explain that the 'seed' represents?",
        "question_ta": "விதைக்கிறவனின் உவமையில், 'விதை' எதைக் குறிக்கிறது என்று இயேசு விளக்கினார்?",
        "options_en": [
            "Worldly wealth",
            "The Word of God",
            "Human wisdom",
            "Good intentions"
        ],
        "options_ta": [
            "உலக ஐசுவரியம்",
            "தேவனுடைய வசனம்",
            "மனித ஞானம்",
            "நல்ல நோக்கங்கள்"
        ],
        "correct_index": 1,
        "reference": "Luke 8:11 / லூக்கா 8:11",
        "explanation_en": "Now the parable is this: The seed is the word of God.",
        "explanation_ta": "அந்த உவமையின் கருத்தாவது: விதை தேவனுடைய வசனம்."
    },
    {
        "id": 47,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What is the very final word in the Holy Scriptures in Revelation 22:21?",
        "question_ta": "வெளிப்படுத்தின விசேஷம் 22:21 இல் பரிசுத்த வேதாகமத்தின் மிகக் கடைசி வார்த்தை என்ன?",
        "options_en": [
            "Hallelujah",
            "Amen",
            "Peace",
            "Glory"
        ],
        "options_ta": [
            "அல்லேலூயா",
            "ஆமென்",
            "சமாதானம்",
            "மகிமை"
        ],
        "correct_index": 1,
        "reference": "Revelation 22:21 / வெளிப்படுத்தின விசேஷம் 22:21",
        "explanation_en": "The grace of our Lord Jesus Christ be with you all. Amen.",
        "explanation_ta": "நம்முடைய கர்த்தராகிய இயேசுகிறிஸ்துவின் கிருபை உங்கள் அனைவரோடுங்கூட இருப்பதாக. ஆமென்."
    },
    {
        "id": 48,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "To whom did the resurrected Jesus first appear on the first Easter Sunday morning?",
        "question_ta": "உயிர்த்தெழுந்த இயேசு கிறிஸ்து முதல் ஈஸ்டர் ஞாயிறு காலையில் முதலில் யாருக்குக் காட்சியளித்தார்?",
        "options_en": [
            "Simon Peter",
            "Mary Magdalene",
            "John the Beloved",
            "Cleopas"
        ],
        "options_ta": [
            "சீமோன் பேதுரு",
            "மகதலேனா மரியாள்",
            "அன்பான சீடனாகிய யோவான்",
            "கிலெயோப்பா"
        ],
        "correct_index": 1,
        "reference": "Mark 16:9 / மாற்கு 16:9",
        "explanation_en": "Now when Jesus was risen early the first day of the week, he appeared first to Mary Magdalene.",
        "explanation_ta": "வாரத்தின் முதலாம் நாள் அதிகாலையிலே இயேசு உயிர்த்தெழுந்தபின்பு, மகதலேனா மரியாளுக்கு முதன்முதலாகத் தரிசனமானார்."
    },
    {
        "id": 49,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who became the first recorded Christian martyr, crying out for his executioners' forgiveness as he was stoned?",
        "question_ta": "தன்னைக் கல்லெறிந்தவர்களுக்காக மன்னிப்புக் கேட்டு ஜெபித்து மரித்த முதல் கிறிஸ்தவ இரத்தசாட்சி யார்?",
        "options_en": [
            "James the son of Zebedee",
            "Stephen",
            "Philip",
            "Barnabas"
        ],
        "options_ta": [
            "செபதேயுவின் மகன் யாக்கோபு",
            "ஸ்தேவான்",
            "பிலிப்பு",
            "பர்னபா"
        ],
        "correct_index": 1,
        "reference": "Acts 7:59-60 / அப்போஸ்தலர் 7:59-60",
        "explanation_en": "Stephen kneeled down, and cried with a loud voice, Lord, lay not this sin to their charge. And when he had said this, he fell asleep.",
        "explanation_ta": "ஸ்தேவான் முழங்கால்படியிட்டு: ஆண்டவரே, இவர்கள்மேல் இந்தப் பாவத்தைச் சுமத்தாதிரும் என்று உரத்த சத்தமாய்க் கூப்பிட்டு ஜீவனை விட்டான்."
    },
    {
        "id": 50,
        "category": "old_testament",
        "difficulty": "hard",
        "question_en": "What were the original Hebrew names of Shadrach, Meshach, and Abednego in Daniel 1:6-7?",
        "question_ta": "தானியேல் 1:6-7 இல் சாத்ராக், மேஷாக், ஆபேத்நேகோ ஆகியோரின் அசல் எபிரெய பெயர்கள் என்ன?",
        "options_en": [
            "Eliezer, Gershom, and Hur",
            "Hananiah, Mishael, and Azariah",
            "Eliab, Abinadab, and Shammah",
            "Nadab, Abihu, and Eleazar"
        ],
        "options_ta": [
            "எலியேசர், கெர்சோம், ஊர்",
            "அனனியா, மீஷாவேல், அசரியா",
            "எலியாப், அபினதாப், சம்மா",
            "நாதாப், அபியூ, எலெயாசார்"
        ],
        "correct_index": 1,
        "reference": "Daniel 1:6-7 / தானியேல் 1:6-7",
        "explanation_en": "Among these were of the children of Judah, Daniel, Hananiah, Mishael, and Azariah, whom the prince of the eunuchs renamed.",
        "explanation_ta": "யூதா புத்திரரில் தானியேல், அனனியா, மீஷாவேல், அசரியா என்பவர்கள் இருந்தார்கள்; பிரதானி அவர்களுக்கு சாத்ராக், மேஷாக், ஆபேத்நேகோ என்று மறுபேரிட்டான்."
    },
    {
        "id": 51,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "What gifts did the wise men (Magi) present to the young child Jesus in Bethlehem?",
        "question_ta": "சாஸ்திரிகள் (ஞானிகள்) பெத்லகேமில் பாலன் இயேசுவுக்கு என்னென்ன காணிக்கைகளைப் படைத்தார்கள்?",
        "options_en": [
            "Silver, frankincense, and silk",
            "Gold, frankincense, and myrrh",
            "Gold, olive oil, and pearls",
            "Bread, wine, and honey"
        ],
        "options_ta": [
            "வெள்ளி, தூபவர்க்கம், பட்டு",
            "பொன், தூபவர்க்கம், வெள்ளைப்போளம்",
            "பொன், ஒலிவ எண்ணெய், முத்துக்கள்",
            "அப்பம், திராட்சரசம், தேன்"
        ],
        "correct_index": 1,
        "reference": "Matthew 2:11 / மத்தேயு 2:11",
        "explanation_en": "They opened their treasures and presented unto him gifts: gold, frankincense, and myrrh.",
        "explanation_ta": "அவர்கள் தங்கள் பொக்கிஷங்களைத் திறந்து, பொன்னையும் தூபவர்க்கத்தையும் வெள்ளைப்போளத்தையும் அவருக்குக் காணிக்கையாக வைத்தார்கள்."
    },
    {
        "id": 52,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "In which river was Jesus baptized by John the Baptist?",
        "question_ta": "இயேசு கிறிஸ்து யோவான் ஸ்நானகனால் எந்த நதியில் ஞானஸ்நானம் பெற்றார்?",
        "options_en": [
            "Nile River",
            "Euphrates River",
            "Jordan River",
            "Tigris River"
        ],
        "options_ta": [
            "நைல் நதி",
            "யூப்ரடீஸ் நதி",
            "யோர்தான் நதி",
            "டைகிரிஸ் நதி"
        ],
        "correct_index": 2,
        "reference": "Matthew 3:13 / மத்தேயு 3:13",
        "explanation_en": "Then cometh Jesus from Galilee to Jordan unto John, to be baptized of him.",
        "explanation_ta": "அப்பொழுது இயேசு யோவானால் ஞானஸ்நானம் பெறுவதற்கு கலிலேயாவை விட்டு யோர்தானுக்கு வந்தார்."
    },
    {
        "id": 53,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "How many days and nights did Jesus fast in the wilderness before being tempted by the devil?",
        "question_ta": "பிசாசினால் சோதிக்கப்படுவதற்கு முன்பு இயேசு வனாந்தரத்தில் எத்தனை நாட்கள் உபவாசம் இருந்தார்?",
        "options_en": [
            "7 days and 7 nights",
            "12 days and 12 nights",
            "40 days and 40 nights",
            "50 days and 50 nights"
        ],
        "options_ta": [
            "7 இரவும் 7 பகலும்",
            "12 இரவும் 12 பகலும்",
            "40 இரவும் 40 பகலும்",
            "50 இரவும் 50 பகலும்"
        ],
        "correct_index": 2,
        "reference": "Matthew 4:2 / மத்தேயு 4:2",
        "explanation_en": "And when he had fasted forty days and forty nights, he was afterward an hungred.",
        "explanation_ta": "அவர் இரவும் பகலும் நாற்பது நாள் உபவாசமாயிருந்தபின்பு, அவருக்குப் பசியுண்டாயிற்று."
    },
    {
        "id": 54,
        "category": "gospels",
        "difficulty": "medium",
        "question_en": "Which two Old Testament figures appeared talking with Jesus on the Mount of Transfiguration?",
        "question_ta": "மறுரூப மலையில் இயேசுவோடு பேசிக்கொண்டிருந்த இரண்டு பழைய ஏற்பாட்டு நபர்கள் யார்?",
        "options_en": [
            "Abraham and David",
            "Moses and Elijah",
            "Noah and Daniel",
            "Enoch and Samuel"
        ],
        "options_ta": [
            "ஆபிரகாமும் தாவீதும்",
            "மோசேயும் எலியாவும்",
            "நோவாவும் தானியேலும்",
            "ஏனோக்கும் சாமுவேலும்"
        ],
        "correct_index": 1,
        "reference": "Matthew 17:3 / மத்தேயு 17:3",
        "explanation_en": "And, behold, there appeared unto them Moses and Elias talking with him.",
        "explanation_ta": "அப்பொழுது மோசேயும் எலியாவும் அவரோடே பேசுகிறவர்களாக அவர்களுக்குக் காணப்பட்டார்கள்."
    },
    {
        "id": 55,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "Which Roman governor washed his hands and sentenced Jesus to be crucified despite finding no fault in Him?",
        "question_ta": "இயேசுவிடம் எந்தக் குற்றமும் காணவில்லை என்று கூறி தன் கைகளைக் கழுவி, அவரைச் சிலுவையில் அறையத் தீர்ப்பளித்த ரோம ஆளுநர் யார்?",
        "options_en": [
            "Julius Caesar",
            "Pontius Pilate",
            "Herod Antipas",
            "Felix"
        ],
        "options_ta": [
            "ஜூலியஸ் சீசர்",
            "பொந்தியு பிலாத்து",
            "ஏரோது அந்திபா",
            "பேலிக்ஸ்"
        ],
        "correct_index": 1,
        "reference": "Matthew 27:24 / மத்தேயு 27:24",
        "explanation_en": "Pilate took water, and washed his hands before the multitude, saying, I am innocent of the blood of this just person.",
        "explanation_ta": "பிலாத்து தண்ணீரை அள்ளி, ஜனங்களுக்கு முன்பாகக் கைகளைக் கழுவி: இந்த நீதிமானுடைய இரத்தப்பழிக்கு நான் குற்றமற்றவன் என்றான்."
    },
    {
        "id": 56,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "For how many pieces of silver did Judas Iscariot agree to betray Jesus?",
        "question_ta": "யூதாஸ் காரியோத்து எத்தனை வெள்ளிக்காசுகளுக்காக இயேசுவைக் காட்டிக்கொடுக்க உடன்பட்டான்?",
        "options_en": [
            "20 pieces of silver",
            "30 pieces of silver",
            "50 pieces of silver",
            "100 pieces of silver"
        ],
        "options_ta": [
            "20 வெள்ளிக்காசு",
            "30 வெள்ளிக்காசு",
            "50 வெள்ளிக்காசு",
            "100 வெள்ளிக்காசு"
        ],
        "correct_index": 1,
        "reference": "Matthew 26:15 / மத்தேயு 26:15",
        "explanation_en": "And they covenanted with him for thirty pieces of silver.",
        "explanation_ta": "அவர்கள் அவனுக்கு முப்பது வெள்ளிக்காசை நிறுத்திக் கொடுத்தார்கள்."
    },
    {
        "id": 57,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "Which disciple denied knowing Jesus three times before the rooster crowed?",
        "question_ta": "சேவல் கூவுவதற்கு முன்னே இயேசுவை அறியேன் என்று மூன்று முறை மறுதலித்த சீடர் யார்?",
        "options_en": [
            "Andrew",
            "Thomas",
            "Simon Peter",
            "John"
        ],
        "options_ta": [
            "அந்திரேயா",
            "தோமா",
            "சீமோன் பேதுரு",
            "யோவான்"
        ],
        "correct_index": 2,
        "reference": "Matthew 26:74-75 / மத்தேயு 26:74-75",
        "explanation_en": "Immediately the cock crew. And Peter remembered the word of Jesus, which said, Before the cock crow, thou shalt deny me thrice.",
        "explanation_ta": "உடனே சேவல் கூவிற்று. சேவல் கூவுகிறதற்கு முன்னே, நீ என்னை மூன்று தரம் மறுதலிப்பாய் என்று இயேசு சொன்ன வார்த்தையை பேதுரு நினைவுகூர்ந்தான்."
    },
    {
        "id": 58,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "In which garden did Jesus pray with deep agony before being arrested?",
        "question_ta": "இயேசு கிறிஸ்து கைது செய்யப்படுவதற்கு முன்பு மிகுந்த வேதனையோடு ஜெபித்த தோட்டம் எது?",
        "options_en": [
            "Garden of Eden",
            "Garden of Gethsemane",
            "Garden of Babylon",
            "Garden of Siloam"
        ],
        "options_ta": [
            "ஏதேன் தோட்டம்",
            "கெத்செமனே தோட்டம்",
            "பாபிலோன் தோட்டம்",
            "சீலோவாம் தோட்டம்"
        ],
        "correct_index": 1,
        "reference": "Matthew 26:36 / மத்தேயு 26:36",
        "explanation_en": "Then cometh Jesus with them unto a place called Gethsemane, and saith unto the disciples, Sit ye here, while I go and pray yonder.",
        "explanation_ta": "அப்பொழுது இயேசு அவர்களுடனே கெத்செமனே என்னப்பட்ட இடத்திற்கு வந்து: நான் அங்கே போய் ஜெபம்பண்ணுமளவும் நீங்கள் இங்கே உட்கார்ந்திருங்கள் என்றார்."
    },
    {
        "id": 59,
        "category": "gospels",
        "difficulty": "medium",
        "question_en": "Who was compelled by Roman soldiers to carry the cross behind Jesus to Golgotha?",
        "question_ta": "கொல்கொதாவுக்குச் செல்லும் வழியில் இயேசுவின் சிலுவையைச் சுமக்கும்படி ரோம வீரர்களால் கட்டாயப்படுத்தப்பட்டவர் யார்?",
        "options_en": [
            "Joseph of Arimathea",
            "Nicodemus",
            "Simon of Cyrene",
            "Zacchaeus"
        ],
        "options_ta": [
            "அரிமத்தியா ஊரானாகிய யோசேப்பு",
            "நிக்கோதேமு",
            "சிரேனே ஊரானாகிய சீமோன்",
            "சகேயு"
        ],
        "correct_index": 2,
        "reference": "Luke 23:26 / லூக்கா 23:26",
        "explanation_en": "They laid hold upon one Simon, a Cyrenian, coming out of the country, and on him they laid the cross, that he might bear it after Jesus.",
        "explanation_ta": "நாட்டிலிருந்து வருகிற சிரேனே ஊரானாகிய சீமோன் என்பவனைப் பிடித்து, சிலுவையை இயேசுவுக்குப் பின்னே சுமந்துகொண்டு வரும்படி அதை அவன்மேல் வைத்தார்கள்."
    },
    {
        "id": 60,
        "category": "gospels",
        "difficulty": "easy",
        "question_en": "What victorious word did Jesus declare on the cross right before giving up His spirit in John 19:30?",
        "question_ta": "யோவான் 19:30 இல் இயேசு தமது ஜீவனை விடுவதற்கு சற்று முன்பு சிலுவையில் முழங்கிய வெற்றி வார்த்தை என்ன?",
        "options_en": [
            "Forgive them",
            "It is finished",
            "I am rising",
            "Remember me"
        ],
        "options_ta": [
            "மன்னியும்",
            "முடிந்தது",
            "நான் உயிர்த்தெழுகிறேன்",
            "என்னை நினைவுகூரும்"
        ],
        "correct_index": 1,
        "reference": "John 19:30 / யோவான் 19:30",
        "explanation_en": "When Jesus therefore had received the vinegar, he said, It is finished: and he bowed his head, and gave up the ghost.",
        "explanation_ta": "இயேசு காடியை வாங்கினபின்பு, முடிந்தது என்று சொல்லி, தலையைச் சாய்த்து, ஆவியை ஒப்புக்கொடுத்தார்."
    },
    {
        "id": 61,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "In the Parable of the Good Samaritan, which two religious men passed by the beaten traveler without helping?",
        "question_ta": "நல்ல சமாரியன் உவமையில் காயம்பட்டுக் கிடந்த மனிதனைக் கண்டும் உதவாமல் கடந்து சென்ற இருவர் யார்?",
        "options_en": [
            "A Pharisee and a Sadducee",
            "A priest and a Levite",
            "A scribe and an elder",
            "A centurion and a soldier"
        ],
        "options_ta": [
            "பரிசேயனும் சதுசேயனும்",
            "ஆசாரியனும் லேவியனும்",
            "வேதபாரகனும் மூப்பனும்",
            "நூற்றுக்கு அதிபதியும் சேவகனும்"
        ],
        "correct_index": 1,
        "reference": "Luke 10:31-32 / லூக்கா 10:31-32",
        "explanation_en": "By chance there came down a certain priest that way... And likewise a Levite, when he was at the place, came and looked on him, and passed by on the other side.",
        "explanation_ta": "அப்பொழுது தற்செயலாய் ஒரு ஆசாரியன் அந்த வழியே வந்து... அப்படியே ஒரு லேவியனும் அந்த இடத்துக்கு வந்து பார்த்து, பக்கமாய் விலகிப்போனான்."
    },
    {
        "id": 62,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "How many loaves of barley bread and small fish did Jesus multiply to feed 5,000 men?",
        "question_ta": "5,000 பேருக்கு உணவளிக்க இயேசு ஆசீர்வதித்துப் பெருகப்பண்ணிய அப்பங்கள் மற்றும் மீன்களின் எண்ணிக்கை என்ன?",
        "options_en": [
            "7 loaves and 3 fish",
            "5 loaves and 2 fish",
            "12 loaves and 5 fish",
            "3 loaves and 2 fish"
        ],
        "options_ta": [
            "7 அப்பங்களும் 3 மீன்களும்",
            "5 அப்பங்களும் 2 மீன்களும்",
            "12 அப்பங்களும் 5 மீன்களும்",
            "3 அப்பங்களும் 2 மீன்களும்"
        ],
        "correct_index": 1,
        "reference": "Matthew 14:17-19 / மத்தேயு 14:17-19",
        "explanation_en": "They say unto him, We have here but five loaves, and two fishes... and he blessed, and brake, and gave the loaves to his disciples.",
        "explanation_ta": "அவர்கள் அவரிடத்தில்: இங்கே எங்களிடத்தில் ஐந்து அப்பமும் இரண்டு மீன்களுமேயன்றி வேறொன்றும் இல்லை என்றார்கள்... அவர் அப்பங்களை ஆசீர்வதித்து, பிட்டு சீஷர்களிடத்தில் கொடுத்தார்."
    },
    {
        "id": 63,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "In the Parable of the Prodigal Son, what did the loving father put on his repentant son upon his return?",
        "question_ta": "காணாமற்போன மகன் உவமையில், மனந்திரும்பி வந்த மகனுக்கு அன்பான தந்தை எவற்றைக் கொடுத்து அலங்கரித்தார்?",
        "options_en": [
            "Sackcloth and ashes",
            "The best robe, a ring, and sandals",
            "A crown of gold and jewels",
            "A sword and a staff"
        ],
        "options_ta": [
            "இரட்டும் சாம்பலும்",
            "விசேஷித்த வஸ்திரம், மோதிரம், பாதரட்சை",
            "பொன் கிரீடமும் ஆபரணங்களும்",
            "பட்டயமும் கோலும்"
        ],
        "correct_index": 1,
        "reference": "Luke 15:22 / லூக்கா 15:22",
        "explanation_en": "Bring forth the best robe, and put it on him; and put a ring on his hand, and shoes on his feet.",
        "explanation_ta": "நீங்கள் சீக்கிரமாய் விசேஷித்த வஸ்திரத்தைக் கொண்டுவந்து, இவனுக்கு உடுத்தி, இவன் கைக்கு மோதிரத்தையும் கால்களுக்குப் பாதரட்சைகளையும் போடுங்கள்."
    },
    {
        "id": 64,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "When Jesus cleansed ten lepers, how many returned to give glory to God and thank Him?",
        "question_ta": "இயேசு பத்து குஷ்டரோகிகளைச் சுகமாக்கியபோது, திரும்பிவந்து தேவனை மகிமைப்படுத்தி நன்றி கூறியவர்கள் எத்தனை பேர்?",
        "options_en": [
            "All 10",
            "5 of them",
            "Only 1",
            "None of them"
        ],
        "options_ta": [
            "10 பேரும்",
            "5 பேர்",
            "ஒருவன் மாத்திரம்",
            "ஒருவருமில்லை"
        ],
        "correct_index": 2,
        "reference": "Luke 17:15-17 / லூக்கா 17:15-17",
        "explanation_en": "And one of them, when he saw that he was healed, turned back, and with a loud voice glorified God... And Jesus answering said, Were there not ten cleansed? but where are the nine?",
        "explanation_ta": "அவர்களில் ஒருவன் தான் ஆரோக்கியமானதைக் கண்டு, திரும்பிவந்து, உரத்த சத்தத்தோடே தேவனை மகிமைப்படுத்தி... இயேசு: சுத்தமானவர்கள் பத்துப்பேர் அல்லவா? மற்ற ஒன்பதுபேர் எங்கே? என்றார்."
    },
    {
        "id": 65,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "Whom did Jesus raise from the dead after he had been in the tomb for four days in Bethany?",
        "question_ta": "பெத்தானியாவில் கல்லறையில் அடக்கம் பண்ணப்பட்டு நான்கு நாட்கள் கழித்து இயேசுவினால் உயிரோடு எழுப்பப்பட்டவர் யார்?",
        "options_en": [
            "Jairus' daughter",
            "The widow's son at Nain",
            "Lazarus",
            "Nicodemus"
        ],
        "options_ta": [
            "யவீருவின் மகள்",
            "நாயீன் ஊர் கைம்பெண்ணின் மகன்",
            "லாசரு",
            "நிக்கோதேமு"
        ],
        "correct_index": 2,
        "reference": "John 11:43-44 / யோவான் 11:43-44",
        "explanation_en": "He cried with a loud voice, Lazarus, come forth. And he that was dead came forth, bound hand and foot with graveclothes.",
        "explanation_ta": "லாசருவே, வெளியே வா என்று உரத்த சத்தமாய்க் கூப்பிட்டார். அப்பொழுது, மரித்தவன் வெளியே வந்தான்."
    },
    {
        "id": 66,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "In the Parable of the Ten Virgins, what crucial item did the five foolish virgins fail to take with them?",
        "question_ta": "பத்து கன்னிகைகள் உவமையில், புத்தியில்லாத ஐந்து கன்னிகைகள் தங்களோடு எடுத்துச் செல்லத் தவறியது எது?",
        "options_en": [
            "Extra clothing",
            "Water bottles",
            "Extra oil with their lamps",
            "Matches and wicks"
        ],
        "options_ta": [
            "கூடுதல் ஆடைகள்",
            "தண்ணீர் பாத்திரங்கள்",
            "தங்கள் தீவட்டிகளுடன் எண்ணெய்",
            "தீக்குச்சிகளும் திரிகளும்"
        ],
        "correct_index": 2,
        "reference": "Matthew 25:3-4 / மத்தேயு 25:3-4",
        "explanation_en": "They that were foolish took their lamps, and took no oil with them: But the wise took oil in their vessels with their lamps.",
        "explanation_ta": "புத்தியில்லாதவர்கள் தங்கள் தீவட்டிகளை எடுத்துக்கொண்டுபோனார்கள், எண்ணெயையோ கூடக் கொண்டுபோகவில்லை. புத்தியுள்ளவர்கள் தங்கள் பாத்திரங்களில் எண்ணெயை எடுத்துக்கொண்டுபோனார்கள்."
    },
    {
        "id": 67,
        "category": "miracles_parables",
        "difficulty": "medium",
        "question_en": "Whose servant was healed from afar when he told Jesus, 'Speak the word only, and my servant shall be healed'?",
        "question_ta": "'ஒரு வார்த்தை மாத்திரம் சொல்லும், அப்பொழுது என் வேலைக்காரன் சொஸ்தமாவான்' என்று விசுவாசத்தோடு இயேசுவிடம் கூறியவர் யார்?",
        "options_en": [
            "The Roman Centurion",
            "Jairus the synagogue ruler",
            "The nobleman of Capernaum",
            "Zacchaeus the chief tax collector"
        ],
        "options_ta": [
            "ரோம நூற்றுக்கு அதிபதி",
            "ஜெப ஆலயத் தலைவனாகிய யவீரு",
            "கப்பர்நகூமின் அரச அலுவலர்",
            "வரிதண்டுவோரின் தலைவன் சகேயு"
        ],
        "correct_index": 0,
        "reference": "Matthew 8:8-10 / மத்தேயு 8:8-10",
        "explanation_en": "The centurion answered and said, Lord... speak the word only, and my servant shall be healed. When Jesus heard it, he marvelled, and said... I have not found so great faith, no, not in Israel.",
        "explanation_ta": "நூற்றுக்கு அதிபதி பிரதியுத்தரமாக: ஆண்டவரே... ஒரு வார்த்தைமாத்திரம் சொல்லும், அப்பொழுது என் வேலைக்காரன் சொஸ்தமாவான் என்றான். இயேசு இதைக் கேட்டு ஆச்சரியப்பட்டு... இஸ்ரவேலருக்குள்ளும் நான் இப்படிப்பட்ட விசுவாசத்தைக் காணவில்லை என்றார்."
    },
    {
        "id": 68,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "What did Jesus say to the violent storm on the Sea of Galilee that immediately produced a great calm?",
        "question_ta": "கலிலேயா கடலில் வீசிய பெருங்காற்றையும் கொந்தளிப்பையும் உடனே அடங்கப்பண்ண இயேசு என்ன கட்டளையிட்டார்?",
        "options_en": [
            "Depart from us",
            "Peace, be still",
            "Hear the voice of God",
            "Let there be light"
        ],
        "options_ta": [
            "எங்களை விட்டு விலகிப்போ",
            "அமைதியாயிரு, இரையாதே",
            "தேவனின் குரலைக் கேள்",
            "வெளிச்சம் உண்டாகக்கடவது"
        ],
        "correct_index": 1,
        "reference": "Mark 4:39 / மாற்கு 4:39",
        "explanation_en": "And he arose, and rebuked the wind, and said unto the sea, Peace, be still. And the wind ceased, and there was a great calm.",
        "explanation_ta": "அவர் எழுந்து, காற்றை அதட்டி, கடலைப் பார்த்து: இரையாதே, அமைதலாயிரு என்றார். அப்பொழுது காற்று நின்றுபோய், மிகுந்த அமைதல் உண்டாயிற்று."
    },
    {
        "id": 69,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "Jesus taught that faith as tiny as what seed could command a mountain to move?",
        "question_ta": "எந்த விதையளவான விசுவாசம் இருந்தால் இந்த மலையைப் பார்த்து இடம் பெயர்ந்து போ என்று சொல்ல அது பெயர்ந்து போகும் என்று இயேசு கற்பித்தார்?",
        "options_en": [
            "Wheat grain",
            "Mustard seed",
            "Pomegranate seed",
            "Olive seed"
        ],
        "options_ta": [
            "கோதுமை மணி",
            "கடுகு விதை",
            "மாதளை விதை",
            "ஒலிவ விதை"
        ],
        "correct_index": 1,
        "reference": "Matthew 17:20 / மத்தேயு 17:20",
        "explanation_en": "If ye have faith as a grain of mustard seed, ye shall say unto this mountain, Remove hence to yonder place; and it shall remove.",
        "explanation_ta": "கடுகுவிதையளவு விசுவாசம் உங்களுக்கு இருந்தால், நீங்கள் இந்த மலையைப் பார்த்து, இவ்விடம் விட்டு அப்புறம்போ என்று சொல்ல அது அப்புறம் போம்."
    },
    {
        "id": 70,
        "category": "miracles_parables",
        "difficulty": "easy",
        "question_en": "In the Parable of the Lost Sheep, how many sheep did the shepherd leave behind to search for the one that went astray?",
        "question_ta": "காணாமற்போன ஆட்டின் உவமையில், வழிதப்பிப்போன ஓர் ஆட்டைத் தேட மேய்ப்பன் வனாந்தரத்தில் விட்டுச்சென்ற ஆடுகள் எத்தனை?",
        "options_en": [
            "10 sheep",
            "50 sheep",
            "99 sheep",
            "100 sheep"
        ],
        "options_ta": [
            "10 ஆடுகள்",
            "50 ஆடுகள்",
            "99 ஆடுகள்",
            "100 ஆடுகள்"
        ],
        "correct_index": 2,
        "reference": "Luke 15:4 / லூக்கா 15:4",
        "explanation_en": "What man of you, having an hundred sheep, if he lose one of them, doth not leave the ninety and nine in the wilderness, and go after that which is lost, until he find it?",
        "explanation_ta": "உங்களில் எந்த மனுஷனாவது நூறு ஆடுகளை உடையவனாயிருந்து, அவைகளில் ஒன்று காணாமற்போனால், தொண்ணூற்றொன்பது ஆடுகளையும் வனாந்தரத்திலே விட்டு, காணாமற்போன ஆட்டைக் கண்டுபிடிக்குமளவும் தேடாமலிருப்பானோ?"
    },
    {
        "id": 71,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "What was the very first thing God called into existence on Day 1 of Creation in Genesis 1:3?",
        "question_ta": "ஆதியாகமம் 1:3 இல் சிருஷ்டிப்பின் முதல் நாளில் தேவன் உண்டாகும்படி கட்டளையிட்ட முதல் படைப்பு எது?",
        "options_en": [
            "Sun and Moon",
            "Land and Seas",
            "Light",
            "Plants and Trees"
        ],
        "options_ta": [
            "சூரியனும் சந்திரனும்",
            "நிலமும் கடலும்",
            "வெளிச்சம்",
            "தாவரங்களும் மரங்களும்"
        ],
        "correct_index": 2,
        "reference": "Genesis 1:3 / ஆதியாகமம் 1:3",
        "explanation_en": "And God said, Let there be light: and there was light.",
        "explanation_ta": "தேவன் வெளிச்சம் உண்டாகக்கடவது என்றார், வெளிச்சம் உண்டாயிற்று."
    },
    {
        "id": 72,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "How many days and nights did it rain upon the earth during the Great Flood in Genesis 7:12?",
        "question_ta": "நோவாவின் காலத்தில் பெருவெள்ளத்தின்போது பூமியின் மேல் எத்தனை நாட்கள் தொடர்ச்சியாக மழை பெய்தது?",
        "options_en": [
            "7 days and nights",
            "30 days and nights",
            "40 days and nights",
            "150 days and nights"
        ],
        "options_ta": [
            "7 இரவும் பகலும்",
            "30 இரவும் பகலும்",
            "40 இரவும் பகலும்",
            "150 இரவும் பகலும்"
        ],
        "correct_index": 2,
        "reference": "Genesis 7:12 / ஆதியாகமம் 7:12",
        "explanation_en": "And the rain was upon the earth forty days and forty nights.",
        "explanation_ta": "மழை நாற்பது நாள் இரவும் பகலும் பூமியின்மேல் பெய்தது."
    },
    {
        "id": 73,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "Who was the longest-living person recorded in the Bible, having lived 969 years?",
        "question_ta": "வேதாகமத்தில் குறிப்பிடப்பட்டுள்ள மனிதர்களில் 969 ஆண்டுகள் வரை மிக அதிக காலம் வாழ்ந்தவர் யார்?",
        "options_en": [
            "Adam",
            "Enoch",
            "Methuselah",
            "Noah"
        ],
        "options_ta": [
            "ஆதாம்",
            "ஏனோக்கு",
            "மெத்தூசலா",
            "நோவா"
        ],
        "correct_index": 2,
        "reference": "Genesis 5:27 / ஆதியாகமம் 5:27",
        "explanation_en": "And all the days of Methuselah were nine hundred sixty and nine years: and he died.",
        "explanation_ta": "மெத்தூசலாவின் நாளெல்லாம் தொளாயிரற்று அறுபத்தொன்பது வருஷம்; அவன் மரித்தான்."
    },
    {
        "id": 74,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "Which ancient fortified city's walls collapsed flat after the Israelites shouted and blew trumpets on the seventh day?",
        "question_ta": "இஸ்ரவேலர் ஏழாம் நாளில் எக்காளம் ஊதி ஆர்ப்பரித்தபோது எந்தப் பட்டணத்தின் மதில்கள் தரைமட்டமாய் விழுந்தன?",
        "options_en": [
            "Jericho",
            "Ai",
            "Gibeon",
            "Babylon"
        ],
        "options_ta": [
            "எரிகோ",
            "ஆயி",
            "கிபியோன்",
            "பாபிலோன்"
        ],
        "correct_index": 0,
        "reference": "Joshua 6:20 / யோசுவா 6:20",
        "explanation_en": "The people shouted with a great shout, that the wall fell down flat, so that the people went up into the city.",
        "explanation_ta": "ஜனங்கள் ஆர்ப்பரிக்கும்போது, எக்காளங்கள் ஊதப்பட்டது... மதில் இடிந்து விழுந்தது; அப்பொழுது ஜனங்கள் பட்டணத்திற்குள் ஏறினார்கள்."
    },
    {
        "id": 75,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "Which runaway prophet was swallowed by a great sea creature when fleeing from God's mission to Nineveh?",
        "question_ta": "நினிவேக்குப் போகாமல் தர்ஷீசுக்கு ஓடிப்போக முயன்றபோது ஒரு பெரிய மீனினால் விழுங்கப்பட்ட தீர்க்கதரிசி யார்?",
        "options_en": [
            "Micah",
            "Jonah",
            "Nahum",
            "Amos"
        ],
        "options_ta": [
            "மீகா",
            "யோனா",
            "நாகூம்",
            "ஆமோஸ்"
        ],
        "correct_index": 1,
        "reference": "Jonah 1:17 / யோனா 1:17",
        "explanation_en": "Now the Lord had prepared a great fish to swallow up Jonah. And Jonah was in the belly of the fish three days and three nights.",
        "explanation_ta": "யோனாவை விழுங்கும்படி ஒரு பெரிய மீனை கர்த்தர் கட்டளையிட்டிருந்தார்; அந்த மீனின் வயிற்றில் யோனா இரவும் பகலும் மூன்று நாள் இருந்தான்."
    },
    {
        "id": 76,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "What visible sign did God set in the clouds as His covenant promise never to destroy all flesh again by flood?",
        "question_ta": "இனி பூமியின் மாம்சமெல்லாம் பெருவெள்ளத்தினால் அழிக்கப்படுவதில்லை என்பதற்கு அடையாளமாக தேவன் மேகத்தில் வைத்த உடன்படிக்கையின் அடையாளம் எது?",
        "options_en": [
            "A pillar of fire",
            "A rainbow",
            "A golden star",
            "A white dove"
        ],
        "options_ta": [
            "அக்கினி ஸ்தம்பம்",
            "வானவில்",
            "பொன் நட்சத்திரம்",
            "வெண்புறா"
        ],
        "correct_index": 1,
        "reference": "Genesis 9:13 / ஆதியாகமம் 9:13",
        "explanation_en": "I do set my bow in the cloud, and it shall be for a token of a covenant between me and the earth.",
        "explanation_ta": "என் வில்லை மேகத்தில் வைத்தேன்; அது எனக்கும் பூமிக்கும் நடுவே உள்ள உடன்படிக்கைக்கு அடையாளமாய் இருக்கும்."
    },
    {
        "id": 77,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "Who was given a coat of many colors by his father and later sold by his brothers into slavery for twenty pieces of silver?",
        "question_ta": "தந்தையால் பலவர்ண அங்கி கொடுக்கப்பட்டு, பொறாமைகொண்ட தன் சகோதரர்களால் 20 வெள்ளிக்காசுக்கு அடிமையாக விற்கப்பட்டவர் யார்?",
        "options_en": [
            "Benjamin",
            "Joseph",
            "Reuben",
            "Judah"
        ],
        "options_ta": [
            "பென்யமீன்",
            "யோசேப்பு",
            "ரூபன்",
            "யூதா"
        ],
        "correct_index": 1,
        "reference": "Genesis 37:3,28 / ஆதியாகமம் 37:3,28",
        "explanation_en": "Israel loved Joseph more than all his children... and he made him a coat of many colours... and they sold Joseph to the Ishmeelites for twenty pieces of silver.",
        "explanation_ta": "இஸ்ரவேல் யோசேப்பை அதிகமாய் நேசித்து, அவனுக்குப் பலவர்ண அங்கியைச் செய்வித்தான்... சகோதரர்கள் யோசேப்பை இஸ்மவேலரிடத்தில் இருபது வெள்ளிக்காசுக்கு விற்றுப்போட்டார்கள்."
    },
    {
        "id": 78,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "What was the first of the ten plagues brought upon Egypt through Moses and Aaron?",
        "question_ta": "மோசே மற்றும் ஆரோன் மூலமாக எகிப்தின் மேல் தேவன் வரப்பண்ணிய பத்து வாதைகளில் முதல் வாதை எது?",
        "options_en": [
            "Frogs across the land",
            "Waters turned into blood",
            "Hail and fire",
            "Darkness for three days"
        ],
        "options_ta": [
            "நாடு முழுவதும் தவளைகள்",
            "தண்ணீர்கள் இரத்தமாக மாறுதல்",
            "கல்மழையும் அக்கினியும்",
            "மூன்று நாள் காரிருள்"
        ],
        "correct_index": 1,
        "reference": "Exodus 7:20 / யாத்திராகமம் 7:20",
        "explanation_en": "He lifted up the rod, and smote the waters that were in the river... and all the waters that were in the river were turned to blood.",
        "explanation_ta": "ஆரோன் தன் கோலை ஓங்கி, நதியிலுள்ள தண்ணீரை அடித்தான்; அப்பொழுது நதியிலுள்ள தண்ணீரெல்லாம் இரத்தமாய் மாறிற்று."
    },
    {
        "id": 79,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "What bread-like substance miraculously fell from heaven each morning to sustain the Israelites in the desert?",
        "question_ta": "இஸ்ரவேலர் வனாந்தரத்தில் பிரயாணம் செய்தபோது தினமும் காலையில் வானத்திலிருந்து இறங்கி அவர்களைப் போஷித்த உணவு எது?",
        "options_en": [
            "Manna",
            "Unleavened bread",
            "Quail flesh",
            "Wild honey"
        ],
        "options_ta": [
            "மன்னா",
            "புளிப்பில்லா அப்பம்",
            "காடை இறைச்சி",
            "காட்டுத் தேன்"
        ],
        "correct_index": 0,
        "reference": "Exodus 16:31 / யாத்திராகமம் 16:31",
        "explanation_en": "And the house of Israel called the name thereof Manna: and it was like coriander seed, white; and the taste of it was like wafers made with honey.",
        "explanation_ta": "இஸ்ரவேல் வம்சத்தார் அதற்கு மன்னா என்று பேரிட்டார்கள்; அது கொத்துமல்லி விதைபோலவும், வெண்மையாயும், தேன் கலந்த பணியாரத்தின் ருசியாயும் இருந்தது."
    },
    {
        "id": 80,
        "category": "old_testament",
        "difficulty": "medium",
        "question_en": "Which brave Jewish queen declared, 'If I perish, I perish,' before going into King Ahasuerus' presence uninvited to save her people?",
        "question_ta": "'நான் செத்தாலும் சாகிறேன்' என்று கூறி, தன் யூத இனத்தைக் காப்பாற்ற அழைக்கப்படாமல் ராஜாவின் சந்நிதியில் பிரவேசித்த யூத அரசி யார்?",
        "options_en": [
            "Queen Vashti",
            "Queen Jezebel",
            "Queen Esther",
            "Queen of Sheba"
        ],
        "options_ta": [
            "வஸ்தி அரசி",
            "யேசபேல் அரசி",
            "எஸ்தர் அரசி",
            "சேபா நாட்டு அரசி"
        ],
        "correct_index": 2,
        "reference": "Esther 4:16 / எஸ்தர் 4:16",
        "explanation_en": "I will go in unto the king, which is not according to the law: and if I perish, I perish.",
        "explanation_ta": "சட்டத்திற்கு மாறாக நான் ராஜாவினிடத்தில் பிரவேசிப்பேன்; நான் செத்தாலும் சாகிறேன் என்றாள்."
    },
    {
        "id": 81,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Which prophet was taken up into heaven in a whirlwind by a chariot and horses of fire without experiencing death?",
        "question_ta": "மரணத்தைக் காணாமல் அக்கினி ரதமும் அக்கினிக் குதிரைகளும் சூழ சுழல்காற்றிலே பரலோகத்திற்கு எடுத்துக்கொள்ளப்பட்ட தீர்க்கதரிசி யார்?",
        "options_en": [
            "Moses",
            "Elijah",
            "Elisha",
            "Isaiah"
        ],
        "options_ta": [
            "மோசே",
            "எலியா",
            "எலிசா",
            "ஏசாயா"
        ],
        "correct_index": 1,
        "reference": "2 Kings 2:11 / 2 இராஜாக்கள் 2:11",
        "explanation_en": "There appeared a chariot of fire, and horses of fire, and parted them both asunder; and Elijah went up by a whirlwind into heaven.",
        "explanation_ta": "இதோ, ஒரு அக்கினி ரதமும் அக்கினிக் குதிரைகளும் தோன்றி, அவர்கள் இருவரையும் பிரித்தது; எலியா சுழல்காற்றிலே பரலோகத்திற்கு ஏறிப்போனான்."
    },
    {
        "id": 82,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who asked for and received a 'double portion' of the prophet Elijah's spirit?",
        "question_ta": "தீர்க்கதரிசியாகிய எலியாவின் ஆவியின் இரட்டிப்பான பங்கை விரும்பிப் பெற்றுக்கொண்டவர் யார்?",
        "options_en": [
            "Gehazi",
            "Elisha",
            "Obadiah",
            "Jeremiah"
        ],
        "options_ta": [
            "கேயாசி",
            "எலிசா",
            "ஒபதியா",
            "எரேமியா"
        ],
        "correct_index": 1,
        "reference": "2 Kings 2:9-10 / 2 இராஜாக்கள் 2:9-10",
        "explanation_en": "And Elisha said, I pray thee, let a double portion of thy spirit be upon me. And he said, Thou hast asked a hard thing: nevertheless...",
        "explanation_ta": "எலிசா: உம்முடைய ஆவியின் வரம் எனக்கு இரட்டிப்பாய் இருக்கும்படி வேண்டுகிறேன் என்றான். அதற்கு அவன்: அரிதான காரியத்தைக் கேட்டாய்... என்றான்."
    },
    {
        "id": 83,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Which biblical judge possessed extraordinary God-given strength connected to his Nazirite vow never to cut his hair?",
        "question_ta": "தன் தலைமுடி சவரம் செய்யப்படாமல் நசரேய விரதத்தைக் காக்கும் வரை மகா பலம் பெற்றிருந்த இஸ்ரவேலின் நியாயாதிபதி யார்?",
        "options_en": [
            "Gideon",
            "Jephthah",
            "Samson",
            "Barak"
        ],
        "options_ta": [
            "கிதியோன்",
            "யெப்தா",
            "சிம்சோன்",
            "பாராக்"
        ],
        "correct_index": 2,
        "reference": "Judges 16:17 / நியாயாதிபதிகள் 16:17",
        "explanation_en": "There hath not come a razor upon mine head; for I have been a Nazarite unto God from my mother's womb: if I be shaven, then my strength will go from me.",
        "explanation_ta": "என் தலையின்மேல் சவரகன் கத்தி படவில்லை; நான் என் தாயின் கர்ப்பத்திலானதுமுதல் தேவனுக்கென்று நசரேயனானவன்; என் தலை சவரம்பண்ணப்பட்டால், என் பலம் என்னை விட்டுப் போய்விடும் என்றான்."
    },
    {
        "id": 84,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who interpreted Pharaoh's dreams of seven fat cows and seven lean cows, saving Egypt and surrounding nations from famine?",
        "question_ta": "எகிப்தின் பார்வோன் கண்ட ஏழு கொழுத்த பசுக்கள் மற்றும் ஏழு மெலிந்த பசுக்களின் சொப்பனங்களுக்கு விளக்கம் கொடுத்து பஞ்சத்திலிருந்து தேசத்தைக் காத்தவர் யார்?",
        "options_en": [
            "Daniel",
            "Joseph",
            "Moses",
            "Nehemiah"
        ],
        "options_ta": [
            "தானியேல்",
            "யோசேப்பு",
            "மோசே",
            "நெகேமியா"
        ],
        "correct_index": 1,
        "reference": "Genesis 41:25-30 / ஆதியாகமம் 41:25-30",
        "explanation_en": "Joseph said unto Pharaoh, The dream of Pharaoh is one... Behold, there come seven years of great plenty... And there shall arise after them seven years of famine.",
        "explanation_ta": "யோசேப்பு பார்வோனை நோக்கி: பார்வோனுடைய சொப்பனம் ஒன்றே... இதோ, எகிப்து தேசமெங்கும் மிகுந்த விளைவுண்டாயிருக்கும் ஏழு வருஷம் வரும். அதற்குப்பின்பு ஏழு வருஷம் பஞ்சம் உண்டாகும் என்றார்."
    },
    {
        "id": 85,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "On which mountain did the prophet Elijah challenge and triumph over 450 false prophets of Baal when fire consumed his sacrifice?",
        "question_ta": "தீர்க்கதரிசியாகிய எலியா பாகாலின் 450 போலித் தீர்க்கதரிசிகளுக்கு சவால் விடுத்து, வானத்திலிருந்து அக்கினி இறங்கி பலியைத் தகிக்கச் செய்த மலை எது?",
        "options_en": [
            "Mount Sinai",
            "Mount Carmel",
            "Mount of Olives",
            "Mount Hermon"
        ],
        "options_ta": [
            "சீனாய் மலை",
            "கர்மேல் மலை",
            "ஒலிவ மலை",
            "எர்மோன் மலை"
        ],
        "correct_index": 1,
        "reference": "1 Kings 18:19-38 / 1 இராஜாக்கள் 18:19-38",
        "explanation_en": "Gather to me all Israel unto mount Carmel, and the prophets of Baal four hundred and fifty... Then the fire of the Lord fell, and consumed the burnt sacrifice.",
        "explanation_ta": "கர்மேல் பர்வதத்திலே இஸ்ரவேலர் எல்லாரையும், பாகாலின் தீர்க்கதரிசிகள் நானூற்றைம்பது பேரையும் என்னிடத்தில் கூட்டிச்சேர்க்க ஆட்களை அனுப்பும்... அப்பொழுது கர்த்தருடைய அக்கினி இறங்கி, சர்வாங்க தகனபலியைத் பட்சித்தது."
    },
    {
        "id": 86,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who was cast into a den of hungry lions for praying to the God of heaven, but was preserved without a scratch by an angel?",
        "question_ta": "தேவனிடம் மட்டுமே ஜெபித்த குற்றத்திற்காக சிங்கங்களின் கெபியில் போடப்பட்டு, தேவனுடைய தூதனால் ஒரு சேதமுமின்றி காப்பாற்றப்பட்டவர் யார்?",
        "options_en": [
            "Nehemiah",
            "Daniel",
            "Mordecai",
            "Ezekiel"
        ],
        "options_ta": [
            "நெகேமியா",
            "தானியேல்",
            "மொர்தெகாய்",
            "எசேக்கியேல்"
        ],
        "correct_index": 1,
        "reference": "Daniel 6:16-22 / தானியேல் 6:16-22",
        "explanation_en": "My God hath sent his angel, and hath shut the lions' mouths, that they have not hurt me: forasmuch as before him innocency was found in me.",
        "explanation_ta": "சிங்கங்கள் என்னைச் சேதப்படுத்தாதபடிக்கு என் தேவன் தம்முடைய தூதனை அனுப்பி, அவைகளின் வாய்களைக் கட்டிப்போட்டார்; அவர் முன்பாக நான் குற்றமற்றவனாய்க் காணப்பட்டேன்."
    },
    {
        "id": 87,
        "category": "heroes",
        "difficulty": "easy",
        "question_en": "Who was appointed by God to succeed Moses and lead the children of Israel into the Promised Land of Canaan?",
        "question_ta": "மோசேக்குப் பின் இஸ்ரவேல் மக்களை வழிநடத்தி வாக்குத்தத்தம் பண்ணப்பட்ட கானான் தேசத்திற்குள் அழைத்துச் செல்ல தேவனால நியமிக்கப்பட்ட தலைவர் யார்?",
        "options_en": [
            "Caleb",
            "Joshua",
            "Eleazar",
            "Gideon"
        ],
        "options_ta": [
            "காலேப்",
            "யோசுவா",
            "எலெயாசார்",
            "கிதியோன்"
        ],
        "correct_index": 1,
        "reference": "Joshua 1:1-2 / யோசுவா 1:1-2",
        "explanation_en": "The Lord spake unto Joshua the son of Nun, Moses' minister, saying, Moses my servant is dead; now therefore arise, go over this Jordan.",
        "explanation_ta": "கர்த்தர் மோசேயின் ஊழியக்காரனான நூனின் குமாரன் யோசுவாவை நோக்கி: என் ஊழியக்காரனாகிய மோசே மரித்துப்போனான்; இப்போதும் நீயும் இந்த ஜனங்கள் எல்லாரும் எழுந்து, இந்த யோர்தானைக் கடந்துபோங்கள் என்றார்."
    },
    {
        "id": 88,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Who was the only female judge of Israel mentioned in the book of Judges, who sat under a palm tree and inspired Barak to victory?",
        "question_ta": "பேரீச்சமரத்தின் கீழ் அமர்ந்து இஸ்ரவேலுக்கு நியாயந்தீர்த்து, பாராக்கை ஊக்கப்படுத்தி மாபெரும் வெற்றியைப் பெற்றுத்தந்த பெண் நியாயாதிபதி யார்?",
        "options_en": [
            "Ruth",
            "Deborah",
            "Hannah",
            "Abigail"
        ],
        "options_ta": [
            "ரூத்",
            "தெபொராள்",
            "அன்னாள்",
            "அபிகாயில்"
        ],
        "correct_index": 1,
        "reference": "Judges 4:4-5 / நியாயாதிபதிகள் 4:4-5",
        "explanation_en": "And Deborah, a prophetess, the wife of Lapidoth, she judged Israel at that time. And she dwelt under the palm tree of Deborah.",
        "explanation_ta": "லப்பிதோத்தின் மனைவியாகிய தெபொராள் என்னும் தீர்க்கதரிசியானவள் அக்காலத்திலே இஸ்ரவேலை நியாயம் விசாரித்தாள். அவள் தெபொராளின் பேரீச்சமரத்தின்கீழ் வாசம்பண்ணினாள்."
    },
    {
        "id": 89,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Which prophet is famously known as the 'Weeping Prophet' because of his heartfelt sorrow over Jerusalem's rebellion and captivity?",
        "question_ta": "எருசலேமின் அழிவையும் சிறையிருப்பையும் கண்டு கண்ணீரோடு புலம்பியதால் 'கண்ணீரின் தீர்க்கதரிசி' என்று அழைக்கப்படுபவர் யார்?",
        "options_en": [
            "Isaiah",
            "Ezekiel",
            "Jeremiah",
            "Hosea"
        ],
        "options_ta": [
            "ஏசாயா",
            "எசேக்கியேல்",
            "எரேமியா",
            "ஓசியா"
        ],
        "correct_index": 2,
        "reference": "Jeremiah 9:1 / எரேமியா 9:1",
        "explanation_en": "Oh that my head were waters, and mine eyes a fountain of tears, that I might weep day and night for the slain of the daughter of my people!",
        "explanation_ta": "என் ஜனமாகிய குமாரத்தியின் காயம்பட்டவர்களுக்காக நான் இரவும் பகலும் அழுதுகொண்டிருக்கத்தக்கதாக, என் தலை தண்ணீரும், என் கண்கள் கண்ணீரூற்றுமானால் நலமாயிருக்கும்!"
    },
    {
        "id": 90,
        "category": "heroes",
        "difficulty": "medium",
        "question_en": "Which prophet had a vision of a valley of dry bones coming together and breathing life again by the Spirit of God?",
        "question_ta": "தேவனுடைய ஆவியினால் உலர்ந்த எலும்புகள் நிறைந்த பள்ளத்தாக்கு உயிர்பெற்று பெரும் சேனையாக நின்ற தரிசனத்தைக் கண்ட தீர்க்கதரிசி யார்?",
        "options_en": [
            "Ezekiel",
            "Daniel",
            "Zechariah",
            "Habakkuk"
        ],
        "options_ta": [
            "எசேக்கியேல்",
            "தானியேல்",
            "சகரியா",
            "ஆபகூக்"
        ],
        "correct_index": 0,
        "reference": "Ezekiel 37:1-10 / எசேக்கியேல் 37:1-10",
        "explanation_en": "Prophesy upon these bones, and say unto them, O ye dry bones, hear the word of the Lord... and the breath came into them, and they lived, and stood up upon their feet, an exceeding great army.",
        "explanation_ta": "நீ இந்த எலும்புகளைக் குறித்துத் தீர்க்கதரிசனம் சொல்லி... உலர்ந்த எலும்புகளே, கர்த்தருடைய வார்த்தையைக் கேளுங்கள்... ஆவி அவர்களுக்குள் பிரவேசிக்க, அவர்கள் உயிரடைந்து, காலூன்றி, மகா பெரிய சேனையாக நின்றார்கள்."
    },
    {
        "id": 91,
        "category": "general",
        "difficulty": "easy",
        "question_en": "On which sacred feast day did the Holy Spirit descend upon the apostles like tongues of fire in Acts 2?",
        "question_ta": "அப்போஸ்தலர் 2 ஆம் அதிகாரத்தில் அப்போஸ்தலர்கள் மேல் அக்கினி நாவுகள் போல பரிசுத்த ஆவியானவர் இறங்கிவந்த புனித நாள் எது?",
        "options_en": [
            "Passover",
            "Day of Atonement",
            "Day of Pentecost",
            "Feast of Tabernacles"
        ],
        "options_ta": [
            "பஸ்கா பண்டிகை",
            "பாவநிவாரண நாள்",
            "பெந்தெகொஸ்தே நாள்",
            "கூடாரப் பண்டிகை"
        ],
        "correct_index": 2,
        "reference": "Acts 2:1-4 / அப்போஸ்தலர் 2:1-4",
        "explanation_en": "When the day of Pentecost was fully come... there appeared unto them cloven tongues like as of fire, and it sat upon each of them. And they were all filled with the Holy Ghost.",
        "explanation_ta": "பெந்தெகொஸ்தே என்னும் நாள் வந்தபோது... அக்கினிமயமான நாவுகள்போலப் பிரிந்திருக்கும் நாவுகள் அவர்களுக்குக் காணப்பட்டு, அவர்கள் ஒவ்வொருவர்மேலும் வந்து அமர்ந்தது. அவர்களெல்லாரும் பரிசுத்த ஆவியினாலே நிரப்பப்பட்டார்கள்."
    },
    {
        "id": 92,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What was the Hebrew name of the Apostle Paul before Jesus encountered him in a bright light on the road to Damascus?",
        "question_ta": "தமஸ்குவுக்குப் போகும் வழியில் இயேசுவைச் சந்திப்பதற்கு முன்பு அப்போஸ்தலனாகிய பவுலின் பெயர் என்ன?",
        "options_en": [
            "Silas",
            "Saul of Tarsus",
            "Barnabas",
            "Stephen"
        ],
        "options_ta": [
            "சீலா",
            "தர்சு பட்டணத்தானாகிய சவுல்",
            "பர்னபா",
            "ஸ்தேவான்"
        ],
        "correct_index": 1,
        "reference": "Acts 9:1-4 / அப்போஸ்தலர் 9:1-4",
        "explanation_en": "And as he journeyed, he came near Damascus: and suddenly there shined round about him a light from heaven: And he fell to the earth, and heard a voice saying unto him, Saul, Saul, why persecutest thou me?",
        "explanation_ta": "அவன் பிரயாணமாய்ப் போய், தமஸ்குவுக்குச் சமீபித்தபோது, சடிதியிலே வானத்திலிருந்து ஒரு ஒளி அவனைச் சுற்றிப் பிரகாசித்தது. அவன் தரையிலே விழுந்தான்; அப்பொழுது: சவுலே, சவுலே, நீ என்னை ஏன் துன்பப்படுத்துகிறாய் என்று தன்னுடனே சொல்லுகிற ஒரு சத்தத்தைக் கேட்டான்."
    },
    {
        "id": 93,
        "category": "general",
        "difficulty": "medium",
        "question_en": "In which historical city were the disciples of Jesus first given the name 'Christians'?",
        "question_ta": "இயேசுவின் சீஷர்கள் முதன்முதலில் எந்தப் பட்டணத்தில் 'கிறிஸ்தவர்கள்' என்று அழைக்கப்பட்டார்கள்?",
        "options_en": [
            "Jerusalem",
            "Rome",
            "Antioch",
            "Ephesus"
        ],
        "options_ta": [
            "எருசலேம்",
            "ரோமாபுரி",
            "அந்தியோகியா",
            "எபேசு"
        ],
        "correct_index": 2,
        "reference": "Acts 11:26 / அப்போஸ்தலர் 11:26",
        "explanation_en": "And the disciples were called Christians first in Antioch.",
        "explanation_ta": "முதல்முதல் அந்தியோகியாவிலே சீஷர்களுக்குக் கிறிஸ்தவர்கள் என்கிற பேர் வழங்கிற்று."
    },
    {
        "id": 94,
        "category": "general",
        "difficulty": "medium",
        "question_en": "Which famous New Testament chapter is widely celebrated as the 'Hall of Faith' recounting heroes from Abel to David?",
        "question_ta": "ஆபேல் முதல் தாவீது வரையிலான விசுவாச வீரர்களைப் பட்டியலிடும் புதிய ஏற்பாட்டின் 'விசுவாசப் பட்டியல்' அதிகாரம் எது?",
        "options_en": [
            "Romans 8",
            "1 Corinthians 13",
            "Hebrews 11",
            "James 2"
        ],
        "options_ta": [
            "ரோமர் 8",
            "1 கொரிந்தியர் 13",
            "எபிரெயர் 11",
            "யாக்கோபு 2"
        ],
        "correct_index": 2,
        "reference": "Hebrews 11:1-40 / எபிரெயர் 11:1-40",
        "explanation_en": "Hebrews 11 defines faith and honors ancient patriarchs and prophets who walked by faith.",
        "explanation_ta": "எபிரெயர் 11 விசுவாசத்தை வரையறுத்து, விசுவாசத்தினால் வாழ்ந்து சாட்சிபெற்ற விசுவாச வீரர்களை விவரிக்கிறது."
    },
    {
        "id": 95,
        "category": "general",
        "difficulty": "easy",
        "question_en": "According to Jesus in Matthew 22:37-38, what is the first and greatest commandment?",
        "question_ta": "மத்தேயு 22:37-38 இல் இயேசு கூறியபடி நியாயப்பிரமாணத்தில் முதன்மையானதும் பெரிதுமான கற்பனை எது?",
        "options_en": [
            "Do not bear false witness",
            "Love the Lord your God with all your heart, soul, and mind",
            "Honor your father and mother",
            "Keep the Sabbath holy"
        ],
        "options_ta": [
            "பொய்ச்சாட்சி சொல்லாதிருப்பாயாக",
            "உன் தேவனாகிய கர்த்தரிடத்தில் உன் முழு இருதயத்தோடும் முழு ஆத்துமாவோடும் முழு மனதோடும் அன்புகூருவாயாக",
            "உன் தகப்பனையும் தாயையும் கனம்பண்ணுவாயாக",
            "ஓய்வுநாளைப் பரிசுத்தமாய் ஆசரிக்க நினைப்பாயாக"
        ],
        "correct_index": 1,
        "reference": "Matthew 22:37-38 / மத்தேயு 22:37-38",
        "explanation_en": "Thou shalt love the Lord thy God with all thy heart, and with all thy soul, and with all thy mind. This is the first and great commandment.",
        "explanation_ta": "உன் தேவனாகிய கர்த்தரிடத்தில் உன் முழு இருதயத்தோடும் உன் முழு ஆத்துமாவோடும் உன் முழு மனதோடும் அன்புகூருவாயாக; இது முதலாம் பிரதான கற்பனை."
    },
    {
        "id": 96,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What is the shortest verse in the English Bible, consisting of just two words in John 11:35?",
        "question_ta": "யோவான் 11:35 இல் ஆங்கில வேதாகமத்தின் மிகக் குறுகிய வசனம் எது?",
        "options_en": [
            "Praise the Lord",
            "Jesus wept",
            "Pray without ceasing",
            "God is love"
        ],
        "options_ta": [
            "கர்த்தரைத் துதியுங்கள்",
            "இயேசு கண்ணீர் விட்டார்",
            "இடைவிடாமல் ஜெபம்பண்ணுங்கள்",
            "தேவன் அன்பாகவே இருக்கிறார்"
        ],
        "correct_index": 1,
        "reference": "John 11:35 / யோவான் 11:35",
        "explanation_en": "Jesus wept.",
        "explanation_ta": "இயேசு கண்ணீர் விட்டார்."
    },
    {
        "id": 97,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What is the longest chapter in the entire Bible, featuring 176 verses in praise of God's Word?",
        "question_ta": "தேவனுடைய வார்த்தையின் மகிமையை விவரிக்கும் 176 வசனங்களைக் கொண்ட வேதாகமத்தின் மிக நீண்ட அதிகாரம் எது?",
        "options_en": [
            "Genesis 1",
            "Psalm 23",
            "Psalm 119",
            "Isaiah 53"
        ],
        "options_ta": [
            "ஆதியாகமம் 1",
            "சங்கீதம் 23",
            "சங்கீதம் 119",
            "ஏசாயா 53"
        ],
        "correct_index": 2,
        "reference": "Psalm 119 / சங்கீதம் 119",
        "explanation_en": "Psalm 119 is an acrostic poem with 176 verses celebrating the statutes and commandments of God.",
        "explanation_ta": "சங்கீதம் 119 மொத்தம் 176 வசனங்களைக் கொண்டு, கர்த்தருடைய வேதத்தையும் பிரமாணங்களையும் போற்றும் வேதாகமத்தின் மிக நீண்ட அதிகாரமாகும்."
    },
    {
        "id": 98,
        "category": "general",
        "difficulty": "easy",
        "question_en": "What is the very first fruit of the Holy Spirit listed by Paul in Galatians 5:22?",
        "question_ta": "கலாத்தியர் 5:22 இல் பவுலால் பட்டியலிடப்பட்டுள்ள ஆவியின் கனிகளில் முதன்மையானது எது?",
        "options_en": [
            "Peace",
            "Joy",
            "Love",
            "Faithfulness"
        ],
        "options_ta": [
            "சமாதானம்",
            "சந்தோஷம்",
            "அன்பு",
            "உண்மை"
        ],
        "correct_index": 2,
        "reference": "Galatians 5:22 / கலாத்தியர் 5:22",
        "explanation_en": "But the fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith...",
        "explanation_ta": "ஆவியின் கனியோ: அன்பு, சந்தோஷம், சமாதானம், நீடியபொறுமை, தயவு, நற்குணம், விசுவாசம்..."
    },
    {
        "id": 99,
        "category": "general",
        "difficulty": "medium",
        "question_en": "Who was the devout Roman centurion in Caesarea whose prayers and alms came up before God, becoming the first Gentile convert in Acts 10?",
        "question_ta": "செசரியாவிலிருந்த தேவபக்தியுள்ள ரோம நூற்றுக்கு அதிபதியும், அப்போஸ்தலர் 10 இல் புறஜாதியாரில் முதலாவது விசுவாசியாக மாறியவருமான நபர் யார்?",
        "options_en": [
            "Cornelius",
            "Festus",
            "Agrippa",
            "Claudius Lysias"
        ],
        "options_ta": [
            "கொர்நேலியு",
            "பேஸ்து",
            "அகிரிப்பா",
            "கிலவுதியு லீசியா"
        ],
        "correct_index": 0,
        "reference": "Acts 10:1-4 / அப்போஸ்தலர் 10:1-4",
        "explanation_en": "There was a certain man in Caesarea called Cornelius, a centurion of the band called the Italian band... Thy prayers and thine alms are come up for a memorial before God.",
        "explanation_ta": "செசரியாவிலே இத்தாலிக்கா என்னப்பட்ட பட்டாளத்திலே நூற்றுக்கு அதிபதியாகிய கொர்நேலியு என்னும் பேருள்ள ஒரு மனுஷன் இருந்தான்... உன் ஜெபங்களும் உன் தர்மங்களும் தேவனுக்கு முன்பாக நினைப்பூட்டுதலாக வந்து எட்டினது என்றார்."
    },
    {
        "id": 100,
        "category": "general",
        "difficulty": "medium",
        "question_en": "In which epistle does Paul exhort believers to put on the 'Whole Armor of God' to withstand spiritual warfare?",
        "question_ta": "பொல்லாத நாளில் எதிர்த்து நிற்கும்படி 'தேவனுடைய சர்வாயுதவர்க்கத்தையும்' தரித்துக்கொள்ளும்படி பவுல் எந்த நிருபத்தில் அறிவுறுத்துகிறார்?",
        "options_en": [
            "Philippians 4",
            "Ephesians 6",
            "Colossians 3",
            "2 Corinthians 10"
        ],
        "options_ta": [
            "பிலிப்பியர் 4",
            "எபேசியர் 6",
            "கொலோசெயர் 3",
            "2 கொரிந்தியர் 10"
        ],
        "correct_index": 1,
        "reference": "Ephesians 6:11-17 / எபேசியர் 6:11-17",
        "explanation_en": "Put on the whole armour of God, that ye may be able to stand against the wiles of the devil.",
        "explanation_ta": "நீங்கள் பிசாசின் தந்திரங்களோடு எதிர்த்து நிற்கத் திராணியுள்ளவர்களாகும்படி, தேவனுடைய சர்வாயுதவர்க்கத்தையும் தரித்துக்கொள்ளுங்கள்."
    }
]
