import csv
import sys
import re
import jiwer
from num2words import num2words
from tqdm import tqdm
from torchmetrics.text import CharErrorRate
from decimal import Decimal, InvalidOperation
import argparse

alphabet = 'abcdefghijklmnopqrstuvwxyzáéíóúâêîôûãõàèìòùç '

spontaneous_expressions = ["tá", "né", "ué", "tipo", "poxa", "pô", 
                           "daí", "aí", "hein", "aham", "ixi",  
                           "puxa", "ô", "caraca", "opa", "beleza", 
                           "vixe", "eita", "ó", "eh"]

def normalize(phrase):
    phrase = phrase.lower()
    new_words = []
    for word in phrase.split():
        word = re.sub(r"\d+[%]", lambda x: x.group() + " por cento", word)
        word = re.sub(r"%", "", word)
        
        # controle de erros
        try:
            word = re.sub(r"\d+[o]{1}", lambda x: num2words(x.group()[:-1], to='ordinal', lang='pt_BR'), word)
        except (OverflowError, InvalidOperation, ValueError):
            pass

        ref = word
        try:
            word = re.sub(r"\d+[a]{1}", lambda x: num2words(x.group()[:-1], to='ordinal', lang='pt_BR'), word)
        except (OverflowError, InvalidOperation, ValueError):
            pass

        if word != ref:
            segs = word.split(' ')
            word = ''
            for seg in segs:
                word = word + seg[:-1] + 'a' + ' '
            word = word[:-1]

        if any(i.isdigit() for i in word):
            segs = re.split(r"[?.!\s]", word)
            word = ''
            for seg in segs:
                try:
                    if seg.isnumeric() and abs(int(seg)) < 10**15:  # limite de valor
                        seg = num2words(seg, lang='pt_BR')
                except (OverflowError, InvalidOperation, ValueError):
                    continue  # pula segmentação problemática
                word = word + seg + ' '
            word = word[:-1]
        new_words.append(word)

    phrase = ' '.join(new_words)
    
    for c in phrase:
        if c not in alphabet:
            phrase = phrase.replace(c, '')

    return phrase

def calculate_cer(ground_truth, transcription):
    cer = CharErrorRate()
    ground_truth = normalize(ground_truth)
    transcription = normalize(transcription)
    if not ground_truth or not transcription:
        return None
    cer.update([transcription], [ground_truth])
    return cer.compute().item()

def add_expression(phrase_wo_expr, phrase_w_expr, expression):
    how_many_expr = phrase_w_expr.split().count(expression)
    cer = jiwer.cer(normalize(phrase_wo_expr), normalize(phrase_w_expr))
    for i in range(how_many_expr):
        phrase_wo_expr_split = phrase_wo_expr.split()
        for j in range(len(phrase_wo_expr_split)):
            temp = phrase_wo_expr_split.copy()
            temp.insert(j, f'<{expression}>')
            temp = ' '.join(temp)
            if jiwer.wer(normalize(temp), normalize(phrase_w_expr)) < jiwer.wer(normalize(phrase_wo_expr), normalize(phrase_w_expr)):
                phrase_wo_expr = temp.replace(' ,', ',').replace(' .', '.').replace(' ?', '?').replace(' !', '!')
                cer = jiwer.cer(normalize(temp), normalize(phrase_w_expr))
    return phrase_wo_expr

def is_empty_row(row, column1, column2):
    try:
        return not normalize(row[column1]).strip() or not normalize(row[column2]).strip()
    except KeyError:
        return True 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Processamento de transcrições e cálculo de CER")
    parser.add_argument("input_file", type=str, help="Caminho do arquivo CSV de entrada")
    parser.add_argument("output_file", type=str, help="Caminho do arquivo CSV de saída")
    parser.add_argument("column1", type=str, help="Nome da coluna contendo a transcrição de referência")
    parser.add_argument("column2", type=str, help="Nome da coluna contendo a transcrição a ser analisada")
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as in_f, open(args.output_file, 'w', encoding='utf-8') as out_f:
        reader = csv.DictReader(in_f, delimiter='|')
        print("Column names:", reader.fieldnames)
        fieldnames = reader.fieldnames + ['cer-antigo', 'cer-novo']
        writer = csv.DictWriter(out_f, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()

        for row in tqdm(reader):
            if is_empty_row(row, args.column1, args.column2):
                continue

            try:
                cer_antigo = calculate_cer(row[args.column1], row[args.column2])
                if cer_antigo is None:
                    continue

                row['cer-antigo'] = cer_antigo

                for expression in spontaneous_expressions:
                    if f' {expression} ' in row[args.column2] or f'{expression} ' in row[args.column2] or f' {expression}' in row[args.column2]:
                        row[args.column1] = add_expression(row[args.column1], row[args.column2], expression)

                cer_novo = calculate_cer(row[args.column1], row[args.column2])
                if cer_novo is None:
                    continue

                row['cer-novo'] = cer_novo
                writer.writerow(row)
            except (OverflowError, InvalidOperation, ValueError, KeyError):
                continue
