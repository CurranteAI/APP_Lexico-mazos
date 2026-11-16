"""Build the grammar deck from the existing theory and word-only audio manifest."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

TRANSLATIONS = {
    'Interrogativos': 'dónde|de dónde|adónde|cuándo|cómo|por qué|qué|quién|a quién (acusativo)|a quién (dativo)|de quién|cuánto|cuántos/cuántas|qué/cuál (masculino)|qué/cuál (femenino)|qué/cuál (neutro)',
    'Pronombres acusativo': 'me/a mí|te/a ti|lo/a él|la/a ella|lo (neutro)|nos/a nosotros|os/a vosotros|los/las/a ellos o ellas|a usted/ustedes (acusativo)',
    'Pronombres dativo': 'me/a mí|te/a ti|le/a él|le/a ella|nos/a nosotros|os/a vosotros|les/a ellos o ellas|le/les/a usted o ustedes',
    'Determinantes y cantidad': 'ningún (masculino o neutro)|ninguna|este|esta|este (neutro)|cada (masculino)|cada (femenino)|cada (neutro)|todos/todas|muchos/muchas|algunos/algunas|algo/un poco de|nada|todo',
    'Posesivos': 'mi (masculino o neutro)|mi (femenino o plural)|tu (masculino o neutro)|tu (femenino o plural)|su (de él; masculino o neutro)|su (de él; femenino o plural)|su (de ella; masculino o neutro)|su (de ella; femenino o plural)|nuestro (masculino o neutro)|nuestra/nuestros/nuestras|vuestro (masculino o neutro)|vuestra/vuestros/vuestras|su (de ellos; masculino o neutro)|su (de ellos; femenino o plural)|su (de usted/ustedes; masculino o neutro)|su (de usted/ustedes; femenino o plural)',
    'Preposiciones': 'de/desde (origen)|en casa de/junto a|con|a/hacia|de (procedencia o pertenencia)|a/hacia|para|sin|a las/alrededor de|hasta|por/a través de|contra|en/dentro de|en/junto a|sobre/encima de|debajo de|sobre/por encima de|delante de/antes de|detrás de|al lado de|entre',
    'Conectores y contracciones': 'y|o|pero|porque|sino|por eso|porque|si/cuando|en el (in + dem)|el/en el (an + dem)|al (zu + dem)|a la (zu + der)|del (von + dem)|al/dentro del (in + das)',
    'Tiempo y frecuencia': 'hoy|mañana|ayer|ahora|más tarde|temprano|tarde|siempre|a menudo|a veces|pocas veces/raramente|nunca|otra vez|ya|todavía|primero|después/entonces|pronto|ahora mismo|por las mañanas|por las tardes/noches',
    'Lugar y modo': 'aquí|allí|ahí|a la izquierda|a la derecha|arriba|abajo|dentro|fuera|juntos|solo/a|con gusto (gustar hacer algo)|preferentemente (preferir)|muy|demasiado|también|solo/solamente|lamentablemente|quizá/tal vez',
    'Negación y partículas': 'no|sí|no|sí que sí (frente a una negación)|por favor|gracias|más|menos|suficiente|tan/así',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio_source', type=Path, help='Folder containing manifest.json and MP3s')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((args.audio_source / 'manifest.json').read_text(encoding='utf-8'))
    theory = json.loads((root / 'teoria/gramatica.json').read_text(encoding='utf-8'))
    sections = {s['title']: s['items'] for s in theory['sections']['Gramática']}
    audio = {a['text']: a for a in manifest['audio']}
    words = []
    for group, tokens in manifest['groups'].items():
        phrases = sections[group] if group != 'Conectores y contracciones' else sections['Conectores'] + sections['Contracciones']
        translations = TRANSLATIONS[group].split('|')
        assert len(tokens) == len(phrases) == len(translations), group
        slug = re.sub(r'[^a-z]+', '-', group.lower()).strip('-')
        for index, (word, (phrase, _), es) in enumerate(zip(tokens, phrases, translations), 1):
            pattern = re.compile(r'(?<!\w)' + re.escape(word) + r'(?!\w)', re.I)
            marked, count = pattern.subn(lambda m: '[[' + m[0] + ']]', phrase, count=1)
            assert count == 1, (word, phrase)
            clip = audio[word.lower()]
            source = args.audio_source / clip['file']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == clip['sha256'], word
            target = root / 'audio' / clip['file']
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
            words.append({'id': f'grammar-{slug}-{index:02}', 'family': group, 'de': word,
                          'es': es, 'phrase': marked, 'contextMode': 'word', 'audio': 'audio/' + clip['file']})
    pack = {'format': 'lexico-mazo', 'version': 1, 'deck': {'id': 'gramatica', 'name': 'Gramática', 'status': 'active'}, 'words': words}
    (root / 'decks/gramatica.json').write_text(json.dumps(pack, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    catalog_file = root / 'catalog.json'
    catalog = json.loads(catalog_file.read_text(encoding='utf-8'))
    item = {'kind': 'deck', 'id': 'gramatica', 'name': 'Gramática',
            'description': '148 tarjetas en 10 submazos. Frase de apoyo hasta acertar; vuelve tras un fallo. Audio de cada palabra.',
            'file': 'decks/gramatica.json', 'words': len(words), 'version': 1}
    catalog['items'] = [i for i in catalog['items'] if not (i['kind'] == 'deck' and i['id'] == 'gramatica')] + [item]
    catalog['updated'] = '2026-11-16'
    catalog_file.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (root / 'audio/grammar-voice.json').write_text(json.dumps({'provider': manifest['provider'], 'voice': manifest['voice'], 'rate': manifest['rate'], 'audio': manifest['audio']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(words)} cards in {len(manifest["groups"])} families; {len(audio)} MP3s.')


if __name__ == '__main__':
    main()
