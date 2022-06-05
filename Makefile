tardir=ep2-andre-bruno
tar=${tardir}.tar.gz

default:
	@echo "Leia o LEIAME.txt para instruções de uso"

data:
	-@mkdir $@

runserver: data
	./src/server.py

runclient1:
	./src/Client.py 127.0.0.1 5000 7000

runclient2:
	./src/Client.py 127.0.0.1 5000 7001

slide.pdf: slide.md
	pandoc -t beamer -o $@ $^

${tar}: slide.pdf LEIAME.txt Makefile src/
	-@mkdir ${tardir}
	@cp -r $^ ${tardir}
	-@rm -r ${tardir}/src/__pycache__/
	tar czf $@ ${tardir}
	-@rm -r ${tardir}

tar: ${tar}

.PHONY: default runserver runclient1 runclient2 tar
