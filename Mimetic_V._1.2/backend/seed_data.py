import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.utils import normalize_text

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "mimetic_ai")

symptoms = [
    {"name": "fiebre", "description": "Temperatura corporal elevada (>38°C)", "category": "generales"},
    {"name": "cefalea", "description": "Dolor de cabeza intenso", "category": "neurologico"},
    {"name": "dolor", "description": "Dolor localizado o generalizado", "category": "generales"},
    {"name": "eritema", "description": "Enrojecimiento de la piel", "category": "dermatologico"},
    {"name": "linfadenopatía", "description": "Inflamación de los ganglios linfáticos", "category": "generales"},
    {"name": "parestesia", "description": "Hormigueo o adormecimiento", "category": "neurologico"},
    {"name": "rinorrea", "description": "Secreción o fluido nasal", "category": "respiratorio"},
    {"name": "tos", "description": "Tos seca o productiva", "category": "respiratorio"},
    {"name": "dolor de cabeza", "description": "Cefalea o dolor craneal", "category": "neurologico"},
    {"name": "fatiga", "description": "Cansancio o debilidad general", "category": "generales"},
    {"name": "dificultad para respirar", "description": "Disnea o falta de aire", "category": "respiratorio"},
    {"name": "dolor de garganta", "description": "Odinofagia o dolor faríngeo", "category": "respiratorio"},
    {"name": "congestión nasal", "description": "Nariz tapada o mucosidad", "category": "respiratorio"},
    {"name": "escalofríos", "description": "Sensación de frío con temblores", "category": "generales"},
    {"name": "dolor muscular", "description": "Mialgias o dolores corporales", "category": "musculoesqueletico"},
    {"name": "pérdida del gusto", "description": "Ageusia o pérdida del sentido del gusto", "category": "neurologico"},
    {"name": "pérdida del olfato", "description": "Anosmia o pérdida del olfato", "category": "neurologico"},
    {"name": "náuseas", "description": "Náuseas o ganas de vomitar", "category": "digestivo"},
    {"name": "vómito", "description": "Vómito o emesis", "category": "digestivo"},
    {"name": "diarrea", "description": "Heces sueltas o líquidas frecuentes", "category": "digestivo"},
    {"name": "dolor abdominal", "description": "Dolor en la región del abdomen", "category": "digestivo"},
    {"name": "deshidratación", "description": "Pérdida excesiva de líquidos corporales", "category": "generales"},
    {"name": "sarpullido", "description": "Erupción cutánea o rash", "category": "dermatologico"},
    {"name": "dolor en el pecho", "description": "Dolor torácico", "category": "cardiovascular"},
    {"name": "presión arterial alta", "description": "Hipertensión o PA elevada", "category": "cardiovascular"},
    {"name": "mareos", "description": "Vértigo o sensación de desmayo", "category": "neurologico"},
    {"name": "dolor de oído", "description": "Otalgia o dolor auricular", "category": "otologico"},
    {"name": "secreción del oído", "description": "Otorrea o líquido del oído", "category": "otologico"},
    {"name": "ardor al orinar", "description": "Disuria o dolor miccional", "category": "urinario"},
    {"name": "frecuencia urinaria", "description": "Polaquiuria u orinar con frecuencia", "category": "urinario"},
    {"name": "dolor lumbar", "description": "Dolor en la región baja de la espalda", "category": "musculoesqueletico"},
    {"name": "fiebre alta persistente", "description": "Fiebre >39°C que no cede", "category": "generales"},
    {"name": "confusión", "description": "Estado de confusión o desorientación", "category": "neurologico"},
    {"name": "rigidez de cuello", "description": "Rigidez nucal o cuello tieso", "category": "neurologico"},
    {"name": "dolor articular", "description": "Artralgia o dolor en las articulaciones", "category": "musculoesqueletico"},
    {"name": "hinchazón", "description": "Edema o inflamación de tejidos", "category": "generales"},
    {"name": "ictericia", "description": "Coloración amarillenta de piel/ojos", "category": "digestivo"},
    {"name": "pérdida de apetito", "description": "Anorexia o inapetencia", "category": "digestivo"},
    {"name": "heces con sangre", "description": "Rectorragia o sangre en heces", "category": "digestivo"},
    {"name": "tos con sangre", "description": "Hemoptisis o expectoración con sangre", "category": "respiratorio"},
    {"name": "sudoración nocturna", "description": "Hiperhidrosis nocturna", "category": "generales"},
    {"name": "pérdida de peso", "description": "Pérdida de peso involuntaria", "category": "generales"},
    {"name": "comezón", "description": "Prurito o picazón en la piel", "category": "dermatologico"},
    {"name": "ojos rojos", "description": "Hiperemia conjuntival", "category": "oftalmologico"},
    {"name": "sensibilidad a la luz", "description": "Fotofobia", "category": "neurologico"},
    {"name": "dolor detrás de los ojos", "description": "Dolor retroorbitario", "category": "oftalmologico"},
    {"name": "mialgias", "description": "Dolores musculares generalizados", "category": "musculoesqueletico"},
    {"name": "orina turbia", "description": "Orina con aspecto turbio", "category": "urinario"},
    {"name": "orina maloliente", "description": "Orina con olor fuerte", "category": "urinario"},
    {"name": "urgencia urinaria", "description": "Necesidad imperiosa de orinar", "category": "urinario"},
    {"name": "petequias", "description": "Pequeñas manchas rojas en la piel", "category": "dermatologico"},
    {"name": "sangrado de encías", "description": "Sangrado gingival", "category": "generales"},
    {"name": "dolor abdominal intenso", "description": "Dolor abdominal severo", "category": "digestivo"},
    {"name": "fatiga extrema", "description": "Cansancio severo o agotamiento", "category": "generales"},
    {"name": "expectoración purulenta", "description": "Flema con pus", "category": "respiratorio"},
    {"name": "taquipnea", "description": "Frecuencia respiratoria elevada", "category": "respiratorio"},
    {"name": "cianosis", "description": "Coloración azulada de piel por falta de oxígeno", "category": "cardiovascular"},
    {"name": "expectoración", "description": "Flema o mucosidad expulsada al toser", "category": "respiratorio"},
    {"name": "sibilancias", "description": "Silbido al respirar", "category": "respiratorio"},
    {"name": "malestar general intenso", "description": "Sensación de enfermedad severa", "category": "generales"},
    {"name": "dolor ocular", "description": "Dolor en los ojos", "category": "oftalmologico"},
    {"name": "letargo", "description": "Somnolencia o falta de energía extrema", "category": "neurologico"},
    {"name": "convulsiones", "description": "Crisis convulsivas o ataques epilépticos", "category": "neurologico"},
    {"name": "signo de Kernig", "description": "Imposibilidad de extender la rodilla con cadera flexionada", "category": "neurologico"},
    {"name": "signo de Brudzinski", "description": "Flexión involuntaria de caderas al flexionar el cuello", "category": "neurologico"},
    {"name": "tos crónica (>3 semanas)", "description": "Tos persistente por más de 3 semanas", "category": "respiratorio"},
    {"name": "inflamación de amígdalas", "description": "Amígdalas rojas e inflamadas", "category": "respiratorio"},
    {"name": "exudado purulento", "description": "Secreción amarillenta de pus", "category": "generales"},
    {"name": "adenopatías cervicales", "description": "Ganglios inflamados en el cuello", "category": "generales"},
    {"name": "rinorrea acuosa", "description": "Secreción nasal líquida y clara", "category": "respiratorio"},
    {"name": "prurito nasal", "description": "Picazón dentro de la nariz", "category": "respiratorio"},
    {"name": "lagrimeo", "description": "Producción excesiva de lágrimas", "category": "oftalmologico"},
    {"name": "dificultad para tragar", "description": "Disfagia o dificultad al deglutir", "category": "digestivo"},
    {"name": "estornudos", "description": "Estornudos frecuentes", "category": "respiratorio"},
    {"name": "tenesmo", "description": "Sensación de evacuación incompleta", "category": "digestivo"},
    {"name": "irritabilidad", "description": "Estado de irritación o mal humor", "category": "neurologico"},
    {"name": "pérdida auditiva temporal", "description": "Disminución pasajera de la audición", "category": "otologico"},
    {"name": "sensación de oído tapado", "description": "Plenitud auricular", "category": "otologico"},
    {"name": "orina oscura", "description": "Orina de color oscuro como té o cola", "category": "urinario"},
    {"name": "heces pálidas", "description": "Heces de color arcilla o gris claro", "category": "digestivo"},
    {"name": "malestar general", "description": "Sensación inespecífica de enfermedad", "category": "generales"},
    {"name": "dolor torácico opresivo", "description": "Dolor en el pecho con sensación de presión", "category": "cardiovascular"},
    {"name": "dolor irradiado a brazo izquierdo", "description": "Dolor que se extiende al brazo izquierdo", "category": "cardiovascular"},
    {"name": "disnea", "description": "Falta de aire o dificultad respiratoria", "category": "respiratorio"},
    {"name": "sudoración profusa", "description": "Sudoración excesiva y abundante", "category": "generales"},
    {"name": "palpitaciones", "description": "Sensación de latidos cardíacos rápidos o fuertes", "category": "cardiovascular"},
    {"name": "ansiedad", "description": "Estado de preocupación o nerviosismo intenso", "category": "neurologico"},
    {"name": "dolor epigástrico", "description": "Dolor en la parte superior del abdomen", "category": "digestivo"},
    {"name": "síncope", "description": "Desmayo o pérdida breve de conciencia", "category": "neurologico"},
    {"name": "disnea de esfuerzo", "description": "Falta de aire al realizar actividad física", "category": "respiratorio"},
    {"name": "edema en piernas", "description": "Hinchazón en las extremidades inferiores", "category": "cardiovascular"},
    {"name": "taquipnea nocturna", "description": "Respiración rápida durante la noche", "category": "respiratorio"},
    {"name": "ortopnea", "description": "Dificultad para respirar al estar acostado", "category": "respiratorio"},
    {"name": "aumento de peso súbito", "description": "Ganancia rápida de peso por retención de líquidos", "category": "generales"},
    {"name": "tos nocturna", "description": "Tos que empeora durante la noche", "category": "respiratorio"},
    {"name": "disminución de la tolerancia al ejercicio", "description": "Menor capacidad para hacer actividad física", "category": "generales"},
    {"name": "dolor de cabeza occipital", "description": "Dolor en la parte posterior de la cabeza", "category": "neurologico"},
    {"name": "vértigo", "description": "Sensación de movimiento giratorio", "category": "neurologico"},
    {"name": "visión borrosa", "description": "Pérdida de nitidez visual", "category": "oftalmologico"},
    {"name": "zumbido de oídos", "description": "Tinnitus o pitidos en los oídos", "category": "otologico"},
    {"name": "epistaxis", "description": "Sangrado nasal", "category": "generales"},
    {"name": "enrojecimiento facial", "description": "Rubor o cara roja", "category": "dermatologico"},
    {"name": "poliuria", "description": "Producción excesiva de orina", "category": "urinario"},
    {"name": "polidipsia", "description": "Sed excesiva", "category": "generales"},
    {"name": "polifagia", "description": "Hambre excesiva o aumento del apetito", "category": "digestivo"},
    {"name": "pérdida de peso inexplicada", "description": "Pérdida de peso sin causa aparente", "category": "generales"},
    {"name": "infecciones frecuentes", "description": "Infecciones recurrentes", "category": "generales"},
    {"name": "cicatrización lenta", "description": "Heridas que tardan en sanar", "category": "generales"},
    {"name": "hormigueo en extremidades", "description": "Parestesia en brazos o piernas", "category": "neurologico"},
    {"name": "aumento de peso", "description": "Ganancia de peso involuntaria", "category": "generales"},
    {"name": "intolerancia al frío", "description": "Sensibilidad excesiva al frío", "category": "generales"},
    {"name": "piel seca", "description": "Piel descamada o reseca", "category": "dermatologico"},
    {"name": "caída de cabello", "description": "Alopecia o pérdida de cabello", "category": "dermatologico"},
    {"name": "estreñimiento", "description": "Dificultad para evacuar o heces duras", "category": "digestivo"},
    {"name": "bradicardia", "description": "Frecuencia cardíaca lenta (<60 lpm)", "category": "cardiovascular"},
    {"name": "depresión", "description": "Estado de ánimo bajo o tristeza persistente", "category": "neurologico"},
    {"name": "bocio", "description": "Aumento de tamaño de la glándula tiroides", "category": "endocrino"},
    {"name": "pérdida de peso con apetito aumentado", "description": "Adelgazamiento pese a comer más", "category": "endocrino"},
    {"name": "taquicardia", "description": "Frecuencia cardíaca acelerada (>100 lpm)", "category": "cardiovascular"},
    {"name": "intolerancia al calor", "description": "Sensibilidad excesiva al calor", "category": "generales"},
    {"name": "sudoración excesiva", "description": "Hiperhidrosis", "category": "generales"},
    {"name": "nerviosismo", "description": "Estado de agitación o inquietud", "category": "neurologico"},
    {"name": "temblores", "description": "Temblor fino en manos o dedos", "category": "neurologico"},
    {"name": "insomnio", "description": "Dificultad para dormir", "category": "neurologico"},
    {"name": "exoftalmos", "description": "Ojos saltones o protrusión ocular", "category": "oftalmologico"},
    {"name": "fatiga muscular", "description": "Debilidad en los músculos", "category": "musculoesqueletico"},
    {"name": "dolor de cabeza pulsátil unilateral", "description": "Dolor de cabeza como latido en un solo lado", "category": "neurologico"},
    {"name": "fotofobia", "description": "Molestia o intolerancia a la luz", "category": "neurologico"},
    {"name": "fonofobia", "description": "Molestia o intolerancia al ruido", "category": "neurologico"},
    {"name": "aura visual", "description": "Alucinaciones visuales previas a la migraña", "category": "neurologico"},
    {"name": "parestesias", "description": "Hormigueo o adormecimiento", "category": "neurologico"},
    {"name": "dolor empeora con actividad física", "description": "Dolor que aumenta con el movimiento", "category": "musculoesqueletico"},
    {"name": "debilidad facial unilateral", "description": "Parálisis o debilidad de un lado de la cara", "category": "neurologico"},
    {"name": "debilidad en extremidades", "description": "Pérdida de fuerza en brazos o piernas", "category": "neurologico"},
    {"name": "confusión súbita", "description": "Desorientación repentina", "category": "neurologico"},
    {"name": "dificultad para hablar", "description": "Disartria o dificultad para articular palabras", "category": "neurologico"},
    {"name": "pérdida de visión", "description": "Pérdida parcial o total de la vista", "category": "oftalmologico"},
    {"name": "dolor de cabeza súbito severo", "description": "Cefalea intensa de inicio repentino", "category": "neurologico"},
    {"name": "pérdida de equilibrio", "description": "Inestabilidad al caminar", "category": "neurologico"},
    {"name": "marcha inestable", "description": "Caminar con dificultad o tambaleo", "category": "neurologico"},
    {"name": "pérdida de conciencia", "description": "Pérdida del conocimiento o desmayo", "category": "neurologico"},
    {"name": "convulsiones tónico-clónicas", "description": "Movimientos violentos involuntarios de todo el cuerpo", "category": "neurologico"},
    {"name": "ausencias", "description": "Episodios breves de desconexión", "category": "neurologico"},
    {"name": "sacudidas mioclónicas", "description": "Movimientos musculares breves e involuntarios", "category": "neurologico"},
    {"name": "movimientos involuntarios", "description": "Movimientos anormales no controlados", "category": "neurologico"},
    {"name": "aura epigástrica", "description": "Sensación ascendente en el abdomen previa a crisis", "category": "neurologico"},
    {"name": "confusión postictal", "description": "Desorientación después de una convulsión", "category": "neurologico"},
    {"name": "mordedura de lengua", "description": "Herida en la lengua por mordedura durante convulsión", "category": "neurologico"},
    {"name": "temblor en reposo", "description": "Temblor que aparece cuando el miembro está en reposo", "category": "neurologico"},
    {"name": "rigidez muscular", "description": "Aumento del tono muscular", "category": "musculoesqueletico"},
    {"name": "bradicinesia", "description": "Lentitud de movimientos", "category": "neurologico"},
    {"name": "inestabilidad postural", "description": "Dificultad para mantener el equilibrio", "category": "neurologico"},
    {"name": "marcha arrastrada", "description": "Caminar arrastrando los pies", "category": "neurologico"},
    {"name": "micrografía", "description": "Letra pequeña y apretada", "category": "neurologico"},
    {"name": "hipomimia", "description": "Falta de expresión facial o cara de máscara", "category": "neurologico"},
    {"name": "disfagia", "description": "Dificultad para tragar", "category": "digestivo"},
    {"name": "deterioro cognitivo", "description": "Disminución de la capacidad mental", "category": "neurologico"},
    {"name": "dolor articular simétrico", "description": "Dolor en las mismas articulaciones de ambos lados", "category": "musculoesqueletico"},
    {"name": "rigidez matutina (>30 min)", "description": "Rigidez articular al despertar que dura más de 30 min", "category": "musculoesqueletico"},
    {"name": "inflamación articular", "description": "Articulaciones hinchadas", "category": "musculoesqueletico"},
    {"name": "nódulos reumatoides", "description": "Bultos subcutáneos cerca de articulaciones", "category": "musculoesqueletico"},
    {"name": "deformidad articular", "description": "Deformación visible de las articulaciones", "category": "musculoesqueletico"},
    {"name": "dolor a la palpación", "description": "Dolor al tocar o presionar", "category": "generales"},
    {"name": "erupción en mariposa facial", "description": "Rash facial con forma de mariposa", "category": "dermatologico"},
    {"name": "fotosensibilidad", "description": "Reacción exagerada de la piel al sol", "category": "dermatologico"},
    {"name": "úlceras orales", "description": "Llagas en la boca", "category": "digestivo"},
    {"name": "artritis", "description": "Inflamación de las articulaciones", "category": "musculoesqueletico"},
    {"name": "serositis", "description": "Inflamación de las membranas serosas", "category": "generales"},
    {"name": "nefritis", "description": "Inflamación del riñón", "category": "urinario"},
    {"name": "fenómeno de Raynaud", "description": "Cambio de coloración de dedos con el frío", "category": "cardiovascular"},
    {"name": "fiebre cíclica con escalofríos", "description": "Fiebre que aparece en ciclos con temblores", "category": "generales"},
    {"name": "dolor de cabeza intenso", "description": "Cefalea severa", "category": "neurologico"},
    {"name": "hepatomegalia", "description": "Aumento del tamaño del hígado", "category": "digestivo"},
    {"name": "esplenomegalia", "description": "Aumento del tamaño del bazo", "category": "digestivo"},
    {"name": "fiebre elevada escalonada", "description": "Fiebre que sube gradualmente en días", "category": "generales"},
    {"name": "cefalea frontal", "description": "Dolor de cabeza en la región frontal", "category": "neurologico"},
    {"name": "bradicardia relativa", "description": "Frecuencia cardíaca baja para la fiebre presente", "category": "cardiovascular"},
    {"name": "manchas rosadas en tronco", "description": "Rash de color rosado en el torso", "category": "dermatologico"},
    {"name": "estreñimiento o diarrea", "description": "Alteración del ritmo intestinal", "category": "digestivo"},
    {"name": "hepatoesplenomegalia", "description": "Aumento de tamaño de hígado y bazo", "category": "digestivo"},
    {"name": "exantema vesicular pruriginoso", "description": "Erupción con ampollas que pican", "category": "dermatologico"},
    {"name": "vesículas en diferentes estadios", "description": "Ampollas en distintas etapas de evolución", "category": "dermatologico"},
    {"name": "lesiones en cuero cabelludo", "description": "Lesiones cutáneas en el cuero cabelludo", "category": "dermatologico"},
    {"name": "erupción vesicular dermatomal", "description": "Ampollas siguiendo un dermatoma nervioso", "category": "dermatologico"},
    {"name": "dolor urente o punzante", "description": "Dolor como quemadura o pinchazo", "category": "neurologico"},
    {"name": "hipersensibilidad de la piel", "description": "Piel sensible al tacto", "category": "dermatologico"},
    {"name": "prurito", "description": "Picazón", "category": "dermatologico"},
    {"name": "faringitis", "description": "Inflamación de la faringe", "category": "respiratorio"},
    {"name": "linfadenopatía generalizada", "description": "Ganglios inflamados en todo el cuerpo", "category": "generales"},
    {"name": "artralgias", "description": "Dolor en las articulaciones", "category": "musculoesqueletico"},
    {"name": "rash maculopapular", "description": "Erupción cutánea con manchas y pápulas", "category": "dermatologico"},
    {"name": "úlceras orales o genitales", "description": "Llagas en boca o genitales", "category": "dermatologico"},
    {"name": "fatiga severa", "description": "Cansancio extremo", "category": "generales"},
    {"name": "linfadenopatía cervical posterior", "description": "Ganglios inflamados en la parte trasera del cuello", "category": "generales"},
    {"name": "faringitis exudativa", "description": "Inflamación faríngea con secreción purulenta", "category": "respiratorio"},
    {"name": "rash máculo-papular", "description": "Erupción con manchas planas y elevadas", "category": "dermatologico"},
    {"name": "cefalea severa", "description": "Dolor de cabeza muy intenso", "category": "neurologico"},
    {"name": "mialgias (especialmente gemelares)", "description": "Dolor muscular en las pantorrillas", "category": "musculoesqueletico"},
    {"name": "inyección conjuntival", "description": "Ojos rojos por vasos dilatados", "category": "oftalmologico"},
    {"name": "insuficiencia renal", "description": "Falla de la función renal", "category": "urinario"},
    {"name": "hemorragias", "description": "Sangrados activos", "category": "generales"},
    {"name": "congestión pulmonar", "description": "Acumulación de líquido en los pulmones", "category": "respiratorio"},
    {"name": "fiebre ondulante", "description": "Fiebre que sube y baja en ondas", "category": "generales"},
    {"name": "opresión torácica", "description": "Sensación de presión en el pecho", "category": "cardiovascular"},
    {"name": "empeoramiento nocturno o matutino", "description": "Síntomas que empeoran de noche o al amanecer", "category": "respiratorio"},
    {"name": "respiración corta", "description": "Respiración superficial y rápida", "category": "respiratorio"},
    {"name": "uso de musculatura accesoria", "description": "Usar músculos del cuello y hombros para respirar", "category": "respiratorio"},
    {"name": "disnea progresiva", "description": "Falta de aire que empeora con el tiempo", "category": "respiratorio"},
    {"name": "tos crónica", "description": "Tos persistente por mucho tiempo", "category": "respiratorio"},
    {"name": "infecciones respiratorias recurrentes", "description": "Infecciones frecuentes de las vías respiratorias", "category": "respiratorio"},
    {"name": "disfonía o afonía", "description": "Ronquera o pérdida de la voz", "category": "respiratorio"},
    {"name": "tos seca", "description": "Tos sin producción de flema", "category": "respiratorio"},
    {"name": "sensación de cuerpo extraño en garganta", "description": "Sensación de tener algo atorado en la garganta", "category": "respiratorio"},
    {"name": "fiebre leve", "description": "Temperatura ligeramente elevada (<38°C)", "category": "generales"},
    {"name": "odinofagia", "description": "Dolor al tragar", "category": "respiratorio"},
    {"name": "edema de cuerdas vocales", "description": "Hinchazón de las cuerdas vocales", "category": "respiratorio"},
    {"name": "dolor abdominal periumbilical que migra a fosa ilíaca derecha", "description": "Dolor que empieza en el ombligo y se mueve al lado derecho bajo", "category": "digestivo"},
    {"name": "defensa abdominal", "description": "Tensión involuntaria de los músculos abdominales", "category": "digestivo"},
    {"name": "signo de Blumberg", "description": "Dolor al soltar la presión en el abdomen", "category": "digestivo"},
    {"name": "signo de Rovsing", "description": "Dolor en lado derecho al presionar lado izquierdo", "category": "digestivo"},
    {"name": "dolor en hipocondrio derecho", "description": "Dolor en la parte superior derecha del abdomen", "category": "digestivo"},
    {"name": "signo de Murphy", "description": "Dolor al presionar la vesícula biliar al inhalar", "category": "digestivo"},
    {"name": "dolor irradiado a hombro derecho", "description": "Dolor que se extiende al hombro derecho", "category": "digestivo"},
    {"name": "ictericia leve", "description": "Coloración amarillenta leve de la piel", "category": "digestivo"},
    {"name": "distensión abdominal", "description": "Abdomen inflamado o hinchado", "category": "digestivo"},
    {"name": "dolor abdominal epigástrico quemante", "description": "Ardor en la boca del estómago", "category": "digestivo"},
    {"name": "dolor alivia con alimentos", "description": "Dolor que mejora al comer", "category": "digestivo"},
    {"name": "dolor nocturno", "description": "Dolor que aparece durante la noche", "category": "digestivo"},
    {"name": "hematemesis", "description": "Vómito con sangre", "category": "digestivo"},
    {"name": "melena", "description": "Heces negras por sangre digerida", "category": "digestivo"},
    {"name": "saciedad temprana", "description": "Sensación de llenura al comer poco", "category": "digestivo"},
    {"name": "acidez retroesternal", "description": "Ardor en el pecho", "category": "digestivo"},
    {"name": "regurgitación ácida", "description": "Devolución de contenido ácido a la boca", "category": "digestivo"},
    {"name": "ronquera matutina", "description": "Voz ronca al despertar", "category": "respiratorio"},
    {"name": "sensación de globo faríngeo", "description": "Sensación de nudo en la garganta", "category": "digestivo"},
    {"name": "erosión dental", "description": "Desgaste del esmalte dental por ácido", "category": "digestivo"},
    {"name": "dolor lumbar intenso unilateral", "description": "Dolor fuerte en un lado de la espalda baja", "category": "musculoesqueletico"},
    {"name": "dolor irradiado a genitales", "description": "Dolor que se extiende a los genitales", "category": "urinario"},
    {"name": "inquietud extrema", "description": "Incapacidad de estar quieto por el dolor", "category": "neurologico"},
    {"name": "hematuria", "description": "Sangre en la orina", "category": "urinario"},
    {"name": "disuria", "description": "Dolor o dificultad al orinar", "category": "urinario"},
    {"name": "disminución de la diuresis", "description": "Reducción del volumen de orina", "category": "urinario"},
    {"name": "edema generalizado", "description": "Hinchazón en todo el cuerpo", "category": "generales"},
    {"name": "hipertensión arterial", "description": "Presión arterial elevada", "category": "cardiovascular"},
    {"name": "hiperkalemia", "description": "Potasio elevado en sangre", "category": "generales"},
    {"name": "asterixis", "description": "Temblor en las manos al extender las muñecas", "category": "neurologico"},
    {"name": "eritema localizado", "description": "Enrojecimiento de la piel en un área", "category": "dermatologico"},
    {"name": "calor local", "description": "Aumento de temperatura en la piel", "category": "dermatologico"},
    {"name": "edema", "description": "Hinchazón por acumulación de líquido", "category": "generales"},
    {"name": "ampollas", "description": "Vesículas llenas de líquido", "category": "dermatologico"},
    {"name": "linfangitis", "description": "Inflamación de los vasos linfáticos", "category": "dermatologico"},
    {"name": "linfadenopatía regional", "description": "Ganglios inflamados cerca del área afectada", "category": "generales"},
    {"name": "habones eritematosos", "description": "Ronchas rojas en la piel", "category": "dermatologico"},
    {"name": "prurito intenso", "description": "Picazón severa", "category": "dermatologico"},
    {"name": "edema angioneurótico", "description": "Hinchazón profunda de la piel y mucosas", "category": "dermatologico"},
    {"name": "lesiones evanescentes (<24h)", "description": "Lesiones que desaparecen en menos de 24 horas", "category": "dermatologico"},
    {"name": "dermografismo", "description": "Ronchas que aparecen al rascar la piel", "category": "dermatologico"},
    {"name": "palidez del centro de las lesiones", "description": "Centro pálido rodeado de enrojecimiento", "category": "dermatologico"},
    {"name": "sensación de ardor", "description": "Sensación de quemadura en la piel", "category": "dermatologico"},
    {"name": "liquenificación", "description": "Engrosamiento de la piel por rascado crónico", "category": "dermatologico"},
    {"name": "exudación y costras", "description": "Supuración con formación de costras", "category": "dermatologico"},
    {"name": "lesiones flexurales", "description": "Lesiones en pliegues de la piel", "category": "dermatologico"},
    {"name": "xerosis", "description": "Sequedad excesiva de la piel", "category": "dermatologico"},
    {"name": "alteración del sueño por prurito", "description": "Problemas para dormir por picazón", "category": "dermatologico"},
    {"name": "dolor suprapúbico", "description": "Dolor sobre el pubis", "category": "urinario"},
    {"name": "frecuencia urinaria", "description": "Orinar frecuentemente día y noche", "category": "urinario"},
    {"name": "dolor al llenar la vejiga", "description": "Dolor al acumularse la orina", "category": "urinario"},
    {"name": "alivio con vaciamiento", "description": "Mejoría del dolor al orinar", "category": "urinario"},
    {"name": "dispareunia", "description": "Dolor durante las relaciones sexuales", "category": "urinario"},
    {"name": "dolor musculoesquelético generalizado", "description": "Dolor en músculos y huesos de todo el cuerpo", "category": "musculoesqueletico"},
    {"name": "trastornos del sueño", "description": "Dificultad para conciliar o mantener el sueño", "category": "neurologico"},
    {"name": "rigidez matutina", "description": "Rigidez articular al despertar", "category": "musculoesqueletico"},
    {"name": "síndrome de colon irritable", "description": "Trastorno digestivo con dolor y alteración del ritmo", "category": "digestivo"},
    {"name": "dificultades cognitivas", "description": "Problemas de concentración o memoria", "category": "neurologico"},
    {"name": "hematoma", "description": "Acumulación de sangre bajo la piel por un golpe (moretón o morado)", "category": "musculoesqueletico"},
    {"name": "contusión", "description": "Lesión por golpe sin herida abierta, que causa dolor, inflamación y moretón", "category": "musculoesqueletico"},
]

diseases = [
    {
        "name": "Influenza (Gripe)",
        "description": "Infección viral respiratoria aguda causada por el virus de la influenza",
        "symptoms": ["fiebre", "tos", "dolor de cabeza", "fatiga", "dolor de garganta", "congestión nasal", "escalofríos", "dolor muscular", "malestar general intenso", "pérdida de apetito", "dolor ocular"],
        "severity": "moderate",
    },
    {
        "name": "Resfriado Común",
        "description": "Infección viral leve del tracto respiratorio superior",
        "symptoms": ["tos", "dolor de garganta", "congestión nasal", "dolor de cabeza", "fatiga", "estornudos", "rinorrea"],
        "severity": "mild",
    },
    {
        "name": "COVID-19",
        "description": "Enfermedad infecciosa causada por el coronavirus SARS-CoV-2",
        "symptoms": ["fiebre", "tos", "fatiga", "pérdida del gusto", "pérdida del olfato", "dolor de cabeza", "dolor de garganta", "dificultad para respirar", "mialgias", "diarrea", "congestión nasal", "escalofríos"],
        "severity": "high",
    },
    {
        "name": "Gastroenteritis Aguda",
        "description": "Inflamación del estómago e intestinos, comúnmente por infección viral o bacteriana",
        "symptoms": ["diarrea", "náuseas", "vómito", "dolor abdominal", "fiebre", "fatiga", "deshidratación", "pérdida de apetito", "dolor muscular"],
        "severity": "moderate",
    },
    {
        "name": "Neumonía",
        "description": "Infección pulmonar que inflama los alvéolos, puede ser bacteriana o viral",
        "symptoms": ["fiebre", "tos", "dificultad para respirar", "dolor en el pecho", "escalofríos", "fatiga", "expectoración purulenta", "taquipnea", "cianosis"],
        "severity": "high",
    },
    {
        "name": "Otitis Media",
        "description": "Infección del oído medio, común en niños",
        "symptoms": ["dolor de oído", "fiebre", "secreción del oído", "dolor de cabeza", "irritabilidad", "pérdida auditiva temporal", "sensación de oído tapado"],
        "severity": "moderate",
    },
    {
        "name": "Infección Urinaria",
        "description": "Infección del tracto urinario, generalmente bacteriana",
        "symptoms": ["ardor al orinar", "frecuencia urinaria", "dolor abdominal", "fiebre", "dolor lumbar", "orina turbia", "orina maloliente", "urgencia urinaria", "escalofríos"],
        "severity": "moderate",
    },
    {
        "name": "Dengue",
        "description": "Enfermedad viral transmitida por mosquitos Aedes",
        "symptoms": ["fiebre alta persistente", "dolor de cabeza", "dolor muscular", "dolor articular", "dolor detrás de los ojos", "sarpullido", "náuseas", "vómito", "petequias", "sangrado de encías", "dolor abdominal intenso", "fatiga extrema"],
        "severity": "high",
    },
    {
        "name": "Meningitis",
        "description": "Inflamación de las membranas que recubren el cerebro y la médula espinal",
        "symptoms": ["fiebre", "dolor de cabeza", "rigidez de cuello", "confusión", "náuseas", "vómito", "sensibilidad a la luz", "letargo", "convulsiones", "signo de Kernig", "signo de Brudzinski"],
        "severity": "critical",
    },
    {
        "name": "Hepatitis A",
        "description": "Infección viral del hígado transmitida por alimentos o agua contaminados",
        "symptoms": ["fatiga", "pérdida de apetito", "ictericia", "dolor abdominal", "náuseas", "fiebre", "orina oscura", "heces pálidas", "malestar general", "dolor articular"],
        "severity": "moderate",
    },
    {
        "name": "Bronquitis Aguda",
        "description": "Inflamación de los bronquios, generalmente por infección viral",
        "symptoms": ["tos", "fatiga", "dificultad para respirar", "dolor en el pecho", "fiebre", "dolor de garganta", "expectoración", "sibilancias"],
        "severity": "moderate",
    },
    {
        "name": "Amigdalitis",
        "description": "Infección e inflamación de las amígdalas",
        "symptoms": ["dolor de garganta", "fiebre", "dolor de cabeza", "fatiga", "dificultad para tragar", "inflamación de amígdalas", "exudado purulento", "adenopatías cervicales"],
        "severity": "moderate",
    },
    {
        "name": "Rinitis Alérgica",
        "description": "Reacción alérgica que causa inflamación nasal",
        "symptoms": ["congestión nasal", "estornudos", "ojos rojos", "comezón", "rinorrea acuosa", "prurito nasal", "lagrimeo"],
        "severity": "mild",
    },
    {
        "name": "Intoxicación Alimentaria",
        "description": "Enfermedad causada por consumir alimentos contaminados",
        "symptoms": ["diarrea", "vómito", "dolor abdominal", "náuseas", "fiebre", "deshidratación", "escalofríos", "heces con sangre"],
        "severity": "moderate",
    },
    {
        "name": "Tuberculosis",
        "description": "Infección bacteriana pulmonar grave causada por Mycobacterium tuberculosis",
        "symptoms": ["tos con sangre", "sudoración nocturna", "pérdida de peso", "fiebre", "fatiga", "dolor en el pecho", "tos crónica (>3 semanas)", "expectoración", "escalofríos"],
        "severity": "critical",
    },
    {
        "name": "Shigelosis (Disentería)",
        "description": "Infección bacteriana intestinal que causa diarrea con sangre",
        "symptoms": ["diarrea", "heces con sangre", "fiebre", "dolor abdominal", "náuseas", "deshidratación", "tenesmo", "escalofríos"],
        "severity": "high",
    },
    {
        "name": "Infarto Agudo de Miocardio",
        "description": "Necrosis del miocardio por isquemia prolongada",
        "symptoms": ["dolor torácico opresivo", "dolor irradiado a brazo izquierdo", "disnea", "náuseas", "vómito", "sudoración profusa", "palpitaciones", "ansiedad", "dolor epigástrico", "fatiga extrema", "síncope"],
        "severity": "critical",
    },
    {
        "name": "Insuficiencia Cardíaca",
        "description": "Incapacidad del corazón para bombear sangre adecuadamente",
        "symptoms": ["disnea de esfuerzo", "fatiga", "edema en piernas", "taquipnea nocturna", "ortopnea", "aumento de peso súbito", "tos nocturna", "palpitaciones", "disminución de la tolerancia al ejercicio"],
        "severity": "high",
    },
    {
        "name": "Hipertensión Arterial",
        "description": "Presión arterial elevada crónica",
        "symptoms": ["dolor de cabeza occipital", "vértigo", "visión borrosa", "zumbido de oídos", "epistaxis", "fatiga", "palpitaciones", "enrojecimiento facial"],
        "severity": "moderate",
    },
    {
        "name": "Diabetes Mellitus Tipo 2",
        "description": "Trastorno metabólico con hiperglucemia crónica",
        "symptoms": ["poliuria", "polidipsia", "polifagia", "pérdida de peso inexplicada", "fatiga", "visión borrosa", "infecciones frecuentes", "cicatrización lenta", "hormigueo en extremidades"],
        "severity": "high",
    },
    {
        "name": "Hipotiroidismo",
        "description": "Disminución de la función tiroidea",
        "symptoms": ["fatiga extrema", "aumento de peso", "intolerancia al frío", "piel seca", "caída de cabello", "estreñimiento", "bradicardia", "depresión", "letargo", "bocio"],
        "severity": "moderate",
    },
    {
        "name": "Hipertiroidismo",
        "description": "Producción excesiva de hormonas tiroideas",
        "symptoms": ["pérdida de peso con apetito aumentado", "taquicardia", "intolerancia al calor", "sudoración excesiva", "nerviosismo", "temblores", "insomnio", "exoftalmos", "bocio", "fatiga muscular"],
        "severity": "moderate",
    },
    {
        "name": "Migraña",
        "description": "Cefalea primaria con aura o sin aura",
        "symptoms": ["dolor de cabeza pulsátil unilateral", "fotofobia", "fonofobia", "náuseas", "vómito", "aura visual", "parestesias", "dolor empeora con actividad física"],
        "severity": "moderate",
    },
    {
        "name": "Accidente Cerebrovascular (ACV)",
        "description": "Interrupción súbita del flujo sanguíneo cerebral",
        "symptoms": ["debilidad facial unilateral", "debilidad en extremidades", "confusión súbita", "dificultad para hablar", "pérdida de visión", "dolor de cabeza súbito severo", "pérdida de equilibrio", "marcha inestable", "pérdida de conciencia"],
        "severity": "critical",
    },
    {
        "name": "Epilepsia",
        "description": "Trastorno neurológico con convulsiones recurrentes",
        "symptoms": ["convulsiones tónico-clónicas", "ausencias", "sacudidas mioclónicas", "movimientos involuntarios", "pérdida de conciencia", "aura epigástrica", "confusión postictal", "mordedura de lengua"],
        "severity": "high",
    },
    {
        "name": "Enfermedad de Parkinson",
        "description": "Trastorno neurodegenerativo del movimiento",
        "symptoms": ["temblor en reposo", "rigidez muscular", "bradicinesia", "inestabilidad postural", "marcha arrastrada", "micrografía", "hipomimia", "disfagia", "depresión", "deterioro cognitivo"],
        "severity": "moderate",
    },
    {
        "name": "Artritis Reumatoide",
        "description": "Enfermedad autoinmune inflamatoria crónica de articulaciones",
        "symptoms": ["dolor articular simétrico", "rigidez matutina (>30 min)", "inflamación articular", "fatiga", "fiebre", "pérdida de peso", "nódulos reumatoides", "deformidad articular", "dolor a la palpación"],
        "severity": "high",
    },
    {
        "name": "Lupus Eritematoso Sistémico",
        "description": "Enfermedad autoinmune multisistémica",
        "symptoms": ["erupción en mariposa facial", "fotosensibilidad", "úlceras orales", "artritis", "serositis", "nefritis", "fatiga extrema", "fiebre", "caída de cabello", "fenómeno de Raynaud"],
        "severity": "high",
    },
    {
        "name": "Malaria",
        "description": "Enfermedad parasitaria transmitida por mosquito Anopheles",
        "symptoms": ["fiebre cíclica con escalofríos", "sudoración profusa", "dolor de cabeza intenso", "dolor muscular", "fatiga extrema", "náuseas", "vómito", "ictericia", "hepatomegalia", "esplenomegalia"],
        "severity": "high",
    },
    {
        "name": "Fiebre Tifoidea",
        "description": "Infección bacteriana sistémica por Salmonella typhi",
        "symptoms": ["fiebre elevada escalonada", "dolor abdominal", "cefalea frontal", "bradicardia relativa", "manchas rosadas en tronco", "estreñimiento o diarrea", "hepatoesplenomegalia", "letargo"],
        "severity": "high",
    },
    {
        "name": "Varicela",
        "description": "Infección viral aguda por virus varicela-zóster",
        "symptoms": ["exantema vesicular pruriginoso", "fiebre", "fatiga", "dolor de cabeza", "pérdida de apetito", "vesículas en diferentes estadios", "lesiones en cuero cabelludo"],
        "severity": "moderate",
    },
    {
        "name": "Herpes Zóster",
        "description": "Reactivación del virus varicela-zóster en nervios",
        "symptoms": ["erupción vesicular dermatomal", "dolor urente o punzante", "parestesia", "fiebre", "cefalea", "malestar general", "hipersensibilidad de la piel", "prurito"],
        "severity": "moderate",
    },
    {
        "name": "VIH (Infección Aguda)",
        "description": "Infección inicial por virus de inmunodeficiencia humana",
        "symptoms": ["fiebre", "fatiga", "faringitis", "linfadenopatía generalizada", "cefalea", "mialgias", "artralgias", "náuseas", "diarrea", "rash maculopapular", "úlceras orales o genitales"],
        "severity": "moderate",
    },
    {
        "name": "Mononucleosis Infecciosa",
        "description": "Infección viral por Epstein-Barr",
        "symptoms": ["fatiga severa", "fiebre", "linfadenopatía cervical posterior", "faringitis exudativa", "esplenomegalia", "hepatomegalia", "cefalea", "rash máculo-papular", "sudoración nocturna"],
        "severity": "moderate",
    },
    {
        "name": "Leptospirosis",
        "description": "Infección bacteriana transmitida por agua contaminada con orina de animales",
        "symptoms": ["fiebre", "cefalea severa", "mialgias (especialmente gemelares)", "inyección conjuntival", "dolor abdominal", "vómito", "ictericia", "insuficiencia renal", "hemorragias", "congestión pulmonar"],
        "severity": "high",
    },
    {
        "name": "Brucelosis",
        "description": "Infección bacteriana por Brucella transmitida por animales",
        "symptoms": ["fiebre ondulante", "sudoración profusa", "fatiga extrema", "cefalea", "dolor lumbar", "artralgias", "esplenomegalia", "linfadenopatía", "pérdida de peso", "hepatomegalia"],
        "severity": "moderate",
    },
    {
        "name": "Asma Bronquial",
        "description": "Enfermedad inflamatoria crónica de la vía aérea",
        "symptoms": ["sibilancias", "disnea", "tos seca", "opresión torácica", "empeoramiento nocturno o matutino", "respiración corta", "uso de musculatura accesoria", "taquipnea"],
        "severity": "moderate",
    },
    {
        "name": "EPOC",
        "description": "Enfermedad pulmonar obstructiva crónica",
        "symptoms": ["disnea progresiva", "tos crónica", "expectoración", "sibilancias", "fatiga", "pérdida de peso", "infecciones respiratorias recurrentes", "cianosis"],
        "severity": "high",
    },
    {
        "name": "Laringitis Aguda",
        "description": "Inflamación aguda de la laringe",
        "symptoms": ["disfonía o afonía", "dolor de garganta", "tos seca", "sensación de cuerpo extraño en garganta", "fiebre leve", "odinofagia", "edema de cuerdas vocales"],
        "severity": "mild",
    },
    {
        "name": "Apendicitis Aguda",
        "description": "Inflamación aguda del apéndice cecal",
        "symptoms": ["dolor abdominal periumbilical que migra a fosa ilíaca derecha", "náuseas", "vómito", "pérdida de apetito", "fiebre", "defensa abdominal", "signo de Blumberg", "signo de Rovsing"],
        "severity": "high",
    },
    {
        "name": "Colecistitis",
        "description": "Inflamación aguda de la vesícula biliar",
        "symptoms": ["dolor en hipocondrio derecho", "fiebre", "náuseas", "vómito", "signo de Murphy", "dolor irradiado a hombro derecho", "ictericia leve", "distensión abdominal"],
        "severity": "high",
    },
    {
        "name": "úlcera Péptica",
        "description": "Lesión erosiva en mucosa gástrica o duodenal",
        "symptoms": ["dolor abdominal epigástrico quemante", "dolor alivia con alimentos", "dolor nocturno", "náuseas", "pérdida de peso", "hematemesis", "melena", "saciedad temprana", "distensión abdominal"],
        "severity": "moderate",
    },
    {
        "name": "Reflujo Gastroesofágico (ERGE)",
        "description": "Retorno anormal del contenido gástrico al esófago",
        "symptoms": ["acidez retroesternal", "regurgitación ácida", "dolor en el pecho", "disfagia", "tos crónica", "ronquera matutina", "sensación de globo faríngeo", "erosión dental"],
        "severity": "mild",
    },
    {
        "name": "Cólico Nefrítico",
        "description": "Dolor por obstrucción aguda del tracto urinario por cálculo",
        "symptoms": ["dolor lumbar intenso unilateral", "dolor irradiado a genitales", "inquietud extrema", "náuseas", "vómito", "hematuria", "disuria"],
        "severity": "moderate",
    },
    {
        "name": "Insuficiencia Renal Aguda",
        "description": "Pérdida súbita de la función renal",
        "symptoms": ["disminución de la diuresis", "edema generalizado", "fatiga", "confusión", "náuseas", "vómito", "disnea", "hipertensión arterial", "hiperkalemia", "asterixis", "convulsiones"],
        "severity": "critical",
    },
    {
        "name": "Celulitis",
        "description": "Infección bacteriana de la piel y tejido subcutáneo",
        "symptoms": ["eritema localizado", "calor local", "dolor", "edema", "fiebre", "escalofríos", "ampollas", "linfangitis", "linfadenopatía regional", "malestar general"],
        "severity": "moderate",
    },
    {
        "name": "Urticaria",
        "description": "Reacción cutánea con ronchas pruriginosas transitorias",
        "symptoms": ["habones eritematosos", "prurito intenso", "edema angioneurótico", "lesiones evanescentes (<24h)", "dermografismo", "palidez del centro de las lesiones", "sensación de ardor"],
        "severity": "mild",
    },
    {
        "name": "Dermatitis Atópica",
        "description": "Enfermedad inflamatoria crónica de la piel de origen inmune",
        "symptoms": ["prurito intenso", "piel seca", "eritema", "liquenificación", "exudación y costras", "lesiones flexurales", "xerosis", "alteración del sueño por prurito"],
        "severity": "moderate",
    },
    {
        "name": "Cistitis Intersticial",
        "description": "Inflamación crónica de la vejiga sin causa infecciosa",
        "symptoms": ["dolor suprapúbico", "frecuencia urinaria", "urgencia urinaria", "dolor al llenar la vejiga", "alivio con vaciamiento", "dispareunia", "fatiga"],
        "severity": "moderate",
    },
    {
        "name": "Fibromialgia",
        "description": "Trastorno de dolor crónico generalizado",
        "symptoms": ["dolor musculoesquelético generalizado", "fatiga severa", "trastornos del sueño", "rigidez matutina", "cefalea", "síndrome de colon irritable", "dificultades cognitivas", "parestesias", "depresión", "ansiedad"],
        "severity": "moderate",
    },
    {
        "name": "Contusión y Trauma Físico",
        "description": "Lesión de tejidos blandos por un golpe o caída, que produce dolor, inflamación y hematoma (moretón) en la zona afectada",
        "symptoms": ["hematoma", "contusión", "hinchazón", "dolor muscular", "dolor articular"],
        "severity": "mild",
    },
]


treatments = [
    {
        "disease_name": "Influenza (Gripe)",
        "medicines": [
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/día",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepática grave"
          ],
          "allergies": [
            "Paracetamol"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Evitar en hepatopatía grave. Máx 2g/día si enfermedad hepática.",
          "pediatric": "Niños: 10-15 mg/kg/dosis cada 6-8 horas. Máx 60 mg/kg/día. No más de 5 dosis en 24h.",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoría B. Seguro en dosis terapéuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad. Anticoagulantes: potenciación del efecto.",
                "monitoring": "Función hepática en uso prolongado.",
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Oseltamivir",
                "patient_summary": "Antiviral para la gripe. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "150 mg/día",
                "frequency": "75 mg cada 12 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a oseltamivir"
          ],
          "allergies": [
            "Oseltamivir"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Ajustar dosis en ERC avanzada (ClCr <30 mL/min): 75 mg/día",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis por peso en niños ≥1 año: <15 kg: 30 mg/12h; 15-23 kg: 45 mg/12h; 23-40 kg: 60 mg/12h; >40 kg: 75 mg/12h",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoría C. Usar solo si beneficio > riesgo."
        },
                "interactions_warning": "No se han reportado interacciones farmacológicas significativas.",
                "monitoring": "Vigilar síntomas respiratorios, fiebre, tolerancia gastrointestinal.",
                "dosage": "75mg"
            },
            # ---
            {
                "name": "Loratadina",
                "patient_summary": "Alivia la alergia y los estornudos. Una sola toma al dia.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10 mg/día",
                "frequency": "10 mg cada 24 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a loratadina"
          ],
          "allergies": [
            "Loratadina",
            "Antihistamínicos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Precaución en insuficiencia hepática grave.",
          "pediatric": "Segura en niños >2 años.",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoría B."
        },
                "interactions_warning": "Ketoconazol, eritromicina: pueden aumentar niveles séricos.",
                "monitoring": "Vigilar somnolencia (poco frecuente).",
                "dosage": "10mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Ibuprofeno",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/día",
                "frequency": "Cada 6-8 horas",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia renal grave",
            "Úlcera péptica activa",
            "Embarazo tercer trimestre"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Contraindicado en IR grave",
          "hepatic": "Contraindicado en hepatopatía grave",
          "pediatric": "Dosis por peso",
          "geriatric": "Usar dosis mínima efectiva",
          "pregnancy": "Evitar en tercer trimestre"
        },
                "interactions_warning": "Anticoagulantes: mayor riesgo de sangrado.",
                "monitoring": "Función renal, síntomas GI."
            },
        ],
        "non_pharmacological_treatments": [
            "Reposo relativo durante la fase aguda (3-5 días)",
            "Hidratación abundante (agua, caldos, sopas, jugos naturales)",
            "Lavado de manos frecuente para evitar propagación del virus"
        ],
        "general_recommendations": "Acudir a urgencias si presenta: dificultad para respirar, fiebre >39°C que no cede, confusión o desorientación."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Resfriado Común",
        "medicines": [
            {
                "name": "Paracetamol",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "4000 mg/día (adultos)",
                "frequency": "Cada 6-8 horas según necesidad",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepática grave",
            "Alcoholismo crónico"
          ],
          "allergies": [
            "Paracetamol"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Precaución en IR grave; evitar uso prolongado",
          "hepatic": "Contraindicado en hepatopatía grave. Precaución: máx 2000 mg/día",
          "pediatric": "Dosis por peso (10-15 mg/kg/dosis)",
          "geriatric": "Usar dosis mínima efectiva",
          "pregnancy": "Categoría B, seguro en dosis terapéuticas"
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad. Anticoagulantes: puede potenciar efecto (uso crónico).",
                "monitoring": "Función hepática, síntomas de fiebre y dolor.",
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Pseudoefedrina",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "240 mg/día",
                "frequency": "30-60 mg cada 12 horas",
                "duration": "3-5 días (máximo 7 días)",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipertensión arterial severa",
            "Enfermedad coronaria",
            "Hipertiroidismo",
            "Glaucoma de ángulo cerrado",
            "Hiperplasia prostática benigna con retención urinaria"
          ],
          "allergies": [
            "Pseudoefedrina",
            "Descongestionantes simpaticomiméticos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Precaución en IR, puede acumularse",
          "hepatic": "No requiere ajuste",
          "pediatric": "No recomendado en <6 años. 6-12 años: 15-30 mg/12h. >12 años: 30-60 mg/12h",
          "geriatric": "Mayor riesgo de efectos secundarios (retención urinaria, elevación de PA, insomnio)",
          "pregnancy": "Categoría C. Evitar en primer trimestre. Riesgo potencial de gastrosquisis."
        },
                "interactions_warning": "IMAO: crisis hipertensiva (contraindicado). Betabloqueadores: hipertensión. Antidepresivos tricíclicos: potenciación de efectos simpaticomiméticos.",
                "monitoring": "Presión arterial, frecuencia cardíaca, retención urinaria en adultos mayores.",
                "dosage": "30mg"
            },
            # ---
            {
                "name": "Vitamina C (Ácido ascórbico)",
                "patient_summary": "Ayuda a las defensas del cuerpo. Tomala durante resfriados.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2000 mg/día",
                "frequency": "500-1000 mg/día",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia renal grave",
            "Litiasis renal",
            "Hemocromatosis",
            "Deficiencia de G6PD"
          ],
          "allergies": [
            "Ácido ascórbico"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar en IR avanzada (riesgo de hiperoxaluria)",
          "hepatic": "No requiere ajuste",
          "pediatric": "Niños: 50-100 mg/día. No exceder 400 mg/día en <3 años",
          "geriatric": "Dosis habitual, sin ajuste",
          "pregnancy": "Categoría A – seguro en dosis fisiológicas. No exceder 1800 mg/día."
        },
                "interactions_warning": "Aumenta absorción de hierro (precaución en hemocromatosis). Dosis altas pueden interferir con pruebas de glucosa.",
                "monitoring": "Tolerancia digestiva. En pacientes con litiasis renal: vigilancia de oxalato urinario.",
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Ibuprofeno",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/día (sin receta); 2400 mg/día (con indicación médica)",
                "frequency": "Cada 6-8 horas",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia renal grave",
            "Úlcera péptica activa",
            "Embarazo tercer trimestre",
            "Sangrado gastrointestinal activo",
            "Enfermedad cardiovascular severa"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Contraindicado en IR grave. Precaución en IR leve-moderada",
          "hepatic": "Contraindicado en hepatopatía grave",
          "pediatric": "Dosis por peso",
          "geriatric": "Usar dosis mínima. Mayor riesgo de sangrado GI y nefrotoxicidad",
          "pregnancy": "Evitar en 3er trimestre. Precaución en 1er y 2do."
        },
                "interactions_warning": "Anticoagulantes: mayor riesgo de sangrado. IECA/ARAII: reducción efecto antihipertensivo. Litio, metotrexato: aumento de toxicidad.",
                "monitoring": "Función renal, síntomas GI, presión arterial."
            },
            # ---
            {
                "name": "Dextrometorfano",
                "patient_summary": "Para la tos seca. No lo tomes con antidepresivos sin consultar.",
                "dosage_mg_kg": None,
                "max_daily_dose": "120 mg/día",
                "frequency": "10-20 mg cada 4-6 horas",
                "duration": "3-5 días (máx 7 días)",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Uso de IMAO (actual o en 14 días)",
            "Asma severa no controlada",
            "Neumonía",
            "EPOC exacerbado",
            "Tos productiva abundante"
          ],
          "allergies": [
            "Dextrometorfano"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Precaución en IR: puede haber acumulación de metabolitos",
          "hepatic": "Insuficiencia hepática grave: reducir dosis o evitar",
          "pediatric": "2-5 años: 2.5-5 mg/4h; 6-11 años: 5-10 mg/4h; ≥12 años: 10-20 mg/4h",
          "geriatric": "Mayor sensibilidad a efectos sedantes. Usar dosis mínima efectiva",
          "pregnancy": "Categoría C. Evitar en primer trimestre."
        },
                "interactions_warning": "IMAO: riesgo de síndrome serotoninérgico (contraindicado). ISRS: riesgo de síndrome serotoninérgico. Alcohol: potenciación de sedación.",
                "monitoring": "Estado neurológico (sedación, mareo), síntomas respiratorios."
            },
        ],
        "non_pharmacological_treatments": [
            "Reposo moderado y descanso adecuado",
            "Hidratación oral abundante (agua, infusiones calientes, caldos)",
            "Miel en infusión o directamente para aliviar la irritación de garganta",
            "Gárgaras con agua salada tibia (1/2 cucharadita de sal en un vaso de agua) 2-3 veces al día",
            "Vapor de agua o duchas calientes para descongestión nasal",
            "Elevación de cabeza al dormir para facilitar respiración nocturna",
            "Evitar cambios bruscos de temperatura y ambientes con humo o polvo",
            "Lavado de manos frecuente"
        ],
        "general_recommendations": "El resfriado común es una infección viral autolimitada (3-7 días). No requiere antibióticos. Acudir a urgencias si: fiebre >39°C por más de 3 días, dificultad respiratoria, dolor de oído intenso, secreción purulenta, empeoramiento súbito."
    },
    # ──────────────────────────────────
    {
        "disease_name": "COVID-19",
        "medicines": [
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 6-8 horas",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Paxlovid (Nirmatrelvir/Ritonavir)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg/100mg",
                "frequency": "Cada 12 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["enfermedad renal grave (filtrado glomerular estimado <30 ml/min)", "enfermedad hepatica grave"],
                                         "allergies": ["hipersensibilidad a nirmatrelvir o ritonavir"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Requiere ajuste de dosis en insuficiencia renal moderada (filtrado 30-59 ml/min)",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "No administrar con rifampicina, carbamazepina, fenitoina ni hierba de San Juan; revise con su medico otros medicamentos (algunas estatinas, benzodiazepinas).",
                "monitoring": None,
                "dosage": "300mg/100mg"
            },
            # ---
            {
                "name": "Dexametasona 6mg",
                "patient_summary": "Corticosteroide potente para inflamacion severa. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "6mg",
                "frequency": "Cada 24 horas",
                "duration": "10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["infeccion sistemica no controlada", "infeccion fungica sistemica no controlada"],
                                         "allergies": ["hipersensibilidad a corticosteroides"],
                                         "comorbidities": ["diabetes mellitus descontrolada (vigilar glucemia)", "hipertension arterial severa"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "No suspender bruscamente tras uso prolongado; vigilar glucemia en diabeticos.",
                "monitoring": None,
                "dosage": "6mg"
            },
            # ---
            {
                "name": "Enoxaparina 40mg",
                "patient_summary": "Anticoagulante inyectable para prevenir trombosis. Sigue las instrucciones de aplicacion.",
                "dosage_mg_kg": None,
                "max_daily_dose": "40mg",
                "frequency": "Cada 24 horas SQ",
                "duration": "Durante hospitalización",
                "route": "Subcutánea",
                "contraindications": {
                                         "conditions": ["hemorragia activa significativa", "trombocitopenia inducida por heparina (actual o previa)", "hemorragia intracraneal reciente o neurocirugia", "endocarditis bacteriana aguda"],
                                         "allergies": ["hipersensibilidad a enoxaparina o heparina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Reducir dosis en insuficiencia renal grave",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "En mayores de 75 anos ajustar dosis en profilaxis",
                                   "pregnancy": "Usar con precaucion; evaluar riesgo-beneficio",
                               },
                "interactions_warning": "Riesgo de sangrado aumentado con otros anticoagulantes, antiagregantes y AINE.",
                "monitoring": "Vigilar signos de sangrado y el recuento de plaquetas.",
                "dosage": "40mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "dosage": "400mg",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Ulcera peptica activa",
            "Insuficiencia renal grave"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar si ClCr <30 mL/min",
          "hepatic": "Usar con precaucion",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "Usar dosis minima por riesgo gastrointestinal",
          "pregnancy": "Categoria C. Evitar en 3er trimestre."
        },
                "interactions_warning": "AINEs + anticoagulantes: riesgo de sangrado. AINEs + IECA: reducen efecto antihipertensivo.",
                "monitoring": "Funcion renal, signos de sangrado gastrointestinal.",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Evitar exposicion al humo de tabaco y contaminantes ambientales",
            "Mantener hidratacion adecuada (2 litros de agua al dia)",
            "Reposo relativo durante la fase aguda",
            "Elevar la cabecera de la cama para facilitar la respiracion",
            "Evitar cambios bruscos de temperatura",
            "Realizar lavados nasales con solucion salina si hay congestion"
        ],
        "general_recommendations": "Aislamiento obligatorio. Monitoreo de saturación de oxígeno. Acudir a urgencias si saturación <90% o dificultad respiratoria severa."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Gastroenteritis Aguda",
        "medicines": [
            {
                "name": "Solución de rehidratación oral",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1L",
                "frequency": "A demanda, pequeños sorbos",
                "duration": "Durante cuadro",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ileo u obstruccion intestinal", "vomitos incoercibles con riesgo de aspiracion", "estado de shock"],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1L"
            },
            # ---
            {
                "name": "Lactobacillus (probiótico)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1 sobre",
                "frequency": "Cada 12 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["inmunodeficiencia grave", "pancreatitis aguda grave"],
                                         "allergies": ["hipersensibilidad a componentes del probiotico"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1 sobre"
            },
            # ---
            {
                "name": "Loperamida 2mg",
                "patient_summary": "Detiene la diarrea. Tomala despues de cada deposicion liquida. No mas de 2 dias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2mg",
                "frequency": "Después de cada evacuación (máx 8mg/día)",
                "duration": "Máx 2 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["obstruccion o ileo intestinal", "colitis ulcerosa activa en brote", "disenteria bacteriana con fiebre y heces con sangre", "colitis pseudomembranosa por antibioticos", "menores de 2 anos"],
                                         "allergies": ["hipersensibilidad a loperamida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Esomeprazol 20mg",
                "dosage": "20mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "40 mg/dia",
                "frequency": "20 mg cada 24 horas",
                "duration": "4-8 semanas",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a IBP"
          ],
          "allergies": [
            "Esomeprazol",
            "Omeprazol"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 20mg/dia en insuficiencia hepatica grave",
          "pediatric": "Seguro en >12 anos",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Reduce absorcion de clopidogrel, metotrexato y hierro.",
                "monitoring": "Sintomas gastricos, niveles de magnesio en uso prolongado.",
                "patient_summary": "Protege el estomago reduciendo el acido. Tomala antes del desayuno."
            },
            # ---
            {
                "name": "Hioscina 10mg",
                "dosage": "10mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "60 mg/dia",
                "frequency": "10 mg cada 8 horas si hay dolor",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Glaucoma",
            "Miastenia gravis"
          ],
          "allergies": [
            "Hioscina"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "No requiere ajuste",
          "pediatric": "Seguro en >6 anos",
          "geriatric": "Puede causar retencion urinaria",
          "pregnancy": "Categoria C."
        },
                "interactions_warning": "Potencia efectos anticolinergicos de otros farmacos.",
                "monitoring": "Dolor abdominal, distension.",
                "patient_summary": "Alivia los colicos y el dolor de estomago. Tomala antes de las comidas."
            },
        ],
        "non_pharmacological_treatments": [
            "Dieta blanda y fraccionada (5-6 comidas pequenas al dia)",
            "Evitar alimentos irritantes: picantes, fritos, grasosos, cafe, alcohol",
            "No acostarse inmediatamente despues de comer (esperar 2-3 horas)",
            "Manterse hidratado, preferiblemente con agua o te suave",
            "Identificar y evitar alimentos que desencadenan los sintomas"
        ],
        "general_recommendations": "Dieta blanda (arroz, manzana, zanahoria reposo GI). Suspender lácteos temporalmente. Signos de alarma: fiebre >39°C o heces con sangre."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Neumonía",
        "medicines": [
            {
                "name": "Amoxicilina 500mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["mononucleosis infecciosa (riesgo de exantema)"],
                                         "allergies": ["alergia a penicilinas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Salbutamol inhalador",
                "patient_summary": "Inhalador que abre las vias respiratorias. Usalo cuando sientas silbido en el pecho.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 6-8 horas PRN",
                "duration": "Según síntomas",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": ["taquiarritmias no controladas"],
                                         "allergies": ["hipersensibilidad a salbutamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "REQUIERE HOSPITALIZACIÓN si saturación <92%. Fisioterapia respiratoria. Oxígeno suplementario si es necesario."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Otitis Media",
        "medicines": [
            {
                "name": "Amoxicilina 250-500mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "250-500mg",
                "frequency": "Cada 8 horas",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["mononucleosis infecciosa (riesgo de exantema)"],
                                         "allergies": ["alergia a penicilinas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "250-500mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
            # ---
            {
                "name": "Gotas óticas (antimicrobianas)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "3 gotas",
                "frequency": "Cada 8 horas",
                "duration": "7 días",
                "route": "Ótico",
                "contraindications": {
                                         "conditions": ["perforacion timpanica (riesgo de ototoxicidad segun el componente)"],
                                         "allergies": ["hipersensibilidad al principio activo de las gotas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "3 gotas"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Cefalexina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "25-50 mg/kg/dia",
                "max_daily_dose": "4000 mg/dia",
                "frequency": "500 mg cada 6 horas",
                "duration": "7-10 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a cefalosporinas"
          ],
          "allergies": [
            "Cefalexina",
            "Cefalosporinas"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Ajustar si ClCr <50 mL/min",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis por peso cada 6 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Anticoagulantes: potenciacion del efecto.",
                "monitoring": "Funcion renal, signos de alergia, diarrea asociada a antibioticos.",
                "patient_summary": "Antibiotico para infecciones de piel, garganta y orina. Tomalo completo."
            },
            # ---
            {
                "name": "Azitromicina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10 mg/kg/dia",
                "max_daily_dose": "500 mg/dia",
                "frequency": "500 mg cada 24 horas por 3 dias",
                "duration": "3 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave",
            "Prolongacion QT"
          ],
          "allergies": [
            "Azitromicina",
            "Macrolidos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Evitar en hepatopatia grave",
          "pediatric": "Dosis por peso cada 24 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Antiacidos: reducir absorcion. Anticoagulantes: potenciacion.",
                "monitoring": "Funcion hepatica, ritmo cardiaco, tolerancia gastrointestinal.",
                "patient_summary": "Antibiotico de 3 dias para infecciones respiratorias. Tomalo completo."
            },
        ],
        "non_pharmacological_treatments": [
            "Completar el ciclo completo de antibioticos aunque haya mejoria",
            "Lavado frecuente de manos con agua y jabon",
            "Reposo durante la fase aguda de la infeccion",
            "Hidratacion abundante (2-3 litros de agua al dia)",
            "Evitar el contacto cercano con otras personas durante el periodo de contagio",
            "No automedicarse con antibioticos sin formula medica"
        ],
        "general_recommendations": "Evitar entrada de agua en el oído. No introducir objetos. Evaluar por ORL si recurrente."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Infección Urinaria",
        "medicines": [
            {
                "name": "Fosfomicina trometamol 3g",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "3g",
                "frequency": "Dosis única",
                "duration": "1 dosis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a fosfomicina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "3g"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "3 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Aumentar ingesta de agua (>2L/día). Urocultivo si es recurrente. Evaluar por urología si más de 3 infecciones al año."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Dengue",
        "medicines": [
            {
                "name": "Acetaminofén 500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 6 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Solución de rehidratación oral",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1-2L",
                "frequency": "A demanda",
                "duration": "Durante cuadro",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ileo u obstruccion intestinal", "vomitos incoercibles con riesgo de aspiracion", "estado de shock"],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1-2L"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Cefalexina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "25-50 mg/kg/dia",
                "max_daily_dose": "4000 mg/dia",
                "frequency": "500 mg cada 6 horas",
                "duration": "7-10 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a cefalosporinas"
          ],
          "allergies": [
            "Cefalexina",
            "Cefalosporinas"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Ajustar si ClCr <50 mL/min",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis por peso cada 6 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Anticoagulantes: potenciacion del efecto.",
                "monitoring": "Funcion renal, signos de alergia, diarrea asociada a antibioticos.",
                "patient_summary": "Antibiotico para infecciones de piel, garganta y orina. Tomalo completo."
            },
            # ---
            {
                "name": "Azitromicina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10 mg/kg/dia",
                "max_daily_dose": "500 mg/dia",
                "frequency": "500 mg cada 24 horas por 3 dias",
                "duration": "3 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave",
            "Prolongacion QT"
          ],
          "allergies": [
            "Azitromicina",
            "Macrolidos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Evitar en hepatopatia grave",
          "pediatric": "Dosis por peso cada 24 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Antiacidos: reducir absorcion. Anticoagulantes: potenciacion.",
                "monitoring": "Funcion hepatica, ritmo cardiaco, tolerancia gastrointestinal.",
                "patient_summary": "Antibiotico de 3 dias para infecciones respiratorias. Tomalo completo."
            },
        ],
        "non_pharmacological_treatments": [
            "Completar el ciclo completo de antibioticos aunque haya mejoria",
            "Lavado frecuente de manos con agua y jabon",
            "Reposo durante la fase aguda de la infeccion",
            "Hidratacion abundante (2-3 litros de agua al dia)",
            "Evitar el contacto cercano con otras personas durante el periodo de contagio",
            "No automedicarse con antibioticos sin formula medica"
        ],
        "general_recommendations": "NO USAR AINES (ibuprofeno, aspirina) por riesgo de sangrado. Reposo absoluto. Monitorear signos de alarma: dolor abdominal intenso, vómitos persistentes, sangrado de encías. Acudir a urgencias de inmediato si presenta signos de alarma."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Meningitis",
        "medicines": [
            {
                "name": "Ceftriaxona 2g IV",
                "patient_summary": "Antibiotico inyectable para infecciones graves. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2g",
                "frequency": "Cada 12 horas IV",
                "duration": "14 días",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hiperbilirrubinemia neonatal"],
                                         "allergies": ["hipersensibilidad a cefalosporinas", "alergia grave a penicilinas (reaccion anafilactica)"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2g"
            },
            # ---
            {
                "name": "Dexametasona 0.15mg/kg IV",
                "patient_summary": "Corticosteroide potente para inflamacion severa. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "0.15mg/kg",
                "frequency": "Cada 6 horas IV",
                "duration": "4 días",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["infeccion sistemica no controlada", "infeccion fungica sistemica no controlada"],
                                         "allergies": ["hipersensibilidad a corticosteroides"],
                                         "comorbidities": ["diabetes mellitus descontrolada (vigilar glucemia)", "hipertension arterial severa"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No suspender bruscamente tras uso prolongado; vigilar glucemia en diabeticos.",
                "monitoring": None,
                "dosage": "0.15mg/kg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 6 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Cefalexina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "25-50 mg/kg/dia",
                "max_daily_dose": "4000 mg/dia",
                "frequency": "500 mg cada 6 horas",
                "duration": "7-10 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a cefalosporinas"
          ],
          "allergies": [
            "Cefalexina",
            "Cefalosporinas"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Ajustar si ClCr <50 mL/min",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis por peso cada 6 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Anticoagulantes: potenciacion del efecto.",
                "monitoring": "Funcion renal, signos de alergia, diarrea asociada a antibioticos.",
                "patient_summary": "Antibiotico para infecciones de piel, garganta y orina. Tomalo completo."
            },
            # ---
            {
                "name": "Azitromicina 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10 mg/kg/dia",
                "max_daily_dose": "500 mg/dia",
                "frequency": "500 mg cada 24 horas por 3 dias",
                "duration": "3 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave",
            "Prolongacion QT"
          ],
          "allergies": [
            "Azitromicina",
            "Macrolidos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Evitar en hepatopatia grave",
          "pediatric": "Dosis por peso cada 24 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Antiacidos: reducir absorcion. Anticoagulantes: potenciacion.",
                "monitoring": "Funcion hepatica, ritmo cardiaco, tolerancia gastrointestinal.",
                "patient_summary": "Antibiotico de 3 dias para infecciones respiratorias. Tomalo completo."
            },
        ],
        "non_pharmacological_treatments": [
            "Completar el ciclo completo de antibioticos aunque haya mejoria",
            "Lavado frecuente de manos con agua y jabon",
            "Reposo durante la fase aguda de la infeccion",
            "Hidratacion abundante (2-3 litros de agua al dia)",
            "Evitar el contacto cercano con otras personas durante el periodo de contagio",
            "No automedicarse con antibioticos sin formula medica"
        ],
        "general_recommendations": "EMERGENCIA MÉDICA - Hospitalización inmediata. Punción lumbar para diagnóstico. Aislamiento respiratorio. Monitoreo neurológico estricto."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Hepatitis A",
        "medicines": [
        ],
        "alternative_medicines": [
            {
                "name": "Esomeprazol 20mg",
                "dosage": "20mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "40 mg/dia",
                "frequency": "20 mg cada 24 horas",
                "duration": "4-8 semanas",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a IBP"
          ],
          "allergies": [
            "Esomeprazol",
            "Omeprazol"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 20mg/dia en insuficiencia hepatica grave",
          "pediatric": "Seguro en >12 anos",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Reduce absorcion de clopidogrel, metotrexato y hierro.",
                "monitoring": "Sintomas gastricos, niveles de magnesio en uso prolongado.",
                "patient_summary": "Protege el estomago reduciendo el acido. Tomala antes del desayuno."
            },
            # ---
            {
                "name": "Hioscina 10mg",
                "dosage": "10mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "60 mg/dia",
                "frequency": "10 mg cada 8 horas si hay dolor",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Glaucoma",
            "Miastenia gravis"
          ],
          "allergies": [
            "Hioscina"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "No requiere ajuste",
          "pediatric": "Seguro en >6 anos",
          "geriatric": "Puede causar retencion urinaria",
          "pregnancy": "Categoria C."
        },
                "interactions_warning": "Potencia efectos anticolinergicos de otros farmacos.",
                "monitoring": "Dolor abdominal, distension.",
                "patient_summary": "Alivia los colicos y el dolor de estomago. Tomala antes de las comidas."
            },
        ],
        "non_pharmacological_treatments": [
            "Dieta blanda y fraccionada (5-6 comidas pequenas al dia)",
            "Evitar alimentos irritantes: picantes, fritos, grasosos, cafe, alcohol",
            "No acostarse inmediatamente despues de comer (esperar 2-3 horas)",
            "Manterse hidratado, preferiblemente con agua o te suave",
            "Identificar y evitar alimentos que desencadenan los sintomas"
        ],
        "general_recommendations": "Reposo absoluto. Dieta baja en grasas. Evitar alcohol por 6 meses. Hidratación. La mayoría se resuelve sola en 2-4 semanas. No hay tratamiento antiviral específico. Vacunación para contactos."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Bronquitis Aguda",
        "medicines": [
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Salbutamol inhalador",
                "patient_summary": "Inhalador que abre las vias respiratorias. Usalo cuando sientas silbido en el pecho.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 6-8 horas PRN",
                "duration": "Según síntomas",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": ["taquiarritmias no controladas"],
                                         "allergies": ["hipersensibilidad a salbutamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
            # ---
            {
                "name": "Acetilcisteína 600mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "600mg",
                "frequency": "Cada 24 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["broncoespasmo grave (precaucion en asmaticos)"],
                                         "allergies": ["hipersensibilidad a acetilcisteina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "600mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "dosage": "400mg",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Ulcera peptica activa",
            "Insuficiencia renal grave"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar si ClCr <30 mL/min",
          "hepatic": "Usar con precaucion",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "Usar dosis minima por riesgo gastrointestinal",
          "pregnancy": "Categoria C. Evitar en 3er trimestre."
        },
                "interactions_warning": "AINEs + anticoagulantes: riesgo de sangrado. AINEs + IECA: reducen efecto antihipertensivo.",
                "monitoring": "Funcion renal, signos de sangrado gastrointestinal.",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Evitar exposicion al humo de tabaco y contaminantes ambientales",
            "Mantener hidratacion adecuada (2 litros de agua al dia)",
            "Reposo relativo durante la fase aguda",
            "Elevar la cabecera de la cama para facilitar la respiracion",
            "Evitar cambios bruscos de temperatura",
            "Realizar lavados nasales con solucion salina si hay congestion"
        ],
        "general_recommendations": "No requiere antibióticos a menos que se sospeche infección bacteriana. Nebulizaciones con solución salina. Evitar irritantes como humo de tabaco."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Amigdalitis",
        "medicines": [
            {
                "name": "Amoxicilina 500mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["mononucleosis infecciosa (riesgo de exantema)"],
                                         "allergies": ["alergia a penicilinas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
            # ---
            {
                "name": "Gárgaras con solución salina",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "Vaso de agua tibia + sal",
                "frequency": "Cada 6 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "Vaso de agua tibia + sal"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "dosage": "400mg",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Ulcera peptica activa",
            "Insuficiencia renal grave"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar si ClCr <30 mL/min",
          "hepatic": "Usar con precaucion",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "Usar dosis minima por riesgo gastrointestinal",
          "pregnancy": "Categoria C. Evitar en 3er trimestre."
        },
                "interactions_warning": "AINEs + anticoagulantes: riesgo de sangrado. AINEs + IECA: reducen efecto antihipertensivo.",
                "monitoring": "Funcion renal, signos de sangrado gastrointestinal.",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Evitar exposicion al humo de tabaco y contaminantes ambientales",
            "Mantener hidratacion adecuada (2 litros de agua al dia)",
            "Reposo relativo durante la fase aguda",
            "Elevar la cabecera de la cama para facilitar la respiracion",
            "Evitar cambios bruscos de temperatura",
            "Realizar lavados nasales con solucion salina si hay congestion"
        ],
        "general_recommendations": "Reposo vocal. Hidratación con líquidos fríos o tibios. Evaluar si hay absceso periamigdalino. Considerar amigdalectomía si es recurrente (>5 episodios/año)."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Rinitis Alérgica",
        "medicines": [
            {
                "name": "Loratadina 10mg",
                "patient_summary": "Alivia la alergia y los estornudos. Una sola toma al dia.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 24 horas",
                "duration": "Según temporada",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a loratadina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10mg"
            },
            # ---
            {
                "name": "Budesonida nasal",
                "patient_summary": "Inhalador que baja la inflamacion de los pulmones. Usalo a diario. No es de rescate.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 atomizaciones",
                "frequency": "Cada 12 horas",
                "duration": "Durante exposición",
                "route": "Nasal",
                "contraindications": {
                                         "conditions": ["infeccion nasal no tratada"],
                                         "allergies": ["hipersensibilidad a budesonida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 atomizaciones"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Identificar y evitar alérgenos. Lavados nasales con solución salina. Considerar inmunoterapia si es severa."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Intoxicación Alimentaria",
        "medicines": [
            {
                "name": "Solución de rehidratación oral",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1L",
                "frequency": "A demanda",
                "duration": "Durante cuadro",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ileo u obstruccion intestinal", "vomitos incoercibles con riesgo de aspiracion", "estado de shock"],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1L"
            },
            # ---
            {
                "name": "Lactobacillus (probiótico)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1 sobre",
                "frequency": "Cada 12 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["inmunodeficiencia grave", "pancreatitis aguda grave"],
                                         "allergies": ["hipersensibilidad a componentes del probiotico"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1 sobre"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Hidratación abundante. Dieta blanda. Carbón activado solo si fue hace <1 hora. Signos de alarma: fiebre >38.5°C, heces con sangre, signos de deshidratación severa."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Tuberculosis",
        "medicines": [
            {
                "name": "Rifampicina 600mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "600mg",
                "frequency": "Cada 24 horas",
                "duration": "6 meses",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ictericia previa con rifampicina", "porfiria"],
                                         "allergies": ["hipersensibilidad a rifampicina"],
                                         "comorbidities": ["hepatopatia grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Potente inductor enzimatico: puede reducir la eficacia de anticonceptivos, warfarina y otros medicamentos.",
                "monitoring": "Vigilar funcion hepatica.",
                "dosage": "600mg"
            },
            # ---
            {
                "name": "Isoniacida 300mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Cada 24 horas",
                "duration": "6 meses",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hepatopatia aguda", "neuropatia periferica previa por isoniacida"],
                                         "allergies": ["hipersensibilidad a isoniacida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "El alcohol aumenta la hepatotoxicidad.",
                "monitoring": "Vigilar funcion hepatica.",
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Pirazinamida 1500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1500mg",
                "frequency": "Cada 24 horas",
                "duration": "2 meses",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hepatopatia grave"],
                                         "allergies": ["hipersensibilidad a pirazinamida"],
                                         "comorbidities": ["gota (hiperuricemia)"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": "Vigilar acido urico y funcion hepatica.",
                "dosage": "1500mg"
            },
            # ---
            {
                "name": "Etambutol 800mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "800mg",
                "frequency": "Cada 24 horas",
                "duration": "2 meses",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["neuritis optica"],
                                         "allergies": ["hipersensibilidad a etambutol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": "Vigilar agudeza visual y campos visuales.",
                "dosage": "800mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "dosage": "400mg",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Ulcera peptica activa",
            "Insuficiencia renal grave"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar si ClCr <30 mL/min",
          "hepatic": "Usar con precaucion",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "Usar dosis minima por riesgo gastrointestinal",
          "pregnancy": "Categoria C. Evitar en 3er trimestre."
        },
                "interactions_warning": "AINEs + anticoagulantes: riesgo de sangrado. AINEs + IECA: reducen efecto antihipertensivo.",
                "monitoring": "Funcion renal, signos de sangrado gastrointestinal.",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Evitar exposicion al humo de tabaco y contaminantes ambientales",
            "Mantener hidratacion adecuada (2 litros de agua al dia)",
            "Reposo relativo durante la fase aguda",
            "Elevar la cabecera de la cama para facilitar la respiracion",
            "Evitar cambios bruscos de temperatura",
            "Realizar lavados nasales con solucion salina si hay congestion"
        ],
        "general_recommendations": "TRATAMIENTO SUPERVISADO (DOTS). Notificación obligatoria a salud pública. Aislamiento respiratorio las primeras 2 semanas de tratamiento. Monitoreo de función hepática por hepatotoxicidad de los fármacos."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Shigelosis (Disentería)",
        "medicines": [
            {
                "name": "Ciprofloxacina 500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 12 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["tendinopatia o ruptura tendinosa previa por quinolonas", "miastenia gravis", "embarazo y lactancia (evitar)", "menores de 18 anos (evitar como primera linea)"],
                                         "allergies": ["hipersensibilidad a fluoroquinolonas"],
                                         "comorbidities": ["prolongacion del intervalo QT", "epilepsia"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar antiacidos, hierro, calcio y zinc cerca de la toma; el uso de corticosteroides aumenta el riesgo de tendinopatia.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Solución de rehidratación oral",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1-2L",
                "frequency": "A demanda",
                "duration": "Durante cuadro",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ileo u obstruccion intestinal", "vomitos incoercibles con riesgo de aspiracion", "estado de shock"],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1-2L"
            },
            # ---
            {
                "name": "Lactobacillus (probiótico)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1 sobre",
                "frequency": "Cada 12 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["inmunodeficiencia grave", "pancreatitis aguda grave"],
                                         "allergies": ["hipersensibilidad a componentes del probiotico"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1 sobre"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Aislamiento entérico. Higiene de manos estricta. No usar loperamida (riesgo de megacolon tóxico). Reporte a salud pública obligatorio."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Infarto Agudo de Miocardio",
        "medicines": [
            {
                "name": "Ácido acetilsalicílico 300mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Dosis única masticado",
                "duration": "1 dosis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa", "hemorragia gastrointestinal activa", "hemofilia u otro trastorno de la coagulacion", "tercer trimestre del embarazo"],
                                         "allergies": ["hipersensibilidad a acido acetilsalicilico u otros AINE", "asma sensible a AINE"],
                                         "comorbidities": ["diatesis hemorragica"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Nitroglicerina sublingual 0.5mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "0.5mg",
                "frequency": "Cada 5 minutos (máx 3 dosis)",
                "duration": "Durante dolor",
                "route": "Sublingual",
                "contraindications": {
                                         "conditions": ["uso de sildenafil, tadalafil o vardenafil en las ultimas 24-48 horas", "hipotension grave", "shock", "estenosis aortica critica", "miocardiopatia hipertrofica obstructiva", "taponamiento pericardico"],
                                         "allergies": ["hipersensibilidad a nitratos"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No combinar con sildenafil, tadalafil o vardenafil.",
                "monitoring": None,
                "dosage": "0.5mg"
            },
            # ---
            {
                "name": "Clopidogrel 300mg",
                "patient_summary": "Anticoagulante para prevenir infartos. Tomala a la misma hora todos los dias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Dosis única",
                "duration": "1 dosis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["sangrado activo patologico (ulcera hemorragica, hemorragia intracraneal)"],
                                         "allergies": ["hipersensibilidad a clopidogrel"],
                                         "comorbidities": ["enfermedad hepatica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar omeprazol y esomeprazol; riesgo de sangrado con AINE e ibuprofeno.",
                "monitoring": None,
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Heparina sódica IV",
                "patient_summary": "Anticoagulante inyectable para prevenir coagulos. Solo uso hospitalario.",
                "dosage_mg_kg": None,
                "max_daily_dose": "60 UI/kg",
                "frequency": "Bolo inicial",
                "duration": "Durante hospitalización",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hemorragia activa", "trombocitopenia inducida por heparina (actual o previa)", "hemorragia intracraneal reciente", "cirugia cerebral, ocular o espinal reciente"],
                                         "allergies": ["hipersensibilidad a heparina"],
                                         "comorbidities": ["trombocitopenia grave", "coagulopatia grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sangrado con antiagregantes, anticoagulantes, AINE y tromboliticos.",
                "monitoring": "Controlar aPTT y recuento de plaquetas.",
                "dosage": "60 UI/kg"
            },
            # ---
            {
                "name": "Morfina 2-4mg IV",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2-4mg",
                "frequency": "Cada 5-15 minutos PRN",
                "duration": "Durante dolor severo",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["depresion respiratoria", "ileo paralitico", "obstruccion intestinal", "asma aguda grave", "hipersensibilidad a opioides"],
                                         "allergies": ["hipersensibilidad a morfina u opioides"],
                                         "comorbidities": ["insuficiencia renal o hepatica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "El alcohol y los sedantes aumentan la depresion respiratoria.",
                "monitoring": "Vigilar nivel de conciencia y frecuencia respiratoria.",
                "dosage": "2-4mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "EMERGENCIA MÉDICA - Activar código infarto. Traslado a unidad de hemodinamia. Monitoreo cardíaco continuo. Reposo absoluto. Oxígeno suplementario. Angioplastía primaria idealmente <90 min."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Insuficiencia Cardíaca",
        "medicines": [
            {
                "name": "Furosemida 40mg",
                "patient_summary": "Ayuda a eliminar liquido acumulado en el cuerpo. Tomala en la manana para no orinar de noche.",
                "dosage_mg_kg": None,
                "max_daily_dose": "40mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["anuria", "hipovolemia o deshidratacion grave", "hipopotasemia grave"],
                                         "allergies": ["hipersensibilidad a furosemida o sulfonamidas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "40mg"
            },
            # ---
            {
                "name": "Enalapril 10mg",
                "patient_summary": "Controla la presion arterial. Tomala a la misma hora todos los dias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo (segundo y tercer trimestre)", "angioedema previo por IECA", "hiperpotasemia"],
                                         "allergies": ["hipersensibilidad a IECA"],
                                         "comorbidities": ["estenosis bilateral de la arteria renal"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10mg"
            },
            # ---
            {
                "name": "Carvedilol 6.25mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "6.25mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["asma o broncoespasmo", "bloqueo AV de segundo o tercer grado", "bradicardia sintomatica", "insuficiencia cardiaca descompensada refractaria", "enfermedad hepatica grave"],
                                         "allergies": ["hipersensibilidad a carvedilol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "6.25mg"
            },
            # ---
            {
                "name": "Espironolactona 25mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "25mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hiperpotasemia", "insuficiencia renal grave (filtrado <30 ml/min)", "enfermedad de Addison", "embarazo"],
                                         "allergies": ["hipersensibilidad a espironolactona"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "La asociacion con IECA, ARA-II o suplementos de potasio aumenta el riesgo de hiperpotasemia.",
                "monitoring": None,
                "dosage": "25mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Restricción de sodio (<2g/día). Control diario de peso. Monitoreo de ingesta y diuresis. Evaluar fracción de eyección. Considerar trasplante cardíaco si refractario."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Hipertensión Arterial",
        "medicines": [
            {
                "name": "Losartán 50mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo (segundo y tercer trimestre)", "hiperpotasemia"],
                                         "allergies": ["hipersensibilidad a losartan u otros ARA-II"],
                                         "comorbidities": ["estenosis bilateral de la arteria renal"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "50mg"
            },
            # ---
            {
                "name": "Hidroclorotiazida 12.5mg",
                "patient_summary": "Diuretico para controlar la presion arterial. Tomala en la manana.",
                "dosage_mg_kg": None,
                "max_daily_dose": "12.5mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["anuria"],
                                         "allergies": ["hipersensibilidad a tiazidas o sulfonamidas"],
                                         "comorbidities": ["gota", "hiponatremia"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "12.5mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Reducción de sodio en la dieta. Ejercicio aeróbico 150 min/semana. Control de peso. Monitoreo de PA en casa. Evaluar daño a órgano blanco (corazón, riñón, cerebro)."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Diabetes Mellitus Tipo 2",
        "medicines": [
            {
                "name": "Metformina 850mg",
                "patient_summary": "Controla el azucar en la sangre. Tomala con las comidas para evitar molestias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "850mg",
                "frequency": "Cada 12 horas con comidas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia renal grave (filtrado <30 ml/min)", "acidosis lactica previa", "hipoxia o sepsis"],
                                         "allergies": ["hipersensibilidad a metformina"],
                                         "comorbidities": ["insuficiencia hepatica grave", "consumo excesivo de alcohol"],
                                     },
                "adjustments": {
                                   "renal": "No usar si el filtrado es <30 ml/min; evaluar dosis entre 30-45 ml/min",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "Suspender temporalmente antes de estudios con contraste yodado y verificar funcion renal.",
                "monitoring": "Vigilar funcion renal periodicamente.",
                "dosage": "850mg"
            },
            # ---
            {
                "name": "Glibenclamida 5mg",
                "patient_summary": "Baja el azucar en la sangre. Tomala antes del desayuno.",
                "dosage_mg_kg": None,
                "max_daily_dose": "5mg",
                "frequency": "Cada 24 horas antes del desayuno",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["cetoacidosis diabetica", "insuficiencia renal grave", "insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad a sulfonilureas o sulfonamidas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Riesgo aumentado de hipoglucemia en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y los AINE pueden aumentar el riesgo de hipoglucemia.",
                "monitoring": None,
                "dosage": "5mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Vitamina D 1000 UI",
                "dosage": "1000 UI",
                "dosage_mg_kg": None,
                "max_daily_dose": "4000 UI/dia",
                "frequency": "1000 UI cada 24 horas",
                "duration": "Cronico",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipercalcemia"
          ],
          "allergies": [],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Monitorear niveles calcio",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis ajustada por peso",
          "geriatric": "Frecuente deficiencia, monitorizar",
          "pregnancy": "Seguro en dosis recomendadas."
        },
                "interactions_warning": "Diureticos tiazidicos: riesgo de hipercalcemia.",
                "monitoring": "Niveles sericos de vitamina D y calcio.",
                "patient_summary": "Vitamina esencial para huesos y defensas. Tomala con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Mantener horarios regulares de comida (3 comidas principales + 2 meriendas)",
            "Realizar actividad fisica moderada 150 minutos a la semana",
            "Monitorear niveles de glucosa/tiroides segun indicacion medica",
            "Evitar azucares refinados y harinas blancas",
            "No suspender la medicacion sin consultar al medico",
            "Mantener un peso saludable"
        ],
        "general_recommendations": "Plan de alimentación saludable. Ejercicio regular. Automonitoreo de glucosa capilar. Control de HbA1c cada 3 meses. Evaluación anual de fondo de ojo, pie diabético y función renal."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Hipotiroidismo",
        "medicines": [
            {
                "name": "Levotiroxina sódica 50-100mcg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50-100mcg",
                "frequency": "Cada 24 horas en ayunas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["tirotoxicosis no corregida", "insuficiencia suprarrenal no tratada", "infarto agudo de miocardio"],
                                         "allergies": ["hipersensibilidad a levotiroxina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "50-100mcg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Vitamina D 1000 UI",
                "dosage": "1000 UI",
                "dosage_mg_kg": None,
                "max_daily_dose": "4000 UI/dia",
                "frequency": "1000 UI cada 24 horas",
                "duration": "Cronico",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipercalcemia"
          ],
          "allergies": [],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Monitorear niveles calcio",
          "hepatic": "No requiere ajuste",
          "pediatric": "Dosis ajustada por peso",
          "geriatric": "Frecuente deficiencia, monitorizar",
          "pregnancy": "Seguro en dosis recomendadas."
        },
                "interactions_warning": "Diureticos tiazidicos: riesgo de hipercalcemia.",
                "monitoring": "Niveles sericos de vitamina D y calcio.",
                "patient_summary": "Vitamina esencial para huesos y defensas. Tomala con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Mantener horarios regulares de comida (3 comidas principales + 2 meriendas)",
            "Realizar actividad fisica moderada 150 minutos a la semana",
            "Monitorear niveles de glucosa/tiroides segun indicacion medica",
            "Evitar azucares refinados y harinas blancas",
            "No suspender la medicacion sin consultar al medico",
            "Mantener un peso saludable"
        ],
        "general_recommendations": "Tomar levotiroxina 30-60 min antes del desayuno. Monitorear TSH cada 6-8 semanas hasta ajuste, luego anual. Evitar calcio y hierro junto con la medicación."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Hipertiroidismo",
        "medicines": [
            {
                "name": "Metimazol 15-30mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "15-30mg",
                "frequency": "Cada 24 horas",
                "duration": "12-18 meses",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["agranulocitosis o neutropenia previa", "primer trimestre del embarazo (preferir alternativa)"],
                                         "allergies": ["hipersensibilidad a metimazol o tiouracilos"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": "Control periodico de hemograma por riesgo de agranulocitosis.",
                "dosage": "15-30mg"
            },
            # ---
            {
                "name": "Propranolol 40mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "40mg",
                "frequency": "Cada 8 horas",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["asma", "bradicardia severa", "bloqueo AV de segundo o tercer grado", "shock cardiogenico", "insuficiencia cardiaca descompensada"],
                                         "allergies": ["hipersensibilidad a betabloqueantes"],
                                         "comorbidities": ["enfermedad vascular periferica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No suspender bruscamente; precaucion con verapamilo y diltiazem.",
                "monitoring": None,
                "dosage": "40mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Monitoreo de función tiroidea cada 4-6 semanas. Evaluar remisión después de 12-18 meses. Considerar yodo radiactivo o cirugía si no responde. Evitar cafeína y estimulantes."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Migraña",
        "medicines": [
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas",
                "duration": "Durante crisis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
            # ---
            {
                "name": "Sumatriptán 50mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50mg",
                "frequency": "Dosis única al inicio del dolor",
                "duration": "Durante crisis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["cardiopatia isquemica o vasoespasmo coronario", "infarto de miocardio, ACV o AIT recientes", "hipertension arterial no controlada", "migrana hemiplejica o basilar", "insuficiencia renal o hepatica grave"],
                                         "allergies": ["hipersensibilidad a triptanes"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No combinar con ergotaminas ni IMAO; riesgo de sindrome serotoninergico con ISRS/IRSN.",
                "monitoring": None,
                "dosage": "50mg"
            },
            # ---
            {
                "name": "Metoclopramida 10mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Durante crisis",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["feocromocitoma", "obstruccion o perforacion gastrointestinal", "enfermedad de Parkinson", "epilepsia (precaucion)"],
                                         "allergies": ["hipersensibilidad a metoclopramida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Uso prolongado mayor a 5 dias eleva el riesgo de discinesia tardia.",
                "monitoring": None,
                "dosage": "10mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Identificar y evitar desencadenantes. Habitación oscura y silenciosa durante crisis. Considerar profilaxis si >4 crisis/mes con topiramato o propranolol."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Accidente Cerebrovascular (ACV)",
        "medicines": [
            {
                "name": "Activador de plasminógeno tisular (tPA)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "0.9mg/kg IV",
                "frequency": "Dosis única dentro de 4.5h",
                "duration": "1 dosis",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hemorragia intracraneal previa o activa", "ACV isquemico en los ultimos 3 meses", "cirugia mayor o traumatismo craneal en los ultimos 3 meses", "sangrado interno activo", "presion arterial >185/110 mmHg no controlable", "trombocitopenia o coagulopatia grave"],
                                         "allergies": ["hipersensibilidad a alteplasa"],
                                         "comorbidities": ["endocarditis bacteriana", "aneurisma o malformacion arteriovenosa cerebral"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sangrado grave con anticoagulantes, antiagregantes y heparinoides.",
                "monitoring": "Vigilar signos neurologicos y hemorragicos; control estricto de presion arterial.",
                "dosage": "0.9mg/kg IV"
            },
            # ---
            {
                "name": "Ácido acetilsalicílico 100mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "100mg",
                "frequency": "Cada 24 horas (post tPA)",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa", "hemorragia gastrointestinal activa", "hemofilia u otro trastorno de la coagulacion", "tercer trimestre del embarazo"],
                                         "allergies": ["hipersensibilidad a acido acetilsalicilico u otros AINE", "asma sensible a AINE"],
                                         "comorbidities": ["diatesis hemorragica"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "100mg"
            },
            # ---
            {
                "name": "Clopidogrel 75mg",
                "patient_summary": "Anticoagulante para prevenir infartos. Tomala a la misma hora todos los dias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "75mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["sangrado activo patologico (ulcera hemorragica, hemorragia intracraneal)"],
                                         "allergies": ["hipersensibilidad a clopidogrel"],
                                         "comorbidities": ["enfermedad hepatica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar omeprazol y esomeprazol; riesgo de sangrado con AINE e ibuprofeno.",
                "monitoring": None,
                "dosage": "75mg"
            },
            # ---
            {
                "name": "Atorvastatina 40mg",
                "patient_summary": "Baja el colesterol malo. Tomala en la noche para mejor efecto.",
                "dosage_mg_kg": None,
                "max_daily_dose": "40mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["enfermedad hepatica activa o transaminasas elevadas persistentes", "embarazo y lactancia"],
                                         "allergies": ["hipersensibilidad a estatinas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de miopatia con fibratos, ciclosporina, claritromicina y antifungicos azolicos.",
                "monitoring": None,
                "dosage": "40mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "EMERGENCIA MÉDICA - Activación de código ACV. TC cerebral inmediato. Ventana de trombólisis 4.5 horas. Unidad de ACV. Rehabilitación temprana: fonoaudiología, terapia ocupacional, fisioterapia."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Epilepsia",
        "medicines": [
            {
                "name": "Ácido valproico 500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hepatopatia aguda o grave", "trastorno mitocondrial documentado (p. ej. sindrome POLG)", "pancreatitis previa", "embarazo (teratogeno; requiere evaluacion estricta)"],
                                         "allergies": ["hipersensibilidad a valproato"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": "Control de funcion hepatica y hemograma.",
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Levetiracetam 500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a levetiracetam"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Lorazepam 1mg",
                "dosage": "1mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "3 mg/dia",
                "frequency": "1 mg cada 12-24 horas si es necesario",
                "duration": "2-4 semanas",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia respiratoria severa",
            "Miastenia gravis"
          ],
          "allergies": [
            "Benzodiazepinas"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Reducir dosis en hepatopatia",
          "pediatric": "No recomendado en <6 anos",
          "geriatric": "Dosis reducida por riesgo de caidas",
          "pregnancy": "Categoria D. Evitar en embarazo."
        },
                "interactions_warning": "Alcohol: depresion respiratoria. Opioides: riesgo aumentado de sedacion.",
                "monitoring": "Somnolencia, dependencia, funciones cognitivas.",
                "patient_summary": "Para la ansiedad severa y el insomnio. Solo uso temporal."
            },
        ],
        "non_pharmacological_treatments": [
            "Establecer una rutina de sueno regular (7-8 horas diarias)",
            "Reducir el consumo de cafeina y estimulantes",
            "Practicar tecnicas de manejo del estres como respiracion profunda",
            "Realizar actividad fisica regular (caminar 30 minutos al dia)",
            "Evitar el aislamiento social, mantener contacto con familiares y amigos",
            "Llevar un diario de sintomas para identificar desencadenantes"
        ],
        "general_recommendations": "Evitar desencadenantes (falta de sueño, alcohol, luces). No suspender medicación abruptamente. Evaluar conducción vehicular según normativa local. EEG y control neurológico periódico."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Enfermedad de Parkinson",
        "medicines": [
            {
                "name": "Levodopa/Carbidopa 250/25mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "250/25mg",
                "frequency": "Cada 8 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["glaucoma de angulo estrecho", "melanoma maligno (precaucion)"],
                                         "allergies": ["hipersensibilidad a levodopa o carbidopa"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No combinar con IMAO no selectivos.",
                "monitoring": None,
                "dosage": "250/25mg"
            },
            # ---
            {
                "name": "Pramipexol 0.25mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "0.25mg",
                "frequency": "Cada 8 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a pramipexol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "0.25mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Lorazepam 1mg",
                "dosage": "1mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "3 mg/dia",
                "frequency": "1 mg cada 12-24 horas si es necesario",
                "duration": "2-4 semanas",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia respiratoria severa",
            "Miastenia gravis"
          ],
          "allergies": [
            "Benzodiazepinas"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Reducir dosis en hepatopatia",
          "pediatric": "No recomendado en <6 anos",
          "geriatric": "Dosis reducida por riesgo de caidas",
          "pregnancy": "Categoria D. Evitar en embarazo."
        },
                "interactions_warning": "Alcohol: depresion respiratoria. Opioides: riesgo aumentado de sedacion.",
                "monitoring": "Somnolencia, dependencia, funciones cognitivas.",
                "patient_summary": "Para la ansiedad severa y el insomnio. Solo uso temporal."
            },
        ],
        "non_pharmacological_treatments": [
            "Establecer una rutina de sueno regular (7-8 horas diarias)",
            "Reducir el consumo de cafeina y estimulantes",
            "Practicar tecnicas de manejo del estres como respiracion profunda",
            "Realizar actividad fisica regular (caminar 30 minutos al dia)",
            "Evitar el aislamiento social, mantener contacto con familiares y amigos",
            "Llevar un diario de sintomas para identificar desencadenantes"
        ],
        "general_recommendations": "Fisioterapia y terapia ocupacional. Ejercicio regular (tai chi, baile). Evaluar disfagia y riesgo de caídas. Apoyo psicológico. Considerar estimulación cerebral profunda en casos avanzados."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Artritis Reumatoide",
        "medicines": [
            {
                "name": "Metotrexato 7.5-15mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "7.5-15mg",
                "frequency": "1 vez por semana",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo y lactancia", "insuficiencia hepatica significativa", "insuficiencia renal significativa", "inmunodeficiencia", "ulcera peptica activa", "discrasias sanguineas"],
                                         "allergies": ["hipersensibilidad a metotrexato"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El uso con AINE y trimetoprim-sulfametoxazol aumenta la toxicidad; es necesario suplementar acido folico.",
                "monitoring": "Hemograma, funcion hepatica y renal periodicos.",
                "dosage": "7.5-15mg"
            },
            # ---
            {
                "name": "Ácido fólico 5mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "5mg",
                "frequency": "Cada 24 horas excepto día de metotrexato",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad al acido folico"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "5mg"
            },
            # ---
            {
                "name": "Prednisolona 5-10mg",
                "patient_summary": "Corticosteroide para bajar inflamacion severa. Tomala exactamente como te la receten.",
                "dosage_mg_kg": None,
                "max_daily_dose": "5-10mg",
                "frequency": "Cada 24 horas",
                "duration": "Dosis descendente",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["infeccion sistemica no controlada", "infeccion fungica sistemica no controlada"],
                                         "allergies": ["hipersensibilidad a corticosteroides"],
                                         "comorbidities": ["diabetes mellitus descontrolada (vigilar glucemia)", "hipertension arterial severa"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "5-10mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Reumatología de seguimiento. Fisioterapia para mantener rango articular. Ejercicios de bajo impacto. Evaluar necesidad de terapia biológica si no responde. Monitoreo de efectos adversos del metotrexato."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Lupus Eritematoso Sistémico",
        "medicines": [
            {
                "name": "Hidroxicloroquina 200mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "200mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["retinopatia previa", "hipersensibilidad a 4-aminoquinolinas"],
                                         "allergies": ["hipersensibilidad a hidroxicloroquina"],
                                         "comorbidities": ["psoriasis (puede exacerbarse)"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": "Evaluacion oftalmologica periodica por riesgo de retinopatia.",
                "dosage": "200mg"
            },
            # ---
            {
                "name": "Prednisolona 10-60mg",
                "patient_summary": "Corticosteroide para bajar inflamacion severa. Tomala exactamente como te la receten.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10-60mg",
                "frequency": "Cada 24 horas",
                "duration": "Según actividad",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["infeccion sistemica no controlada", "infeccion fungica sistemica no controlada"],
                                         "allergies": ["hipersensibilidad a corticosteroides"],
                                         "comorbidities": ["diabetes mellitus descontrolada (vigilar glucemia)", "hipertension arterial severa"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10-60mg"
            },
            # ---
            {
                "name": "Micofenolato mofetilo 1g",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1g",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo y lactancia (teratogeno)", "infeccion activa"],
                                         "allergies": ["hipersensibilidad a micofenolato"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar la combinacion con azatioprina; aumenta el riesgo de infecciones.",
                "monitoring": None,
                "dosage": "1g"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Protección solar estricta (FPS 50+). Evaluación periódica de función renal. Control de presión arterial. Vacunación antineumocócica y antigripal. Evitar embarazo no planificado (alto riesgo)."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Malaria",
        "medicines": [
            {
                "name": "Artemeter-Lumefantrina 20/120mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "4 comprimidos",
                "frequency": "Cada 12 horas",
                "duration": "3 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["primer trimestre del embarazo", "prolongacion del intervalo QT"],
                                         "allergies": ["hipersensibilidad a artemeter o lumefantrina"],
                                         "comorbidities": ["cardiopatia con QT prolongado"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar farmacos que prolongan el intervalo QT e inductores de CYP3A4 (rifampicina, algunos antifungicos).",
                "monitoring": None,
                "dosage": "4 comprimidos"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Tratamiento supervisado. Notificación obligatoria. Mosquitero impregnado con insecticida. Evaluar complicaciones: malaria cerebral, insuficiencia renal, edema pulmonar. Seguimiento de parasitemia a las 48h."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Fiebre Tifoidea",
        "medicines": [
            {
                "name": "Ceftriaxona 2g IV",
                "patient_summary": "Antibiotico inyectable para infecciones graves. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2g",
                "frequency": "Cada 24 horas",
                "duration": "7-10 días",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hiperbilirrubinemia neonatal"],
                                         "allergies": ["hipersensibilidad a cefalosporinas", "alergia grave a penicilinas (reaccion anafilactica)"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2g"
            },
            # ---
            {
                "name": "Azitromicina 500mg",
                "patient_summary": "Antibiotico de 3 dias para infecciones respiratorias. Tomalo completo.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 24 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hepatopatia grave"],
                                         "allergies": ["hipersensibilidad a macrolidos"],
                                         "comorbidities": ["prolongacion del intervalo QT"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de prolongacion del intervalo QT con antiarritmicos y antipsicoticos.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Aislamiento entérico. Notificación obligatoria. Higiene de manos. Evitar alimentos contaminados. Seguimiento de portadores asintomáticos. Vacunación para viajeros."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Varicela",
        "medicines": [
            {
                "name": "Acetaminofén 500mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 6 horas PRN",
                "duration": "5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Loción de calamina",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "Tópica",
                "frequency": "Cada 6 horas PRN",
                "duration": "Según necesidad",
                "route": "Tópico",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a calamina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "Tópica"
            },
            # ---
            {
                "name": "Aciclovir 800mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "800mg",
                "frequency": "5 veces al día",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a aciclovir"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "800mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "NO USAR ASPIRINA por riesgo de síndrome de Reye. Aislamiento hasta que todas las lesiones estén en costra (5-7 días). Baños de avena para prurito. Mantener uñas cortas para evitar infección secundaria. Vacunación para contactos susceptibles."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Herpes Zóster",
        "medicines": [
            {
                "name": "Aciclovir 800mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "800mg",
                "frequency": "5 veces al día",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a aciclovir"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "800mg"
            },
            # ---
            {
                "name": "Gabapentina 300mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Cada 8 horas",
                "duration": "Según dolor",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a gabapentina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumenta el efecto sedante con alcohol y otros depresores del sistema nervioso central.",
                "monitoring": None,
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Lidocaína parche 5%",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1 parche",
                "frequency": "Cada 12 horas",
                "duration": "Durante dolor agudo",
                "route": "Tópico",
                "contraindications": {
                                         "conditions": ["hipersensibilidad a anestesicos locales tipo amida", "piel danada o infeccion en la zona de aplicacion"],
                                         "allergies": ["hipersensibilidad a lidocaina o anestesicos amida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1 parche"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Tratamiento antiviral temprano reduce riesgo de neuralgia postherpética. Mantener lesiones limpias y secas. Evaluar vacunación (Zostavax/Shingrix) en >50 años. El dolor puede persistir meses después de la erupción."
    },
    # ──────────────────────────────────
    {
        "disease_name": "VIH (Infección Aguda)",
        "medicines": [
            {
                "name": "Tenofovir disoproxil 300mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a tenofovir"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": "Vigilar funcion renal y densidad osea.",
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Emtricitabina 200mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "200mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a emtricitabina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "200mg"
            },
            # ---
            {
                "name": "Dolutegravir 50mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a dolutegravir"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No combinar con dofetilida; precaucion con rifampicina y metformina.",
                "monitoring": None,
                "dosage": "50mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Inicio inmediato de TAR. Notificación obligatoria. Prueba de carga viral y CD4 al diagnóstico. Perfil de resistencia. Evaluar coinfecciones (TB, hepatitis). PrEP para parejas. Uso de condón. Seguimiento mensual hasta supresión viral."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Mononucleosis Infecciosa",
        "medicines": [
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "5-7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "5-7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "REPOSO ABSOLUTO. Evitar deportes de contacto por riesgo de ruptura esplénica (por 4-8 semanas). Hidratación abundante. Gárgaras de agua tibia con sal. No usar ampicilina/amoxicilina (causa rash). La fatiga puede persistir semanas."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Leptospirosis",
        "medicines": [
            {
                "name": "Doxiciclina 100mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. No te expongas al sol durante el tratamiento.",
                "dosage_mg_kg": None,
                "max_daily_dose": "100mg",
                "frequency": "Cada 12 horas",
                "duration": "7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo", "ninos menores de 8 anos (afecta el esmalte dental)"],
                                         "allergies": ["hipersensibilidad a tetraciclinas"],
                                         "comorbidities": ["hepatopatia"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "La exposicion solar aumenta la fotosensibilidad.",
                "monitoring": None,
                "dosage": "100mg"
            },
            # ---
            {
                "name": "Ceftriaxona 1g IV",
                "patient_summary": "Antibiotico inyectable para infecciones graves. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1g",
                "frequency": "Cada 24 horas",
                "duration": "7 días",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hiperbilirrubinemia neonatal"],
                                         "allergies": ["hipersensibilidad a cefalosporinas", "alergia grave a penicilinas (reaccion anafilactica)"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1g"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Notificación obligatoria. Hospitalización si hay ictericia o insuficiencia renal. Evitar exposición a aguas contaminadas. Uso de botas y guantes en trabajos de riesgo. Monitoreo de función renal y hepática."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Brucelosis",
        "medicines": [
            {
                "name": "Doxiciclina 100mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. No te expongas al sol durante el tratamiento.",
                "dosage_mg_kg": None,
                "max_daily_dose": "100mg",
                "frequency": "Cada 12 horas",
                "duration": "6 semanas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["embarazo", "ninos menores de 8 anos (afecta el esmalte dental)"],
                                         "allergies": ["hipersensibilidad a tetraciclinas"],
                                         "comorbidities": ["hepatopatia"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "La exposicion solar aumenta la fotosensibilidad.",
                "monitoring": None,
                "dosage": "100mg"
            },
            # ---
            {
                "name": "Rifampicina 600mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "600mg",
                "frequency": "Cada 24 horas",
                "duration": "6 semanas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ictericia previa con rifampicina", "porfiria"],
                                         "allergies": ["hipersensibilidad a rifampicina"],
                                         "comorbidities": ["hepatopatia grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Potente inductor enzimatico: puede reducir la eficacia de anticonceptivos, warfarina y otros medicamentos.",
                "monitoring": "Vigilar funcion hepatica.",
                "dosage": "600mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Notificación obligatoria. Evitar consumo de lácteos no pasteurizados. Protección en mataderos y establos. Monitoreo de recaídas (pueden ocurrir hasta 6 meses después). Evaluar complicaciones como espondilitis y endocarditis."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Asma Bronquial",
        "medicines": [
            {
                "name": "Salbutamol inhalador 100mcg",
                "patient_summary": "Inhalador que abre las vias respiratorias. Usalo cuando sientas silbido en el pecho.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 4-6 horas PRN",
                "duration": "Durante crisis",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": ["taquiarritmias no controladas"],
                                         "allergies": ["hipersensibilidad a salbutamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
            # ---
            {
                "name": "Budesonida inhalador 200mcg",
                "patient_summary": "Inhalador que baja la inflamacion de los pulmones. Usalo a diario. No es de rescate.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a budesonida"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
            # ---
            {
                "name": "Montelukast 10mg",
                "patient_summary": "Pastilla para prevenir ataques de asma. Tomala en la noche.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a montelukast"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Notificar cambios de animo o comportamiento (posibles efectos neuropsiquiatricos).",
                "monitoring": None,
                "dosage": "10mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Identificar y evitar desencadenantes (ácaros, polen, humo). Plan de acción escrito. Técnica inhalatoria correcta. Pico-flujo diario. Vacunación antigripal y antineumocócica. Evaluar control cada 3 meses."
    },
    # ──────────────────────────────────
    {
        "disease_name": "EPOC",
        "medicines": [
            {
                "name": "Salbutamol inhalador 100mcg",
                "patient_summary": "Inhalador que abre las vias respiratorias. Usalo cuando sientas silbido en el pecho.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 4-6 horas PRN",
                "duration": "Crónico",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": ["taquiarritmias no controladas"],
                                         "allergies": ["hipersensibilidad a salbutamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
            # ---
            {
                "name": "Tiotropio inhalador 18mcg",
                "patient_summary": "Inhalador diario para respirar mejor con EPOC. Una sola inhalacion al dia.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1 inhalación",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": ["glaucoma de angulo estrecho", "retencion urinaria (hiperplasia prostatica significativa)"],
                                         "allergies": ["hipersensibilidad a tiotropio, atropina o ipratropio"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1 inhalación"
            },
            # ---
            {
                "name": "Fluticasona/Salmeterol 250/50mcg",
                "patient_summary": "Inhalador para controlar la inflamacion de los pulmones. Usalo todos los dias.",
                "dosage_mg_kg": None,
                "max_daily_dose": "2 inhalaciones",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a fluticasona o salmeterol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No es para el alivio inmediato de una crisis; enjuagar la boca tras cada uso.",
                "monitoring": None,
                "dosage": "2 inhalaciones"
            },
            # ---
            {
                "name": "Oxígeno domiciliario",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1-2L/min",
                "frequency": "≥16 horas/día",
                "duration": "Crónico si PaO2 <55mmHg",
                "route": "Inhalado",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1-2L/min"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "dosage": "400mg",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "1200 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Ulcera peptica activa",
            "Insuficiencia renal grave"
          ],
          "allergies": [
            "Ibuprofeno",
            "AINEs"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "Evitar si ClCr <30 mL/min",
          "hepatic": "Usar con precaucion",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "Usar dosis minima por riesgo gastrointestinal",
          "pregnancy": "Categoria C. Evitar en 3er trimestre."
        },
                "interactions_warning": "AINEs + anticoagulantes: riesgo de sangrado. AINEs + IECA: reducen efecto antihipertensivo.",
                "monitoring": "Funcion renal, signos de sangrado gastrointestinal.",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida."
            },
        ],
        "non_pharmacological_treatments": [
            "Evitar exposicion al humo de tabaco y contaminantes ambientales",
            "Mantener hidratacion adecuada (2 litros de agua al dia)",
            "Reposo relativo durante la fase aguda",
            "Elevar la cabecera de la cama para facilitar la respiracion",
            "Evitar cambios bruscos de temperatura",
            "Realizar lavados nasales con solucion salina si hay congestion"
        ],
        "general_recommendations": "CESAR DE FUMAR es la medida más importante. Vacunación antigripal y antineumocócica anual. Rehabilitación pulmonar. Evaluación de gasometría arterial. Valorar cirugía de reducción de volumen en casos seleccionados."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Laringitis Aguda",
        "medicines": [
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "REPOSO VOCAL ABSOLUTO (no hablar ni susurrar). Hidratación abundante. Evitar irritantes (tabaco, alcohol). Vaporizaciones con agua tibia. No requiere antibióticos (viral en >90%). Si persiste >2 semanas, evaluar por ORL."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Apendicitis Aguda",
        "medicines": [
            {
                "name": "Ceftriaxona 1g IV",
                "patient_summary": "Antibiotico inyectable para infecciones graves. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1g",
                "frequency": "Cada 12 horas IV",
                "duration": "Hasta cirugía",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hiperbilirrubinemia neonatal"],
                                         "allergies": ["hipersensibilidad a cefalosporinas", "alergia grave a penicilinas (reaccion anafilactica)"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1g"
            },
            # ---
            {
                "name": "Metronidazol 500mg IV",
                "patient_summary": "Antibiotico para infecciones intestinales y dentales. No tomes alcohol durante el tratamiento.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas IV",
                "duration": "Hasta cirugía",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["primer trimestre del embarazo (evitar en lo posible)"],
                                         "allergies": ["hipersensibilidad a metronidazol o nitroimidazoles"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar el consumo de alcohol durante el tratamiento y 48 h despues (efecto disulfiram).",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Analgesia (Tramadol 50mg IV)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Hasta cirugía",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["epilepsia no controlada", "depresion respiratoria aguda", "uso de IMAO"],
                                         "allergies": ["hipersensibilidad a opioides"],
                                         "comorbidities": ["insuficiencia renal o hepatica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sindrome serotoninergico con ISRS, IRSN y antidepresivos.",
                "monitoring": None,
                "dosage": "50mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "URGENCIA QUIRÚRGICA - Apendicectomía laparoscópica o abierta. NADA VÍA ORAL (NPO). Ayuno prequirúrgico. Antibióticos preoperatorios. Si hay perforación, antibióticos por 7-10 días postcirugía."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Colecistitis",
        "medicines": [
            {
                "name": "Ceftriaxona 1g IV",
                "patient_summary": "Antibiotico inyectable para infecciones graves. Solo con formula medica.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1g",
                "frequency": "Cada 12 horas IV",
                "duration": "Hasta cirugía",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["hiperbilirrubinemia neonatal"],
                                         "allergies": ["hipersensibilidad a cefalosporinas", "alergia grave a penicilinas (reaccion anafilactica)"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1g"
            },
            # ---
            {
                "name": "Metronidazol 500mg IV",
                "patient_summary": "Antibiotico para infecciones intestinales y dentales. No tomes alcohol durante el tratamiento.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas IV",
                "duration": "Hasta cirugía",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["primer trimestre del embarazo (evitar en lo posible)"],
                                         "allergies": ["hipersensibilidad a metronidazol o nitroimidazoles"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Evitar el consumo de alcohol durante el tratamiento y 48 h despues (efecto disulfiram).",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Hioscina 20mg IV",
                "patient_summary": "Alivia los colicos abdominales y el dolor de estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "20mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Durante dolor",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["glaucoma de angulo estrecho", "retencion urinaria", "obstruccion intestinal mecanica", "taquiarritmias", "miastenia gravis"],
                                         "allergies": ["hipersensibilidad a hioscina o anticolinergicos"],
                                         "comorbidities": ["megaesofago o estenosis pilorica"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "20mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Esomeprazol 20mg",
                "dosage": "20mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "40 mg/dia",
                "frequency": "20 mg cada 24 horas",
                "duration": "4-8 semanas",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Hipersensibilidad a IBP"
          ],
          "allergies": [
            "Esomeprazol",
            "Omeprazol"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 20mg/dia en insuficiencia hepatica grave",
          "pediatric": "Seguro en >12 anos",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B."
        },
                "interactions_warning": "Reduce absorcion de clopidogrel, metotrexato y hierro.",
                "monitoring": "Sintomas gastricos, niveles de magnesio en uso prolongado.",
                "patient_summary": "Protege el estomago reduciendo el acido. Tomala antes del desayuno."
            },
            # ---
            {
                "name": "Hioscina 10mg",
                "dosage": "10mg",
                "dosage_mg_kg": None,
                "max_daily_dose": "60 mg/dia",
                "frequency": "10 mg cada 8 horas si hay dolor",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Glaucoma",
            "Miastenia gravis"
          ],
          "allergies": [
            "Hioscina"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "No requiere ajuste",
          "pediatric": "Seguro en >6 anos",
          "geriatric": "Puede causar retencion urinaria",
          "pregnancy": "Categoria C."
        },
                "interactions_warning": "Potencia efectos anticolinergicos de otros farmacos.",
                "monitoring": "Dolor abdominal, distension.",
                "patient_summary": "Alivia los colicos y el dolor de estomago. Tomala antes de las comidas."
            },
        ],
        "non_pharmacological_treatments": [
            "Dieta blanda y fraccionada (5-6 comidas pequenas al dia)",
            "Evitar alimentos irritantes: picantes, fritos, grasosos, cafe, alcohol",
            "No acostarse inmediatamente despues de comer (esperar 2-3 horas)",
            "Manterse hidratado, preferiblemente con agua o te suave",
            "Identificar y evitar alimentos que desencadenan los sintomas"
        ],
        "general_recommendations": "URGENCIA QUIRÚRGICA - Colecistectomía laparoscópica. Dieta baja en grasas. NPO prequirúrgico. Ultrasonido abdominal para confirmar. Evaluar coledocolitiasis con MRCP si hay ictericia o elevación de bilirrubina."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Úlcera Péptica",
        "medicines": [
            {
                "name": "Omeprazol 20mg",
                "patient_summary": "Protege tu estomago del acido. Tomala 30 minutos antes del desayuno.",
                "dosage_mg_kg": None,
                "max_daily_dose": "20mg",
                "frequency": "Cada 12 horas",
                "duration": "8 semanas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a inhibidores de la bomba de protones"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "20mg"
            },
            # ---
            {
                "name": "Amoxicilina 1g",
                "patient_summary": "Antibiotico para infecciones bacterianas. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "1g",
                "frequency": "Cada 12 horas",
                "duration": "14 días (si H. pylori)",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["mononucleosis infecciosa (riesgo de exantema)"],
                                         "allergies": ["alergia a penicilinas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "1g"
            },
            # ---
            {
                "name": "Claritromicina 500mg",
                "patient_summary": "Antibiotico para infecciones respiratorias y de estomago. Tomalo completo.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 12 horas",
                "duration": "14 días (si H. pylori)",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a claritromicina o macrolidos"],
                                         "comorbidities": ["prolongacion del intervalo QT"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "No combinar con colchicina ni con estatinas de alto riesgo; riesgo de QT prolongado con antiarritmicos.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Antiácido (Hidróxido de aluminio)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10ml",
                "frequency": "Cada 6 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia renal grave (riesgo de acumulacion de aluminio)"],
                                         "allergies": ["hipersensibilidad al hidroxido de aluminio"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10ml"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Prueba de H. pylori con antígeno en heces o aliento. Si es positivo: triple terapia 14 días. Evitar AINEs, alcohol y tabaco. Comidas pequeñas y frecuentes. Endoscopia de control si persisten síntomas. Signos de alarma: hematemesis, melena, dolor abdominal severo."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Reflujo Gastroesofágico (ERGE)",
        "medicines": [
            {
                "name": "Omeprazol 20mg",
                "patient_summary": "Protege tu estomago del acido. Tomala 30 minutos antes del desayuno.",
                "dosage_mg_kg": None,
                "max_daily_dose": "20mg",
                "frequency": "Cada 24 horas antes del desayuno",
                "duration": "8 semanas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a inhibidores de la bomba de protones"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "20mg"
            },
            # ---
            {
                "name": "Antiácido (Almagato)",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10ml",
                "frequency": "Cada 6 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia renal grave"],
                                         "allergies": ["hipersensibilidad a almagato"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10ml"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Elevar cabecera de cama 30°. Evitar comidas 3h antes de dormir. Reducir café, té, chocolate, cítricos, fritos. Pérdida de peso si sobrepeso. Evitar ropa apretada. Endoscopia si síntomas de alarma (disfagia, pérdida de peso)."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Cólico Nefrítico",
        "medicines": [
            {
                "name": "Diclofenaco 75mg IM",
                "patient_summary": "Baja la inflamacion y el dolor en articulaciones. Tomalo con comida.",
                "dosage_mg_kg": None,
                "max_daily_dose": "75mg",
                "frequency": "Dosis única",
                "duration": "Durante dolor",
                "route": "IM",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa", "hemorragia gastrointestinal", "insuficiencia renal grave", "tercer trimestre del embarazo", "asma sensible a AINE", "insuficiencia cardiaca grave"],
                                         "allergies": ["hipersensibilidad a diclofenaco u otros AINE"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de nefrotoxicidad con diureticos e IECA.",
                "monitoring": None,
                "dosage": "75mg"
            },
            # ---
            {
                "name": "Hioscina 20mg IV",
                "patient_summary": "Alivia los colicos abdominales y el dolor de estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "20mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Durante dolor",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["glaucoma de angulo estrecho", "retencion urinaria", "obstruccion intestinal mecanica", "taquiarritmias", "miastenia gravis"],
                                         "allergies": ["hipersensibilidad a hioscina o anticolinergicos"],
                                         "comorbidities": ["megaesofago o estenosis pilorica"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "20mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Tamsulosina 0.4mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "0.4mg",
                "frequency": "Cada 24 horas",
                "duration": "Hasta expulsión del cálculo",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a tamsulosina"],
                                         "comorbidities": ["hipotension ortostatica"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "0.4mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Aumentar ingesta de agua (>3L/día). Filtrar la orina para recuperar el cálculo y analizarlo. Analgesia agresiva. Evaluar con TAC de abdomen sin contraste. Si fiebre o dolor intratable: hospitalización. Litotricia o ureteroscopia si cálculo >5mm."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Insuficiencia Renal Aguda",
        "medicines": [
            {
                "name": "Furosemida 40-80mg IV",
                "patient_summary": "Ayuda a eliminar liquido acumulado en el cuerpo. Tomala en la manana para no orinar de noche.",
                "dosage_mg_kg": None,
                "max_daily_dose": "40-80mg",
                "frequency": "Cada 8-12 horas",
                "duration": "Según respuesta",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["anuria", "hipovolemia o deshidratacion grave", "hipopotasemia grave"],
                                         "allergies": ["hipersensibilidad a furosemida o sulfonamidas"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "40-80mg"
            },
            # ---
            {
                "name": "Kayexalato 15g",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "15g",
                "frequency": "Cada 6 horas",
                "duration": "Hasta corregir hiperkalemia",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ileo u obstruccion intestinal", "antecedente reciente de cirugia gastrointestinal (riesgo de necrosis colonica)", "hipernatremia"],
                                         "allergies": ["hipersensibilidad a poliestireno sulfonato sodico"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "15g"
            },
            # ---
            {
                "name": "Bicarbonato de sodio 1M IV",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50-100ml",
                "frequency": "Dosis única si acidosis severa",
                "duration": "1 dosis",
                "route": "IV",
                "contraindications": {
                                         "conditions": ["alcalosis metabolica", "hipopotasemia no corregida", "hipernatremia", "hipocalcemia"],
                                         "allergies": [],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "50-100ml"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "HOSPITALIZACIÓN. Identificar causa: prerrenal, renal o postrenal. Suspender nefrotóxicos. Balance hídrico estricto. Dieta baja en potasio y proteínas. Evaluar necesidad de diálisis urgente si hiperkalemia severa, acidosis refractaria o edema pulmonar."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Celulitis",
        "medicines": [
            {
                "name": "Amoxicilina/Ácido clavulánico 875/125mg",
                "patient_summary": "Antibiotico para infecciones bacterianas. Tomalo completo aunque te sientas mejor.",
                "dosage_mg_kg": None,
                "max_daily_dose": "875/125mg",
                "frequency": "Cada 12 horas",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["mononucleosis infecciosa (riesgo de exantema)"],
                                         "allergies": ["alergia a penicilinas"],
                                         "comorbidities": ["antecedente de disfuncion hepatica con amoxicilina/clavulanico"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "875/125mg"
            },
            # ---
            {
                "name": "Clindamicina 300mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "300mg",
                "frequency": "Cada 8 horas",
                "duration": "7-10 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a clindamicina"],
                                         "comorbidities": ["enfermedad inflamatoria intestinal", "colitis previa por Clostridium difficile"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de colitis pseudomembranosa con uso prolongado.",
                "monitoring": None,
                "dosage": "300mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Hidrocortisona 1% crema",
                "dosage": "Aplicar capa fina",
                "dosage_mg_kg": None,
                "max_daily_dose": None,
                "frequency": "Cada 12 horas",
                "duration": "7-14 dias",
                "route": "Tópico",
                "contraindications": {
          "conditions": [
            "Infeccion cutanea no tratada"
          ],
          "allergies": [
            "Corticoides topicos"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No aplica",
          "hepatic": "No aplica",
          "pediatric": "Usar la minima potencia efectiva",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria C. Evitar en areas extensas."
        },
                "interactions_warning": "Uso concomitante con otros topicos puede irritar.",
                "monitoring": "Mejoria de lesiones, signos de infeccion secundaria, adelgazamiento de piel.",
                "patient_summary": "Crema que baja la inflamacion y la picazon en la piel."
            },
        ],
        "non_pharmacological_treatments": [
            "Usar jabones suaves sin fragancia ni alcohol",
            "Aplicar crema humectante inmediatamente despues del bano",
            "Evitar rascarse las lesiones para prevenir infecciones secundarias",
            "Usar ropa de algodon y evitar tejidos sinteticos",
            "Mantener las unas cortas y limpias",
            "Evitar exposicion prolongada al sol sin proteccion"
        ],
        "general_recommendations": "Inmovilización y elevación del miembro afectado. Marcar borde del eritema con bolígrafo para monitorizar extensión. Hospitalización si: fiebre alta, linfangitis, rápida progresión, inmunosupresión. Evaluar presencia de absceso que requiera drenaje."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Urticaria",
        "medicines": [
            {
                "name": "Cetirizina 10mg",
                "patient_summary": "Alivia la alergia en piel y ojos. Una sola toma al dia. Puede dar sueno.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 24 horas",
                "duration": "7-14 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a cetirizina o hidroxizina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10mg"
            },
            # ---
            {
                "name": "Loratadina 10mg",
                "patient_summary": "Alivia la alergia y los estornudos. Una sola toma al dia.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 24 horas",
                "duration": "7-14 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a loratadina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10mg"
            },
            # ---
            {
                "name": "Prednisolona 30mg",
                "patient_summary": "Corticosteroide para bajar inflamacion severa. Tomala exactamente como te la receten.",
                "dosage_mg_kg": None,
                "max_daily_dose": "30mg",
                "frequency": "Cada 24 horas por 3 días",
                "duration": "3 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["infeccion sistemica no controlada", "infeccion fungica sistemica no controlada"],
                                         "allergies": ["hipersensibilidad a corticosteroides"],
                                         "comorbidities": ["diabetes mellitus descontrolada (vigilar glucemia)", "hipertension arterial severa"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "30mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Identificar y evitar desencadenantes (alimentos, medicamentos, infecciones, estrés). Antihistamínicos diarios. Si hay compromiso de vía aérea o angioedema severo: URGENCIA (adrenalina IM). Llevar diario de síntomas."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Dermatitis Atópica",
        "medicines": [
            {
                "name": "Hidrocortisona crema 1%",
                "patient_summary": "Corticosteroide para emergencias alergicas. Solo uso hospitalario.",
                "dosage_mg_kg": None,
                "max_daily_dose": "Tópico",
                "frequency": "Cada 12 horas",
                "duration": "7-14 días",
                "route": "Tópico",
                "contraindications": {
                                         "conditions": ["infeccion cutanea bacteriana, viral o fungica sin tratar"],
                                         "allergies": ["hipersensibilidad a corticosteroides topicos"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "Tópico"
            },
            # ---
            {
                "name": "Tacrolimus ungüento 0.1%",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "Tópico",
                "frequency": "Cada 12 horas",
                "duration": "Crónico intermitente",
                "route": "Tópico",
                "contraindications": {
                                         "conditions": ["embarazo y lactancia", "infeccion cutanea activa", "inmunodeficiencia"],
                                         "allergies": ["hipersensibilidad a tacrolimus"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "Tópico"
            },
            # ---
            {
                "name": "Cetirizina 10mg",
                "patient_summary": "Alivia la alergia en piel y ojos. Una sola toma al dia. Puede dar sueno.",
                "dosage_mg_kg": None,
                "max_daily_dose": "10mg",
                "frequency": "Cada 24 horas",
                "duration": "Según prurito",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a cetirizina o hidroxizina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "10mg"
            },
            # ---
            {
                "name": "Emolientes (crema hidratante)",
                "patient_summary": "Aplica esta crema en la zona afectada segun la indicacion.",
                "dosage_mg_kg": None,
                "max_daily_dose": "Tópico",
                "frequency": "Cada 12 horas y tras baño",
                "duration": "Crónico",
                "route": "Tópico",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a componentes de la crema"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "Tópico"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Baños cortos con agua tibia. Jabón suave sin fragancia. Hidratación abundante de la piel (emolientes). Evitar rascado (mantener uñas cortas). Ropa de algodón. Evitar alérgenos conocidos. Control de infecciones secundarias (Staphylococcus aureus)."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Cistitis Intersticial",
        "medicines": [
            {
                "name": "Amitriptilina 25mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "25mg",
                "frequency": "Cada 24 horas al acostarse",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["infarto de miocardio reciente", "arritmias", "glaucoma de angulo estrecho", "retencion urinaria", "uso de IMAO"],
                                         "allergies": ["hipersensibilidad a antidepresivos triciclicos"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sindrome serotoninergico con IMAO y de prolongacion del QT con antiarritmicos.",
                "monitoring": None,
                "dosage": "25mg"
            },
            # ---
            {
                "name": "Pentosano polisulfato 100mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "100mg",
                "frequency": "Cada 8 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["hemorragia activa", "trombocitopenia"],
                                         "allergies": ["hipersensibilidad a pentosano polisulfato"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": None,
                "monitoring": None,
                "dosage": "100mg"
            },
            # ---
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Baja la inflamacion, la fiebre y el dolor. Tomalo con comida para cuidar tu estomago.",
                "dosage_mg_kg": None,
                "max_daily_dose": "400mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según síntomas",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["ulcera peptica activa o hemorragia gastrointestinal", "insuficiencia renal grave (filtrado <30 ml/min)", "tercer trimestre del embarazo", "asma sensible a AINE"],
                                         "allergies": ["hipersensibilidad a ibuprofeno u otros AINE"],
                                         "comorbidities": ["insuficiencia cardiaca significativa", "diatesis hemorragica"],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": "Menor dosis y menor duracion en adultos mayores",
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumento del riesgo de sangrado con anticoagulantes, antiagregantes y corticosteroides.",
                "monitoring": None,
                "dosage": "400mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Evitar alimentos irritantes (café, té, cítricos, picante, tomate, alcohol). Técnicas de relajación y manejo del estrés. Fisioterapia de suelo pélvico. Micción programada. Evaluar por urología para cistoscopia. Considerar instilaciones vesicales intravesicales."
    },
    # ──────────────────────────────────
    {
        "disease_name": "Fibromialgia",
        "medicines": [
            {
                "name": "Pregabalina 75mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "75mg",
                "frequency": "Cada 12 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": [],
                                         "allergies": ["hipersensibilidad a pregabalina"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": "Ajustar dosis en insuficiencia renal",
                                   "hepatic": None,
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "Aumenta el efecto sedante con alcohol y otros depresores del sistema nervioso central.",
                "monitoring": None,
                "dosage": "75mg"
            },
            # ---
            {
                "name": "Duloxetina 60mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "60mg",
                "frequency": "Cada 24 horas",
                "duration": "Crónico",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["glaucoma de angulo estrecho", "insuficiencia renal grave (filtrado <30 ml/min)", "hepatopatia grave", "uso de IMAO"],
                                         "allergies": ["hipersensibilidad a duloxetina"],
                                         "comorbidities": ["hipertension arterial no controlada"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sindrome serotoninergico con ISRS, IMAO y triptanes.",
                "monitoring": None,
                "dosage": "60mg"
            },
            # ---
            {
                "name": "Paracetamol 500mg",
                "patient_summary": "Tomalo para bajar la fiebre y aliviar el dolor. No tomes alcohol mientras lo uses.",
                "dosage_mg_kg": None,
                "max_daily_dose": "500mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Según dolor",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["insuficiencia hepatica grave"],
                                         "allergies": ["hipersensibilidad al paracetamol"],
                                         "comorbidities": [],
                                     },
                "adjustments": {
                                   "renal": None,
                                   "hepatic": "Evitar en enfermedad hepatica grave",
                                   "pediatric": None,
                                   "geriatric": None,
                                   "pregnancy": None,
                               },
                "interactions_warning": "El alcohol y el uso prolongado aumentan el riesgo de dano hepatico.",
                "monitoring": None,
                "dosage": "500mg"
            },
            # ---
            {
                "name": "Tramadol 50mg",
                "patient_summary": "Toma segun la indicacion medica. Consulta si tienes dudas sobre la dosis.",
                "dosage_mg_kg": None,
                "max_daily_dose": "50mg",
                "frequency": "Cada 8 horas PRN",
                "duration": "Máximo 7 días",
                "route": "Oral",
                "contraindications": {
                                         "conditions": ["epilepsia no controlada", "depresion respiratoria aguda", "uso de IMAO"],
                                         "allergies": ["hipersensibilidad a opioides"],
                                         "comorbidities": ["insuficiencia renal o hepatica grave"],
                                     },
                "adjustments": {
          "renal": None,
          "hepatic": None,
          "pediatric": None,
          "geriatric": None,
          "pregnancy": None
        },
                "interactions_warning": "Riesgo de sindrome serotoninergico con ISRS, IRSN y antidepresivos.",
                "monitoring": None,
                "dosage": "50mg"
            },
        ],
        "alternative_medicines": [
            {
                "name": "Acetaminofen 500mg",
                "dosage": "500mg",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/dia",
                "frequency": "Cada 6-8 horas",
                "duration": "5 dias",
                "route": "Oral",
                "contraindications": {
          "conditions": [
            "Insuficiencia hepatica grave"
          ],
          "allergies": [
            "Acetaminofen"
          ],
          "comorbidities": []
        },
                "adjustments": {
          "renal": "No requiere ajuste",
          "hepatic": "Max 2g/dia si enfermedad hepatica",
          "pediatric": "Dosis por peso cada 6-8 horas",
          "geriatric": "No requiere ajuste",
          "pregnancy": "Categoria B. Seguro en dosis terapeuticas."
        },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad.",
                "monitoring": "Funcion hepatica en uso prolongado.",
                "patient_summary": "Para bajar la fiebre y calmar el dolor. No tomes alcohol."
            },
        ],
        "non_pharmacological_treatments": [
            "Realizar actividad fisica de bajo impacto adaptada a la condicion",
            "Mantener una dieta equilibrada rica en calcio y vitamina D",
            "Evitar el sedentarismo prolongado",
            "Consultar al medico antes de tomar suplementos o remedios caseros",
            "Asistir a controles regulares con el especialista"
        ],
        "general_recommendations": "Ejercicio aeróbico de bajo impacto (caminar, natación, tai chi) progresivo. Terapia cognitivo-conductual. Higiene del sueño. Reducción del estrés. Evitar opioides a largo plazo. Grupos de apoyo. El tratamiento es multidisciplinario (reumatología, psiquiatría, fisioterapia)."
    },
    {
        "disease_name": "Contusión y Trauma Físico",
        "medicines": [
            {
                "name": "Acetaminofén",
                "patient_summary": "Analgésico para aliviar el dolor del golpe. Tomalo como te indique el doctor y no tomes alcohol mientras lo uses.",
                "dosage_mg_kg": "10-15 mg/kg/dosis",
                "max_daily_dose": "3000 mg/día",
                "frequency": "Cada 8 horas",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
                    "conditions": ["Insuficiencia hepática grave"],
                    "allergies": ["Acetaminofén", "Paracetamol"],
                    "comorbidities": []
                },
                "adjustments": {
                    "renal": "No requiere ajuste",
                    "hepatic": "Evitar en hepatopatía grave. Máx 2g/día si enfermedad hepática.",
                    "pediatric": "10-15 mg/kg/dosis cada 6-8 horas. Máx 60 mg/kg/día.",
                    "geriatric": "No requiere ajuste",
                    "pregnancy": "Categoría B. Seguro en dosis terapéuticas."
                },
                "interactions_warning": "Alcohol: riesgo de hepatotoxicidad. Anticoagulantes: potenciación del efecto.",
                "monitoring": "Función hepática en uso prolongado.",
                "dosage": "500-650 mg"
            },
            {
                "name": "Ibuprofeno 400mg",
                "patient_summary": "Antiinflamatorio para bajar la hinchazón y el dolor del moretón. Tomalo con comida.",
                "dosage_mg_kg": "5-10 mg/kg/dosis",
                "max_daily_dose": "2400 mg/día",
                "frequency": "Cada 8 horas con alimentos",
                "duration": "3-5 días",
                "route": "Oral",
                "contraindications": {
                    "conditions": ["Úlcera péptica activa", "Insuficiencia renal", "Insuficiencia cardíaca", "Asma sensible a AINEs"],
                    "allergies": ["Ibuprofeno", "AINEs"],
                    "comorbidities": ["Enfermedad renal crónica", "Enfermedad cardiovascular"]
                },
                "adjustments": {
                    "renal": "Evitar o reducir dosis en insuficiencia renal",
                    "hepatic": "No requiere ajuste en hepatopatía leve",
                    "pediatric": "5-10 mg/kg/dosis cada 8 horas",
                    "geriatric": "Usar la menor dosis eficaz por riesgo gastrointestinal",
                    "pregnancy": "Evitar en el tercer trimestre"
                },
                "interactions_warning": "Antiagregantes y anticoagulantes: riesgo de sangrado. Diuréticos e IECA: riesgo de insuficiencia renal.",
                "monitoring": "Función renal y signos de sangrado gastrointestinal.",
                "dosage": "400mg"
            },
        ],
        "non_pharmacological_treatments": [
            "Aplicar hielo envuelto en un paño sobre la zona afectada durante 15-20 minutos, varias veces al día, las primeras 48 horas",
            "Mantener la zona elevada para reducir la hinchazón",
            "Vendaje compresivo sin apretar demasiado, para limitar la inflamación",
            "Reposo relativo y evitar actividades que agraven el dolor",
            "Observar la evolución del moretón (debe cambiar de color a amarillo-verde a medida que cicatriza)"
        ],
        "general_recommendations": "Acudir a urgencias si el golpe fue intenso en cabeza, tórax o abdomen, si hay dificultad para mover una articulación, deformidad, dolor muy intenso que no cede, adormecimiento, o si aparece fiebre. Aplicar el método RICE (reposo, hielo, compresión, elevación) las primeras 48 horas y cambiar a calor húmedo después para favorecer la reabsorción del hematoma."
    },
]


async def _upsert_many(collection, documents, key_field):
    """Inserta o actualiza documentos por un campo clave (idempotente).

    El valor de ``key_field`` se normaliza (lowercase + sin acentos) para que
    el seed no reintroduzca variantes con tilde ("Vómito") que inflarían el
    catálogo tras la deduplicación.
    """
    count = 0
    for doc in documents:
        key_value = doc.get(key_field)
        if key_value is None:
            continue
        key_value = normalize_text(key_value)
        if not key_value:
            continue
        filter_clause = {key_field: key_value}
        # El _id no se debe reasignar al hacer `$set` de todo el documento
        patch = {k: v for k, v in doc.items() if k != "_id"}
        patch[key_field] = key_value
        await collection.update_one(filter_clause, {"$set": patch}, upsert=True)
        count += 1
    return count


async def dedupe_collection(collection, key_field: str) -> int:
    """Elimina documentos duplicados dejando el de menor _id y unifica la clave.

    Agrupa por el valor **normalizado** de ``key_field`` (lowercase + sin
    acentos) para colapsar colisiones como "Vómito"/"vomito" que inflan el
    catálogo. Conserva el documento de menor ``_id``, elimina los redundantes
    y actualiza el campo conservado al valor normalizado canónico.
    """
    docs = None
    try:
        docs = await collection.find({key_field: {"$exists": True, "$ne": None}}).to_list(length=None)
    except Exception:
        return 0
    if docs is None:
        return 0

    groups: dict[str, dict] = {}
    for doc in docs:
        key = normalize_text(doc.get(key_field) or "")
        if not key:
            continue
        existing = groups.get(key)
        if existing is None or doc["_id"] < existing["_id"]:
            groups[key] = doc

    to_remove = []
    for doc in docs:
        key = normalize_text(doc.get(key_field) or "")
        if not key or key not in groups:
            continue
        if doc["_id"] != groups[key]["_id"]:
            to_remove.append(doc["_id"])

    removed = 0
    if to_remove:
        await collection.delete_many({"_id": {"$in": to_remove}})
        removed = len(to_remove)

    for key, keep in groups.items():
        current = keep.get(key_field)
        if current is not None and current != key:
            await collection.update_one({"_id": keep["_id"]}, {"$set": {key_field: key}})

    return removed


async def seed():
    """Siembra los catálogos de forma idempotente (no borra lo existente)."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        # Limpia duplicados residuales para que los upserts idempotentes
        # no fallen por el índice único.
        await dedupe_collection(db.symptoms, "name")
        await dedupe_collection(db.diseases, "name")
        await dedupe_collection(db.treatments, "disease_name")

        n_symptoms = await _upsert_many(db.symptoms, symptoms, "name")
        print(f"Upserted {n_symptoms} symptoms")

        n_diseases = await _upsert_many(db.diseases, diseases, "name")
        print(f"Upserted {n_diseases} diseases")

        n_treatments = await _upsert_many(db.treatments, treatments, "disease_name")
        print(f"Upserted {n_treatments} treatments")
    finally:
        client.close()

    print("Seed completed!")


async def force_rebuild(confirm: bool = False):
    """Borra y vuelve a sembrar todo (DESTRUCTIVO: solo con confirm=True)."""
    if not confirm:
        print("ABORTADO: force_rebuild() es destructivo. Pasa confirm=True para ejecutarlo.")
        return
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        for coll_name in ("symptoms", "diseases", "treatments"):
            if coll_name in await db.list_collection_names():
                await db[coll_name].drop()
                print(f"Dropped {coll_name}")

        await db.symptoms.insert_many(symptoms)
        print(f"Inserted {len(symptoms)} symptoms")
        await db.diseases.insert_many(diseases)
        print(f"Inserted {len(diseases)} diseases")
        await db.treatments.insert_many(treatments)
        print(f"Inserted {len(treatments)} treatments")
    finally:
        client.close()

    print("Force rebuild completed!")


if __name__ == "__main__":
    asyncio.run(seed())
