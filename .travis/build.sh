#!/bin/bash

set -e

sudo apt-get update

# -- create a test enviroment --
conda env create -q -f environment.yml
source activate multiscale
conda install -q -y python=$TRAVIS_PYTHON_VERSION

# -- ensure supporting tools are available --
check curl git unzip

cd

# -- download Fiji.app --
if [ ! -d Fiji.app ]
then
  echo
  echo "--> Downloading Fiji"
  curl -fsO http://downloads.imagej.net/fiji/latest/fiji-nojre.zip

  echo "--> Unpacking Fiji"
  rm -rf Fiji.app
  unzip fiji-nojre.zip
fi

# -- Determine correct ImageJ launcher executable --
case "$(uname -s),$(uname -m)" in
  Linux,x86_64) launcher=ImageJ-linux64 ;;
  Linux,*) launcher=ImageJ-linux32 ;;
  Darwin,*) launcher=Contents/MacOS/ImageJ-macosx ;;
  MING*,*) launcher=ImageJ-win32.exe ;;
  *) die "Unknown platform" ;;
esac

echo
echo "--> Updating Fiji"
Fiji.app/$launcher --update update-force-pristine
Fiji.app/$launcher --update edit-update-site BigStitcher https://sites.imagej.net/BigStitcher/
Fiji.app/$launcher --update update

# -- run the Python code --
cd $TRAVIS_BUILD_DIR

# -- set ij dirctory --
ij_dir=$HOME/Fiji.app
echo "ij_dir = $ij_dir"
python setup.py install

# -- run test with debug flag --
python -m pytest --ij="$ij_dir"
