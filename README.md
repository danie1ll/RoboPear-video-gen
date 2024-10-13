# RoboPear-video-gen

# How to run
### pip
`pip install -r requirements.txt`
### OR conda
```
conda env create -n robopear python=3.12
conda activate robopear
python -m pip install -r requirements.txt
```

### Set OpenAI API key
create a file called `openaikey` and put your OpenAI API key in it.

### Launch server
`uvicorn main:app --reload`



## Website Gen

```
python webserver.py
```

to make the website available to the internet, use ngrok
```
ngrok http 8000
```

