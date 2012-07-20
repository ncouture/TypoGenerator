#!/usr/bin/python

import sys
import os
import json
import subprocess
import SocketServer
import SimpleXMLRPCServer

from nltk.corpus import wordnet

from daemon import daemon, pidlockfile

PORT = 2828
LISTEN = "0"
DICTIONARY = "/usr/share/dict/words"

if not os.path.isfile(DICTIONARY):
    raise FileNotFound("Could not find dictionary: %s" % DICTIONARY)

PID_FILE = '/home/self/backup/dev/TypoGenerator/typogenerator.pid'

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
vowels = "aeiouy"

connectives = [
    "I", "the", "of", "and", "to", "a", "in", "that", 
    "is", "was", "he", "for", "it", "with", "as", "his", 
    "on", "be", "at", "by", "i", "this", "had", "not", 
    "are", "but", "from", "or", "have", "an", "they", 
    "which", "one", "you", "were", "her", "all", "she", 
    "there", "would", "their", "we", "him", "been", "has", 
    "when", "who", "will", "more", "no", "if", "out", 
    "so", "said", "what", "u", "its", "about", "into", 
    "than", "them", "can", "only", "other", "new", "some", 
    "could", "time", "these", "two", "may", "then", "do", 
    "first", "any", "my", "now", "such", "like", "our", 
    "over", "man", "me", "even", "most", "made", "after", 
    "also", "did", "many", "before", "must", "through", 
    "back", "years", "where", "much", "your", "way", 
    "well", "down", "should", "because", "each", "just", 
    "those", "eople", "mr", "how", "too", "little",
     "state", "good", "very", "make", "world", "still", 
     "own", "see", "men", "work", "long", "get", "here", 
     "between", "both", "life", "being", "under", "never", 
     "day", "same", "another", "know", "while", "last", 
     "might", "us", "great", "old", "year", "off", 
     "come", "since", "against", "go", "came", "right", 
     "used", "take", "three",
     "whoever", "nonetheless", "therefore", "although",
     "consequently", "furthermore", "whereas",
     "nevertheless", "whatever", "however", "besides",
     "henceforward", "yet", "until", "alternatively",
     "meanwhile", "notwithstanding", "whenever",
     "moreover", "despite", "similarly", "firstly",
     "secondly", "lastly", "eventually", "gradually",
     "finally", "thus", "hence", "accordingly",
     "otherwise", "indeed", "though", "unless"
]

class FileNotFound(Exception):
    pass

class TypoGenerator:
    def insertedKey(self, s):
        """Produce a list of keywords using the `inserted key' method
        """
        kwds = []

        for i in range(0, len(s)):
            for char in alphabet:
                kwds.append(s[:i+1] + char + s[i+1:])

        return json.dumps(kwds)
        
    def skipLetter(self, s):
        """Produce a list of keywords using the `skip letter' method
        """
        kwds = []

        for i in range(1, len(s)+1):
            kwds.append(s[:i-1] + s[i:])

        return json.dumps(kwds)

    def doubleLetter(self, s):
        """Produce a list of keywords using the `double letter' method
        """
        kwds = []

        for i in range(0, len(s)+1):
            kwds.append(s[:i] + s[i-1] + s[i:])

        return json.dumps(kwds)

    def reverseLetter(self, s):
        """Produce a list of keywords using the `reverse letter' method
        """
        kwds = []

        for i in range(0, len(s)):
            letters = s[i-1:i+1:1]
            if len(letters) != 2:
                continue
        
            reverse_letters = letters[1] + letters[0]
            kwds.append(s[:i-1] + reverse_letters + s[i+1:])

        return json.dumps(kwds)

    def wrongVowel(self, s):
        """Produce a list of keywords using the `wrong vowel' method (for soundex)
        """
        kwds = []

        for i in range(0, len(s)):
            for letter in vowels:
                if s[i] in vowels:
                    for vowel in vowels:
                        s_list = list(s)
                        s_list[i] = vowel
                        kwd = "".join(s_list)
                        kwds.append(kwd)

        return json.dumps(kwds)

    def wrongKey(self, s):
        """Produce a list of keywords using the `wrong key' method
        """
        kwds = []

        for i in range(0, len(s)):
            for letter in alphabet:
                kwd = s[:i] + letter + s[i+1:]
                kwds.append(kwd)
                
        return json.dumps(kwds)

    def _is_connective(self, word):
        """ Guesses whether the word is a connective.
        
        Connectives are conjunctions such as "and", "or", "but",
        transition signals such as "moreover", "finally",
        and words like "I", "she".
        
        It's useful to filter out connectives
        when guessing the concept of a piece of text.
        ... you don't want "whatever" to be the most important word
        parsed from a text.
        
        """
        if word.lower() in connectives:
            return True
        else:
            return False


    def _findWords(self, s):
        """Produces a list of words found in string `s'
        """
        matches = []

        words = file(DICTIONARY).read()

        for word in words.split('\n'):
            if s.find(word) != -1 and word != '' and len(word) > 1: # and not self._is_connective(word):
                matches.append(word)

        return matches

    def _getSynonyms(self, word):
        """Returns a list of synonyms for `word'
        """
        synset = []

        for word_type in [wordnet.ADJ, wordnet.ADV, wordnet.NOUN, wordnet.VERB]:
            synset += [lemma.name.lower().replace("_", "")
                       for lemma in sum([ss.lemmas
                                         for ss in wordnet.synsets(word, word_type)],[])]

        return synset

    def synonymSubstitution(self, s):
        """Produces a list of strings with alternative synonyms from the words found in `s'
        """
        alt_strings = []
        for word in self._findWords(s):
            for synonym in self._getSynonyms(word):
                orig_s = s
                alt_strings.append( orig_s.replace(word, synonym))

        return json.dumps(list(set(alt_strings)))

    def rhymeSubstitution(self, s):
        """Produces a list of strings with alternative rhyming words.
        """
        # http://packages.debian.org/sid/text/rhyme
        alt_strings = []
        for word in self._findWords(s):
            process = subprocess.Popen(["rhyme", word], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outp = process.stdout.read()
            if "wasn't found" in outp:
                continue
            rhymes = outp.replace("Finding perfect rhymes for city...", "").replace(
                "\n1:", "").replace("\n2:", "").replace("\n3:", "").replace(
                "\n4:", "").replace("\n", ",").replace(" ", "").split(",")
            for rhyme in rhymes:
                orig_s = s
                if (not "(" in rhyme) and (
                    not "'" in rhyme) and (
                    not "." in rhyme):
                    alt_strings.append( orig_s.replace(word, rhyme))

        return json.dumps(list(set(alt_strings)))

#    def getAllTypos(self, s):
#        """Calls all our typo generation methods on a string and return the result
#        """
#        kwds = []
#        kwds += self.insertedKey(s)
#        kwds += self.wrongKey(s)
#        kwds += self.skipLetter(s)
#        kwds += self.doubleLetter(s)
#        kwds += self.reverseLetter(s)
#        kwds += self.wrongVowel(s)
#        kwds += self.synonymSubstitution(s)
#        return kwds


class SimpleThreadedXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    pass

if __name__ == "__main__":
    pidlock = pidlockfile.PIDLockFile(PID_FILE)

    if pidlock.is_locked():
        sys.exit(1)

    context = daemon.DaemonContext()
    context.pidfile = pidlock
    context.open()

    try:
        server = SimpleThreadedXMLRPCServer((LISTEN, PORT))
        server.register_instance(TypoGenerator())
        server.serve_forever()
    finally:
        context.close()
