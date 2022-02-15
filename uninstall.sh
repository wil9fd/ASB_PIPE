cd
conda install anaconda-clean -y
anaconda-clean -y
rm -rf *conda* .anaconda* ASB* .conda* ~/.condarc ~/.conda ~/.continuum
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.bashrc
sed -i '/^# >>> conda/,/^\# <<< conda/d' ~/.zshrc
sed -i '/conda.*/d' ~/.bashrc
sed -i '/cd ASB_PIPE/d' ~/.bashrc
reset
exec bash
