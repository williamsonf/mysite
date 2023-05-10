'''
Created on May 9, 2023

@author: Fred
'''
import logging, datetime
log_format=f'[%(asctime)s] [%(levelname)-8s] %(message)s'
logging.basicConfig(filename="logs/" + str(datetime.date.today()) + ".log", encoding='utf-8', level=logging.WARNING, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')
#logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')
import json, traceback
from flask import Flask, render_template, abort, url_for
from waitress import serve

app = Flask(__name__)
_AUTHOR = "Fred Williamson"
_GITHUB = "https://github.com/williamsonf"

def get_navlinks() -> str:
    linklist = ['home', 'stories']
    url_list = {}
    for link in linklist:
        url = url_for(link)
        url_list[link] = (url, link.title())
    url_list['github'] = (_GITHUB, 'Github')
    linklist.append('github')
    
    result = f""
    for link in linklist:
        result += f"<a href='{url_list[link][0]}'>{url_list[link][1]}</a>"
        
    return result

def get_header() -> str:
    with open('static/content/header.txt', 'r') as f:
        return f.read()
    
def get_footer() -> str:
    with open('static/content/footer.txt', 'r') as f:
        return f.read()

@app.route('/')
def home() -> render_template:
    try:
        with open('static/content/welcome.txt', 'r') as f:
            body = f.read()
            
        return render_template('main.html', content= body, navlink= get_navlinks(), headertext= get_header(), footertext= get_footer())
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

@app.route('/stories')
def stories() -> render_template:
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
        with open('stories/stories_manifest.json', 'rb') as f:
            manifest = json.load(f)
        
        toc = {'novella' : {},
               'novelette' : {},
               'short' : {},
               'flash' : {},
               'poetry' : {}}
        
        parsed_toc = f''
        
        #we start by just grabbing the information we need from the manifest and properly sorting it
        for item in manifest.keys():
            form = manifest[item]['form']
            toc[form] = {item : manifest[item]['file']}
            
        for form in ['novella', 'novelette', 'short', 'flash', 'poetry']:
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
            
        return render_template('main.html', content= parsed_toc, navlink= get_navlinks(), headertext= get_header(), footertext= get_footer())
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

@app.route('/stories/<story>')
def story(story: str) -> render_template:
    try:
        with open('stories/stories_manifest.json', 'r') as f:
            manifest = json.load(f)
        for item in manifest.keys():
            if manifest[item]['file'] == story:
                title = f"<h1>{item}</h1>by {_AUTHOR}"
                try:
                    preface = manifest[item]['preface']
                except:
                    preface = None
                break
        
        content = f""
        with open(f'stories/{story}', 'r') as f:
            content = f.read()
        
        return render_template('story.html', title=title, preface=preface, content=content, navlink= get_navlinks(), headertext= get_header(), footertext= get_footer())
    except Exception as e:
        logging.critical(traceback.format_exc())
        abort(404)

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    serve(app, host='0.0.0.0', port=8080)