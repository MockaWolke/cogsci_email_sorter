from joblib import dump, load
import pandas as pd
import numpy as np


model = load('gradient_booster.model')
labels = np.array(["Important", "VP_Hours", 'Job_Advertisemnts'])


vp_counts = ['experiment', 'study', 'studie', 'amazon', 'vp', 'stunde', 'hour','numbers']

def get_vp_score(text):

    

    text = text.lower()

    counts = [text.count(w) for w in vp_counts[:-1]]


    number_count = 0

    pos = text.find('vp')

    while pos != -1:

        pos = text.find('vp',pos + 1)

        window_before = text[max(0,pos -  10): pos]
        for c in window_before:
            number_count += c.isnumeric()

    counts.append(number_count)

    return counts


job_count_words = ['hiwi','job','praktikum','intern','internship','praktikant','program','phd',
    'thesis','projects', 'position','offer',
    'doctoral','tutors','hilfskr','stelle','ausschreibung']
def get_job_score(text):

    text = text.lower()

    


    return [text.count(w) for w in job_count_words]


def data_pipe_line(texts):

    return np.array([get_job_score(t) + get_vp_score(t) for t in texts])




def get_email_predictions(email_texts):


    vals = data_pipe_line(email_texts)


    prediction = model.predict(vals) 


    return labels[prediction]

    