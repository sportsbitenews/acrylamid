#!/usr/bin/env python

from HTMLParser import HTMLParser

class Summarizer(HTMLParser):

    def __init__(self, text, href, maxwords=100):
        HTMLParser.__init__(self)
        self.maxwords = maxwords
        self.href = href
        self.summarized = ''
        self.words = 0
        self.stack = []

        self.feed(text)

    def handle_starttag(self, tag, attrs):
        '''Apply and stack each read tag until we reach maxword.'''

        def tagify(tag, attrs):
            '''convert parsed tag back into a html tag'''
            if attrs:
                return ' <%s %s>' % (tag, ' '.join(['%s="%s"' % (k, v) for k,v in attrs]))
            else:
                return '<%s>' % tag

        if self.words < self.maxwords:
            self.stack.append(tag)
            self.summarized += tagify(tag, attrs)

    def handle_data(self, data):

        if self.words >= self.maxwords:
            pass
        else:
            words = data.split(' ')
            if self.words + len(words) < self.maxwords:
                '''if the next few words will not go over maxwords'''
                self.words += len(words)
                self.summarized += data
            else:
                '''we can put some words before we reach the word limit'''
                somewords = self.maxwords - self.words
                self.words += somewords
                self.summarized += ' '.join(words[:somewords]) + ' '
                self.summarized += '... <a href="%s" class="continue">weiterlesen</a>.' % self.href

    def handle_endtag(self, tag):
        '''Until we reach not the maxwords limit, we can safely pop every ending tag,
           added by handle_starttag. Afterwards, we apply missing endings tags if missing.'''
        if self.words < self.maxwords:
            self.stack.pop()
            self.summarized += '</%s>' % tag
        else:
            if self.stack:
                for x in range(len(self.stack)):
                    self.summarized += '</%s>' % self.stack.pop()
                    
    def handle_entityref(self, name):
        '''handle &shy; correctly'''
        if self.words < self.maxwords:
            self.summarized += '&'  + name + ';'


def cb_prepare(request):
    
    config = request._config
    data = request._data
    t = data.get('type', 'item')
    
    for i, entry in enumerate(data['entry_list']):
        
        if t == 'page':
            data['entry_list'][i]['body'] = Summarizer(entry['body'], entry['url'], 200).summarized
    
    return request