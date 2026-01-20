./sparse.py --devmode --verbose --file test > curOut.txt

if diff curOut.txt knownGood.txt > /dev/null ; then
    echo -e "\033[31;1;32mSPARSE passes test (output is as expected from knownGood.txt)\033[0m"
else
    echo -e "\033[31;1mSPARSE fails test (output is not as expected from knownGood.txt)\033[0m"
    colordiff knownGood.txt curOut.txt
fi


