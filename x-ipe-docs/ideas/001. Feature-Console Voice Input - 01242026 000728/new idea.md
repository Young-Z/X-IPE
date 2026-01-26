I would like to add a voice input function.
- on console bar, move connected status to lefside beside console text
- on console bar, on left side of + icon, add a mic toggle
- on left side of mic toggle, if toggle on, show voice animation indicate voice is on
- if voice is on, then if the focus is set to any terminal window, let's send live voice to server side
- service side can leverage llm "gummy-realtime-v1" to convert voice to text, online doc "https://help.aliyun.com/zh/model-studio/real-time-speech-recognition?spm=a2c4g.11186623.help-menu-2400256.d_0_5_0.490c23f5SE6gyr&scm=20140722.H_2842554._.OR_help-T_cn~zh-V_1"
- then with converted text, similate human input text into terminal
- if you hear "close mic", mic toggle should off, voice function should be disable, until next toggle on.
- for current design you can reference 'current design reference.png'