cd
conda install anaconda-clean -y
anaconda-clean -y

# Remove all ASB_PIPE related directories
rm -rf *conda* .anaconda* ASB* .conda* ~/.condarc ~/.conda ~/.continuum

# Remove conda remnants from bashrc ans zshrc
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.bashrc
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.zshrc
sed -i '/conda.*/d' ~/.bashrc
sed -i '/cd ASB_PIPE/d' ~/.bashrc

reset
exec bash
