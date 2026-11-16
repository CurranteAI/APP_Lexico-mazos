"""Build additive corrected decks and resumable Microsoft Tanja audio assets."""
import asyncio
import hashlib
import json
import shutil
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
VOICE = 'de-DE-TanjaNeural'
RATE = '-10%'
GENDERS = {'der': 'm', 'die': 'f', 'das': 'n'}
ADDITIONAL_NOUNS = [
    ('Morgen', 'der', 'la mañana (parte del día)', 'Morgen_Tageszeit'),
    ('Tag', 'der', 'el día', 'Tag_Zeiteinheit'),
    ('Abend', 'der', 'la tarde / la noche (antes de acostarse)', 'Abend'),
    ('Nacht', 'die', 'la noche', 'Nacht'),
    ('Wiedersehen', 'das', 'el reencuentro / volver a verse', 'Wiedersehen'),
    ('Entschuldigung', 'die', 'la disculpa / el perdón', 'Entschuldigung'),
    ('Hilfe', 'die', 'la ayuda', 'Hilfe'),
]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def audio_path(text):
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()[:24]
    return 'audio/tanja-correccion-' + digest + '.mp3'


def corrected(source_file):
    source = read_json(ROOT / source_file)
    original_id = source['deck']['id']
    result = json.loads(json.dumps(source))
    result['deck']['id'] = original_id + '-correccion'
    result['deck']['name'] = source['deck']['name'] + '_corrección'
    result['sourceDeck'] = original_id
    result['audioVoice'] = VOICE
    result['audioRate'] = RATE
    result['audioProvider'] = 'Microsoft Edge text-to-speech via edge-tts'
    for word in result['words']:
        word['sourceWord'] = word['id']
        word['id'] += '-correccion'
    return result


def build_decks():
    nouns = corrected('decks/nouns-a1-100.json')
    for word in nouns['words']:
        article, lemma = word['de'].split(' ', 1)
        if article not in GENDERS:
            raise ValueError('Unexpected noun article: ' + word['de'])
        word.update(article=article, gender=GENDERS[article], lemma=lemma)

    basics = corrected('decks/a1.json')
    for word in basics['words']:
        if word['family'] != 'Artículos':
            continue
        article, lemma = word['de'].split(' ', 1)
        gender = {'Mann': 'm', 'Frau': 'f', 'Kind': 'n', 'Kinder': 'n'}[lemma]
        word.update(article=article, gender=gender, lemma='Kind' if lemma == 'Kinder' else lemma)
        if lemma == 'Kinder':
            word['number'] = 'plural'
            word['es'] += ' (plural de das Kind; género neutro)'

    for lemma, article, es, reference in ADDITIONAL_NOUNS:
        basics['words'].append({
            'id': 'a1-noun-' + lemma.lower() + '-correccion',
            'family': 'Sustantivos de las expresiones',
            'de': article + ' ' + lemma,
            'es': es,
            'lemma': lemma,
            'article': article,
            'gender': GENDERS[article],
            'source': 'https://www.duden.de/rechtschreibung/' + reference,
        })

    result = [('decks/a1_correccion.json', basics), ('decks/nouns-a1-100_correccion.json', nouns)]
    for _, deck in result:
        for word in deck['words']:
            word['audio'] = audio_path(word['de'])
    return result


async def main():
    decks = build_decks()
    texts = sorted({w['de'] for _, deck in decks for w in deck['words']})
    (ROOT / 'audio').mkdir(exist_ok=True)
    # Reuse only clips whose manifest explicitly identifies the same voice and rate.
    cache_dir = ROOT.parent / 'GEMINI/gramatica_audio' / VOICE
    manifest_path = cache_dir / 'manifest.json'
    reuse = {}
    if manifest_path.is_file():
        cached = read_json(manifest_path)
        if cached.get('voice') == VOICE and cached.get('rate') == RATE:
            reuse = {a['text']: a for a in cached.get('audio', [])}
    reused = 0
    for text in texts:
        entry = reuse.get(text)
        if not entry:
            continue
        source = cache_dir / entry['file']
        target = ROOT / audio_path(text)
        if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == entry.get('sha256'):
            if not target.exists():
                shutil.copyfile(source, target)
                reused += 1
    sample = ROOT / 'audio/tanja-prueba.mp3'
    if sample.exists():
        sample.replace(ROOT / audio_path('die Entschuldigung'))
    semaphore = asyncio.Semaphore(2)
    completed = 0
    failures = []
    print(f'{len(texts)} distinct clips; {reused} reused from verified Tanja manifest.', flush=True)

    async def generate(text):
        nonlocal completed
        async with semaphore:
            target = ROOT / audio_path(text)
            if not target.exists() or target.stat().st_size < 1000:
                for attempt in range(4):
                    temp = target.with_suffix('.part')
                    try:
                        await asyncio.wait_for(edge_tts.Communicate(text, VOICE, rate=RATE).save(str(temp)), timeout=40)
                        if temp.stat().st_size < 1000:
                            raise ValueError('Empty or truncated synthesis')
                        temp.replace(target)
                        break
                    except Exception as exc:
                        if attempt == 3:
                            failures.append({'text': text, 'error': str(exc)})
                        else:
                            await asyncio.sleep(2 * (attempt + 1))
            completed += 1
            if completed % 20 == 0 or completed == len(texts):
                print(f'{completed}/{len(texts)} clips processed; {len(failures)} failures.', flush=True)

    await asyncio.gather(*(generate(text) for text in texts))
    if failures:
        write_json(ROOT / 'herramientas/correction-audio-failures.json', failures)
        raise RuntimeError(f'{len(failures)} audio files could not be created; decks/catalog not written.')

    clips = []
    for text in texts:
        filename = audio_path(text)
        path = ROOT / filename
        clips.append({'text': text, 'file': filename, 'bytes': path.stat().st_size,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    for filename, deck in decks:
        write_json(ROOT / filename, deck)
    catalog = read_json(ROOT / 'catalog.json')
    ids = {deck['deck']['id'] for _, deck in decks}
    catalog['items'] = [i for i in catalog['items'] if i['id'] not in ids]
    for filename, deck in decks:
        catalog['items'].append({
            'kind': 'deck', 'id': deck['deck']['id'], 'name': deck['deck']['name'],
            'description': ('Copia con artículos, género y audios Microsoft Tanja. '
                            + ('Conserva las 168 tarjetas y añade 7 sustantivos de las expresiones.'
                               if deck['sourceDeck'] == 'a1' else 'Conserva los 100 sustantivos originales.')),
            'file': filename, 'words': len(deck['words']), 'version': 1,
        })
    catalog['updated'] = '2026-11-16'
    write_json(ROOT / 'catalog.json', catalog)
    write_json(ROOT / 'herramientas/correction-audio-manifest.json', {
        'voice': VOICE, 'rate': RATE, 'provider': 'Microsoft Edge via edge-tts',
        'decks': [filename for filename, _ in decks], 'audio': clips,
    })
    print('Completed: two corrected decks and catalog ready.', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
