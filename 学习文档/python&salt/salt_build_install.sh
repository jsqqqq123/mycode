#!/bin/bash

MainPath=$(cd $(dirname $0)&&pwd)

cd $MainPath

mkdir -pv /usr/local/services/dreamlib/

yum -y install zlib
yum -y install zlib-devel
yum -y install unzip

# install bzip2
tar -xzvf bzip2-1.0.6.tar.gz
cd bzip2-1.0.6
make -f Makefile-libbz2_so
make install PREFIX=/usr/local/services/dreamlib/bzip2
cd ..

#install ncurses
tar -xzvf ncurses-5.9.tgz
cd ncurses-5.9
./configure --prefix=/usr/local/services/dreamlib/ncurses/
make
make install
cd ..

#install readline
tar -xzvf readline-6.2.tgz
cd readline-6.2
for i in {1..4}
do 
    wget http://ftp.gnu.org/gnu/readline/readline-6.2-patches/readline62-00${i}
done
for i in {1..4}
do 
    patch -p0 < readline62-00${i}
done
sed -i '/MV.*old/d' Makefile.in
sed -i '/{OLDSUFF}/c:' support/shlib-install
./configure --prefix=/usr/local/services/dreamlib/readline && make SHLIB_LIBS='-L/usr/local/services/dreamlib/ncurses/lib -Wl,-R/usr/local/services/dreamlib/ncurses/lib' 
make install
cd ..

#install gdbm
tar -xzvf gdbm-1.10.tar.gz
cd gdbm-1.10
./configure --prefix=/usr/local/services/dreamlib/gdbm/
make
make install
cd ..

#install gmp5
bzip2 -d gmp-5.1.2.tar.bz2
tar -xvf gmp-5.1.2.tar
cd gmp-5.1.2
./configure --prefix=/usr/local/services/dreamlib/gmp5
make
make install
cd ..

#install python2.7
tar -xzvf Python-2.7.5.tgz
cd Python-2.7.5

./configure --prefix=/usr/local/services/python27 \
CPPFLAGS='-I/usr/local/services/dreamlib/gmp5/include -I/usr/local/services/dreamlib/openssl/include -I/usr/local/services/dreamlib/bzip2/include -I/usr/local/services/dreamlib/ncurses/include -I/usr/local/services/dreamlib/readline/include -I/usr/local/services/dreamlib/gdbm/include' \
LDFLAGS='-L/usr/local/services/dreamlib/gmp5/lib -L/usr/local/services/dreamlib/openssl/lib -L/usr/local/services/dreamlib/bzip2/lib -L/usr/local/services/dreamlib/ncurses/lib -L/usr/local/services/dreamlib/readline/lib -L/usr/local/services/dreamlib/gdbm/lib -Wl,-R/usr/local/services/dreamlib/gmp5/lib -Wl,-R/usr/local/services/dreamlib/openssl/lib -Wl,-R/usr/local/services/dreamlib/bzip2/lib -Wl,-R/usr/local/services/dreamlib/ncurses/lib -Wl,-R/usr/local/services/dreamlib/readline/lib -Wl,-R/usr/local/services/dreamlib/gdbm/lib'

make
make install
cd ..

#install setuptool
tar -xzvf setuptools-1.1.4.tar.gz
cd setuptools-1.1.4
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install Cython
tar -xzvf Cython-0.19.1.tar.gz
cd Cython-0.19.1
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install zeromg
tar -xzvf zeromq-3.2.3.tar.gz
cd zeromq-3.2.3
./configure --prefix=/usr/local/services/dreamlib/zeromq/
make
make install
cd ..

#install MarkupSaf
tar -xzvf MarkupSafe-0.18.tar.gz
cd MarkupSafe-0.18
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install  pyzmq-2.1.11
tar -xzvf pyzmq-2.1.11.tar.gz
cd pyzmq-2.1.11
/usr/local/services/python27/bin/python2.7 setup.py install --zmq=/usr/local/services/dreamlib/zeromq/
cd ..

#install pycrypto-2.6
tar -xzvf pycrypto-2.6.tar.gz
cd pycrypto-2.6
CPPFLAGS='-I/usr/local/services/dreamlib/gmp5/include' LDFLAGS='-L/usr/local/services/dreamlib/gmp5/lib -Wl,-R/usr/local/services/dreamlib/gmp5/lib' /usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#ins msgpac-python
tar -xzvf msgpack-python-0.1.12.tar.gz
cd msgpack-python-0.1.12
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install PyYAML-3.10
tar -xzvf PyYAML-3.10.tar.gz
cd PyYAML-3.10
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install Jinja
tar -xzvf Jinja2-2.7.1.tar.gz
cd Jinja2-2.7.1
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install Mako
tar -xvzf Mako-0.9.0.tar.gz
cd Mako-0.9.0
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install openssl
tar -xzvf openssl-1.0.1e.tar.gz
cd openssl-1.0.1e
# static
./config --prefix=/usr/local/services/dreamlib/openssl enable-shared
make
make install
make clean
#dynic
./config --prefix=/usr/local/services/dreamlib/openssl
make
make install
cd ..

#install swig
tar -xzvf swig-2.0.10.tar.gz
cd swig-2.0.10
cp ../pcre-8.33.tar.gz .
./Tools/pcre-build.sh
./configure --prefix=/usr/local/services/dreamlib/swig 
make 
make install
cd ..

#install M2Crypto
tar -xzvf M2Crypto-0.21.1.tar.gz
cd M2Crypto-0.21.1
PATH=$PATH:/usr/local/services/dreamlib/swig/bin
/usr/local/services/python27/bin/python2.7 setup.py build build_ext --openssl=/usr/local/services/dreamlib/openssl
/usr/local/services/python27/bin/python2.7 setup.py install build_ext --openssl=/usr/local/service/dreamlib/openssl
cd ..

#install esky
tar -xzvf esky-0.9.8.tar.gz
cd esky-0.9.8
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install bbfreeze-loader
unzip bbfreeze-loader-1.1.0.zip
cd bbfreeze-loader-1.1.0
/usr/local/services/python27/bin/python2.7 setup.py install

#install altgraph
tar -xzvf altgraph-0.9.tar.gz
cd altgraph-0.9
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install bbfreeze
unzip bbfreeze-1.1.2.zip
cd bbfreeze-1.1.2
/usr/local/services/python27/bin/python2.7 setup.py install
cd ..

#install patchelf
tar -xvzf patchelf-0.6.tar.gz
cd patchelf-0.6
./configure --prefix=/usr/local/service/dreamlib/patchelf
make
make install
cd ..



















































