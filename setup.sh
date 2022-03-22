# Creating a miniconda directory to house everything
mkdir -p /datasets/work/ncmi-gsm/reference/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh -O /datasets/work/ncmi-gsm/reference/miniconda3/miniconda.sh
bash /datasets/work/ncmi-gsm/reference/miniconda3/miniconda.sh -b -u -p /datasets/work/ncmi-gsm/reference/miniconda3
rm -rf /datasets/work/ncmi-gsm/reference/miniconda3/miniconda.sh

# Initialise conda
conda init bash
conda init zsh
. ~/.bashrc
. ~/.zshrc
conda init

# Versioning for water tight opperation
conda install conda=4.11.0 -y
conda create -n ASB -c conda-forge python=3.10.2 -y
conda install -n ASB -c conda-forge gdal=3.4.1 -y
conda install -n ASB -c conda-forge geopandas=0.10.2 -y
conda install -n ASB -c conda-forge lxml=4.7.1 -y
conda install -n ASB -c conda-forge pandas=1.3.5 -y

# Edit bashrc so that ASB is activated and cd into ASB_PIPE when shell opens
echo "conda activate ASB" >> ~/.bashrc
echo "conda config --set auto_activate_base false" >> ~/.bashrc
echo "cd /datasets/work/ncmi-gsm/reference/asb_pipe" >> ~/.bashrc

exec bash
