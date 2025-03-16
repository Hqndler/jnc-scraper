#bin/sh

git clone https://github.com/gvellut/jncep.git --branch nina
cd jncep
sed -i 's|/embed/{slug_id}/{content_type}|/embed/v2/{slug_id}/{content_type}|g' jncep/jnclabs.py
python3 setup.py build
pip install .
export PATH="/home/$USER/.local/bin:$PATH"
cd ..
pip install --no-cache-dir -r requierements.txt