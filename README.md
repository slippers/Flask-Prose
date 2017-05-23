# flask prose

flask prose is an extension to generate various kinds of prose from a corpus of text.
basically you upload a largish text file with unique text and out comes prose.  
from there you can explore the how composed text can be expressed as randomized prose.

the extention exposes a set of endpoints that can be used to authenticate, upload, and get prose
there are no web templates invoved just regular json requests

there is a facility to vote for your favorite prose via grock.

## api enpoints

/corpora/<uuid>  - GET, POST, DELETE

/prose - GET

/grock - PUT

### setup

pip install flask-prose

### configuration

database

restapi endpoints

### documention


### future

* adding more types of prose with a higher level of composition.  
* nltk offers access to word classification for purposes of rhyming.
* scraping external urls for content
* admin classes for flask-admin
