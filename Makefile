PYTHON = python3


.PHONY: app clean copyright ffmpeg login sync word_cloud


sync:
	$(PYTHON) -m lib sync \
		--fast \
		2503094498

app:
	env ADMIN=admin $(PYTHON) -m streamlit run app.py

ffmpeg:
	$(PYTHON) -m lib ffmpeg

login:
	$(PYTHON) -m lib login --driver Firefox

clean:
	@echo $(PYTHON) -m lib clean

copyright:
	$(PYTHON) script/$@.py

word_cloud:
	$(PYTHON) script/$@.py
