conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
conda install -c conda-forge accelerate -y
conda install -c conda-forge diffusers -y
conda install -c conda-forge transformers -y
conda install -c conda-forge protobuf -y
pip install sentencepiece
pip install -r requirements.txt