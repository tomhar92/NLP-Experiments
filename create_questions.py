from flair.data import Sentence
from flair.models import SequenceTagger
from segtok.segmenter import split_single
import wikipedia
from pymongo import MongoClient

client = MongoClient('mongodb://***/wikitrivia')
tagger = SequenceTagger.load('ner')
db = client.wikitrivia
db_questions = db.questions
ready_questions = []
for q in db_questions.find():
    ready_questions.append(q["question"])

inserted = 0
while inserted < 1000:
    sentences = []
    try:
        defi = wikipedia.random(pages=1)
        print(defi)
        defi_question = 0
        content = wikipedia.WikipediaPage(defi).content
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(content)]
        tagger.predict(sentences)
    except Exception as e:
        print("Error: " + str(e))
    for sent in sentences:
        sent_dict = sent.to_dict(tag_type='ner')
        for entity in sent_dict['entities']:
            question = ''
            print(entity)
            if entity['confidence'] > 0.9:
                if entity['type'] == 'LOC':
                    question = 'Where is ' +entity['text']+'?'
                elif entity['type'] == 'PER':
                    question = 'Who is ' +entity['text']+'?'
                else:
                    question = 'What is '+entity['text']+'?'
                if question not in ready_questions:
                    defi_question = defi_question + 1
                    question_id = defi + '_' +str(defi_question)
                    question_dict = {"_id": question_id, "question": question, "answer": ""}
                    try:
                        db_questions.insert_one(question_dict)
                        ready_questions.append(question)
                        print("inserted successfully")
                        inserted = inserted + 1
                    except Exception as e:
                        print("Error inserting to DB: " + str(e))

