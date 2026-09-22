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
    },
    {
        "id": 21,
        "category": "old_testament",
        "difficulty": "easy",
        "question_en": "In how many days did God complete the creation of the heavens and the earth before resting?",
        "question_ta": "தேவன் எத்தனை நாட்களில் வானத்தையும் பூமியையும் படைத்து முடித்து ஓய்ந்திருந்தார்?",
        "options_en": ["3 days", "6 days", "7 days", "10 days"],
        "options_ta": ["3 நாட்கள்", "6 நாட்கள்", "7 நாட்கள்", "10 நாட்கள்"],
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
        "options_en": ["7", "10", "12", "70"],
        "options_ta": ["7", "10", "12", "70"],
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
        "options_en": ["Moses", "Abraham", "David", "Elijah"],
        "options_ta": ["மோசே", "ஆபிரகாம்", "தாவீது", "எலியா"],
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
        "options_en": ["Rebekah", "Rachel", "Sarah", "Leah"],
        "options_ta": ["ரெபேக்காள்", "ராகேல்", "சாராள்", "லேயாள்"],
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
        "options_en": ["Vashti", "Esther", "Deborah", "Jezebel"],
        "options_ta": ["வஸ்தி", "எஸ்தர்", "தெபொராள்", "யேசபேல்"],
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
        "options_en": ["A Priest", "A Levite", "A Good Samaritan", "A Roman Soldier"],
        "options_ta": ["ஆசாரியன்", "லேவியன்", "நல்ல சமாரியன்", "ரோம போர்வீரன்"],
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
        "options_en": ["Elisha", "Enoch", "Elijah", "Isaiah"],
        "options_ta": ["எலிசா", "ஏனோக்கு", "எலியா", "ஏசாயா"],
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
        "options_en": ["David", "Saul", "Solomon", "Rehoboam"],
        "options_ta": ["தாவீது", "சவுல்", "சாலொமோன்", "ரெகொபெயாம்"],
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
        "options_en": ["Romans", "Acts of the Apostles", "Hebrews", "Galatians"],
        "options_ta": ["ரோமர்", "அப்போஸ்தலருடைய நடபடிகள்", "எபிரெயர்", "கலாத்தியர்"],
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
        "options_en": ["10 pieces", "20 pieces", "30 pieces", "50 pieces"],
        "options_ta": ["10 வெள்ளிக்காசு", "20 வெள்ளிக்காசு", "30 வெள்ளிக்காசு", "50 வெள்ளிக்காசு"],
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
        "options_en": ["Gideon", "Samson", "Barak", "Jephthah"],
        "options_ta": ["கிதியோன்", "சிம்சோன்", "பாராக்", "யெப்தா"],
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
        "options_en": ["Latin", "Greek", "Hebrew", "Aramaic"],
        "options_ta": ["லத்தீன்", "கிரேக்கம்", "எபிரெயம்", "அரமேயம்"],
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
        "options_en": ["Bartimaeus", "Nicodemus", "Zacchaeus", "Cornelius"],
        "options_ta": ["பர்த்திமேயு", "நிக்கோதேமு", "சகேயு", "கொர்நேலியு"],
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
        "options_en": ["David", "Solomon", "Hezekiah", "Josiah"],
        "options_ta": ["தாவீது", "சாலொமோன்", "எசேக்கியா", "யோசியா"],
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
        "options_en": ["Barnabas", "Silas", "Saul of Tarsus", "Apollos"],
        "options_ta": ["பர்னபா", "சீலா", "தர்சு பட்டணத்து சவுல்", "அப்பொல்லோ"],
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
        "options_en": ["John", "Peter", "Thomas", "Andrew"],
        "options_ta": ["யோவான்", "பேதுரு", "தோமா", "அந்திரேயா"],
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
        "options_en": ["Romans", "1 Corinthians", "Ephesians", "Philippians"],
        "options_ta": ["ரோமர்", "1 கொரிந்தியர்", "எபேசியர்", "பிலிப்பியர்"],
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
        "options_en": ["A pillar of cloud", "The rainbow", "A burning bush", "A comet"],
        "options_ta": ["மேக ஸ்தம்பம்", "வானவில்", "முட்செடி", "வால் நட்சத்திரம்"],
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
        "options_en": ["Orpah", "Ruth", "Hannah", "Abigail"],
        "options_ta": ["ஒர்பாள்", "ரூத்", "அன்னாள்", "அபிகாயில்"],
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
        "options_en": ["Hallelujah", "Amen", "Peace", "Glory"],
        "options_ta": ["அல்லேலூயா", "ஆமென்", "சமாதானம்", "மகிமை"],
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
        "options_en": ["James the son of Zebedee", "Stephen", "Philip", "Barnabas"],
        "options_ta": ["செபதேயுவின் மகன் யாக்கோபு", "ஸ்தேவான்", "பிலிப்பு", "பர்னபா"],
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
    }
]
