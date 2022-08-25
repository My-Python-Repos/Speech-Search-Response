from django.shortcuts import render
from django.http import JsonResponse
import json
import csv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import PyPDF2
import re
import sounddevice as sd
import wavio as wv
import speech_recognition as sr
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import os
from os import listdir
from os.path import isfile, join
import time
import pandas as pd
import spacy
import subprocess
from time import sleep
from django.utils.safestring import mark_safe
import time
import pickle5 as pickle

key = "*****"   # Azure resource secret key to be supplied here
endpoint = "https://*****.azure.com/"   # Azure Speech Analytics resource endpoint to be supplied here


# This function renders the landing webpage 
def test(request):
    return render(request, 'test.html')


# This function calls other important functions of the utility and displays the final results on the webpage
def nlp_func(request):
    record()
    speechrecognition()
    client = authenticate_client()
    keyphrases = key_phrase_extraction(client)  
    # keyphrases = ['medical insurance', 'family need', 'insurance', 'covid', 'telehealth services'] (sample list of keyphrases)
    keysentence = ' '.join(word for word in keyphrases)
    keywords = keysentence.split(' ')
    print(keywords)
    result = driver_function(keyphrases, keywords)
    return render(request, 'result.html', {'result': result})


# This function records the user's voice using the computer's audio port
def record():
    print("\n**Recording Audio**")
    freq = 44100
    duration = 10
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
    sd.wait()
    wv.write("audio/recording.wav", recording, freq, sampwidth=2)   # Saves the voice recording as a .wav file
    print("Recording Saved Successfully")


# This function converts the recorded audio into text
def speechrecognition():
    print("\n**Converting Audio to Text**")
    r = sr.Recognizer()
    audio_file = sr.AudioFile(
        'audio/recording.wav')
    # speech recognition
    with audio_file as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source)
    result = r.recognize_google(audio)  # Uses google's speechrecognition API to transcribe audio

    with open('text/recording_text.txt', mode='w') as file: # Saves the converted text into a .txt file
        file.write(result)
        print("Audio Converted Successfully")
        global text
        text = result
        print("Speech to Text =>", text)


# This function authenticates the Microsoft Azure client credentials - key & endpoint
def authenticate_client():
    try:
        print("\n**Authenticating Client**")
        ta_credential = AzureKeyCredential(key)
        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=ta_credential)
        print("Client Authenticated Successfully")
        return text_analytics_client
    except Exception as e:
        print("Client Authentication Failed")
        print(e)
        return False


# This function hits the Azure Speech Analytics API to extract the keyphrases from the text
def key_phrase_extraction(client):
    print("\n**Key Phrase Extraction**")
    try:
        documents = [text]
        ar = list()
        response = client.extract_key_phrases(documents=documents)[0]   # Hits the Azure resource endpoint using the 'client' received after authentication and stores the results in a response variable
        if not response.is_error:
            print("\tKey Phrases:")
            for phrase in response.key_phrases:
                print("\t\t", phrase)
                ar.append(phrase)
        else:
            print(response.id, response.error)
    except Exception as err:
        print("Encountered exception. {}".format(err))
    return ar


# This function reads and returns the entire content of a single PDF
def read_pdf(path):
    pdfFileObj = open(path, mode="rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict = False)
    full_text = ""
    for i in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        pageContent = pageObj.extractText().replace("\n", "").lower()
        full_text = full_text+pageContent
    pdfFileObj.close()
    return full_text


# This function iterates through all the documents in a repository path and stores the contents in a dataframe 
def read_pdfs():
    path = 'src/static/documents'
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    pdf_files = list()
    for f in onlyfiles:
        if(os.path.splitext(f)[1] == '.pdf'):
            pdf_files.append(f)
    ar = list()
    for file in pdf_files:
        ar.append([read_pdf(path+'/'+file), path+'/'+file]) 
    df = pd.DataFrame(ar)   # Stores the textual content of the PDF and its corresponding path in a Pandas dataframe
    df.columns = ['text', 'path']   
    for index in df.index:
        path_split = df.loc[index,'path'].split('/')
        doc = path_split[len(path_split)-1]
        rel_path = "documents/{0}".format(doc)
        df.loc[index, 'path'] = rel_path
    return df


# This function searches the top n documents which matches the keyphrases and in turn searches the top 3 sentences/paras with highest matches within each document
def driver_function(keyphrases, keywords):  # Array of keyphrases and keywords supplied to this function
    print("\n**Searching Documents**")
    t0 = time.time()

    # read_pdfs() function called and resultant dataframe saved as a pickl file to increase process speed
    # df1 = read_pdfs()
    # df1.to_pickle("dataframe/documents_df.pkl")

    df = pd.read_pickle("dataframe/documents_df.pkl")

    # Spacy language model used to create a tokenized corpus from the above dataframe
    # nlp = spacy.load('en_core_web_lg')
    # text_list = df.text.values
    # tok_text = []  # for our tokenised corpus
    # Tokenising using SpaCy:
    # for doc in tqdm(nlp.pipe(text_list)):
    #     tok = [t.text for t in doc if t.is_alpha]
    #     tok_text.append(tok)

    # BM25 object created from tokenized corpus using BM25Okapi alogorithm and saved as a pickl file
    # bm25result = BM25Okapi(tok_text)
    # with open('bm25_object/bm25result', 'wb') as bm25result_file:
    #     pickle.dump(bm25result, bm25result_file)

    with open('bm25_object/bm25result', 'rb') as bm25result_file:
        bm25 = pickle.load(bm25result_file)
    results = bm25.get_top_n(keyphrases, df.values, n=5)    # bm25 library function called to get top n=5 documents with highest keyphrase matches
    t1 = time.time()
    print(f"Searched documents in {round(t1-t0,3)} seconds")
    data_list = list()
    final = []
    t2 = time.time()
    for i in results:   # Searching for top n sentences/paras inside each of the above top matched documents
        tok_list = []
        Sentences = i[0].split(".")
        df1 = pd.DataFrame(Sentences)
        df1.columns = ['text']
        for j in Sentences:
            tok_words = j.split(" ")
            tok_list.append(tok_words)
        bm25_sentence = BM25Okapi(tok_list)
        results_sentence = bm25_sentence.get_top_n(keyphrases, df1.values, n=10)    # bm25 library function called to get top n=10 sentences with highest keyphrase matches
        p = i[1].rfind("/")
        name = i[1][p+1:]
        count = 0
        final_text = ""
        display = {}
        for k in results_sentence:  # Removing results with sentence length <= 50 for getting more relevant results
            if (len(k[0])>50):
                text = k[0]
                for word in keywords:   # Highlighting the keywords in the displayed results on the webpage
                    text = text.replace(word, '<strong>{}</strong>'.format(word))
                final_text = final_text + text + '<br><br>'
                count= count + 1
            if (count > 2):
                break
        final_text = mark_safe(final_text)
        display = dict({'text': final_text, 'link': i[1], 'name': name})    # Passing the document name, path link, and search results for display 
        final.append(display)
    t3 = time.time()
    print(f"Searched sentences in {round(t3 - t2, 3)} seconds")
    print("\n**Displaying Results**")
    return final

