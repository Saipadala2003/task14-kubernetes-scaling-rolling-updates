py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r api\requirements.txt
python train_model.py --epochs 5 --batch-size 128
Get-Item model\cifar10_cnn.pth
