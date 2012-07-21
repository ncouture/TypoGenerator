Python TypoGenerator
=============

This is a typo generator wrapped in an XMLRPC service that returns JSON.


Configuration
-------------
* Edit PID_FILE in typogenerator.py

Methods
-------
### insertedKey
### skipLetter
### doubleLetter
### reverseLetter
### wrongVowel
### wrongKey
### synonymSubstitution
### rhymeSubstitution

Dependencies
------------
* [nltk](http://nltk.org/)
* A dictionary file (eg: /usr/share/dict/words, 
    	       	    	 typogenerator.py:DICTIONARY)
* (optional) [rhyme](http://packages.debian.org/sid/text/rhyme) for the rhymeSubstitution method

Testing
-------
From any python interpreter execute the following:

    >>> import xmlrpclib
    >>> server = xmlrpclib.ServerProxy("http://server:port")
    >>> server.skipLetter("hello")

TODO
----
* logging
