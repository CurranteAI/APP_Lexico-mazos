from pathlib import Path
import json,re
simple='''Ich trinke morgens Wasser.|Bebo agua por las mañanas.
Du lernst jeden Tag Deutsch.|Aprendes alemán todos los días.
Meine Schwester wohnt hier.|Mi hermana vive aquí.
Mein Bruder arbeitet heute.|Mi hermano trabaja hoy.
Wir essen zusammen.|Comemos juntos.
Ihr spielt dort draußen.|Jugáis allí fuera.
Sie liest ein Buch.|Ella lee un libro.
Er schreibt eine E-Mail.|Él escribe un correo electrónico.
Ich höre gern Musik.|Me gusta escuchar música.
Das Kind schläft noch.|El niño todavía duerme.
Meine Mutter ist jetzt zu Hause.|Mi madre está ahora en casa.
Mein Vater kommt später.|Mi padre viene más tarde.
Die Küche ist sehr klein.|La cocina es muy pequeña.
Das Fenster ist offen.|La ventana está abierta.
Die Tür ist geschlossen.|La puerta está cerrada.
Mein Kaffee ist schon kalt.|Mi café ya está frío.
Die Suppe ist noch heiß.|La sopa todavía está caliente.
Ich bin heute müde.|Hoy estoy cansado.
Du bist immer freundlich.|Siempre eres amable.
Wir haben morgen Zeit.|Tenemos tiempo mañana.
Ich habe leider kein Geld.|Por desgracia, no tengo dinero.
Ich brauche einen Stift.|Necesito un bolígrafo.
Sie kauft Brot und Milch.|Ella compra pan y leche.
Wir trinken keinen Wein.|No bebemos vino.
Er isst gern Reis.|A él le gusta comer arroz.
Ich wohne in Madrid.|Vivo en Madrid.
Du kommst aus Spanien.|Vienes de España.
Wir fahren mit dem Bus.|Vamos en autobús.
Der Zug fährt nach Berlin.|El tren va a Berlín.
Ich komme gerade vom Bahnhof.|Ahora mismo vengo de la estación de tren.
Sie arbeitet im Büro.|Ella trabaja en la oficina.
Das Buch liegt auf dem Tisch.|El libro está sobre la mesa.
Die Tasche liegt unter dem Stuhl.|El bolso está debajo de la silla.
Der Supermarkt ist neben der Bank.|El supermercado está al lado del banco.
Die Apotheke ist gegenüber dem Hotel.|La farmacia está enfrente del hotel.
Ich warte hier auf dich.|Te espero aquí.
Er sitzt vor dem Fenster.|Él está sentado delante de la ventana.
Das Fahrrad steht hinter dem Haus.|La bicicleta está detrás de la casa.
Die Lampe hängt über dem Tisch.|La lámpara cuelga encima de la mesa.
Das Café ist zwischen der Bank und dem Kino.|La cafetería está entre el banco y el cine.
Ich esse oft Obst.|Como fruta a menudo.
Wir kochen manchmal zusammen.|A veces cocinamos juntos.
Sie kommt nie zu spät.|Ella nunca llega tarde.
Ich gehe heute früh ins Bett.|Hoy me voy temprano a la cama.
Wir sehen uns bald.|Nos vemos pronto.
Die Kinder spielen drinnen.|Los niños juegan dentro.
Der Aufzug ist links.|El ascensor está a la izquierda.
Die Treppe ist rechts.|La escalera está a la derecha.
Das Bad ist oben.|El baño está arriba.
Die Küche ist unten.|La cocina está abajo.'''
complex='''Heute lerne ich nach der Arbeit eine Stunde Deutsch.|Hoy estudio alemán una hora después del trabajo.
Am Morgen trinke ich zuerst Wasser und dann Kaffee.|Por la mañana bebo primero agua y después café.
Nach dem Essen gehe ich mit meiner Schwester spazieren.|Después de comer voy a pasear con mi hermana.
Um acht Uhr fahren wir mit dem Zug nach Berlin.|A las ocho vamos en tren a Berlín.
Am Wochenende besuche ich meine Eltern auf dem Land.|El fin de semana visito a mis padres en el campo.
In der Schule spreche ich oft mit meinen Freunden.|En la escuela hablo a menudo con mis amigos.
Seit einer Woche lerne ich jeden Abend Deutsch.|Desde hace una semana estudio alemán todas las tardes.
Bis Freitag bleibe ich bei meiner Freundin.|Me quedo en casa de mi amiga hasta el viernes.
Auf dem Weg zur Schule gehe ich durch den Park.|De camino a la escuela paso por el parque.
Morgen fahre ich ohne meinen Bruder zum Flughafen.|Mañana voy al aeropuerto sin mi hermano.
Ich möchte heute ein neues Buch kaufen.|Hoy me gustaría comprar un libro nuevo.
Kannst du mir bitte mit dieser Aufgabe helfen?|¿Puedes ayudarme con este ejercicio, por favor?
Wir müssen morgen um sieben Uhr aufstehen.|Mañana tenemos que levantarnos a las siete.
Du darfst hier nicht mit dem Fahrrad fahren.|Aquí no puedes ir en bicicleta: no está permitido.
Ich will am Samstag mit meinen Freunden kochen.|El sábado quiero cocinar con mis amigos.
Soll ich dir einen Kaffee bringen?|¿Te traigo un café?
Wir können nach der Arbeit zusammen essen.|Podemos comer juntos después del trabajo.
Ich möchte für meine Mutter ein Geschenk kaufen.|Me gustaría comprar un regalo para mi madre.
Musst du heute bis sechs Uhr arbeiten?|¿Tienes que trabajar hoy hasta las seis?
Können Sie mir bitte den Weg zum Bahnhof zeigen?|¿Puede indicarme el camino a la estación, por favor?
Ich stehe jeden Morgen um halb acht auf.|Me levanto cada mañana a las siete y media.
Nach der Arbeit kaufe ich im Supermarkt ein.|Después del trabajo hago la compra en el supermercado.
Ich rufe dich morgen nach dem Unterricht an.|Te llamo mañana después de clase.
Um neun Uhr fängt der Deutschkurs an.|El curso de alemán empieza a las nueve.
Ich mache vor dem Schlafen das Licht aus.|Apago la luz antes de dormir.
Bitte mach das Fenster in der Küche auf.|Abre la ventana de la cocina, por favor.
Wir räumen am Samstag zusammen die Wohnung auf.|El sábado ordenamos juntos el piso.
Bring bitte etwas Brot und Käse mit.|Trae algo de pan y queso, por favor.
Ich nehme heute einen Regenschirm mit.|Hoy me llevo un paraguas.
Nach dem Essen wasche ich das Geschirr ab.|Después de comer lavo los platos.
Ich trinke Tee, aber meine Schwester trinkt Kaffee.|Yo bebo té, pero mi hermana bebe café.
Wir bleiben zu Hause, denn es regnet draußen.|Nos quedamos en casa porque fuera llueve.
Möchtest du Wasser trinken oder lieber einen Tee?|¿Quieres beber agua o prefieres un té?
Ich kaufe keine Äpfel, sondern zwei Bananen.|No compro manzanas, sino dos plátanos.
Er arbeitet heute und hat nur wenig Zeit.|Él trabaja hoy y tiene poco tiempo.
Der Bus kommt zu spät, deshalb gehe ich zu Fuß.|El autobús llega tarde; por eso voy a pie.
Zuerst mache ich meine Hausaufgaben, dann spiele ich.|Primero hago los deberes; después juego.
Ich bin krank, aber morgen gehe ich wieder zur Schule.|Estoy enfermo, pero mañana vuelvo a la escuela.
Meine Schwester kann auch gut Deutsch sprechen.|Mi hermana también sabe hablar bien alemán.
Ich lerne allein, aber am Abend üben wir zusammen.|Estudio solo, pero por la tarde practicamos juntos.
Ich bleibe heute zu Hause, weil ich krank bin.|Hoy me quedo en casa porque estoy enfermo.
Wir nehmen den Bus, weil unser Auto kaputt ist.|Cogemos el autobús porque nuestro coche está averiado.
Ich lerne Deutsch, weil ich in Deutschland arbeiten möchte.|Aprendo alemán porque me gustaría trabajar en Alemania.
Ich glaube, dass der Supermarkt noch offen ist.|Creo que el supermercado todavía está abierto.
Sie sagt, dass sie heute keine Zeit hat.|Ella dice que hoy no tiene tiempo.
Ich weiß, dass du morgen eine Prüfung hast.|Sé que mañana tienes un examen.
Wenn ich Zeit habe, lese ich ein Buch.|Cuando tengo tiempo, leo un libro.
Wenn es regnet, bleiben wir zu Hause.|Si llueve, nos quedamos en casa.
Ich höre Musik, wenn ich mit dem Bus fahre.|Escucho música cuando voy en autobús.
Kannst du mir sagen, wann der nächste Zug kommt?|¿Puedes decirme cuándo llega el próximo tren?'''
root=Path(__file__).resolve().parents[2];words=[]
for difficulty,(family,text) in enumerate([('01 Frases simples',simple),('02 Frases ampliadas',complex)],1):
 rows=[l.split('|')for l in text.splitlines() if l];assert len(rows)==50,(family,len(rows))
 for i,(de,es) in enumerate(rows,1):words.append({'id':f'phrase-a1-{difficulty}-{i:02d}','deck':'phrases-a1-100','family':f"{(difficulty-1)*5+(i-1)//10+1:02d} · {'Simples' if difficulty==1 else 'Ampliadas'} · {((i-1)//10)*10+1}–{((i-1)//10+1)*10}",'de':de,'es':es,'builtin':'phrases-a1-v1','valid':False,'until':0,'difficulty':difficulty})
assert len(words)==100 and len({w['de']for w in words})==100
(root/'public/lex/phrases.json').write_text(json.dumps({'deck':{'id':'phrases-a1-100','name':'Alemán · 100 frases fáciles','status':'active','builtin':'phrases-a1-v1'},'words':words},ensure_ascii=False,separators=(',',':')))
p=root/'public/lex/theory.json';theory=json.loads(p.read_text())
def add(title,rule,items):
 topic={'title':title,'rule':rule,'items':[s.split('|')for s in items.splitlines() if s]};old=next((i for i,t in enumerate(theory['A1'])if t['title']==title),None)
 if old is None:theory['A1'].append(topic)
 else:theory['A1'][old]=topic
add('Preposiciones de las frases','La traducción depende del contexto. Con in, auf, an, unter, über, vor, hinter, neben y zwischen: dativo para ubicación y acusativo para destino. Estas frases también muestran preposiciones que exigen un caso fijo.', '''aus|de / desde; origen (dativo)
in|en / a; ubicación o destino
mit|con / en un medio de transporte (dativo)
ohne|sin (acusativo)
für|para (acusativo)
nach|hacia / a (ciudades y países sin artículo); después de (dativo)
zu|a / hacia; destino (dativo)
von|de / desde (dativo): vom Bahnhof
bei|en casa de / en el lugar de (dativo)
um|a las…; hora (acusativo)
seit|desde / desde hace (dativo)
bis|hasta; en bis Freitag, sin artículo
auf|sobre / en; auf dem Land = en el campo; warten auf + acusativo = esperar a / por
unter|debajo de
über|encima de; sin contacto en estas frases
vor|delante de / antes de
hinter|detrás de
neben|al lado de
zwischen|entre
an|en / junto a; con días y momentos: am Samstag, am Morgen
durch|por / a través de (acusativo)
gegenüber|enfrente de (dativo)'''.replace('a n|','an|'))
add('Contracciones de preposición y artículo','Las preposiciones pueden unirse al artículo. En estas frases, las siguientes contracciones conservan el caso del artículo.', '''im = in dem|en el / en la; dativo: im Büro
am = an dem|el / por la; dativo: am Samstag, am Morgen
zum = zu dem|al / a; dativo masculino o neutro: zum Bahnhof
vom = von dem|de la / del; dativo: vom Bahnhof
zur = zu der|a la; dativo femenino: zur Schule
ins = in das|al / a; acusativo neutro: ins Bett
zu Hause|en casa; expresión fija
zu Fuß|a pie; expresión fija
auf dem Land|en el campo; expresión fija''')
add('Conjunciones y enlaces de las frases','Und, oder, aber, denn y sondern unen oraciones sin enviar el verbo al final. Weil, dass y wenn introducen subordinadas con el verbo conjugado al final: son una introducción a estructuras posteriores al A1 básico.', '''und|y
oder|o
aber|pero
denn|porque; mantiene el orden de oración principal
sondern|sino; rectifica una negación anterior
weil|porque; verbo conjugado al final
dass|que; introduce una información, verbo al final
wenn|si / cuando; condición o situación repetida, verbo al final
deshalb|por eso; es un adverbio conector: deshalb gehe ich…
dann|después / entonces; adverbio conector: dann spiele ich…''')
add('Adverbios de tiempo y frecuencia de las frases','Los adverbios no se declinan. Si un adverbio o un grupo temporal ocupa el primer lugar, el verbo conjugado va en segundo lugar: Heute lerne ich…', '''gerade|ahora mismo; en Ich komme gerade…
heute|hoy
morgen|mañana; el día siguiente
morgens|por las mañanas; habitualmente
jetzt|ahora
später|más tarde
immer|siempre
oft|a menudo
manchmal|a veces
nie|nunca
früh|temprano
spät|tarde
bald|pronto
jeden Tag|todos los días
jeden Morgen|cada mañana
jeden Abend|cada tarde / noche
am Morgen|por la mañana
am Abend|por la tarde / noche
am Wochenende|el fin de semana
zuerst|primero
dann|después / entonces
wieder|otra vez / de nuevo
noch|todavía; según el contexto también más
schon|ya
halb acht|las siete y media; media hora antes de las ocho''')
add('Adverbios de lugar y modo de las frases','Estos términos añaden información sobre lugar, manera o preferencia. Gern y lieber acompañan normalmente a otro verbo: Ich höre gern Musik.', '''hier|aquí
dort|allí
links|a la izquierda
rechts|a la derecha
oben|arriba
unten|abajo
drinnen|dentro / en el interior
draußen|fuera / al aire libre
zusammen|juntos / conjuntamente
allein|solo; sin compañía
gern|con gusto / me gusta hacer algo
lieber|preferentemente / prefiero
sehr|muy
leider|por desgracia / lamentablemente
auch|también
nur|solo / solamente
zu (ante un adjetivo)|demasiado; zu spät = demasiado tarde
nicht|no; niega acciones, cualidades u otros elementos
gut|bien; en gut Deutsch sprechen''')
add('Otras palabras útiles de las frases','Las formas de artículo, pronombre y posesivo dependen de la función de cada palabra. Se indican aquí los usos que aparecen en el mazo.', '''kein / keine / keinen|ningún / ninguna; negación de sustantivos
etwas|algo de / algo
wenig|poco / poca; cantidad
bitte|por favor
mir|me / a mí; dativo: Kannst du mir helfen?
dir|te / a ti; dativo: Soll ich dir einen Kaffee bringen?
dich|te / a ti; acusativo: Ich warte auf dich
uns|nos; Wir sehen uns bald = nos vemos pronto
Sie|usted / ustedes; tratamiento formal, con mayúscula
mein / meine / meinen / meiner|formas de mi, según caso, género y número
dieser|esta; dativo femenino en mit dieser Aufgabe
ein neues Buch|un libro nuevo; el adjetivo lleva una terminación
nächste / nächsten|próximo; formas de nächste en der nächste Zug y den nächsten Zug
unser|nuestro; unser Auto
wann|cuándo; interrogativa indirecta: wann der Zug kommt
weil … arbeiten möchte|porque … me gustaría trabajar; infinitivo antes del modal al final''')
add('Estructuras de las 100 frases','Las 50 frases simples presentan acciones, ubicación, frecuencia y negación. Las 50 ampliadas incorporan complementos, modales, verbos separables y enlaces. Las diez últimas introducen subordinadas sencillas como puente hacia A2.', '''Heute lerne ich nach der Arbeit Deutsch.|Hoy estudio alemán después del trabajo. Verbo en segunda posición.
Ich möchte ein Buch kaufen.|Me gustaría comprar un libro. Modal y verbo al final.
Ich stehe um halb acht auf.|Me levanto a las siete y media. Prefijo separable al final.
Wir bleiben zu Hause, denn es regnet.|Nos quedamos en casa porque llueve. Denn no altera el orden.
Ich bleibe zu Hause, weil ich krank bin.|Me quedo en casa porque estoy enfermo. Bin al final.
Wenn es regnet, bleiben wir zu Hause.|Si llueve, nos quedamos en casa. Tras la subordinada va bleiben.
Kannst du mir sagen, wann der Zug kommt?|¿Puedes decirme cuándo llega el tren? Interrogativa indirecta con kommt al final.''')
p.write_text(json.dumps(theory,ensure_ascii=False,separators=(',',':')))
print('100 sentences created; 50 simple and 50 expanded; added 7 A1 reference topics.')
