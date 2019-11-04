#!/bin/bash

set -e

sudo apt-get update



cd

# -- download Fiji.app --
if [ ! -d Fiji.app ]
then
  echo
  echo "--> Downloading Fiji"
  curl -fsO https://downloads.imagej.net/fiji/latest/fiji-nojre.zip -C - --retry 10
  ls -l fiji-nojre.zip

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
echo "--> Downloading BigStitcher"
Fiji.app/$launcher --update edit-update-site BigStitcher https://sites.imagej.net/BigStitcher/

echo "--> Updating Fiji"
Fiji.app/$launcher --update update
echo "--> Finished updating Fiji"

# -- set ij dirctory --
ij_dir=$HOME/Fiji.app
echo "ij_dir = $ij_dir"

# -- run the Python code --
cd $TRAVIS_BUILD_DIR

# -- create a test enviroment --
conda env create -q -f environment.yml
source activate multiscale
conda install -q -y python=$TRAVIS_PYTHON_VERSION

python setup.py install

# -- run test with debug flag --
python -m pytest --ij="$ij_dir"
