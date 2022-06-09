cd /datasets/work/ncmi-gsm/reference
conda install anaconda-clean -y
anaconda-clean -y

# Remove all ASB_PIPE related directories
rm -rf *conda* .anaconda* asb* .conda* ~/.condarc ~/.conda ~/.continuum ~/datasets/work/ncmi-gsm/reference/.condarc ~/datasets/work/ncmi-gsm/reference/.conda ~/datasets/work/ncmi-gsm/reference/.continuum

# Remove conda remnants from bashrc ans zshrc
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.bashrc
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.zshrc
sed -i '/conda.*/d' ~/.bashrc
sed -i '/cd /datasets/work/ncmi-gsm/reference/asb_pipe/d' ~/.bashrc

reset
exec bash
