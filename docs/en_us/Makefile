
.PHONY: html

Q_FLAG =

ifeq ($(quiet), true)
Q_FLAG = quiet=true
endif

html:
	@cd $(CURDIR)/dashboard && make html $(Q_FLAG)