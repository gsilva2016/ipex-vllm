#!/bin/bash


source activate-conda.sh

if [ "$1" == "--skip" ]
then
	activate_conda	
else
	git clone -b lnl_enable https://github.com/gsilva2016/vllm.git 
	cd vllm
	docker build -f ./docker/Dockerfile.xpu -t vllm-xpu-env --shm-size=4g .
	cd ..
	sudo rm -R vllm && true

	CUR_DIR=`pwd`
        cd /tmp
	miniforge_script=Miniforge3-$(uname)-$(uname -m).sh
	[ -e $miniforge_script ] && rm $miniforge_script
	wget "https://github.com/conda-forge/miniforge/releases/latest/download/$miniforge_script"
	bash $miniforge_script -b -u
	# used to activate conda install
	activate_conda
	conda init
	cd $CUR_DIR


fi

conda create -n vllm_env python=3.10 -y
conda activate vllm_env
pip install google-adk litellm

