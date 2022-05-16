# jack-udp-route

A very specific tool for a specific use case. I'm running 2 X sesssions under 2
different users simultaneously, and I want both of them to have access to audio.
Using Pipewire and `pipewire-jack`, this tool will send audio from one side to
the other, including microphone.

```bash
pip install -r requirements.txt

# Run on one session
pw-jack python3 main.py

# Run on the other X session
pw-jack python3 main.py b
```

You'll have to manually route the audio using Helvum or some other patchbay.
