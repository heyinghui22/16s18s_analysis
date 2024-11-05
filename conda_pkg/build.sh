# this script creates the file with configuration paths to the 16s18s_analysis modules.
echo "# Paths to 16s18s_analysis scripts (dont have to modify)" > bin/config-16s18s_analysis
echo 'mw_path=$(which 16s18s_analysis)' >> bin/config-16s18s_analysis
echo 'bin_path=${mw_path%/*}' >> bin/config-16s18s_analysis
echo 'SOFT=${bin_path}/16s18s_analysis-scripts' >> bin/config-16s18s_analysis
echo 'PIPES=${bin_path}/16s18s_analysis-command' >> bin/config-16s18s_analysis
echo '' >> bin/config-16s18s_analysis

chmod +x bin/config-16s18s_analysis

mkdir -p $PREFIX/bin/
cp bin/16s18s_analysis $PREFIX/bin/
cp bin/config-16s18s_analysis $PREFIX/bin/
cp -r bin/16s18s_analysis-command $PREFIX/bin/
cp -r bin/16s18s_analysis-scripts $PREFIX/bin/

