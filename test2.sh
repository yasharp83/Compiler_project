
python3 compiler.py
for file in syntax_errors.txt parse_tree.txt input.txt ; do
    cp ./$file ./G3/T03/$file
done