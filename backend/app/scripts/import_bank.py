"""
Банк заданий из data/bank/bank.json (собирает app.bankgen.build) → база и хранилище файлов.

    python -m app.scripts.import_bank              # добавить новые и обновить изменившиеся задания
    python -m app.scripts.import_bank --keep-demo  # не скрывать задания демо-банка (external_source = frontend_bank)

Повторный запуск безопасен: задание ищется по (external_source, external_id) и обновляется на месте,
id сохраняется — на него ссылаются ответы учеников и наборы.

  • задания ФИПИ: external_source = 'fipi', источник «ФИПИ», картинки ФИПИ → storage fipi/<файл>;
  • аналоги: external_source = 'bankgen', источник «Банк школы», наши SVG → storage bank/<файл>.
"""
import argparse
import asyncio
import json
import re
from pathlib import Path

from sqlalchemy import delete, select, update

from app.db.database import new_session
from app.db.enums import AnswerType, FileKind, Subject
from app.db.models import ExamNumberModel, SourceModel, TaskFileModel, TaskModel, TopicModel
from app.services.storage import save

DATA = Path(__file__).resolve().parents[2] / 'data'
BANK = DATA / 'bank'
FIPI_PNG = DATA / 'bank' / 'fipi'
SOURCES = {'fipi': 'ФИПИ', 'gen': 'Банк школы'}
EXTERNAL = {'fipi': 'fipi', 'gen': 'bankgen'}
DEMO_SOURCE = 'frontend_bank'


GREEK_TEX = {'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'φ': '\\varphi', 'ω': '\\omega', 'σ': '\\sigma', 'ε': '\\varepsilon',
             'υ': '\\nu', 'ν': '\\nu', 'τ': '\\tau', 'λ': '\\lambda', 'μ': '\\mu', 'ρ': '\\rho', 'π': '\\pi', 'Δ': '\\Delta'}


def _tex_fixes(text: str) -> str:
    """Исправления формул ФИПИ для KaTeX: греческие буквы из \\text{…}, \\frac без скобок, «\\text» без аргумента"""
    def greek(m: re.Match) -> str:
        inner = m.group(1)
        if all(ch in GREEK_TEX or ch.isdigit() or ch == ' ' for ch in inner):
            return ''.join(GREEK_TEX.get(ch, ch) + (' ' if ch in GREEK_TEX else '') for ch in inner.strip()).strip() + ' '
        return m.group(0)
    text = re.sub(r'\s*\$\ufffd\$\s*', 'о', text)   # «бо $�$ ьшую» у ФИПИ — ударная «о» в формуле
    text = text.replace("$№$", "№")
    text = re.sub(r'\*(\$[^$]+\$[.,;:]?)\*', r' \1', text)   # «что*$AT:TD=2:1$.*» — курсив вокруг формулы у ФИПИ
    text = re.sub(r'(?<=[а-яё])\*([A-ZА-Я][^*\s]{0,3})\*', r' *\1*', text)   # «точку*Т*» → «точку *Т*»
    text = re.sub(r'\\text\{([^{}]*)\}', greek, text)
    text = re.sub(r'\\frac([a-zA-Z])([a-zA-Z0-9])', r'\\frac{\1}{\2}', text)
    text = re.sub(r'\\frac([a-zA-Z0-9])\{', r'\\frac{\1}{', text)
    return re.sub(r'\\text(?![a-zA-Z{])', '', text)


LOOKALIKE = str.maketrans('АВСЕКМНОРТХаеоср', 'ABCEKMHOPTXaeocp')


def _subscripts(text: str) -> str:
    """«*АВ* $_{1}$» у ФИПИ (буквы курсивом, индекс отдельной формулой) → «$AB_{1}$»"""
    text = re.sub(r'\*([A-Za-zА-Яа-яЁё]{1,4})\*\s*\$_\{(\w+)\}\$',
                  lambda m: '$' + m.group(1).translate(LOOKALIKE) + '_{' + m.group(2) + '}$', text)
    return re.sub(r'\}\$\$([A-Za-z])', r'}\1', text)   # «$AB_{1}$$C_{1}$» → «$AB_{1}C_{1}$»


def _links(text: str) -> str:
    text = _tex_fixes(_subscripts(text))
    # картинка посреди строки — формула (alt «formula» делает её строчной во фронтенде), в начале абзаца — рисунок
    text = re.sub(r'(?<=[^\n])!\[\]\(fipi://', '![formula](fipi://', text)
    # картинки ФИПИ — прозрачные PNG из app/bankgen/transparent.py
    text = re.sub(r'fipi://([^)\s]+)\.\w+', lambda m: f'storage://fipi/{m.group(1)}@2x.png', text)
    return text.replace('figure://', 'storage://bank/')


def _png(name: str) -> str:
    return name.rsplit('.', 1)[0] + '@2x.png'


def _solution(text: str) -> str:
    """Последний абзац «**Ответ:** …» не храним: карточка задания показывает ответ отдельной строкой"""
    return re.sub(r'\n*\*\*Ответ:\*\*[^\n]*\s*$', '', _links(text)).rstrip()


async def _topics(session) -> dict[tuple[int, str], TopicModel]:
    rows = (await session.execute(select(TopicModel).where(TopicModel.subject == Subject.math, TopicModel.parent_id.is_(None)))).scalars()
    return {(t.task_number, t.name): t for t in rows}


async def run(keep_demo: bool) -> None:
    entries = json.loads((BANK / 'bank.json').read_text(encoding='utf-8'))
    # файлы — один раз, до транзакции
    for name in {f for e in entries for f in e['fipi_images']}:
        save(f'fipi/{_png(name)}', (FIPI_PNG / _png(name)).read_bytes())
    for name in {f for e in entries for f in e['figures']}:
        save(f'bank/{name}', (BANK / 'figures' / name).read_bytes())

    async with new_session() as session:
        scores = dict((await session.execute(
            select(ExamNumberModel.number, ExamNumberModel.max_score).where(ExamNumberModel.subject == Subject.math)
        )).all())
        sources = {}
        for key, name in SOURCES.items():
            source = (await session.execute(select(SourceModel).where(SourceModel.name == name))).scalar_one_or_none()
            if source is None:
                source = SourceModel(name=name)
                session.add(source)
            sources[key] = source
        topics = await _topics(session)
        positions = {}

        existing = {(t.external_source, t.external_id): t for t in (await session.execute(
            select(TaskModel).where(TaskModel.external_source.in_(list(EXTERNAL.values())))
        )).scalars()}
        created = updated = 0
        for e in entries:
            key = (e['number'], e['topic'])
            if key not in topics:
                positions[e['number']] = positions.get(e['number'], 200) + 1   # после тем демо-банка
                topic = TopicModel(subject=Subject.math, task_number=e['number'], name=e['topic'], position=positions[e['number']])
                session.add(topic)
                await session.flush()
                topics[key] = topic
            fields = dict(
                subject=Subject.math, task_number=e['number'], part=1 if e['number'] <= 12 else 2,
                difficulty=e['difficulty'], topic_id=topics[key].id, condition=_links(e['condition']),
                answer_type=AnswerType(e['answer_type']), answer=e['answer'], max_score=scores.get(e['number'], 1),
                solution=_solution(e['solution']), raw={'template': e['template'], 'origin': e.get('origin')}, is_active=True,
            )
            ext = (EXTERNAL[e['source']], e['external_id'])
            task = existing.get(ext)
            if task is None:
                task = TaskModel(**fields, external_source=ext[0], external_id=ext[1], sources=[sources[e['source']]])
                session.add(task)
                created += 1
            else:
                for k, v in fields.items():
                    setattr(task, k, v)
                updated += 1
            await session.flush()
            # файлы-картинки условия и решения
            await session.execute(TaskFileModel.__table__.delete().where(TaskFileModel.task_id == task.id))
            files = [f'fipi/{_png(n)}' for n in e['fipi_images']] + [f'bank/{n}' for n in e['figures']]
            for pos, storage_key in enumerate(files):
                session.add(TaskFileModel(task_id=task.id, kind=FileKind.image, storage_key=storage_key,
                                          filename=storage_key.rsplit('/', 1)[-1], position=pos))

        # темы банка (позиции после 200), оставшиеся без заданий после переразбиения на подтемы, — убираем из фильтра
        used = select(TaskModel.topic_id).where(TaskModel.topic_id.is_not(None))
        await session.execute(delete(TopicModel).where(
            TopicModel.subject == Subject.math, TopicModel.position > 200, TopicModel.id.not_in(used)))

        if not keep_demo:
            # демо-задания из заглушки фронтенда скрываем из банка: на них могут ссылаться ДЗ, поэтому не удаляем
            await session.execute(update(TaskModel).where(TaskModel.external_source == DEMO_SOURCE).values(is_active=False))
        await session.commit()
    print(f'банк: добавлено {created}, обновлено {updated}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep-demo', action='store_true')
    asyncio.run(run(parser.parse_args().keep_demo))


if __name__ == '__main__':
    main()
