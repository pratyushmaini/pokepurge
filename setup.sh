conda create -n pokepurge python=3.12 -y
conda activate pokepurge
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
conda install -c conda-forge diffusers -y
conda install -c conda-forge transformers -y