#!/bin/bash

WORKING_DIR=${1}
if [[ "${WORKING_DIR}" == "" ]]; then
    echo "Specify directory with limitplots"
    exit -1
fi

START_DIR=${PWD}
cd ${WORKING_DIR}
for cat in ljets_j4_t3 ljets_j4_t4 ljets_j5_t3 ljets_j5_tge4 ljets_jge6_t2 ljets_jge6_t3 ljets_jge6_tge4 ljets; do
    hadd comb_limit_${cat}.root comb_limit_${cat}_*.root
    DIR="comb_limit_${cat}"
    mkdir -p ${DIR}
    mv comb_limit_${cat}.root ${DIR}
    mv comb_limit_${cat}_*.root ${DIR}
    mv comb_limit_${cat}_*.out ${DIR}
done
for i in `ls -d -1 comb_limit_ljets*/`; do mv ${i}/${i/\//.root} .; done
cd ${START_DIR}