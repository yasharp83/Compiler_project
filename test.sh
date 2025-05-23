for i in {01..10}; do
    echo "Running test case T$i..."


    cp ./testcases-phase2/T$i/input.txt input.txt

    python3 compiler.py


    for file in syntax_errors.txt parse_tree.txt ; do
        if diff -qw ./$file ./testcases-phase2/T$i/$file > /dev/null; then
            echo "$file: SAME"
        else
            echo "$file: DIFFERENT"
        fi
    done

    echo "-----------------------------------"
done