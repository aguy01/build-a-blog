#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, cgi, jinja2, os, re

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogdb(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)


class NewPost(Handler):
    def render_newpost(self, subject="", content="",error=""):
        #blogposts = db.GqlQuery("select * from Blogdb order by created desc limit 3")
        self.render("newpost.html",subject=subject, content=content,error=error)

    def get(self):
        self.render_newpost()
    def post(self):
        title=self.request.get("subject")
        comment=self.request.get("content")
        #comment = comment.replace('\n', '<br>')
        if title and comment:

            a = Blogdb(subject=title,content=comment)#this creates a new post. which will have title and content
            #content = content.replace('\n', '<br>')

            a.put()#this adds the strings to the Blogdb database.
            newpostid=a.key().id()
            self.redirect('/blog/' + str(newpostid))
            #self.redirect("/newpost") #if success then add the link of blog list here. your blog is now appearing here bloglist
        else:
            error="Error: Subject and comment, both need to be filled"
            self.render_newpost(title, comment, error)

class Bloglist(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Blogdb order by created desc limit 10")
        #content = self.content.replace('\n', '<br>')
        self.render("blog.html", posts = posts)

class ViewPostHandler(Handler): #finds a specific post by posting id stored in Gdatastore. Id must be passed in at the url for this class to work.
    def get(self, id):
        post=Blogdb.get_by_id(int(id))
        if post:
            self.render("singlepost.html", post = post)
        else:
            self.response.write("Sorry "+id+" dont exists")

        #self.response.write(Blogdb.get_by_id(int(id))) #replace this with some code to handle the request


app = webapp2.WSGIApplication([
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/newpost', NewPost),
    ('/blog', Bloglist),
], debug=True)
