
python3 compile_and_exec.py -i ./Test_case_G3/T2/input.txt
for file in output.txt expected.txt semantic_errors.txt ; do
    cp ./$file ./Test_case_G3/T2/$file
done