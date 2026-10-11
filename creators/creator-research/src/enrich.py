import re
W1={'knafaim.ot_by_noy':("נוי","התוכן שמנרמל ולא מפחיד על התפתחות הילד","כניסה לגן"),
'eden_spaiev':("עדן","הרעיונות הפשוטים למשחק ותנועה שאפשר ליישם בבית","כניסה לגן"),
'yeladim_ktanim':("דנה","השילוב של פעילויות, ספרים ומשחקים מהגן ומהבית","אח חדש"),
'etti_haft':("אתי","הגישה של להעצים ילדים דרך משחק","כניסה לגן / כיתה א׳"),
'ima.shir':("שיר","ההומור והאמת על גמילה מחיתולים","גמילה"),
'nataliegaash':("נטלי","ההסברים על יחסי אחים ועל הכנה לאח חדש","אח חדש"),
'hadas.shvat':("הדס","הגישה של משחק חופשי ופשטות בגידול ילדים","משחק חופשי ושגרת ערב"),
'rotem__unger':("רותם","הדרך שבה אבא במשרה מלאה מראה את היום-יום, עם הרבה טבע וטיולים","שגרת ערב"),
'daria_mansour1':("דריה","החיים עם התאומים שמשתפים כאן","אח או אחות"),
'saba.chiche':("סבא צ׳יצ׳ה","הרגעים עם הנכדים","מתנה לנכד או לנכדה"),
'books_are_friends_slp':("אסתי ואושרת","העובדה ששתיכן אמהות וקלינאיות ושכתבתן ספר ילדים","ספר שהילד הוא הגיבור בו"),
'bar.levi.adiel':("בר","הרעיונות למשחק ולמידה בבית עם הקטנטנים","פעילות בבית")}
TOPIC={'Child-dev professional':"התוכן המקצועי והנגיש על התפתחות הילד",'Parent guide / coach':"התוכן על הורות",'Parent':"החיים האמיתיים עם הילדים שמשתפים כאן",'Parent (dad)':"החיים האמיתיים עם הילדים שמשתפים כאן",'Parent (twins)':"החיים האמיתיים עם התאומים שמשתפים כאן",'Parent (single / co-parent / blended)':"הכנות והחיים האמיתיים עם הילדים שמשתפים כאן",'Gan / preschool':"התוכן מהגן",'Family travel & outings':"הרעיונות לטיולים ולבילויים עם ילדים",'Homeschool / alternative ed':"הרעיונות ללמידה ולמשחק בבית",'Elementary & remedial teacher':"התוכן על למידה וקריאה",'Home daycare / childcare':"ההצצה ליום-יום במשפחתון",'Special ed & neurodiversity':"הגישה המכבדת והפרקטית",'Books & reading':"התוכן על ספרים וקריאה",'Community leader / podcaster':"הקהילה שנבנתה כאן",'Grandparent':"הרגעים עם הנכדים",'Screen-free / free play':"הגישה של משחק חופשי",'Bilingual & multicultural':"התוכן על גידול ילדים בכמה שפות"}
def topic(a):
    if a in TOPIC: return TOPIC[a]
    if 'party' in a: return "האווירה בהפעלות ובימי ההולדת"
    if 'photographer' in a: return "התמונות של הילדים והמשפחות"
    if 'activities' in a or 'workshops' in a: return "הרעיונות לפעילויות לילדים"
    return "התוכן שלך"
def moment(role,concept):
    t=(role+' '+concept).lower()
    if re.search(r'potty|diaper|weaning|toilet',t): return "גמילה"
    if re.search(r'sibling',t): return "אח חדש"
    if re.search(r'gan|kindergarten|first grade|grade 1',t): return "כניסה לגן"
    return "גמילה / כניסה לגן / אח חדש"
GREET={'journo_family':'משפחת ג׳ורנו','the_bluepine':'צוות האצטרובל הכחול','beit_hayasmin':'צוות בית היסמין','savta.sulika':'סבתא סוליקה','trainingwheelsclinic':'עדילי וניצן'}
def moment3(role,concept):
    t=(role+' '+concept).lower()
    if re.search(r'potty|napp|dummy|weaning',t): return "גמילה"
    if re.search(r'sibling',t): return "אח חדש"
    if re.search(r'first-grade|first grade',t): return "כניסה לכיתה א׳"
    if re.search(r'\bgan\b|kindergarten|daycare',t): return "כניסה לגן"
    return "גמילה / כניסה לגן / אח חדש"
def enrich(C):
    for c in C:
        h=c['h']
        if h in W1: c['n'],c['l'],c['m']=W1[h]; c['wave']=1; c['own']=1
        else:
            c['n']=GREET.get(h) or c['name'].split()[0]; c['l']=topic(c['arch']); c['m']=moment3(c['role'],c['concept']) if c.get('extra')=='pass3' else moment(c['role'],c['concept']); c['wave']=2; c['own']=0
            pr=c['prac']
            if 'expensive' in pr.lower() or 'Standard paid' in pr or 'management' in c['contact'].lower(): c['wave']=3
