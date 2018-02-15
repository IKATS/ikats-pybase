#sphinx-apidoc -fPMe -o . ../src/ikats
sphinx-apidoc -fPe -o . ../src/ikats
make html
rm -f *.rst

echo "Documentation entry points is located here : _build/html/index.html"
