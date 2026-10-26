import difflib
import re
import unicodedata
from typing import Optional

# ── Built-in synonym dictionary ──────────────────────────────────
SYMPTOM_SYNONYMS: dict[str, list[str]] = {
    "fiebre": [
        "fiebre", "temperatura", "calentura", "fiebre alta", "fiebre leve",
        "estoy caliente", "tengo calor", "febrícula", "escalofríos con fiebre",
        "tengo fiebre", "fiebrecita",
    ],
    "tos": [
        "tos", "tos seca", "tos con flema", "tos productiva", "tos con moco",
        "tos con garganta", "tos persistente", "tos perruna", "ataque de tos",
        "tos con sangre", "expectoración", "tos ferina", "tos constante",
        "tos mucho", "tos muchísimo", "tos frecuente", "tos todo el día",
        "estoy tosiendo", "no paro de toser", "tos muchas veces",
    ],
    "dolor de cabeza": [
        "dolor de cabeza", "cefalea", "cabeza", "dolor craneal",
        "dolor en la cabeza", "jaqueca", "migraña", "presión en la cabeza",
        "cabeza pesada", "dolor de sienes", "me duele la cabeza",
        "dolor de cabeza fuerte", "dolor de cabeza leve",
    ],
    "fatiga": [
        "fatiga", "cansancio", "debilidad", "agotamiento", "sin energía",
        "sin fuerzas", "astenia", "decaimiento", "cansado", "agotado",
        "no tengo energía", "me siento débil", "agotamiento extremo",
        "estoy cansado", "estoy agotado", "sin ganas de hacer nada",
        "no tengo fuerzas",
    ],
    "dificultad para respirar": [
        "dificultad para respirar", "falta de aire", "disnea",
        "no puedo respirar", "respiración rápida", "ahogo",
        "respirar mal", "opresión en el pecho", "se me corta la respiración",
        "respiración agitada", "fatiga al respirar", "me falta el aire",
        "respiración dificultosa", "respirar profundo",
    ],
    "dolor de garganta": [
        "dolor de garganta", "garganta irritada", "garganta inflamada",
        "garganta roja", "dolor al tragar", "odinofagia", "garganta",
        "amígdalas inflamadas", "garganta cerrada", "carraspera",
        "me duele la garganta", "tengo la garganta irritada",
        "tengo garganta", "dolor al pasar saliva",
    ],
    "congestión nasal": [
        "congestión nasal", "nariz tapada", "mucosidad", "mocos",
        "nariz congestionada", "no puedo respirar por la nariz",
        "goteo nasal", "rinorrea", "nariz líquida",
        "obstrucción nasal", "flemas en la nariz", "estornudos",
        "estornudar", "me duele la nariz", "tengo la nariz tapada",
        "se me tapo la nariz", "tapada la nariz",
        "nariz obstruida", "moco en la nariz",
    ],
    "escalofríos": [
        "escalofríos", "temblores", "tiritona", "sensación de frío",
        "tiritar", "pálpito de frío", "piel de gallina", "me da frío",
        "estoy temblando de frío",
    ],
    "dolor muscular": [
        "dolor muscular", "mialgia", "dolor en los músculos",
        "cuerpo cortado", "dolor corporal", "dolor en el cuerpo",
        "me duele todo el cuerpo", "dolor generalizado",
        "dolor de piernas", "dolor de brazos", "agujetas",
        "cuerpo adolorido", "me duele el cuerpo",
    ],
    "pérdida del gusto": [
        "pérdida del gusto", "ageusia", "no sé por comida",
        "no siento el sabor", "perdí el gusto", "comida sin sabor",
        "sin sabor", "no percibo sabores", "no sé a nada la comida",
        "todo sabe igual",
    ],
    "pérdida del olfato": [
        "pérdida del olfato", "anosmia", "no huelo nada",
        "perdí el olfato", "sin olfato", "no percibo olores",
        "no siento olores", "no huele nada",
    ],
    "náuseas": [
        "náuseas", "ganas de vomitar", "arcadas", "asco", "estómago revuelto",
        "mal del estómago", "basca", "mareo con náuseas",
        "tengo náuseas", "me da asco la comida", "estómago mal",
    ],
    "vómito": [
        "vómito", "vomitar", "emesis", "devolver", "echar la comida",
        "vómitos", "explosión estomacal", "estoy vomitando",
        "he vomitado", "voy a vomitar",
    ],
    "diarrea": [
        "diarrea", "heces sueltas", "caca líquida", "deposiciones líquidas",
        "evacuaciones frecuentes", "estar suelto", "descomposición",
        "aflojamiento", "correntada", "estómago suelto", "mucha diarrea",
        "estoy con diarrea", "ida al baño frecuente",
    ],
    "dolor abdominal": [
        "dolor abdominal", "dolor de estómago", "dolor de barriga",
        "dolor intestinal", "cólico", "retorcijón", "punzada en el abdomen",
        "dolor de panza", "estómago inflamado", "distensión abdominal",
        "dolor en el vientre", "retortijón", "me duele la barriga",
        "me duele el estómago", "dolor en la boca del estómago",
    ],
    "deshidratación": [
        "deshidratación", "sed", "boca seca", "labios secos",
        "poca orina", "orina oscura", "piel seca", "mucha sed",
        "tengo sed", "deshidratado",
    ],
    "sarpullido": [
        "sarpullido", "rash", "erupción cutánea", "ronchas",
        "granos en la piel", "manchas rojas", "alergia en la piel",
        "salpullido", "piel irritada", "habones", "piel con manchas",
        "granos en todo el cuerpo",
    ],
    "dolor en el pecho": [
        "dolor en el pecho", "dolor torácico", "opresión en el pecho",
        "presión en el pecho", "dolor al respirar",
        "pesadez en el pecho", "pecho apretado", "me duele el pecho",
    ],
    "presión arterial alta": [
        "presión arterial alta", "hipertensión", "presión alta",
        "tensión alta", "PA elevada", "tengo la presión alta",
    ],
    "mareos": [
        "mareos", "vértigo", "desmayo", "cabeza liviana", "aturdimiento",
        "sensación de desmayo", "inestabilidad", "desequilibrio",
        "se me mueve todo", "cabeza floja", "vaivén",
        "me siento mareado", "me da vueltas la cabeza",
        "me voy a desmayar",
    ],
    "dolor de oído": [
        "dolor de oído", "otalgia", "dolor de oidos", "mal de oído",
        "oído inflamado", "dolor en el oído", "me duele el oído",
        "me duele el oido",
    ],
    "secreción del oído": [
        "secreción del oído", "otorrea", "líquido del oído",
        "supuración del oído", "sale líquido del oído",
        "pus del oído", "me sale liquido del oido",
    ],
    "ardor al orinar": [
        "ardor al orinar", "disuria", "dolor al orinar",
        "me arde al hacer pipí", "escalofrío al orinar",
        "molestia al orinar", "punzada al orinar",
        "me arde al orinar", "ardor al hacer pis",
        "me arde al hacer pis",
    ],
    "frecuencia urinaria": [
        "frecuencia urinaria", "polaquiuria", "orinar mucho",
        "orinar frecuente", "varias veces al baño",
        "no paro de orinar", "micción frecuente",
        "voy mucho al baño", "muchas ganas de orinar",
    ],
    "dolor lumbar": [
        "dolor lumbar", "dolor de espalda baja", "lumbalgia",
        "dolor de riñón", "dolor de riñones",
        "dolor de espalda", "dolor lumbar bajo",
        "parte baja de la espalda", "espalda baja",
    ],
    "fiebre alta persistente": [
        "fiebre alta persistente", "fiebre que no baja",
        "fiebre de 39", "fiebre muy alta",
        "temperatura muy alta", "calentura fuerte",
        "fiebre que no cede", "fiebre rebelde",
        "fiebre de 40",
    ],
    "confusión": [
        "confusión", "desorientación", "no sé dónde estoy",
        "habla incoherente", "delirio", "confundido",
        "aturdimiento mental", "no pienso claro", "confuso",
    ],
    "rigidez de cuello": [
        "rigidez de cuello", "cuello tieso", "nuca rígida",
        "rigidez nucal", "cuello duro", "no puedo mover el cuello",
        "dolor al mover el cuello", "cuello rígido",
    ],
    "dolor articular": [
        "dolor articular", "artralgia", "dolor en las articulaciones",
        "dolor de rodillas", "dolor de codos", "dolor de muñecas",
        "dolor de cadera", "articulaciones inflamadas",
        "reumatismo", "dolor de huesos", "me duelen las articulaciones",
        "me duele la rodilla", "dolor de las articulaciones",
    ],
    "hinchazón": [
        "hinchazón", "edema", "inflamación", "parte del cuerpo hinchada",
        "abultamiento", "tumefacción", "hinchado",
    ],
    "ictericia": [
        "ictericia", "piel amarilla", "ojos amarillos", "color amarillo",
        "amarillento", "ojos amarillentos", "coloración amarilla",
        "piel amarillenta",
    ],
    "pérdida de apetito": [
        "pérdida de apetito", "anorexia", "inapetencia",
        "no tengo hambre", "sin apetito", "no quiero comer",
        "sin ganas de comer", "no me da hambre",
    ],
    "heces con sangre": [
        "heces con sangre", "sangre en heces", "rectorragia",
        "caca con sangre", "deposiciones con sangre",
        "sangre al defecar", "hematoquecia",
    ],
    "tos con sangre": [
        "tos con sangre", "hemoptisis", "expectoración con sangre",
        "flemas con sangre", "esputo con sangre",
    ],
    "sudoración nocturna": [
        "sudoración nocturna", "sudor de noche", "sudor al dormir",
        "despertar sudado", "transpiración nocturna",
        "empapado en sudor", "sudo mucho en la noche",
    ],
    "pérdida de peso": [
        "pérdida de peso", "bajar de peso", "adelgazar",
        "peso bajo", "pérdida involuntaria de peso",
        "estoy perdiendo peso", "bajando de peso",
        "he bajado mucho de peso",
    ],
    "comezón": [
        "comezón", "prurito", "picazón", "picor", "rasquiña",
        "me pica", "escozor", "irritación en la piel", "picazón en la piel",
        "me pica todo el cuerpo",
    ],
    "ojos rojos": [
        "ojos rojos", "hiperemia conjuntival", "ojo rojo",
        "conjuntivitis", "ojos irritados", "enrojecimiento ocular",
        "ojos inyectados de sangre", "tengo los ojos rojos",
        "me arden los ojos", "me queman los ojos", "ardor en los ojos",
        "ojos que arden", "picor en los ojos",
    ],
    "sensibilidad a la luz": [
        "sensibilidad a la luz", "fotofobia", "molesta la luz",
        "no soporto la luz", "me lastima la luz",
        "luz me molesta los ojos", "me molesta la luz",
    ],
    "dolor detrás de los ojos": [
        "dolor detrás de los ojos", "dolor retroorbitario",
        "dolor ocular", "dolor de ojos",
        "presión detrás de los ojos", "me duelen los ojos",
        "dolor en los ojos",
    ],
    "fatiga extrema": [
        "fatiga extrema", "agotamiento extremo", "cansancio severo",
        "no me puedo mover del cansancio", "fatiga severa",
        "agotado total", "exhausto", "derrotado",
    ],
    "fatiga severa": [
        "fatiga severa", "agotamiento extremo", "cansancio extremo",
        "no tengo energía para nada",
    ],
    "mialgias": [
        "mialgias", "dolores musculares", "dolor en todo el cuerpo",
        "cuerpo cortado", "dolor generalizado",
    ],
    "orina turbia": [
        "orina turbia", "orina lechosa", "orina espesa",
        "pipi turbio", "orina nublada",
    ],
    "orina maloliente": [
        "orina maloliente", "orina con mal olor", "pipi apestosa",
        "orina que huele mal", "olor fuerte de orina",
    ],
    "urgencia urinaria": [
        "urgencia urinaria", "ganas repentinas de orinar",
        "no aguanto las ganas", "necesidad urgente de orinar",
        "me aguanto las ganas",
    ],
    "petequias": [
        "petequias", "puntos rojos en la piel", "manchitas rojas",
        "puntos hemorrágicos", "sangrado debajo de la piel",
    ],
    "sangrado de encías": [
        "sangrado de encías", "encias sangrantes", "me sangran las encías",
        "sangre al cepillarme", "encias que sangran",
    ],
    "dolor abdominal intenso": [
        "dolor abdominal intenso", "dolor de estómago fuerte",
        "dolor abdominal severo", "retorcijón fuerte",
    ],
    "expectoración purulenta": [
        "expectoración purulenta", "flema con pus", "flema verde",
        "flema amarilla", "flema purulenta", "esputo purulento",
    ],
    "taquipnea": [
        "taquipnea", "respiración rápida", "respiro muy rápido",
        "respiración acelerada", "respiro rápido",
    ],
    "cianosis": [
        "cianosis", "piel azulada", "labios morados",
        "dedos morados", "coloración azul en la piel",
        "me pongo morado",
    ],
    "expectoración": [
        "expectoración", "flema", "esputo", "mucosidad",
        "flemas al toser", "saco flemas",
    ],
    "sibilancias": [
        "sibilancias", "silbido al respirar", "pito en el pecho",
        "silbido en el pecho", "respiración silbante",
        "me silba el pecho",
    ],
    "malestar general intenso": [
        "malestar general intenso", "me siento muy mal",
        "malestar fuerte", "me siento grave",
    ],
    "dolor ocular": [
        "dolor ocular", "dolor de ojos", "me duelen los ojos",
        "dolor en los globos oculares",
    ],
    "letargo": [
        "letargo", "somnolencia", "mucho sueño", "no me puedo despertar",
        "sueño excesivo", "adormecido", "muy dormido",
    ],
    "convulsiones": [
        "convulsiones", "ataques", "crisis epiléptica",
        "movimientos involuntarios del cuerpo",
        "sacudidas violentas", "crisis convulsiva",
    ],
    "tos crónica": [
        "tos crónica", "tos persistente", "tosiendo por semanas",
        "llevo mucho tiempo tosiendo", "tos que no se quita",
    ],
    "inflamación de amígdalas": [
        "inflamación de amígdalas", "amigdalitis",
        "anginas inflamadas", "amígdalas rojas",
        "anginas rojas", "amígdalas hinchadas",
    ],
    "exudado purulento": [
        "exudado purulento", "pus", "secreción amarilla",
        "supuración", "sale pus",
    ],
    "adenopatías cervicales": [
        "adenopatías cervicales", "ganglios inflamados en el cuello",
        "pelotas en el cuello", "ganglios en el cuello",
        "bultos en el cuello",
    ],
    "rinorrea acuosa": [
        "rinorrea acuosa", "mocos líquidos", "agua por la nariz",
        "secreción nasal clara",
    ],
    "prurito nasal": [
        "prurito nasal", "picazón en la nariz", "me pica la nariz",
        "nariz que pica",
    ],
    "lagrimeo": [
        "lagrimeo", "ojos llorosos", "lloran los ojos",
        "se me salen las lágrimas", "ojos llorones",
    ],
    "dificultad para tragar": [
        "dificultad para tragar", "disfagia", "no puedo tragar bien",
        "me duele al tragar", "atragantamiento",
    ],
    "estornudos": [
        "estornudos", "estornudar", "estornudo mucho",
        "no paro de estornudar", "estornudo frecuente",
    ],
    "tenesmo": [
        "tenesmo", "pujar para hacer del baño",
        "sensación de evacuación incompleta",
        "quiero hacer del baño pero no sale",
    ],
    "irritabilidad": [
        "irritabilidad", "irritable", "mal humor",
        "molesto por todo", "me irrito fácil",
    ],
    "pérdida auditiva temporal": [
        "pérdida auditiva temporal", "no oigo bien",
        "oigo menos", "sordera temporal",
    ],
    "sensación de oído tapado": [
        "sensación de oído tapado", "oído tapado",
        "oído obstruido", "siento el oído tapado",
    ],
    "orina oscura": [
        "orina oscura", "pipi oscuro", "orina color té",
        "orina color cola", "orina concentrada",
    ],
    "heces pálidas": [
        "heces pálidas", "caca blanca", "heces claras",
        "deposiciones pálidas", "heces color arcilla",
    ],
    "malestar general": [
        "malestar general", "no me siento bien",
        "indisposición", "me siento mal en general",
        "malestar",
    ],
    "dolor torácico opresivo": [
        "dolor torácico opresivo", "presión en el pecho",
        "pecho apretado", "opresión torácica severa",
        "pesadez en el pecho",
    ],
    "disnea": [
        "disnea", "falta de aire", "dificultad para respirar",
        "me falta el aire", "respiración corta",
    ],
    "sudoración profusa": [
        "sudoración profusa", "sudor excesivo", "empapado en sudor",
        "sudo mucho", "transpiración abundante",
    ],
    "palpitaciones": [
        "palpitaciones", "corazón acelerado", "taquicardia",
        "corazón saltón", "latidos fuertes",
        "siento el corazón", "corazón rápido",
    ],
    "ansiedad": [
        "ansiedad", "nervios", "angustia", "desesperación",
        "nervioso", "intranquilo",
    ],
    "dolor epigástrico": [
        "dolor epigástrico", "dolor en la boca del estómago",
        "ardor en el estómago", "dolor en el epigastrio",
    ],
    "síncope": [
        "síncope", "desmayo", "pérdida de conocimiento",
        "me desmayé", "perdí el conocimiento", "me caí desmayado",
    ],
    "disnea de esfuerzo": [
        "disnea de esfuerzo", "me falta el aire al caminar",
        "fatiga al caminar", "cansancio al hacer ejercicio",
        "me ahogo al caminar",
    ],
    "edema en piernas": [
        "edema en piernas", "piernas hinchadas",
        "pies hinchados", "tobillos inflamados",
        "retención de líquidos en piernas",
    ],
    "ortopnea": [
        "ortopnea", "no puedo respirar acostado",
        "me ahogo al acostarme", "respirar mejor sentado",
        "necesito almohadas para respirar",
    ],
    "vértigo": [
        "vértigo", "todo da vueltas", "se mueve todo",
        "mareo intenso", "sensación de giro",
    ],
    "visión borrosa": [
        "visión borrosa", "veo borroso", "vista nublada",
        "veo nublado", "pérdida de nitidez visual",
    ],
    "zumbido de oídos": [
        "zumbido de oídos", "tinnitus", "pitido en el oído",
        "zumbido en los oídos", "ruido en el oído",
    ],
    "epistaxis": [
        "epistaxis", "sangrado nasal", "sangre por la nariz",
        "me sangra la nariz", "hemorragia nasal",
    ],
    "poliuria": [
        "poliuria", "orinar mucho", "mucha orina",
        "exceso de orina", "producción excesiva de orina",
    ],
    "polidipsia": [
        "polidipsia", "mucha sed", "sed excesiva",
        "tengo mucha sed", "no me quita la sed",
    ],
    "polifagia": [
        "polifagia", "mucha hambre", "hambre excesiva",
        "como mucho y aún tengo hambre",
    ],
    "pérdida de peso inexplicada": [
        "pérdida de peso inexplicada", "bajo de peso sin razón",
        "adelgazando sin causa", "perdiendo peso sin dieta",
    ],
    "infecciones frecuentes": [
        "infecciones frecuentes", "me enfermo seguido",
        "infecciones recurrentes", "enfermo constantemente",
    ],
    "cicatrización lenta": [
        "cicatrización lenta", "tardan en sanar las heridas",
        "las heridas no sanan", "heridas que no cierran",
    ],
    "hormigueo en extremidades": [
        "hormigueo en extremidades", "parestesia en brazos y piernas",
        "adormecimiento de manos y pies",
        "se me duermen las manos", "alfilerazos en extremidades",
    ],
    "aumento de peso": [
        "aumento de peso", "subir de peso", "engordar",
        "estoy engordando", "aumento de peso inexplicable",
    ],
    "intolerancia al frío": [
        "intolerancia al frío", "siento mucho frío",
        "no aguanto el frío", "siempre tengo frío",
    ],
    "piel seca": [
        "piel seca", "resequedad en la piel", "tengo la piel seca",
        "descamación", "piel que se pela",
    ],
    "caída de cabello": [
        "caída de cabello", "se me cae el pelo", "alopecia",
        "pérdida de pelo", "calvicie",
    ],
    "estreñimiento": [
        "estreñimiento", "estrenido", "no puedo ir al baño",
        "heces duras", "constipación", "dificultad para evacuar",
    ],
    "bradicardia": [
        "bradicardia", "corazón lento", "pulso bajo",
        "latidos lentos", "frecuencia cardíaca baja",
    ],
    "depresión": [
        "depresión", "tristeza profunda", "melancolía",
        "no tengo ganas de vivir", "abatimiento",
    ],
    "bocio": [
        "bocio", "coto en el cuello", "bulto en la garganta",
        "hinchazón en el cuello", "glándula tiroides agrandada",
    ],
    "taquicardia": [
        "taquicardia", "corazón acelerado", "palpitaciones rápidas",
        "pulso rápido", "latidos muy rápidos",
    ],
    "intolerancia al calor": [
        "intolerancia al calor", "siento mucho calor",
        "no aguanto el calor", "siempre tengo calor",
    ],
    "sudoración excesiva": [
        "sudoración excesiva", "hiperhidrosis", "sudo demasiado",
        "transpiración excesiva",
    ],
    "nerviosismo": [
        "nerviosismo", "tenso", "ansioso", "alborotado",
        "agitado", "intranquilo",
    ],
    "temblores": [
        "temblores", "temblor en las manos", "manos temblorosas",
        "me tiemblan las manos", "temblor fino",
    ],
    "insomnio": [
        "insomnio", "no puedo dormir", "desvelo",
        "dificultad para conciliar el sueño",
        "me despierto mucho en la noche",
    ],
    "exoftalmos": [
        "exoftalmos", "ojos saltones", "ojos saltados",
        "protrusión ocular", "ojos hacia afuera",
    ],
    "fatiga muscular": [
        "fatiga muscular", "debilidad muscular", "músculos débiles",
        "no tengo fuerza en los músculos",
        "debilidad en los brazos y piernas",
    ],
    "fotofobia": [
        "fotofobia", "molestia a la luz", "no soporto la luz",
        "me molesta la claridad", "intolerancia a la luz",
    ],
    "fonofobia": [
        "fonofobia", "intolerancia al ruido", "me molesta el ruido",
        "no soporto el ruido",
    ],
    "aura visual": [
        "aura visual", "luces en la visión", "destellos en los ojos",
        "puntos ciegos", "visión de luces parpadeantes",
    ],
    "parestesias": [
        "parestesias", "hormigueo", "adormecimiento",
        "alfilerazos", "sensación de hormigueo",
    ],
    "debilidad facial unilateral": [
        "debilidad facial unilateral", "parálisis facial",
        "se me cae la cara", "boca torcida",
        "no puedo sonreír de un lado",
    ],
    "debilidad en extremidades": [
        "debilidad en extremidades", "pérdida de fuerza en brazos o piernas",
        "no puedo mover un brazo", "se me durmió un lado del cuerpo",
        "parálisis de un brazo",
    ],
    "confusión súbita": [
        "confusión súbita", "desorientación repentina",
        "me desorienté de repente", "no sé qué pasó",
    ],
    "dificultad para hablar": [
        "dificultad para hablar", "disartria", "no puedo hablar bien",
        "habla arrastrada", "se me traba la lengua",
    ],
    "pérdida de visión": [
        "pérdida de visión", "ceguera", "no veo",
        "pérdida visual", "visión perdida",
    ],
    "pérdida de equilibrio": [
        "pérdida de equilibrio", "inestabilidad", "no me puedo sostener",
        "me caigo", "dificultad para caminar derecho",
    ],
    "pérdida de conciencia": [
        "pérdida de conciencia", "desmayo", "me desvanecí",
        "perdí el conocimiento", "me desmayé",
    ],
    "convulsiones tónico-clónicas": [
        "convulsiones tónico-clónicas", "crisis convulsiva generalizada",
        "ataque epiléptico", "gran mal epiléptico",
    ],
    "ausencias": [
        "ausencias", "desconexión breve", "me quedo en blanco",
        "episodios de mirada perdida", "pequeño mal",
    ],
    "movimientos involuntarios": [
        "movimientos involuntarios", "sacudidas", "tics",
        "movimientos que no controlo",
    ],
    "temblor en reposo": [
        "temblor en reposo", "temblor cuando estoy quieto",
        "tiemblo cuando no hago nada",
    ],
    "rigidez muscular": [
        "rigidez muscular", "músculos duros", "tenso muscular",
        "músculos rígidos", "no me puedo mover bien",
    ],
    "bradicinesia": [
        "bradicinesia", "movimientos lentos", "me muevo lento",
        "lentitud de movimientos",
    ],
    "disfagia": [
        "disfagia", "dificultad para tragar", "me atoro al comer",
        "no puedo tragar comida", "disfagia",
    ],
    "deterioro cognitivo": [
        "deterioro cognitivo", "pérdida de memoria", "olvido mucho",
        "no me acuerdo de las cosas", "demencia",
        "problemas de memoria",
    ],
    "inflamación articular": [
        "inflamación articular", "articulaciones hinchadas",
        "rodillas inflamadas", "dedos hinchados",
    ],
    "erupción en mariposa facial": [
        "erupción en mariposa facial", "rash en mariposa en la cara",
        "mancha en la cara con forma de mariposa",
        "eritema malar",
    ],
    "fotosensibilidad": [
        "fotosensibilidad", "sensibilidad al sol",
        "me quemo fácil con el sol", "urticaria solar",
    ],
    "úlceras orales": [
        "úlceras orales", "llagas en la boca", "aftas",
        "heridas en la boca", "boqueras",
    ],
    "artritis": [
        "artritis", "inflamación en articulaciones",
        "articulaciones rojas e hinchadas",
    ],
    "fenómeno de Raynaud": [
        "fenómeno de Raynaud", "dedos blancos con el frío",
        "cambio de color de los dedos con el frío",
    ],
    "fiebre cíclica con escalofríos": [
        "fiebre cíclica con escalofríos", "fiebre que va y viene",
        "fiebre intermitente", "calentura que regresa",
    ],
    "dolor de cabeza intenso": [
        "dolor de cabeza intenso", "cefalea severa",
        "dolor de cabeza muy fuerte", "migraña severa",
    ],
    "hepatomegalia": [
        "hepatomegalia", "hígado inflamado", "hígado grande",
        "hígado agrandado",
    ],
    "esplenomegalia": [
        "esplenomegalia", "bazo inflamado", "bazo grande",
        "bazo agrandado",
    ],
    "sibilancias": [
        "sibilancias", "silbido al respirar", "pito en el pecho",
        "silbido en el pecho", "respiración silbante",
    ],
    "disnea": [
        "disnea", "falta de aire", "dificultad para respirar",
        "me falta el aire",
    ],
    "opresión torácica": [
        "opresión torácica", "presión en el pecho",
        "pecho apretado", "sensación de opresión",
    ],
    "tos seca": [
        "tos seca", "tos sin flema", "tos sin moco",
        "tos irritativa", "tos de perro",
    ],
    "disfonía o afonía": [
        "disfonía o afonía", "ronquera", "pérdida de la voz",
        "voz ronca", "afonía", "no tengo voz",
    ],
    "edema": [
        "edema", "hinchazón", "inflamación",
        "parte del cuerpo hinchada",
    ],
    "dermografismo": [
        "dermografismo", "ronchas al rascarme",
        "me salen ronchas al rascar",
    ],
    "prurito intenso": [
        "prurito intenso", "picazón severa", "me pica mucho",
        "picazón insoportable",
    ],
    "edema angioneurótico": [
        "edema angioneurótico", "hinchazón repentina de labios",
        "hinchazón de cara", "angioedema",
    ],
    "liquenificación": [
        "liquenificación", "piel engrosada", "piel gruesa",
        "endurecimiento de la piel",
    ],
    "xerosis": [
        "xerosis", "piel muy seca", "sequedad de la piel",
        "piel escamosa",
    ],
    "dispareunia": [
        "dispareunia", "dolor al tener relaciones",
        "dolor durante el coito", "dolor sexual",
    ],
    "trastornos del sueño": [
        "trastornos del sueño", "problemas para dormir",
        "mal dormir", "sueño interrumpido",
    ],
    "síndrome de colon irritable": [
        "síndrome de colon irritable", "colon irritable",
        "intestino irritable", "SII",
    ],
    "dificultades cognitivas": [
        "dificultades cognitivas", "niebla mental",
        "problemas de concentración", "no puedo concentrarme",
        "mente nublada",
    ],
    "hematoma": [
        "hematoma", "moretón", "moreton", "morado", "morados",
        "moretone", "mancha morada", "mancha morado", "equimosis",
        "cardenal", "me puse morado", "golpe que deja morado",
        "moretón en la piel", "moratón",
    ],
    "contusión": [
        "contusión", "contusion", "golpe", "golpes", "golpeado",
        "traumatismo", "trauma", "lesión por golpe", "me golpeé",
        "me golpee", "me di un golpe", "me caí y me golpeé",
        "golpe en la cabeza", "golpe en el cuerpo", "choque",
    ],
}

# ── Semantic word index for automatic relationship ──────────────
# Maps important words → list of related canonical symptoms
WORD_INDEX: dict[str, list[str]] = {
    "ojos": ["ojos rojos", "dolor detrás de los ojos", "sensibilidad a la luz"],
    "ojo": ["ojos rojos", "dolor detrás de los ojos", "sensibilidad a la luz"],
    "cabeza": ["dolor de cabeza", "mareos", "fiebre", "fiebre alta persistente", "dolor detrás de los ojos", "confusión"],
    "garganta": ["dolor de garganta", "tos", "dolor de cabeza"],
    "estomago": ["dolor abdominal", "náuseas", "vómito", "diarrea", "pérdida de apetito"],
    "barriga": ["dolor abdominal", "náuseas", "vómito", "diarrea"],
    "nariz": ["congestión nasal", "pérdida del olfato", "estornudos"],
    "pecho": ["dolor en el pecho", "dificultad para respirar", "tos", "tos con sangre"],
    "oido": ["dolor de oído", "secreción del oído"],
    "oído": ["dolor de oído", "secreción del oído"],
    "piel": ["sarpullido", "comezón", "ictericia"],
    "espalda": ["dolor lumbar", "dolor muscular", "dificultad para respirar"],
    "lumbar": ["dolor lumbar"],
    "riñon": ["dolor lumbar", "cólico nefrítico"],
    "rinon": ["dolor lumbar", "cólico nefrítico"],
    "cuello": ["rigidez de cuello", "dolor muscular", "dolor de cabeza"],
    "musculo": ["dolor muscular", "dolor articular"],
    "articulacion": ["dolor articular", "hinchazón", "dolor muscular"],
    "rodilla": ["dolor articular", "hinchazón", "dolor muscular"],
    "hueso": ["dolor articular", "dolor muscular"],
    "orina": ["ardor al orinar", "frecuencia urinaria", "deshidratación"],
    "baño": ["frecuencia urinaria"],
    "bano": ["frecuencia urinaria"],
    "fiebre": ["fiebre", "fiebre alta persistente", "escalofríos"],
    "ardor": ["ardor al orinar", "ojos rojos"],
    "arden": ["ojos rojos"],
    "dolor": ["dolor de cabeza", "dolor muscular", "dolor abdominal", "dolor de garganta",
              "dolor en el pecho", "dolor lumbar", "dolor articular", "dolor de oído",
              "dolor detrás de los ojos"],
    "mareo": ["mareos", "vértigo", "náuseas", "fiebre"],
    "hinchazon": ["hinchazón", "dolor articular", "dolor muscular"],
    "inflamacion": ["hinchazón", "dolor articular", "dolor de garganta"],
    "sangre": ["heces con sangre", "tos con sangre", "ictericia"],
    "peso": ["pérdida de peso", "pérdida de apetito"],
    "apetito": ["pérdida de apetito", "náuseas"],
    "hambre": ["pérdida de apetito", "náuseas"],
    "sed": ["deshidratación", "fiebre", "diarrea"],
    "debilidad": ["fatiga", "deshidratación", "pérdida de peso"],
    "energia": ["fatiga", "pérdida de apetito"],
    "fuerza": ["fatiga", "debilidad"],
    "sudor": ["sudoración nocturna", "fiebre", "escalofríos", "sudoración profusa", "sudoración excesiva"],
    "noche": ["sudoración nocturna", "tos"],
    "corazon": ["palpitaciones", "taquicardia", "bradicardia", "dolor en el pecho", "dolor torácico opresivo"],
    "pierna": ["edema en piernas", "dolor muscular", "debilidad en extremidades"],
    "mano": ["temblores", "temblor en reposo", "parestesias", "hormigueo en extremidades", "fenómeno de Raynaud"],
    "brazo": ["dolor muscular", "debilidad en extremidades", "dolor irradiado a brazo izquierdo"],
    "pecho": ["dolor en el pecho", "dolor torácico opresivo", "disnea", "dificultad para respirar", "tos", "tos con sangre", "opresión torácica", "sibilancias"],
    "respirar": ["dificultad para respirar", "disnea", "disnea de esfuerzo", "ortopnea", "sibilancias", "taquipnea"],
    "traga": ["dificultad para tragar", "disfagia", "dolor de garganta", "odinofagia"],
    "tragar": ["dificultad para tragar", "disfagia"],
    "cuello": ["rigidez de cuello", "dolor muscular", "dolor de cabeza", "adenopatías cervicales", "bocio"],
    "cara": ["debilidad facial unilateral", "enrojecimiento facial", "erupción en mariposa facial", "edema angioneurótico"],
    "ojo": ["ojos rojos", "dolor detrás de los ojos", "sensibilidad a la luz", "visión borrosa", "exoftalmos", "fotofobia", "ojo rojo", "lagrimeo", "pérdida de visión"],
    "boca": ["úlceras orales", "dificultad para hablar", "debilidad facial unilateral", "dolor de garganta"],
    "lengua": ["dificultad para hablar", "mordedura de lengua"],
    "vista": ["visión borrosa", "pérdida de visión", "aura visual"],
    "hablar": ["dificultad para hablar"],
    "caminar": ["marcha inestable", "pérdida de equilibrio", "marcha arrastrada", "debilidad en extremidades"],
    "caer": ["pérdida de equilibrio", "síncope", "mareos", "vértigo"],
    "hambre": ["pérdida de apetito", "náuseas", "polifagia"],
    "comida": ["pérdida de apetito", "náuseas", "vómito", "dolor abdominal"],
    "dormir": ["insomnio", "trastornos del sueño", "sudoración nocturna", "tos nocturna", "ortopnea"],
    "sueno": ["insomnio", "trastornos del sueño", "letargo", "fatiga"],
    "debilidad": ["fatiga", "deshidratación", "pérdida de peso", "debilidad en extremidades", "debilidad facial unilateral", "fatiga muscular", "fatiga extrema"],
    "fuerza": ["fatiga", "debilidad", "fatiga muscular"],
    "pies": ["edema en piernas", "hormigueo en extremidades", "parestesias"],
    "memoria": ["deterioro cognitivo", "confusión", "dificultades cognitivas"],
    "concentrar": ["dificultades cognitivas", "confusión"],
    "orinar": ["ardor al orinar", "frecuencia urinaria", "urgencia urinaria", "poliuria", "disuria", "dolor al llenar la vejiga"],
    "pipi": ["ardor al orinar", "frecuencia urinaria", "orina turbia", "orina maloliente", "hematuria"],
    "hígado": ["hepatomegalia", "ictericia", "dolor en hipocondrio derecho"],
    "higado": ["hepatomegalia", "ictericia", "dolor en hipocondrio derecho"],
    "vesicula": ["dolor en hipocondrio derecho", "signo de Murphy", "ictericia leve"],
    "apendice": ["dolor abdominal periumbilical que migra a fosa ilíaca derecha", "dolor abdominal"],
    "costado": ["dolor lumbar", "dolor en hipocondrio derecho", "cólico nefrítico"],
    "cintura": ["dolor lumbar", "dolor abdominal"],
    "golpe": ["contusión", "hematoma", "dolor muscular"],
    "golpes": ["contusión", "hematoma", "dolor muscular"],
    "moreton": ["hematoma", "contusión"],
    "moretón": ["hematoma", "contusión"],
    "morado": ["hematoma", "contusión", "cianosis"],
    "morados": ["hematoma", "contusión"],
    "hematoma": ["hematoma", "contusión"],
    "contusion": ["contusión", "hematoma"],
    "contusión": ["contusión", "hematoma"],
    "trauma": ["contusión", "hematoma"],
    "equimosis": ["hematoma", "contusión"],
    "cardenal": ["hematoma", "contusión"],
}

# Stop-words to ignore during decomposition
STOP_WORDS = {"me", "te", "se", "lo", "la", "los", "las", "le", "el", "del",
              "un", "una", "con", "sin", "por", "para", "de", "en", "al",
              "y", "e", "o", "a", "que", "es", "no", "si", "pero", "muy",
              "mucho", "poco", "mucho", "tengo", "estoy", "esta", "este",
              "como", "cuando", "donde", "todo", "toda", "cada", "mas"}

# ── Module-level caches ──────────────────────────────────────────
_BUILTIN_REVERSE: dict[str, str] = {}    # synonym phrase → canonical
_FOLDED_REVERSE: dict[str, str] = {}     # accent-folded phrase → canonical
_CANONICAL_LIST: list[str] = []
_LEARNED_REVERSE: dict[str, str] = {}    # custom learned → canonical
_LEARNED_FOLDED: dict[str, str] = {}     # learned, accent-folded → canonical
_CATALOG_FOLDED: set[str] = set()        # folded names from DB catalog sync

# Words that turn the following symptom into a denial (absence).
NEGATION_WORDS = {
    "no", "sin", "nunca", "ni", "tampoco", "nada", "jamas", "jamás",
    "carece", "carezco",
}


def _fold(s: str) -> str:
    """Accent/uppercase-insensitive key (no accents, spaces collapsed)."""
    s = s.lower().strip()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _build_builtin_index():
    global _BUILTIN_REVERSE, _FOLDED_REVERSE, _CANONICAL_LIST
    if _BUILTIN_REVERSE:
        return
    for canonical, variants in SYMPTOM_SYNONYMS.items():
        for variant in variants:
            _BUILTIN_REVERSE[variant] = canonical
            _FOLDED_REVERSE[_fold(variant)] = canonical
        _BUILTIN_REVERSE[canonical] = canonical
        _FOLDED_REVERSE[_fold(canonical)] = canonical
    _CANONICAL_LIST = list(SYMPTOM_SYNONYMS.keys())


def load_learned(learned: dict[str, str]):
    _LEARNED_REVERSE.clear()
    _LEARNED_FOLDED.clear()
    for phrase, canonical in learned.items():
        _LEARNED_REVERSE[phrase] = canonical
        _LEARNED_FOLDED[_fold(phrase)] = canonical


def load_catalog(symptom_names: list[str]):
    """Register the symptom names actually loaded in the DB as canonical.

    Compatibility layer for the routes that sync the knowledge base from
    MongoDB Atlas: DB-specific names become resolvable (accent-insensitive)
    even when they are not part of the built-in synonym catalog.
    """
    _build_builtin_index()
    for name in symptom_names:
        name = (name or "").strip()
        if not name:
            continue
        folded = _fold(name)
        _CATALOG_FOLDED.add(folded)
        if folded not in _FOLDED_REVERSE:
            _FOLDED_REVERSE[folded] = name
        if name not in _BUILTIN_REVERSE:
            _BUILTIN_REVERSE[name] = name
        if name not in _CANONICAL_LIST:
            _CANONICAL_LIST.append(name)


def reset_catalog():
    """Drop the DB-provided names added by ``load_catalog``."""
    _CATALOG_FOLDED.clear()


def has_catalog() -> bool:
    return bool(_CATALOG_FOLDED)


def is_in_catalog(canonical: str) -> bool:
    return bool(canonical) and _fold(canonical) in _CATALOG_FOLDED


def get_learned() -> dict[str, str]:
    return dict(_LEARNED_REVERSE)


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sáéíóúüñ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _keyword_decompose(text: str) -> dict[str, float]:
    """Score each canonical symptom by keyword overlap."""
    scores: dict[str, float] = {}
    words = text.split()
    significant = [w for w in words if len(w) > 2 and w not in STOP_WORDS]

    for word in significant:
        # Check word index
        related = WORD_INDEX.get(word, [])
        for symptom in related:
            scores[symptom] = scores.get(symptom, 0) + 1.0

        # Also check if word appears in canonical name
        for canonical in _CANONICAL_LIST:
            if word in canonical:
                scores[canonical] = scores.get(canonical, 0) + 0.5

    # Normalize by number of significant words
    if significant:
        for k in scores:
            scores[k] = round(scores[k] / len(significant), 2)

    return scores


def find_symptom(user_input: str) -> Optional[str]:
    """Find the canonical symptom that best matches user input."""
    _build_builtin_index()
    cleaned = normalize(user_input)
    if not cleaned:
        return None
    folded = _fold(cleaned)

    # 1. Check custom learned phrases first (accent-insensitive)
    if folded in _LEARNED_FOLDED:
        return _LEARNED_FOLDED[folded]

    # 2. Built-in exact match (accent-insensitive)
    if folded in _FOLDED_REVERSE:
        return _FOLDED_REVERSE[folded]

    # 3. Single-word exact match
    words = folded.split()
    if len(words) == 1 and words[0] in _FOLDED_REVERSE:
        return _FOLDED_REVERSE[words[0]]

    # 4. Substring phrase match (longest first, accent-insensitive)
    for phrase, canonical in sorted(_FOLDED_REVERSE.items(), key=lambda x: -len(x[0])):
        if len(phrase) > 2 and phrase in folded:
            return canonical

    # 5. Learned single-word
    for word in words:
        if word in _LEARNED_FOLDED:
            return _LEARNED_FOLDED[word]

    # 6. Built-in word-by-word exact
    for word in words:
        if word in _FOLDED_REVERSE:
            return _FOLDED_REVERSE[word]

    # 7. Semantic decomposition (keyword index)
    scores = _keyword_decompose(cleaned)
    if scores:
        best = max(scores, key=scores.get)
        best_score = scores[best]
        if best_score >= 0.3:
            return best

    # 8. Fuzzy match per word (high threshold)
    for word in words:
        if len(word) <= 2:
            continue
        matches = difflib.get_close_matches(word, _CANONICAL_LIST, n=1, cutoff=0.7)
        if matches:
            return matches[0]

    return None


def find_negated_symptoms(user_input: str) -> list[str]:
    """Detect symptoms the user explicitly states are ABSENT.

    Handles "no tiene fiebre", "sin tos", "no ha tenido dolor de cabeza",
    "ni fiebre ni tos", "no presenta nauseas", etc. Returns canonical
    symptom names that were denied, so they can be used as negative evidence
    instead of being added as present.
    """
    _build_builtin_index()
    cleaned = normalize(user_input)
    if not cleaned:
        return []
    folded = _fold(cleaned)

    negated: set[str] = set()

    # Split into clauses keeping the separator, so "ni ... ni ..." chains can
    # propagate the denial to each item ("no presenta ni fiebre ni tos").
    parts = re.split(r"(\s+y\s+|\s+ni\s+|\s*,\s*|\s*;\s*|\s+pero\s+)", cleaned)
    prev_neg = False
    prev_sep = ""
    for idx in range(0, len(parts), 2):
        clause = parts[idx].strip()
        sep = parts[idx + 1].strip() if idx + 1 < len(parts) else ""
        if not clause:
            prev_neg = False
            prev_sep = sep
            continue
        words = clause.split()
        has_neg_word = any(w in NEGATION_WORDS for w in words)

        if prev_sep == "ni":
            # Items joined by "ni" inherit the denial opened before.
            is_neg = prev_neg or has_neg_word
        elif has_neg_word:
            is_neg = True
        else:
            # "pero" / "y" / "," after a denial reset it ("no tos pero fiebre").
            is_neg = False

        if is_neg:
            p_folded = _fold(clause)
            # Match symptom phrases within the denied clause (longest first)
            for phrase, canonical in sorted(_FOLDED_REVERSE.items(), key=lambda x: -len(x[0])):
                if len(phrase) > 2 and phrase in p_folded:
                    negated.add(canonical)
                    break
            # Also capture any remaining single-word matches
            for w in words:
                if w in _FOLDED_REVERSE:
                    negated.add(_FOLDED_REVERSE[w])

        prev_neg = is_neg
        prev_sep = sep

    return sorted(negated)


def normalize_symptoms(raw_symptoms: list[str]) -> dict:
    """
    Returns:
        dict with keys:
            - matched: list of canonical symptom names
            - unmatched: list of raw inputs that could not be matched
            - negated: list of canonical symptom names the user said are ABSENT
            - suggestions: dict of {raw_phrase: [suggested_canonical, ...]}
    """
    result = {"matched": [], "unmatched": [], "negated": [], "suggestions": {}}
    for raw in raw_symptoms:
        matched = find_symptom(raw)
        if matched:
            # A symptom the user denied must never be added as present.
            denied = find_negated_symptoms(raw)
            if matched in denied:
                result["negated"].append(matched)
                continue
            result["matched"].append(matched)
            # If phrase contains "y" or commas, try each sub-phrase separately
            # e.g. "me duele al orinar y voy al baño seguido" -> both symptoms
            for sep in (" y ", ", ", " , "):
                if sep in raw:
                    for part in raw.split(sep):
                        part = part.strip()
                        if part and part not in raw_symptoms:
                            extra = find_symptom(part)
                            part_denied = part and extra in find_negated_symptoms(part)
                            if extra and extra not in result["matched"] and extra != matched and not part_denied:
                                result["matched"].append(extra)
                            if part_denied and extra:
                                result["negated"].append(extra)
        else:
            result["unmatched"].append(raw)
            # Generate suggestions via keyword decomposition
            scores = _keyword_decompose(normalize(raw))
            if scores:
                sorted_sugs = sorted(scores, key=scores.get, reverse=True)[:3]
                result["suggestions"][raw] = sorted_sugs
    return result


# ── Conversational AI layer ─────────────────────────────────────
import random

# Category: phrase patterns (will be matched via substring)
CONV_PATTERNS: dict[str, list[str]] = {
    "greeting": [
        "hola", "buenos dias", "buenas tardes", "buenas noches",
        "que tal", "buenas", "saludos", "hey", "holi",
    ],
    "how_are_you": [
        "como estas", "como va", "como te va", "como esta todo",
        "que tal tu dia", "como has estado", "como vas",
        "como te sientes", "como esta mi ia", "todo bien",
    ],
    "mood_negative": [
        "me siento mal", "estoy mal", "no me siento bien",
        "estoy preocupado", "estoy triste", "me siento triste",
        "hoy no es mi dia", "estoy estresado", "estoy agobiado",
        "que dia tan malo", "estoy deprimido", "me siento solo",
        "estoy cansado de todo",
    ],
    "mood_positive": [
        "estoy bien", "me siento bien", "estoy feliz",
        "me siento genial", "todo esta bien", "estoy contento",
        "que buen dia", "estoy excelente", "me siento excelente",
        "estoy motivado",
    ],
    "goodbye": [
        "chao", "adios", "nos vemos", "hasta luego", "hasta pronto",
        "bye", "terminamos", "ya termino", "ahí quedamos",
        "nos vemos luego", "cuídate", "cuidate",
    ],
    "ready_report": [
        "listo", "ya termine", "he terminado", "prepara el informe",
        "genera el reporte", "resume", "resumen", "haz el informe",
        "prepara reporte", "diagnostico final", "envia el reporte",
        "quiero el informe", "terminamos el diagnostico",
    ],
    "what_is": [
        "quien eres", "que eres", "que haces", "como funcionas",
        "para que sirves", "que puedes hacer", "como te llamas",
        "cual es tu nombre", "que sabes hacer",
    ],
    "chatty": [
        "que haces", "en que trabajas", "cuentame algo",
        "aburrido", "no se que hacer",
    ],
    "encouragement": [
        "gracias por tu ayuda", "eres util", "buen trabajo",
        "excelente trabajo", "me gusta como funcionas",
        "eres muy inteligente", "buena ia",
    ],
}

# Response banks
CONV_RESPONSES: dict[str, list[str]] = {
    "greeting": [
        "¡Hola! Soy Mimetic AI. ¿En qué puedo ayudarte con el diagnóstico de hoy?",
        "Hola, encantado de verte. Cuando quieras, empezamos con los síntomas.",
        "¡Buen día! Estoy listo para ayudarte con el diagnóstico. Cuéntame cuando quieras empezar.",
    ],
    "how_are_you": [
        "¡Estoy muy bien! Gracias por preguntar. ¿Y tú? Cuando quieras, empezamos con los síntomas del paciente.",
        "Funcionando a toda máquina por aquí. Cuéntame, ¿estás listo para el diagnóstico o prefieres que charlemos un rato más?",
        "Muy bien, listo para ayudarte. Cuando estés preparado, describe los síntomas y empezamos.",
        "Todo en orden por acá. ¿Vamos directo al diagnóstico o necesitas algo primero?",
    ],
    "mood_negative": [
        "Lamento que te sientas así. Espero que puedas mejorar. Si quieres distraerte un poco, podemos empezar con el diagnóstico del paciente, eso tal vez te ayude a enfocarte en algo productivo.",
        "Lo sé, algunos días son más difíciles que otros. Cuando te sientas listo, aquí estoy para ayudarte con el diagnóstico. Mientras tanto, respira hondo, todo va a estar bien.",
        "Ánimo, los días malos también pasan. Si prefieres, podemos empezar con el diagnóstico para mantenerte ocupado. Cuando quieras, estoy aquí.",
        "Te entiendo. A veces uno simplemente no está bien. Cuando estés listo para trabajar, aquí estoy. Mientras, tómate tu tiempo.",
    ],
    "mood_positive": [
    "¡Me alegra mucho que te sientas bien! Eso se nota en el ambiente. Cuando quieras, empezamos con el diagnóstico.",
        "¡Qué bueno! Un día positivo siempre es mejor para trabajar. ¿Empezamos con los síntomas del paciente?",
        "Me encanta escuchar eso. Aprovechemos este buen ánimo para hacer un gran diagnóstico. ¿Por dónde empezamos?",
    ],
    "goodbye": [
        "Ha sido un placer ayudarte. Cuando necesites hacer otro diagnóstico, aquí estaré. ¡Cuídate!",
        "Hasta luego. Recuerda que puedes volver cuando necesites hacer un nuevo diagnóstico. ¡Que tengas un excelente día!",
        "¡Nos vemos! Si quieres, antes de irte puedo preparar un resumen del diagnóstico. Solo dímelo.",
    ],
    "ready_report": [
        "Claro, déjame preparar el resumen del diagnóstico con los síntomas que hemos registrado.",
        "Entendido. ¿Quieres que genere un informe formal con los diagnósticos y tratamientos sugeridos?",
        "Perfecto. Voy a organizar toda la información del diagnóstico para que la tengas lista.",
    ],
    "what_is": [
        "Soy Mimetic AI, un sistema de apoyo al diagnóstico médico. Analizo los síntomas que me describes y te sugiero posibles enfermedades con su nivel de confianza, y si lo deseas, también te recomiendo tratamientos. ¿Empezamos con algún síntoma?",
        "Soy una inteligencia artificial especializada en diagnóstico médico descriptivo. Tú me describes los síntomas del paciente, yo los comparo con mi base de conocimiento y te sugiero diagnósticos diferenciales. ¿Te parece si empezamos?",
        "Mimetic AI, para servirte. Estoy aquí para ayudarte a identificar posibles enfermedades basado en los síntomas del paciente. También puedo sugerir tratamientos. ¿Con qué síntoma empezamos?",
    ],
    "chatty": [
        "Pues mira, estoy aquí esperando para ayudarte con diagnósticos. Si quieres, podemos empezar con eso. ¿Qué síntomas tiene el paciente?",
        "Jaja, soy un sistema de diagnóstico, así que mi especialidad es la medicina. Pero también sé charlar un poco. ¿Empezamos con los síntomas o prefieres seguir hablando?",
        "Pasito pasito, tomando café virtual y procesando datos médicos. ¿Te ayudo con un diagnóstico hoy?",
    ],
    "encouragement": [
        "¡Gracias! Eso me anima a seguir mejorando. ¿Seguimos con el diagnóstico?",
        "Qué amable. Me alegra ser de utilidad. Cuéntame más sobre el paciente.",
        "Aprecio tus palabras. Ahora, ¿qué síntomas tiene el paciente para analizar?",
    ],
}

UNKNOWN_RESPONSES = [
    "No estoy seguro de entender. ¿Podrías describir los síntomas del paciente?",
    "Disculpa, aún estoy aprendiendo. ¿Me ayudas describiendo qué síntomas físicos tiene el paciente?",
    "Soy un sistema de diagnóstico médico. Por favor, describe los síntomas que observas en el paciente.",
    "Interesante, pero no estoy seguro de cómo procesar eso. ¿Qué síntomas presenta el paciente?",
]

REPORT_TRANSITIONS = [
    "Cuando estés listo para enviar el informe, solo dímelo.",
    "Avísame cuando quieras que genere el resumen final del diagnóstico.",
    "Cuando termines de describir todos los síntomas, pídeme el informe y lo preparo.",
    "Si ya tienes todos los síntomas, dime 'listo' y te preparo el reporte.",
    "Llevo registro de todo. Cuando quieras el diagnóstico completo, solo dilo.",
]


def _match_pattern(text: str) -> str | None:
    """Match text against conversational patterns. Returns category name or None."""
    cleaned = normalize(text)

    for category, patterns in CONV_PATTERNS.items():
        for pattern in patterns:
            if pattern in cleaned:
                return category

    # Check 'gracias' separately (it's shorter)
    if cleaned in {"gracias", "muchas gracias", "te agradezco", "thank you", "thanks"}:
        return "encouragement"

    return None


def classify_conversation(text: str) -> str | None:
    """Classify user input into conversation category."""
    return _match_pattern(text)


def pick_response(category: str) -> str:
    responses = CONV_RESPONSES.get(category, UNKNOWN_RESPONSES)
    return random.choice(responses)


def pick_unknown_response() -> str:
    return random.choice(UNKNOWN_RESPONSES)


def pick_report_transition() -> str:
    return random.choice(REPORT_TRANSITIONS)


def is_conversational(text: str) -> bool:
    return _match_pattern(text) is not None


def is_thank_you(text: str) -> bool:
    cleaned = normalize(text)
    return cleaned in {"gracias", "muchas gracias", "te agradezco", "thank you", "thanks"}


def is_greeting(text: str) -> bool:
    return _match_pattern(text) == "greeting"


def is_goodbye(text: str) -> bool:
    return _match_pattern(text) == "goodbye"


def is_report_request(text: str) -> bool:
    return _match_pattern(text) == "ready_report"
