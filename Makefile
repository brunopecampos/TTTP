tardir=ep2-andre-bruno
tar=${tardir}.tar.gz

default:
	@echo "Leia o LEIAME.txt para instruções de uso"

data:
	-@mkdir $@

runserver: ./src/server.py data
	chmod +x $<
	cd src/ && ./server.py

runclient1: ./src/Client.py
	chmod +x $<
	cd src/ && ./Client.py 127.0.0.1 5000 7000 -t

runclient2: ./src/Client.py
	chmod +x $<
	cd src/ && ./Client.py 127.0.0.1 5000 7001 -t

slide.pdf: slide.md
	pandoc -t beamer -o $@ $^

${tar}: slide.pdf LEIAME.txt Makefile src/ data/
	-@mkdir ${tardir}
	@cp -r $^ ${tardir}
	-@rm -r ${tardir}/src/__pycache__/ ${tardir}/data/db.json ${tardir}/data/log.txt
	tar czf $@ ${tardir}
	-@rm -r ${tardir}

tar: ${tar}

.PHONY: default runserver runclient1 runclient2 tar
