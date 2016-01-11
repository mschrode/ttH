#!/bin/bash

WORKING_DIR=${1}
if [[ "${WORKING_DIR}" == "" ]]; then
    echo "Specify directory with limitplots"
    exit -1
fi

START_DIR=${PWD}
cd ${WORKING_DIR}
QSUB_SCRIPT_NAME="comb_limit"
for dir in ${WORKING_DIR}*; do
    if [[ -d ${dir} ]]; then
	# create datacards
	cd ${dir}
#	mk_datacard_ttbb -d BDT -o datacard.txt ${dir}.root
	cd ..
	
	# create combine qsub scripts per job
	IDX=${dir##*_}
	cat > ${QSUB_SCRIPT_NAME}_${IDX}.sh <<EOF
#!/bin/bash
#
#(make sure the right shell will be used)
#$ -S /bin/bash
#
#(the cpu time for this job)
#$ -l h_cpu=1:59:00
#
#(the maximum memory usage of this job)
#$ -l h_vmem=2000M
#$ -l s_vmem=2000M
#
#(use bird cluster)
#$ -l h=bird*
#(stderr and stdout are merged together to stdout)
#$ -j y
#
# use SL6
#$ -l os=sld6
#
# use current dir and current environment
#$ -cwd
#$ -V
#
#$ -o ${QSUB_SCRIPT_NAME}_${IDX}.out
#
#$ -e ${QSUB_SCRIPT_NAME}_${IDX}.err
cd ${dir}
combine -M Asymptotic -m 125 --minosAlgo stepping datacard.txt
mv higgsCombine*.root ../comb_limit_${IDX}.root
cd ../
EOF

	chmod u+x ${QSUB_SCRIPT_NAME}_${IDX}.sh
    fi
done

# create global submission script
cat > qsub_limits.sh <<"EOF"
#!/bin/bash
for i in comb_limit*.sh; do
	qsub ${i}
done
EOF
chmod u+x qsub_limits.sh

cd ${START_DIR}