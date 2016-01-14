#!/bin/bash

WORKING_DIR=${1}
if [[ "${WORKING_DIR}" == "" ]]; then
    echo "Specify directory with limitplots"
    exit -1
fi

START_DIR=${PWD}
cd ${WORKING_DIR}
for dir in ${WORKING_DIR}*; do
    if [[ -d ${dir} ]]; then
	# create datacards
	cd ${dir}
	mk_datacard_ttbb -d BDT -o datacard_ljets.txt ${dir}.root
	for cat in ljets_j4_t3 ljets_j4_t4 ljets_j5_t3 ljets_j5_tge4 ljets_jge6_t2 ljets_jge6_t3 ljets_jge6_tge4; do
	    mk_datacard_ttbb -d BDT -c "${cat}" -o datacard_${cat}.txt ${dir}.root
	done

	cd ..
	
	# create combine qsub scripts per job
	IDX=${dir##*_}
	echo -e "#!/bin/bash\n" > comb_limit_${IDX}.sh
#	echo -e "#$ -o comb_limit_${IDX}.out" >> comb_limit_${IDX}.sh
#	echo -e "#$ -e comb_limit_${IDX}.err" >> comb_limit_${IDX}.sh
	echo -e "\ncd ${dir}" >> comb_limit_${IDX}.sh
	echo -e "for cat in ljets ljets_j4_t3 ljets_j4_t4 ljets_j5_t3 ljets_j5_tge4 ljets_jge6_t2 ljets_jge6_t3 ljets_jge6_tge4; do" >> comb_limit_${IDX}.sh
	echo -e "    combine -M Asymptotic -m 125 --minosAlgo stepping datacard_\${cat}.txt > comb_limit_\${cat}_${IDX}.out" >> comb_limit_${IDX}.sh
	echo -e "    mv higgsCombine*.root ../comb_limit_\${cat}_${IDX}.root" >> comb_limit_${IDX}.sh
	echo -e "    mv comb_limit_\${cat}*.out ../" >> comb_limit_${IDX}.sh
	echo -e "\ndone\ncd ../" >> comb_limit_${IDX}.sh
	chmod u+x comb_limit_${IDX}.sh
    fi
done

# create global submission script
cat > qsub_limits.sh <<"EOF"
#!/bin/bash
for i in comb_limit*.sh; do
    qsub -S /bin/bash -l h_cpu=1:59:00 -l h_vmem=2000M -l s_vmem=2000M -l h=bird* -j y -l os=sld6 -cwd -V ${i}
done
EOF
chmod u+x qsub_limits.sh

cd ${START_DIR}