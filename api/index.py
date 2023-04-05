from flask import Flask, jsonify
from flask_cors import CORS
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
import os
import ReadGraphOCR
import glob
import sys
import openai
import re
import requests
import urllib
from urllib import request
import ppextractmodule

openai.api_key = "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"  # openAI api key


def generateScripts(slides):
    print("Completing...")
    # list for save generated scripts
    generatedScripts = []
    for slide in slides:
        # create the prompt, substring with regex for remove S1: S2: notation
        promptForGPT = "Write a presentation script->\\n" + \
            re.sub('S\d:', '', slide)
        # call openai for completion
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=promptForGPT,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            max_tokens=200)
        # append to generated scripts list
        print(completion.choices[0].text)
        generatedScripts.append(completion.choices[0].text)
    return generatedScripts


def generateSingleScript(slides):
    print("Completing...")
    # list for save generated scripts
    generatedScript = ""
    # create the prompt, substring with regex for remove S1: S2: notation
    promptForGPT = "Write a presentation script for these slides->\\n" + slides
    # call openai for completion
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=promptForGPT,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        max_tokens=3500)
    # append to generated scripts list
    print(completion.choices[0].text)
    generatedScripts = completion.choices[0].text
    return generatedScripts


def predictAndDescribe(images):
    imagelist = []
    for i in range(images):
        imagelist.append("image" + str(i) + ".png")    
    print(imagelist)
    generatedScriptGraph = {}
    for i in imagelist:
        graphInfo = ReadGraphOCR.readGraph(i)
        if (graphInfo != "False"):
            promptForGPT = "Write a 50 word Description about the following graph. use the following coordinated to get a better understanding->\\n" + \
                re.sub('S\d:', '', graphInfo)

            # call openai for completion
            completion = openai.Completion.create(
                engine="text-davinci-003",
                prompt=promptForGPT,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=200)
            # append to generated scripts list
            generatedScriptGraph[i] = completion.choices[0].text
            print(completion.choices[0].text)

    for i in generatedScriptGraph:  # REMOVE THIS
        print(i)

    return generatedScriptGraph


def extractAndGenerate():
    output = ppextractmodule.process("presentation.pptx")
    scripts = str(output["text"])
    imageCount = output["images"]
    charts = {}
    if imageCount > 0:
        charts = predictAndDescribe(imageCount)
    generated = generateSingleScript(scripts)
    return {"script": generated, "charts": charts}


app = Flask(__name__)
cors = CORS(app, resources={r"/scripts": {"origins": "*"}})


@app.route('/')
def hello_world():
    return 'Hello from ScriptGenAI'


@app.route('/about')
def about():
    return 'About Squadron'


@app.route('/scripts', methods=['GET'])
def scripts():
    URL = FlaskRequest.headers['link']
    response = request.urlretrieve(URL, "presentation.pptx")
    generatedScripts = extractAndGenerate()
    script = generatedScripts["script"]
    charts = generatedScripts["charts"]
    data = {'script': script, 'charts': charts}
    return jsonify(data)


@app.route('/check', methods=['GET'])
def check():
    URL = 'https://firebasestorage.googleapis.com/v0/b/sdgp-squadr.appspot.com/o/files%2Fscg.pptx?alt=media&token=40d1e1ed-7eb7-4b53-b7f1-a6b80876235d'
    response = request.urlretrieve(URL, "presentation.pptx")
    return str(ppextractmodule.process("presentation.pptx")["images"])


app.run()
