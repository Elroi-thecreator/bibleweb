"""
AI Scripture Quiz Generator and Theological Tutor Engine.
Provides dynamic topic-driven biblical quiz question generation (bilingual Tamil & English)
and in-depth AI tutor explanations using the Ask Bible AI plugin with verified fallback.
"""

import json
import logging
import random
import re
from typing import Any, Dict, List, Optional

from ask_bible_ai.config import config as ai_config
from ask_bible_ai.routes import ai_service

logger = logging.getLogger("holy_bible.quiz_ai")

# =====================================================================
# Curated Topic-Grounded Fallback Quiz Question Bank
# =====================================================================

CURATED_AI_QUIZ_TOPICS: Dict[str, List[Dict[str, Any]]] = {
    "parables": [
        {
            "category": "miracles_parables",
            "difficulty": "easy",
            "question_en": "In the Parable of the Prodigal Son, what animal was killed for the celebratory feast when the son returned?",
            "question_ta": "ஊதாரிக்குமாரன் உவமையில், மகன் திரும்பி வந்தபோது கொண்டாட்ட விருந்திற்காக அடிக்கப்பட்ட மிருகம் எது?",
            "options_en": ["A fatted calf", "A young lamb", "A goat", "Two oxen"],
            "options_ta": ["கொழுத்த கன்றுக்குட்டி", "இள ஆட்டுக்குட்டி", "ஒரு வெள்ளாட்டுக்கடா", "இரண்டு எருதுகள்"],
            "correct_index": 0,
            "reference": "Luke 15:23 / லூக்கா 15:23",
            "explanation_en": "The father commanded his servants to bring the fatted calf and kill it, celebrating his son who was lost and is found.",
            "explanation_ta": "தகப்பன் தன் வேலைக்காரர்களை நோக்கி: கொழுத்த கன்றுக் குட்டியைக் கொண்டுவந்து அடியுங்கள்; நாம் புசித்து, சந்தோஷமாயிருப்போம் என்றார்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "medium",
            "question_en": "In the Parable of the Sower, which seed sprang up quickly but withered because it lacked deep root?",
            "question_ta": "விதைக்கிறவன் உவமையில், விரைவில் முளைத்து, ஆனால் ஆழமான வேர் இல்லாததால் காய்ந்துபோன விதை எது?",
            "options_en": ["The seed on rocky places", "The seed along the path", "The seed among thorns", "The seed on good soil"],
            "options_ta": ["கற்பாறை இடங்களில் விழுந்த விதை", "வழியருகே விழுந்த விதை", "முள்ளுள்ள இடங்களில் விழுந்த விதை", "நல்ல நிலத்தில் விழுந்த விதை"],
            "correct_index": 0,
            "reference": "Matthew 13:5-6 / மத்தேயு 13:5-6",
            "explanation_en": "Seed falling on rocky places sprang up quickly because the soil was shallow, but withered under the scorching sun because it had no root.",
            "explanation_ta": "கற்பாறை நிலத்தில் விழுந்த விதைகள் மண் ஆழமாயிராததினால் உடனே முளைத்தது; வெயில் ஏறினபோதோ தீய்ந்துபோய், வேரில்லாமையால் உலர்ந்துபோயிற்று."
        },
        {
            "category": "miracles_parables",
            "difficulty": "easy",
            "question_en": "In the Parable of the Good Samaritan, who walked by and helped the wounded traveler after a priest and a Levite passed by?",
            "question_ta": "நல்ல சமாரியன் உவமையில், ஆசாரியனும் லேவியனும் கடந்து சென்றபின், காயமடைந்த பயணியைக் கண்டு உதவி செய்தவர் யார்?",
            "options_en": ["A Samaritan", "A Roman centurion", "A Pharisee", "A Galilean fisherman"],
            "options_ta": ["ஒரு சமாரியன்", "ஒரு ரோம நூற்றுக்கு அதிபதி", "ஒரு பரிசேயன்", "ஒரு கலிலேய மீனவன்"],
            "correct_index": 0,
            "reference": "Luke 10:33-34 / லூக்கா 10:33-34",
            "explanation_en": "A Samaritan journeying by had compassion, bandaged his wounds pouring on oil and wine, and brought him to an inn.",
            "explanation_ta": "ஒரு சமாரியன் பிரயாணமாய் வருகையில், அவனைக் கண்டு, மனதுருகி, அவன் காயங்களில் எண்ணெயும் திராட்சரசமும் வார்த்துக் கட்டினான்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "medium",
            "question_en": "In the Parable of the Ten Virgins, how many were described as wise and carried extra oil with their lamps?",
            "question_ta": "பத்து கன்னிகைகள் உவமையில், புத்தியுள்ளவர்களாக தங்கள் தீவட்டிகளோடு கூட எண்ணெய் எடுத்துச் சென்றவர்கள் எத்தனை பேர்?",
            "options_en": ["Five", "Three", "Seven", "Ten"],
            "options_ta": ["ஐந்து பேர்", "மூன்று பேர்", "ஏழு பேர்", "பத்து பேர்"],
            "correct_index": 0,
            "reference": "Matthew 25:2-4 / மத்தேயு 25:2-4",
            "explanation_en": "Five were wise and five were foolish. The wise took oil in jars along with their lamps to be ready for the bridegroom.",
            "explanation_ta": "அவர்களில் ஐந்துபேர் புத்தியுள்ளவர்களும், ஐந்துபேர் புத்தியில்லாதவர்களுமாய் இருந்தார்கள். புத்தியுள்ளவர்கள் தங்கள் தீவட்டிகளோடு பாத்திரங்களில் எண்ணெயையும் கொண்டுபோனார்கள்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "hard",
            "question_en": "In the Parable of the Unforgiving Servant, how much did the servant owe his king before being completely pardoned?",
            "question_ta": "மன்னிக்காத வேலைக்காரன் உவமையில், ராஜாவிடம் முற்றிலுமாக மன்னிக்கப்படுவதற்கு முன் அவன் பட்டிருந்த கடன் எவ்வளவு?",
            "options_en": ["Ten thousand talents", "One hundred denarii", "Fifty shekels", "Five hundred talents"],
            "options_ta": ["பத்தாயிரம் தாலந்து", "நூறு வெள்ளிப்பணம் (தினாரி)", "ஐம்பது சேக்கல்", "ஐந்நூறு தாலந்து"],
            "correct_index": 0,
            "reference": "Matthew 18:24 / மத்தேயு 18:24",
            "explanation_en": "The servant owed ten thousand talents—an unpayable fortune—yet the master took pity on him and canceled the entire debt.",
            "explanation_ta": "அவன் கணக்குப்பார்க்கத் தொடங்கினபோது, பத்தாயிரம் தாலந்து கடன் பட்டவன் ஒருவனை அவனுக்கு முன்பாகக் கொண்டுவந்தார்கள்; ஆண்டவன் அவனுக்குக் கடனை மன்னித்துவிட்டான்."
        }
    ],
    "miracles": [
        {
            "category": "miracles_parables",
            "difficulty": "easy",
            "question_en": "At which wedding did Jesus perform His first public miracle by turning water into wine?",
            "question_ta": "இயேசு தண்ணீரைத் திராட்சரசமாக மாற்றி தமது முதல் அற்புதத்தைச் செய்த திருமணம் எங்கே நடைபெற்றது?",
            "options_en": ["Cana in Galilee", "Bethany", "Nazareth", "Capernaum"],
            "options_ta": ["கலிலேயாவிலுள்ள கானா ஊர்", "பெத்தானியா", "நாசரேத்து", "கப்பர்நகூம்"],
            "correct_index": 0,
            "reference": "John 2:1-11 / யோவான் 2:1-11",
            "explanation_en": "This beginning of signs Jesus did in Cana of Galilee, manifesting His divine glory, and His disciples believed in Him.",
            "explanation_ta": "இயேசு இந்த முதலாம் அற்புதத்தைக் கலிலேயாவிலுள்ள கானா ஊரிலே செய்து, தம்முடைய மகிமையை வெளிப்படுத்தினார்; அவருடைய சீஷர்கள் அவரிடத்தில் விசுவாசம் வைத்தார்கள்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "medium",
            "question_en": "How many baskets of leftover fragments were gathered after Jesus miraculously fed the 5,000 men?",
            "question_ta": "இயேசு அற்புதமாக ஐயாயிரம் பேருக்கு போஷித்த பிறகு, மீதியான துண்டுகள் எத்தனை கூடைகள் எடுக்கப்பட்டன?",
            "options_en": ["Twelve baskets", "Seven baskets", "Ten baskets", "Three baskets"],
            "options_ta": ["பன்னிரண்டு கூடைகள்", "ஏழு கூடைகள்", "பத்து கூடைகள்", "மூன்று கூடைகள்"],
            "correct_index": 0,
            "reference": "Matthew 14:20 / மத்தேயு 14:20",
            "explanation_en": "They all ate and were satisfied, and the disciples picked up twelve basketfuls of broken pieces that were left over.",
            "explanation_ta": "எல்லாரும் சாப்பிட்டுத் திருப்தியடைந்தார்கள்; மீதியான துணிக்கைகளைப் பன்னிரண்டு கூடைகள் நிறைய எடுத்தார்கள்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "easy",
            "question_en": "Whom did Jesus raise back to life in Bethany after he had been in the tomb for four days?",
            "question_ta": "பெத்தானியாவில் நான்கு நாட்கள் கல்லறையில் இருந்தபின் இயேசு யாரை உயிரோடு எழுப்பினார்?",
            "options_en": ["Lazarus", "Jairus's daughter", "The widow's son at Nain", "Tabitha"],
            "options_ta": ["லாசரு", "யவீருவின் மகள்", "நாயீன் ஊர் கைம்பெண்ணின் மகன்", "தபீத்தாள்"],
            "correct_index": 0,
            "reference": "John 11:43-44 / யோவான் 11:43-44",
            "explanation_en": "Jesus called with a loud voice, 'Lazarus, come out!' and he who had died came out bound hand and foot with graveclothes.",
            "explanation_ta": "இயேசு: லாசருவே, வெளியே வா என்று, உரத்த சத்தமாய்க் கூப்பிட்டார். அப்பொழுது, மரித்தவன் வெளியே வந்தான்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "medium",
            "question_en": "When Jesus walked on the water on the Sea of Galilee, which disciple stepped out of the boat to walk toward Him?",
            "question_ta": "கலிலேயாக் கடலில் இயேசு கடலின்மேல் நடந்து வந்தபோது, படவிலிருந்து இறங்கி அவரிடம் நடந்து சென்ற சீஷன் யார்?",
            "options_en": ["Peter", "John", "James", "Andrew"],
            "options_ta": ["பேதுரு", "யோவான்", "யாக்கோபு", "அந்திரேயா"],
            "correct_index": 0,
            "reference": "Matthew 14:28-29 / மத்தேயு 14:28-29",
            "explanation_en": "Peter said, 'Lord, if it is You, tell me to come to You on the water.' And Jesus said, 'Come.' Peter walked on water toward Jesus.",
            "explanation_ta": "பேதுரு அவரை நோக்கி: ஆண்டவரே! நீரேயானால் நான் தண்ணீரின்மேல் நடந்து உம்மிடத்தில் வரக் கட்டளையிடும் என்றான். அவர்: வா என்றார். பேதுரு படவை விட்டு இறங்கி இயேசுவினிடத்தில் போனான்."
        },
        {
            "category": "miracles_parables",
            "difficulty": "hard",
            "question_en": "In Luke 17, how many lepers did Jesus cleanse on the way to Jerusalem, and how many returned to praise God?",
            "question_ta": "லூக்கா 17-ல், எருசலேமுக்குப் போகும் வழியில் இயேசு எத்தனை குஷ்டரோகிகளைச் சொஸ்தமாக்கினார், அவர்களில் எத்தனை பேர் தேவனை மகிமைப்படுத்த திரும்பி வந்தார்கள்?",
            "options_en": ["Ten cleansed, one returned", "Seven cleansed, two returned", "Ten cleansed, five returned", "Twelve cleansed, one returned"],
            "options_ta": ["பத்து பேர் சொஸ்தமானார்கள், ஒருவர் திரும்பி வந்தார்", "ஏழு பேர் சொஸ்தமானார்கள், இருவர் திரும்பி வந்தார்கள்", "பத்து பேர் சொஸ்தமானார்கள், ஐந்து பேர் திரும்பி வந்தார்கள்", "பன்னிரண்டு பேர் சொஸ்தமானார்கள், ஒருவர் திரும்பி வந்தார்"],
            "correct_index": 0,
            "reference": "Luke 17:15-17 / லூக்கா 17:15-17",
            "explanation_en": "Ten men with leprosy were healed as they went, but only one—a Samaritan—turned back, praising God with a loud voice and thanking Jesus.",
            "explanation_ta": "பத்துப் பேர் சொஸ்தமானார்கள்; அவர்களில் ஒருவன் தனக்குச் சுகமானதைக் கண்டு, உரத்த சத்தத்தோடே தேவனை மகிமைப்படுத்தி திரும்பி வந்து நன்றி செலுத்தினான்."
        }
    ],
    "prophets": [
        {
            "category": "heroes",
            "difficulty": "easy",
            "question_en": "Which prophet was swallowed by a great fish when running away from God's call to go to Nineveh?",
            "question_ta": "நினிவேக்குச் செல்லும்படி தேவன் அழைத்தபோது, அதைவிட்டு ஓடிப்போய் பெரிய மீனினால் விழுங்கப்பட்ட தீர்க்கதரிசி யார்?",
            "options_en": ["Jonah", "Elijah", "Jeremiah", "Amos"],
            "options_ta": ["யோனா", "எலியா", "எரேமியா", "ஆமோஸ்"],
            "correct_index": 0,
            "reference": "Jonah 1:17 / யோனா 1:17",
            "explanation_en": "The Lord provided a huge fish to swallow Jonah, and Jonah was in the belly of the fish three days and three nights.",
            "explanation_ta": "யோனாவை விழுங்கும்படி ஒரு பெரிய மீனை கர்த்தர் கட்டளையிட்டிருந்தார்; யோனா மூன்று இரவும் மூன்று பகலும் அந்த மீனின் வயிற்றில் இருந்தான்."
        },
        {
            "category": "heroes",
            "difficulty": "medium",
            "question_en": "On which mountain did Elijah challenge the 450 prophets of Baal to a contest of fire?",
            "question_ta": "எலியா தீர்க்கதரிசி பாகாலின் 450 தீர்க்கதரிசிகளுக்கு அக்கினி மூலம் சவால் விட்ட மலை எது?",
            "options_en": ["Mount Carmel", "Mount Sinai", "Mount Horeb", "Mount Nebo"],
            "options_ta": ["கர்மேல் மலை", "சீனாய் மலை", "ஓரேப் மலை", "நேபோ மலை"],
            "correct_index": 0,
            "reference": "1 Kings 18:19-20 / 1 இராஜாக்கள் 18:19-20",
            "explanation_en": "Elijah gathered Israel and the 450 prophets of Baal to Mount Carmel, where God answered Elijah's prayer by sending fire from heaven.",
            "explanation_ta": "இஸ்ரவேலர் எல்லாரையும் பாகாலின் நானூற்றைம்பது தீர்க்கதரிசிகளையும் கர்மேல் மலையிலே என்னிடத்தில் கூட்டிச்சேர்க்கும் என்று எலியா சவால் விட்டான்."
        },
        {
            "category": "heroes",
            "difficulty": "medium",
            "question_en": "Which Old Testament prophet had a vision of the valley of dry bones coming back to life?",
            "question_ta": "பழைய ஏற்பாட்டில் உலர்ந்த எலும்புகள் நிறைந்த பள்ளத்தாக்கு மீண்டும் உயிர்பெற்று எழும் தரிசனத்தைக் கண்ட தீர்க்கதரிசி யார்?",
            "options_en": ["Ezekiel", "Isaiah", "Daniel", "Micah"],
            "options_ta": ["எசேக்கியேல்", "ஏசாயா", "தானியேல்", "மீகா"],
            "correct_index": 0,
            "reference": "Ezekiel 37:1-10 / எசேக்கியேல் 37:1-10",
            "explanation_en": "God set Ezekiel in the midst of a valley full of dry bones and commanded him to prophesy breath into them so they stood as a vast army.",
            "explanation_ta": "கர்த்தருடைய ஆவி எசேக்கியேலை உலர்ந்த எலும்புகள் நிறைந்த ஒரு பள்ளத்தாக்கின் நடுவிலே கொண்டுபோய் நிறுத்தி, தீர்க்கதரிசனம் உரைக்கச் சொன்னார்."
        },
        {
            "category": "heroes",
            "difficulty": "easy",
            "question_en": "Which prophet was thrown into a den of lions for praying to God instead of the king?",
            "question_ta": "ராஜாவைத் தவிர வேறு தேவனிடம் ஜெபம் பண்ணக்கூடாது என்ற கட்டளையை மீறி கர்த்தரிடம் ஜெபித்ததால் சிங்கங்களின் கெபியில் போடப்பட்ட தீர்க்கதரிசி யார்?",
            "options_en": ["Daniel", "Hosea", "Habakkuk", "Joel"],
            "options_ta": ["தானியேல்", "ஓசியா", "ஆபகூக்", "யோவேல்"],
            "correct_index": 0,
            "reference": "Daniel 6:16 / தானியேல் 6:16",
            "explanation_en": "King Darius ordered Daniel thrown into the lions' den, but God sent His angel to shut the lions' mouths because Daniel was found blameless.",
            "explanation_ta": "ராஜா கட்டளையிட்டதின்பேரில், அவர்கள் தானியேலைக் கொண்டுவந்து, அவனைச் சிங்கங்களின் கெபியிலே போட்டார்கள்; ஆனால் தேவன் தம்முடைய தூதனை அனுப்பி சிங்கங்களின் வாயைக் கட்டினார்."
        },
        {
            "category": "heroes",
            "difficulty": "hard",
            "question_en": "Which weeping prophet authored both a major prophetic book and the Book of Lamentations?",
            "question_ta": "கண்ணீரின் தீர்க்கதரிசி என்று அழைக்கப்பட்டு, தமது பெயரிலான தீர்க்கதரிசன புஸ்தகத்தையும் புலம்பல் புஸ்தகத்தையும் எழுதியவர் யார்?",
            "options_en": ["Jeremiah", "Zechariah", "Malachi", "Obadiah"],
            "options_ta": ["எரேமியா", "சகரியா", "மல்கியா", "ஒபதியா"],
            "correct_index": 0,
            "reference": "Jeremiah 9:1; Lamentations 1:1 / எரேமியா 9:1; புலம்பல் 1:1",
            "explanation_en": "Jeremiah is renowned as the weeping prophet who wept over the rebellion and impending destruction of Jerusalem and authored Lamentations.",
            "explanation_ta": "எரேமியா தீர்க்கதரிசி எருசலேமின் அழிவைக் குறித்து இரவும் பகலும் கண்ணீர் வடித்து, புலம்பல் புஸ்தகத்தையும் எழுதினார்."
        }
    ],
    "exodus": [
        {
            "category": "old_testament",
            "difficulty": "easy",
            "question_en": "How did God speak to Moses when calling him at Mount Horeb?",
            "question_ta": "ஓரேப் மலையில் மோசேயை அழைத்தபோது தேவன் எவ்வாறு அவரோடு பேசினார்?",
            "options_en": ["Through a burning bush that was not consumed", "In a gentle whisper", "Through an earthquake", "Through a fleece of wool"],
            "options_ta": ["முட்செடி பற்றியெரிந்தும் வெந்துபோகாத அக்கினி நடுவிலிருந்து", "மெல்லிய சத்தத்தினால்", "பூமி அதிர்ச்சியினால்", "ஆட்டுத் தோலினால்"],
            "correct_index": 0,
            "reference": "Exodus 3:2-4 / யாத்திராகமம் 3:2-4",
            "explanation_en": "The angel of the Lord appeared to Moses in flames of fire from within a bush; the bush burned with fire but was not consumed.",
            "explanation_ta": "ஒரு முட்செடியின் நடுவிலிருந்து புறப்பட்ட அக்கினிஜுவாலையிலே கர்த்தருடைய தூதனானவர் அவனுக்குத் தரிசனமானார்; முட்செடி பற்றியெரிந்தும் வெந்துபோகாமலிருந்தது."
        },
        {
            "category": "old_testament",
            "difficulty": "medium",
            "question_en": "What did the Israelites put on their doorposts so the angel of death would pass over their homes in Egypt?",
            "question_ta": "எகிப்தில் சங்கார தூதன் தங்கள் வீடுகளைக் கடந்துபோகும்படி இஸ்ரவேலர் நிலைக் கால்களில் பூசியது என்ன?",
            "options_en": ["The blood of an unblemished lamb", "Olive oil", "Frankincense", "Salt water"],
            "options_ta": ["பழுதற்ற ஆட்டுக்குட்டியின் இரத்தம்", "ஒலிவ எண்ணெய்", "தூபவர்க்கம்", "உப்பு நீர்"],
            "correct_index": 0,
            "reference": "Exodus 12:7, 13 / யாத்திராகமம் 12:7, 13",
            "explanation_en": "They put the blood of the Passover lamb on the sides and tops of the doorframes, and when God saw the blood, He passed over them.",
            "explanation_ta": "ஆட்டுக்குட்டியின் இரத்தத்தில் கொஞ்சம் எடுத்து, நிலைக் கால்களிலும் நிலைக் கால்களின் மேற்சட்டத்திலும் பூசக்கடவர்கள்; நான் இரத்தத்தைக் கண்டு உங்களைக் கடந்துபோவேன்."
        },
        {
            "category": "old_testament",
            "difficulty": "easy",
            "question_en": "Which sea did God part through Moses so the Israelites could walk through on dry land?",
            "question_ta": "இஸ்ரவேலர் வெட்டாந்தரையின் வழியாய் நடந்துபோகும்படி மோசே மூலமாக தேவன் பிளந்த கடல் எது?",
            "options_en": ["The Red Sea", "The Dead Sea", "The Sea of Galilee", "The Mediterranean Sea"],
            "options_ta": ["செங்கடல்", "சாக்கடல்", "கலிலேயாக் கடல்", "மத்தியதரைக்கடல்"],
            "correct_index": 0,
            "reference": "Exodus 14:21-22 / யாத்திராகமம் 14:21-22",
            "explanation_en": "Moses stretched out his hand over the sea, and the Lord drove the sea back with a strong east wind and turned it into dry land.",
            "explanation_ta": "மோசே தன் கையைச் சமுத்திரத்தின்மேல் நீட்டினான்; அப்பொழுது கர்த்தர் இரவு முழுவதும் பலத்த கீழ்காற்றினால் சமுத்திரம் பின்னிடச் செய்து, சமுத்திரத்தை வெட்டாந்தரையாக்கினார்."
        },
        {
            "category": "old_testament",
            "difficulty": "medium",
            "question_en": "What bread from heaven did God rain down daily to feed the Israelites in the wilderness?",
            "question_ta": "வனாந்தரத்திலே இஸ்ரவேலரை போஷிக்கும்படி தேவன் தினமும் வானத்திலிருந்து பொழிந்த அப்பம் எது?",
            "options_en": ["Manna", "Unleavened barley cakes", "Showbread", "Wafers of figs"],
            "options_ta": ["மன்னா", "புளிப்பில்லாத வாற்கோதுமை அப்பம்", "சமுகத்தப்பம்", "அத்திப்பழ அடை"],
            "correct_index": 0,
            "reference": "Exodus 16:15, 31 / யாத்திராகமம் 16:15, 31",
            "explanation_en": "The Israelites called the bread manna. It was white like coriander seed and tasted like wafers made with honey.",
            "explanation_ta": "இஸ்ரவேல் புத்திரர் அதற்கு மன்னா என்று பேரிட்டார்கள்; அது கொத்துமல்லி விதையளவாயும், வெண்மையாயும், தேன் கலந்த பணியாரத்தின் ருசியாயும் இருந்தது."
        },
        {
            "category": "old_testament",
            "difficulty": "hard",
            "question_en": "On which mountain did Moses receive the Two Stone Tablets inscribed with the Ten Commandments?",
            "question_ta": "பத்துக்கற்பனைகள் எழுதப்பட்ட இரண்டு கற்பலகைகளை மோசே பெற்றுக்கொண்ட மலை எது?",
            "options_en": ["Mount Sinai", "Mount Ararat", "Mount Hermon", "Mount Moriah"],
            "options_ta": ["சீனாய் மலை", "அரராத் மலை", "எர்மோன் மலை", "மோரியா மலை"],
            "correct_index": 0,
            "reference": "Exodus 19:20; 31:18 / யாத்திராகமம் 19:20; 31:18",
            "explanation_en": "The Lord descended on Mount Sinai and gave Moses the two tablets of the Testimony, tablets of stone inscribed by the finger of God.",
            "explanation_ta": "கர்த்தர் சீனாய் மலையிலிறங்கி, தேவனுடைய விரலினால் எழுதப்பட்ட சாட்சியின் பலகைகளாகிய இரண்டு கற்பலகைகளை மோசேக்குக் கொடுத்தார்."
        }
    ],
    "sermon": [
        {
            "category": "gospels",
            "difficulty": "easy",
            "question_en": "In the Beatitudes, who did Jesus say will be comforted?",
            "question_ta": "மலைப்பிரசங்கத்தின் பாக்கியங்களில், ஆறுதல் அடைவார்கள் என்று இயேசு யாரைக் கூறினார்?",
            "options_en": ["Those who mourn", "The meek", "The peacemakers", "The merciful"],
            "options_ta": ["துயரப்படுகிறவர்கள்", "சாந்தகுணமுள்ளவர்கள்", "சமாதானம் பண்ணுகிறவர்கள்", "இரக்கமுள்ளவர்கள்"],
            "correct_index": 0,
            "reference": "Matthew 5:4 / மத்தேயு 5:4",
            "explanation_en": "Jesus taught: 'Blessed are those who mourn, for they shall be comforted.'",
            "explanation_ta": "இயேசு: துயரப்படுகிறவர்கள் பாக்கியவான்கள்; அவர்கள் ஆறுதலடைவார்கள் என்றார்."
        },
        {
            "category": "gospels",
            "difficulty": "medium",
            "question_en": "In the Sermon on the Mount, Jesus called His followers what two metaphors in the world?",
            "question_ta": "மலைப்பிரசங்கத்தில், தம்மைப் பின்பற்றுகிறவர்களை உலகத்திற்கு என்ன இரண்டு உவமைகளாக இயேசு அழைத்தார்?",
            "options_en": ["Salt of the earth and light of the world", "Shepherds and vine-dressers", "Branches and roots", "Shields and spears"],
            "options_ta": ["பூமிக்கு உப்பும் உலகத்திற்கு வெளிச்சமும்", "மேய்ப்பர்களும் திராட்சைத்தோட்டக்காரர்களும்", "கிளைகளும் வேர்களும்", "கேடகமும் ஈட்டியும்"],
            "correct_index": 0,
            "reference": "Matthew 5:13-14 / மத்தேயு 5:13-14",
            "explanation_en": "Jesus proclaimed: 'You are the salt of the earth... You are the light of the world. A city that is set on a hill cannot be hidden.'",
            "explanation_ta": "நீங்கள் பூமிக்கு உப்பாயிருக்கிறீர்கள்... நீங்கள் உலகத்துக்கு வெளிச்சமாயிருக்கிறீர்கள்; மலையின்மேல் இருக்கிற பட்டணம் மறைந்திருக்கமாட்டாது."
        },
        {
            "category": "gospels",
            "difficulty": "easy",
            "question_en": "What model prayer did Jesus teach His disciples during the Sermon on the Mount?",
            "question_ta": "மலைப்பிரசங்கத்தின்போது இயேசு தம்முடைய சீஷர்களுக்குக் கற்றுக்கொடுத்த மாதிரி ஜெபம் எது?",
            "options_en": ["The Lord's Prayer (Our Father in heaven)", "The Prayer of Jabez", "The Aaronic Blessing", "The Magnificat"],
            "options_ta": ["கர்த்தர் கற்பித்த ஜெபம் (பரமண்டலங்களிலிருக்கிற எங்கள் பிதாவே)", "யாபேசின் ஜெபம்", "ஆரோனின் ஆசீர்வாதம்", "மரியாளின் ஸ்தோத்திரப் பாடல்"],
            "correct_index": 0,
            "reference": "Matthew 6:9-13 / மத்தேயு 6:9-13",
            "explanation_en": "Jesus instructed: 'In this manner, therefore, pray: Our Father in heaven, hallowed be Your name...'",
            "explanation_ta": "நீங்கள் ஜெபம்பண்ணவேண்டிய விதமாவது: பரமண்டலங்களிலிருக்கிற எங்கள் பிதாவே, உம்முடைய நாமம் பரிசுத்தப்படுவதாக..."
        },
        {
            "category": "gospels",
            "difficulty": "medium",
            "question_en": "According to Matthew 6:33, what should believers seek first before worrying about food and clothing?",
            "question_ta": "மத்தேயு 6:33-ன் படி, உணவு மற்றும் உடையைக் குறித்து கவலைப்படுவதற்கு முன்பாக விசுவாசிகள் முதலாவது எதைத் தேட வேண்டும்?",
            "options_en": ["The Kingdom of God and His righteousness", "Earthly wisdom and wealth", "The approval of religious leaders", "A safe dwelling place"],
            "options_ta": ["தேவனுடைய ராஜ்யத்தையும் அவருடைய நீதியையும்", "பூமிக்குரிய ஞானத்தையும் ஐசுவரியத்தையும்", "மதத் தலைவர்களின் பாராட்டை", "பாதுகாப்பான உறைவிடத்தை"],
            "correct_index": 0,
            "reference": "Matthew 6:33 / மத்தேயு 6:33",
            "explanation_en": "'Seek first the kingdom of God and His righteousness, and all these things shall be added to you.'",
            "explanation_ta": "முதலாவது தேவனுடைய ராஜ்யத்தையும் அவருடைய நீதியையும் தேடுங்கள்; அப்பொழுது இவைகளெல்லாம் உங்களுக்குக் கூடக் கொடுக்கப்படும்."
        },
        {
            "category": "gospels",
            "difficulty": "medium",
            "question_en": "At the conclusion of the Sermon on the Mount, the wise man built his house on what foundation?",
            "question_ta": "மலைப்பிரசங்கத்தின் முடிவில், புத்தியுள்ள மனுஷன் தன் வீட்டை எந்த அஸ்திபாரத்தின்மேல் கட்டினான்?",
            "options_en": ["Upon the Rock", "Upon the Sand", "Upon fertile river silt", "Upon wooden pillars"],
            "options_ta": ["கன்மலையின் மேல்", "மணலின் மேல்", "வளமான ஆற்றுப்படுகையின் மேல்", "மரத் தூண்களின் மேல்"],
            "correct_index": 0,
            "reference": "Matthew 7:24-25 / மத்தேயு 7:24-25",
            "explanation_en": "Everyone who hears these words of Mine and does them is like a wise man who built his house on the rock, which stood firm against wind and rain.",
            "explanation_ta": "என் வார்த்தைகளைக் கேட்டு, இவைகளின்படி செய்கிறவன் எவனோ, அவனைக் கன்மலையின்மேல் தன் வீட்டைக் கட்டின புத்தியுள்ள மனுஷனுக்கு ஒப்பிடுவேன்."
        }
    ],
    "fruit": [
        {
            "category": "general",
            "difficulty": "easy",
            "question_en": "In Galatians 5:22-23, what is the very first characteristic listed in the Fruit of the Spirit?",
            "question_ta": "கலாத்தியர் 5:22-23-ல், ஆவியின் கனியின் முதல் குணாதிசயமாகக் கூறப்பட்டுள்ளது எது?",
            "options_en": ["Love", "Joy", "Peace", "Patience"],
            "options_ta": ["அன்பு", "சந்தோஷம்", "சமாதானம்", "நீடியபொறுமை"],
            "correct_index": 0,
            "reference": "Galatians 5:22 / கலாத்தியர் 5:22",
            "explanation_en": "The fruit of the Spirit is love, joy, peace, longsuffering, kindness, goodness, faithfulness, gentleness, self-control.",
            "explanation_ta": "ஆவியின் கனியோ: அன்பு, சந்தோஷம், சமாதானம், நீடியபொறுமை, தயவு, நற்குணம், விசுவாசம், சாந்தம், இச்சையடக்கம்."
        },
        {
            "category": "general",
            "difficulty": "medium",
            "question_en": "How many distinct virtues make up the singular Fruit of the Spirit in Paul's letter to the Galatians?",
            "question_ta": "பவுல் கலாத்தியருக்கு எழுதிய நிருபத்தில், ஆவியின் ஒற்றைக் கனி எத்தனை நற்பண்புகளால் விவரிக்கப்பட்டுள்ளது?",
            "options_en": ["Nine virtues", "Seven virtues", "Twelve virtues", "Ten virtues"],
            "options_ta": ["ஒன்பது நற்பண்புகள்", "ஏழு நற்பண்புகள்", "பன்னிரண்டு நற்பண்புகள்", "பத்து நற்பண்புகள்"],
            "correct_index": 0,
            "reference": "Galatians 5:22-23 / கலாத்தியர் 5:22-23",
            "explanation_en": "There are nine harmonious aspects: love, joy, peace, longsuffering, kindness, goodness, faithfulness, gentleness, self-control.",
            "explanation_ta": "அன்பு, சந்தோஷம், சமாதானம், நீடியபொறுமை, தயவு, நற்குணம், விசுவாசம், சாந்தம், இச்சையடக்கம் ஆகிய ஒன்பது நற்குணங்கள்."
        },
        {
            "category": "general",
            "difficulty": "easy",
            "question_en": "In John 15, Jesus said, 'I am the vine, you are the branches.' Who is the True Vinedresser?",
            "question_ta": "யோவான் 15-ல், 'நான் மெய்யான திராட்சச்செடி, நீங்கள் கொடிகள்' என்றார் இயேசு. திராட்சத்தோட்டக்காரர் யார்?",
            "options_en": ["God the Father", "The Holy Spirit", "John the Baptist", "The Apostles"],
            "options_ta": ["பிதாவாகிய தேவன்", "பரிசுத்த ஆவியானவர்", "யோவான் ஸ்நானகன்", "அப்போஸ்தலர்கள்"],
            "correct_index": 0,
            "reference": "John 15:1 / யோவான் 15:1",
            "explanation_en": "Jesus declared: 'I am the true vine, and My Father is the vinedresser. Every branch in Me that does not bear fruit He takes away.'",
            "explanation_ta": "நான் மெய்யான திராட்சச்செடி, என் பிதா திராட்சத்தோட்டக்காரர்; என்னில் கனிகொடாதிருக்கிற கொடி எதுவோ, அதை அவர் அறுத்துப்போடுகிறார்."
        },
        {
            "category": "general",
            "difficulty": "medium",
            "question_en": "What is the final virtue listed in the Fruit of the Spirit in Galatians 5:23?",
            "question_ta": "கலாத்தியர் 5:23-ல் ஆவியின் கனியில் இறுதியாகக் கூறப்பட்டுள்ள நற்குணம் எது?",
            "options_en": ["Self-control (Temperance)", "Kindness", "Faithfulness", "Gentleness"],
            "options_ta": ["இச்சையடக்கம்", "தயவு", "விசுவாசம்", "சாந்தம்"],
            "correct_index": 0,
            "reference": "Galatians 5:23 / கலாத்தியர் 5:23",
            "explanation_en": "The final virtue is self-control (temperance). Against such things there is no law.",
            "explanation_ta": "சாந்தம், இச்சையடக்கம்; இப்படிப்பட்டவைகளுக்கு விரோதமான பிரமாணம் ஒன்றுமில்லை."
        },
        {
            "category": "general",
            "difficulty": "medium",
            "question_en": "In Matthew 7:16, how did Jesus say believers will recognize genuine prophets from wolves in sheep's clothing?",
            "question_ta": "மத்தேயு 7:16-ல், ஆட்டுத்தோலைப் போர்த்துக்கொண்டு வரும் பொய் தீர்க்கதரிசிகளை விசுவாசிகள் எவ்வாறு அறிந்துகொள்வார்கள் என்று இயேசு சொன்னார்?",
            "options_en": ["By their fruits", "By their signs and wonders", "By the loudness of their speech", "By their fine garments"],
            "options_ta": ["அவர்களுடைய கனிகளினாலே", "அவர்களுடைய அடையாளங்களினாலும் அற்புதங்களினாலும்", "அவர்களின் உரத்த பேச்சினால்", "அவர்களது விலையேறப்பெற்ற ஆடைகளினால்"],
            "correct_index": 0,
            "reference": "Matthew 7:16, 20 / மத்தேயு 7:16, 20",
            "explanation_en": "Jesus said: 'You will know them by their fruits. Do men gather grapes from thornbushes or figs from thistles?'",
            "explanation_ta": "அவர்களுடைய கனிகளினாலே அவர்களை அறிவீர்கள். முட்செடிகளில் திராட்சப்பழங்களையும், முட்பூண்டுகளில் அத்திப்பழங்களையும் பறிக்கிறார்களா?"
        }
    ]
}


def _match_topic_key(topic: str) -> str:
    """Matches user input topic string to the most relevant curated topic bank."""
    t = topic.lower().strip()
    if any(k in t for k in ["parable", "sower", "prodigal", "samaritan", "virgin", "talents", "உவமை"]):
        return "parables"
    if any(k in t for k in ["miracle", "wine", "heal", "water", "lazarus", "leper", "feed", "அற்புதம்"]):
        return "miracles"
    if any(k in t for k in ["prophet", "elijah", "jonah", "ezekiel", "daniel", "jeremiah", "isaiah", "தீர்க்கதரிசி"]):
        return "prophets"
    if any(k in t for k in ["exodus", "moses", "sea", "egypt", "plague", "manna", "sinai", "commandment", "யாத்திராகமம்", "மோசே"]):
        return "exodus"
    if any(k in t for k in ["sermon", "mount", "beatitude", "salt", "light", "rock", "sand", "மலைப்பிரசங்கம்"]):
        return "sermon"
    if any(k in t for k in ["fruit", "spirit", "love", "joy", "peace", "galatians", "vine", "கனி", "ஆவி"]):
        return "fruit"
    # Default cycle
    keys = list(CURATED_AI_QUIZ_TOPICS.keys())
    return random.choice(keys)


def get_local_fallback_questions(topic: str, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
    """Returns grounded, curated fallback questions matching requested topic and count."""
    matched_key = _match_topic_key(topic)
    pool = list(CURATED_AI_QUIZ_TOPICS.get(matched_key, []))

    # If count requested is larger than single pool, merge other pools
    if len(pool) < count:
        for k, qs in CURATED_AI_QUIZ_TOPICS.items():
            if k != matched_key:
                pool.extend(qs)

    random.shuffle(pool)
    selected = pool[:count]

    # Assign clean sequence IDs
    result = []
    for idx, q in enumerate(selected, start=1):
        item = dict(q)
        item["id"] = idx
        if difficulty in ("easy", "medium", "hard"):
            item["difficulty"] = difficulty
        result.append(item)

    return result


async def generate_quiz_questions_ai(
    topic: str,
    count: int = 5,
    difficulty: str = "medium",
    language: str = "bilingual",
) -> List[Dict[str, Any]]:
    """
    Generates dynamic biblical quiz questions on custom topic using the Ask Bible AI plugin.
    Guaranteed to return valid question list matching the Holy Bible quiz schema.
    """
    count = max(1, min(15, count))
    topic_clean = topic.strip() or "Parables of Jesus"

    # If AI service is disabled or in simulation mode, return curated fallback questions
    if not ai_config.enabled or ai_config.simulation_mode:
        logger.info(f"[QuizAI] Simulation/Offline mode active. Generating curated questions for '{topic_clean}'.")
        return get_local_fallback_questions(topic_clean, count, difficulty)

    system_prompt = (
        "You are an expert biblical scholar, theologian, and quiz author. "
        "Your task is to generate multiple-choice Bible trivia questions based on the Holy Bible.\n"
        "RULES:\n"
        "1. Strictly output ONLY a valid JSON array of objects. Do not include markdown code fences or any conversational greeting.\n"
        "2. Each question object MUST contain these exact keys:\n"
        "   - 'id': integer sequence starting at 1\n"
        "   - 'category': one of 'gospels', 'old_testament', 'heroes', 'miracles_parables', 'general'\n"
        "   - 'difficulty': 'easy', 'medium', or 'hard'\n"
        "   - 'question_en': clear, accurate question in English\n"
        "   - 'question_ta': faithful, reverent Tamil translation of the question\n"
        "   - 'options_en': list of exactly 4 English options\n"
        "   - 'options_ta': list of exactly 4 Tamil options matching options_en\n"
        "   - 'correct_index': integer (0, 1, 2, or 3) indicating the correct answer\n"
        "   - 'reference': exact scripture reference in format 'Book Chapter:Verse / தமிழ்_புத்தகம் அதிகாரம்:வசனம்'\n"
        "   - 'explanation_en': concise 1-2 sentence biblical explanation in English\n"
        "   - 'explanation_ta': concise 1-2 sentence biblical explanation in Tamil\n"
        "3. Ensure scripture citations and doctrinal accuracy match the Holy Bible."
    )

    user_prompt = (
        f"Generate {count} distinct Bible quiz questions on the topic: '{topic_clean}'.\n"
        f"Difficulty: {difficulty}.\n"
        f"Format: Strict JSON array of {count} question objects."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        raw_res = await ai_service.client.generate_chat_completion(
            messages=messages,
            model=ai_config.model,
            temperature=0.3,
            max_tokens=2048,
        )

        content = raw_res["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if LLM wrapped in ```json ... ```
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content).strip()

        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) > 0:
            valid_questions = []
            for idx, q in enumerate(parsed[:count], start=1):
                if (
                    "question_en" in q
                    and "options_en" in q
                    and len(q.get("options_en", [])) == 4
                    and "correct_index" in q
                ):
                    q["id"] = idx
                    q.setdefault("category", "general")
                    q.setdefault("difficulty", difficulty)
                    q.setdefault("question_ta", q.get("question_en", ""))
                    q.setdefault("options_ta", q.get("options_en", []))
                    q.setdefault("reference", "Holy Scripture / திருவேதாகமம்")
                    q.setdefault("explanation_en", "Correct according to the Holy Scriptures.")
                    q.setdefault("explanation_ta", "திருவேதாகமத்தின்படி சரியானது.")
                    valid_questions.append(q)

            if valid_questions:
                logger.info(f"[QuizAI] Successfully generated {len(valid_questions)} AI questions for '{topic_clean}'.")
                return valid_questions

    except Exception as e:
        logger.warning(f"[QuizAI] LLM question generation failed or invalid JSON: {e}. Falling back to curated bank.")

    # Graceful fallback to curated questions
    return get_local_fallback_questions(topic_clean, count, difficulty)


async def explain_quiz_question_ai(
    question_en: str,
    question_ta: str,
    options_en: List[str],
    options_ta: List[str],
    chosen_index: int,
    correct_index: int,
    reference: str,
    base_explanation_en: str,
    base_explanation_ta: str,
) -> Dict[str, Any]:
    """
    Generates deep theological tutoring and spiritual reflections for a specific quiz question.
    """
    correct_text_en = options_en[correct_index] if 0 <= correct_index < len(options_en) else ""
    correct_text_ta = options_ta[correct_index] if 0 <= correct_index < len(options_ta) else ""

    user_choice_en = options_en[chosen_index] if 0 <= chosen_index < len(options_en) else "None / Time Out"
    is_correct = (chosen_index == correct_index)

    prompt = (
        f"As a wise, reverent Bible Tutor, provide an insightful theological explanation for this scripture quiz question.\n\n"
        f"Question (English): {question_en}\n"
        f"Question (Tamil): {question_ta}\n"
        f"Correct Answer: {correct_text_en} ({correct_text_ta})\n"
        f"Scripture Reference: {reference}\n"
        f"User Answered: {user_choice_en} (Result: {'Correct' if is_correct else 'Incorrect'})\n"
        f"Standard Note: {base_explanation_en} / {base_explanation_ta}\n\n"
        f"Explain in 2-3 warm, clear paragraphs:\n"
        f"1. Why this biblical answer is true and its contextual setting in scripture.\n"
        f"2. The deeper theological significance and spiritual meaning.\n"
        f"3. Practical application for Christian life and faith today.\n"
        f"Provide the response in English, followed by a faithful Tamil reflection under 'ஆவிக்குரிய விளக்கம்'."
    )

    # Check simulation mode
    if not ai_config.enabled or ai_config.simulation_mode:
        simulated_tutoring = (
            f"**Biblical Reflection on {reference}**\n\n"
            f"The correct answer is **{correct_text_en}**.\n\n"
            f"{base_explanation_en}\n\n"
            f"**Spiritual Insight:** In sacred scripture, every event and parable reveals God's eternal covenant of grace, righteousness, and redeeming love. "
            f"When we reflect on {reference}, we are reminded to trust wholeheartedly in God's promises and walk in obedience.\n\n"
            f"---\n"
            f"**ஆவிக்குரிய விளக்கம் ({reference}):**\n\n"
            f"சரியான பதில்: **{correct_text_ta}**.\n\n"
            f"{base_explanation_ta}\n\n"
            f"வேதாகம சத்தியங்களை நாம் விசுவாசத்தோடு தியானிக்கும்போது, பரிசுத்த ஆவியானவர் நம்முடைய ஆவிக்குரிய கண்களைத் திறந்து, "
            f"அனுதின வாழ்க்கையில் கர்த்தருக்குப் பிரியமாய் வாழ நமக்கு உதவி செய்கிறார்."
        )
        return {
            "status": "ok",
            "reference": reference,
            "tutoring": simulated_tutoring,
            "is_correct": is_correct,
            "mode": "simulation",
        }

    try:
        raw_res = await ai_service.client.generate_chat_completion(
            messages=[
                {"role": "system", "content": "You are a gracious, doctrinally sound Christian Bible tutor."},
                {"role": "user", "content": prompt},
            ],
            model=ai_config.model,
            temperature=0.3,
            max_tokens=800,
        )
        tutoring_text = raw_res["choices"][0]["message"]["content"].strip()
        return {
            "status": "ok",
            "reference": reference,
            "tutoring": tutoring_text,
            "is_correct": is_correct,
            "mode": "live",
        }
    except Exception as e:
        logger.warning(f"[QuizAI] AI Tutor explanation failed: {e}. Returning grounded fallback reflection.")
        fallback_tutoring = (
            f"**Theological Reflection on {reference}**\n\n"
            f"The correct answer is **{correct_text_en}** ({correct_text_ta}).\n\n"
            f"{base_explanation_en}\n\n"
            f"**ஆவிக்குரிய விளக்கம்:**\n"
            f"{base_explanation_ta}\n\n"
            f"Scripture Citation: {reference}"
        )
        return {
            "status": "ok",
            "reference": reference,
            "tutoring": fallback_tutoring,
            "is_correct": is_correct,
            "mode": "fallback",
        }
