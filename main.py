'''
Created on May 9, 2023

@author: Fred
'''
import logging, datetime
log_format=f'[%(asctime)s] [%(levelname)-8s] %(message)s'
#logging.basicConfig(filename="logs/" + str(datetime.date.today()) + ".log", encoding='utf-8', level=logging.INFO, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')
import json, traceback
from flask import Flask, render_template, abort, url_for

app = Flask(__name__)

@app.route('/')
def homepage():
    try:
        with open('static/content/welcome.txt', 'r') as f:
            body = f.read()
        return render_template('main.html', content = body)
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

@app.route('/stories')
def story_toc():
    '''
    stories_manifest.json should always contain the following fields:
    The title of the story, serving as a Key (ie. 'Alistair Finch: Wizard for Hire')
        file : str
            the .txt filename of the story (ie. 'alistairfinch.txt')
        form : str
            (novella, novelette, short, flash)
        preface : str
            a string which may act as a preface for the story, probably just information
            about when the story was published and maybe a link to a storepage for an anthology or something
    '''
    try:
        with open('stories/stories_manifest.json', 'r') as f:
            manifest = json.load(f)
        
        toc = {'novella' : {},
               'novelette' : {},
               'short' : {},
               'flash' : {}}
        
        parsed_toc = f''
        
        #we start by just grabbing the information we need from the manifest and properly sorting it
        for item in manifest.keys():
            form = manifest[item]['form']
            toc[form] = {item : manifest[item]['file']}
            
        for form in ['novella', 'novelette', 'short', 'flash']:
            #if there are no stories of this type, we'll just skip it
            if len(toc[form].keys()) <= 0:
                continue
            #now we are going to sort our stories alphabetically
            sorted_list = sorted(toc[form].keys())
            #now, we'll start the list:
            parsed_toc += f'<h2>{form.title()}{"s" if form in ["novella", "novelette"] else " Fiction"}</h2><ol>'
            
            #now adding stories
            for story in sorted_list:
                story_url = url_for('story', story=toc[form][story])
                parsed_toc += f'<li><a href=\'{story_url}\'>{story}</a></li>'
                
            #closing the list
            parsed_toc += f'</ol>'
        
        return render_template('main.html', content=parsed_toc)
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

@app.route('/stories/<story>')
def story(story):
    try:
        with open('stories/stories_manifest.json', 'r') as f:
            manifest = json.load(f)
        for item in manifest.keys():
            if manifest[item]['file'] == story:
                title = item
                try:
                    preface = manifest['preface']
                except:
                    preface = None
                break
        
        content = f""
        with open(f'stories/{story}', 'r') as f:
            content = f.read()
            
        return render_template('story.html', title=title, preface=preface, content=content)
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

if __name__ == '__main__':
    app.run()