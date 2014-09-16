
rm *.c
rm *.so
python CompilCython.py build_ext --inplace

#rm *.pyx

./killMS.py -h
./MakeModel.py -h
python -c "import dsreg"
python -c "import dsc"


chmod 611 *.py
chmod 655 *.pyc
chmod 755 killMS.py
chmod 755 MakeModel.py
chmod 755 dsreg.py
