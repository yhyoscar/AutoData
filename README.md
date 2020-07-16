# AutoData

- Data scrapping
- Big data analysis
- Data mining

## Dependencies:
- pip install nltk
- pip install word2number
- pip install gensim
- Two available libaries to expand contractions:
    - 1. pip install contractions # faster than pycontractions, but a little less performance
    - 2. pip install pycontractions
        + pycontractions needs language-check, which requires java8. Follow this tutorial to install different versions of java
        + make sure:
            - .bash_profile: comment out #export PATH="/usr/local/opt/openjdk/bin:$PATH"
            - .bashrc: add following 
                ```
                # java8
                export PATH="$HOME/.jenv/bin:$PATH"
                eval "$(jenv init -)"
                export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
                ```
- pip install spacy
    + python -m spacy download en
- pip install beautifulsoup4
- pip install selenium
    + Selenium requires a driver to interface with the chosen browser. Firefox, for example, requires geckodriver, which needs to be installed before running the code.
        - For Chrome user: https://chromedriver.chromium.org/downloads
        - For Firefox user: https://github.com/mozilla/geckodriver/releases
    + After decompressing the downloaded driver file, place it in /usr/bin OR /usr/local/bin
