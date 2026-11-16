"""Validate corrected deck data and decode every generated audio before publication."""
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_REF = os.environ.get('LEXICO_BASE_REF', 'HEAD')


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def original(path):
    return json.loads(subprocess.check_output(['git', 'show', BASE_REF + ':' + path], cwd=ROOT))


def check_audio(entry):
    filename = ROOT / entry['file']
    data = filename.read_bytes()
    assert len(data) == entry['bytes']
    assert hashlib.sha256(data).hexdigest() == entry['sha256']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,sample_rate',
        '-of', 'json', str(filename),
    ]))
    assert probe['streams'][0]['codec_name'] == 'mp3'
    assert probe['streams'][0]['sample_rate'] == '24000'
    assert .1 < float(probe['format']['duration']) < 30
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(filename), '-f', 'null', '-'],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return float(probe['format']['duration'])


def main():
    protected = ['decks/a1.json', 'decks/nouns-a1-100.json',
                 'decks/phrases-a1-100.json', 'decks/verbs-40.json', 'teoria/gramatica.json']
    subprocess.run(['git', 'diff', '--exit-code', BASE_REF, '--', *protected], cwd=ROOT, check=True)
    catalog, before = load('catalog.json'), original('catalog.json')
    for item in before['items']:
        assert next(i for i in catalog['items'] if i['id'] == item['id'] and i['kind'] == item['kind']) == item
    assert len(catalog['items']) == len(before['items']) + 2
    old_ids = {w['id'] for p in protected if p.startswith('decks/') for w in load(p)['words']}
    manifest = load('herramientas/correction-audio-manifest.json')
    assert manifest['voice'] == 'de-DE-TanjaNeural'
    assert manifest['rate'] == '-10%'
    audio = {a['file']: a for a in manifest['audio']}
    ids, references = set(), set()
    for path, count in [('decks/a1_correccion.json', 175), ('decks/nouns-a1-100_correccion.json', 100)]:
        deck = load(path)
        source = original('decks/' + deck['sourceDeck'] + '.json')
        assert deck['deck']['name'] == source['deck']['name'] + '_corrección'
        assert deck['deck']['id'] != source['deck']['id']
        assert len(deck['words']) == count
        item = next(i for i in catalog['items'] if i['file'] == path)
        assert item['words'] == count and item['id'] == deck['deck']['id']
        for word in deck['words']:
            assert word['id'] not in old_ids and word['id'] not in ids
            ids.add(word['id'])
            assert re.fullmatch(r'audio/[\w.-]+\.mp3', word['audio'])
            assert audio[word['audio']]['text'] == word['de']
            references.add(word['audio'])
            if word.get('gender'):
                assert word['gender'] in ('m', 'f', 'n')
                assert word['article'] == word['de'].split(' ', 1)[0]
                if word.get('number') == 'plural':
                    assert word['lemma'] == 'Kind' and word['gender'] == 'n'
                elif word['article'] in ('der', 'die', 'das'):
                    assert word['gender'] == {'der': 'm', 'die': 'f', 'das': 'n'}[word['article']]
        if deck['sourceDeck'] == 'nouns-a1-100':
            assert all(w.get('gender') in ('m', 'f', 'n') for w in deck['words'])
            assert [(w['de'], w['es']) for w in deck['words']] == [(w['de'], w['es']) for w in source['words']]
        else:
            for old, new in zip(source['words'], deck['words'][:168]):
                assert old['de'] == new['de']
                assert old['es'] == new['es'] or old['de'] == 'die Kinder'
    assert references == set(audio)
    assert len(audio) == 269 and len(ids) == 275
    assert {str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'audio').glob('tanja-correccion-*.mp3')} == references
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        durations = list(executor.map(check_audio, audio.values()))
    print(f'PASS: 275 independent cards, 269 complete Tanja MP3s ({sum(durations):.1f} seconds), '
          'articles/gender, catalog, and unchanged originals.', flush=True)


if __name__ == '__main__':
    main()
