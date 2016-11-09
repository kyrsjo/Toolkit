export beam=$1
export turns=$2
cd core
rm *.txt
rm *.eps
rm *.png
rm *.dat
rm *.s
find -maxdepth 2 -mindepth 1 -type d -empty -exec echo {} is empty. \;
empty=$(find -maxdepth 2 -mindepth 1 -type d -empty| wc -l)
total=$(find . -mindepth 1 -type d | wc -l)
full=$((total-empty))
echo "total="$total
echo "full="$full
echo "empty="$empty
find results -name "impacts_real.dat" | xargs cat > imp_real.dat
mv imp_real.dat impacts_real.dat
find results -name "LPI_test.s" | xargs cat > LPI.s
mv LPI.s LPI_test.s
cp results/job_1/coll_summary.dat .
cp ../../commons/CollPositions*.dat .
# python ../postScripts/get_losses.py $full
# python ../postScripts/plot_lossmap.py
get_losses.py $full $turns $beam
plot_lossmap.py $beam 'ATLAS B1, Phase jump'
cd ../tail
rm *.txt
rm *.eps
rm *.png
rm *.dat
rm *.s
find -maxdepth 2 -mindepth 1 -type d -empty -exec echo {} is empty. \;
empty=$(find -maxdepth 2 -mindepth 1 -type d -empty| wc -l)
total=$(find . -mindepth 1 -type d | wc -l)
full=$((total-empty))
echo "total="$total
echo "full="$full
echo "empty="$empty
find results -name "impacts_real.dat" | xargs cat > imp_real.dat
mv imp_real.dat impacts_real.dat
find results -name "LPI_test.s" | xargs cat > LPI.s
mv LPI.s LPI_test.s
cp results/job_1/coll_summary.dat .
cp ../../commons/CollPositions*.dat .
# python ../postScripts/get_losses.py $full
# python ../postScripts/plot_lossmap.py
get_losses.py $full $turns $beam
plot_lossmap.py $beam 'ATLAS B1, Phase jump'
cd ..
plot_lossmap.py $beam 'ATLAS B1, Phase jump' core tail