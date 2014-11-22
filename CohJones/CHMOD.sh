
# rm *.c
# #rm *.pyx
# rm *.so
# python CompilCython.py build_ext --inplace
# rm *.c
# rm *.pyx

#rm *.pyx

./CohJones.py -h
./MakeModel.py -h
python -c "import dsreg"
python -c "import dsc"


chmod 611 *.py
chmod 655 *.pyc
chmod 755 CohJones.py
chmod 755 MakeModel.py
chmod 755 dsreg.py
