# tests 6 , 8 are ok (ending and order of some errors are diffrent)
# test 9 is ok order of errors is diffrent
# test 12 is ok (diffrence in ending and EOF)
#tests 14-16 are ok , deffrence in space
#in tests 17-19 seems author fault 
#20  ?
#21 \n ? 
#23 its alright only order is diffrent
#30 its alright , if $ is added only order is diffrent
#31 i think author fault
#32,33,34 i think author fault
#38 its alright , if $ is added only order is diffrent
#39  $ not shown in parser so its ok
#40  $ not shown in parser so its ok and also order in syntax error
#44 i think author fault
#46 $ not shown in parser so its ok and also order in syntax error
for i in {01..05}; do
    echo "Running test case T$i..."


    cp ./testcases-phase2/T$i/input.txt input.txt

    python3 compiler.py


    for file in syntax_errors.txt parse_tree.txt ; do
        if diff -qw ./$file ./testcases-phase2/T$i/$file > /dev/null; then
            echo "$file: SAME"
        else
            echo "$file: DIFFERENT"
        fi
        cp ./testcases-phase2/T$i/$file cur_$file
    done

    echo "-----------------------------------"
done