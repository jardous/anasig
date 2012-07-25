#SRC:=darticlesform.ui dcardeditform.ui dcardseditform.ui dgroupeditform.ui dgroupviewform.ui dlistcardsform.ui dmovelogeditform.ui dproducteditform.ui dreceiptcardform.ui dsupplierseditform.ui dsuppliersform.ui dviewstoreform.ui main.ui
SRC:=$(wildcard */*form.ui)
SRC:=${SRC} $(wildcard */*/*form.ui)

FILES:=$(addsuffix .py, $(basename ${SRC}))

all: ${FILES}
#	echo ${SRC}
#	echo ${FILES}
%.py: %.ui
	pyuic $< > $@

clean:
	rm -f ${FILES}

#lang:
#	pylupdate sklad.pro
