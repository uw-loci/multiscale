!/bin/bash

sudo apt-get update

# -- create a test enviroment --
conda create -q -n multiscale python=$TRAVIS_PYTHON_VERSION
source activate multiscale

# -- install dependencies --
conda install -c simpleitk SimpleITK
conda install cython
conda install h5py
conda install -c conda-forge pyjnius
conda install -c hanslovsky imglyb
conda install pytest
conda install pandas
conda install scipy
conda install matplotlib
conda install pillow
pip install imagej
pip install pyssim
pip install javabridge
pip install python-bioformats
pip install scyjava
pip install pyimagej
pip install -r requirements.txt

# -- install supporting tools --
sudo apt -y install curl
sudo apt -y install git
sudo apt -y install unzip

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
