#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse, csv

class Vaalidata(object):

	def __init__(self, tiedosto):

		# Listan formaatti: sukunimi, etunimi, ikä, sukupuoli, toimiiko kansanedustajana (0, 1)
		with open('vastauksetavoimenadatana1_siivottu.csv', 'rt') as file:
			self.data = list(csv.reader(file))

	def yleisin_nimi(self):
		ehdokkaiden_etunimet = {}
		ehdokkaiden_sukunimet = {}
		for rivi in self.data:
			etunimet = rivi[3].split()
			for nimi in etunimet:
				if not nimi in ehdokkaiden_etunimet:
					ehdokkaiden_etunimet[nimi] = 1
				else:
					ehdokkaiden_etunimet[nimi] += 1
			if not rivi[2] in ehdokkaiden_sukunimet:
				ehdokkaiden_sukunimet[ rivi[2] ] = 1
			else:
				ehdokkaiden_sukunimet[ rivi[2] ] += 1

		etunimien_jarjestysluku = 0
		sukunimien_jarjestysluku = 0
		print("EHDOKKAIDEN YLEISIMMÄT ETUNIMET (väh. 5) \n")
		for etunimi in sorted(ehdokkaiden_etunimet.items(), key=lambda x: x[1], reverse=True):
			if etunimi[1] < 5:
				break
			etunimien_jarjestysluku += 1
			print("%d. %s: %d"  % (etunimien_jarjestysluku, etunimi[0], etunimi[1]) )
		print("\nEHDOKKAIDEN YLEISIMMÄT SUKUNIMET (useampi kuin yksi)\n")
		for sukunimi in sorted(ehdokkaiden_sukunimet.items(), key=lambda x: x[1], reverse=True):
			if sukunimi[1] < 2:
				break
			sukunimien_jarjestysluku += 1
			print("%d. %s: %d"  % (sukunimien_jarjestysluku, sukunimi[0], sukunimi[1]) )

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Vaalidatan prosessointia")
	parser.add_argument("tiedosto", help="File to process.")
	parser.add_argument("-y", "--yleisinnimi", help="Tulosta äänien jakautuminen puolueittain koko maassa", action='store_true')

	args = parser.parse_args()
	vaalidata = Vaalidata(args.tiedosto)
	if args.yleisinnimi:
		vaalidata.yleisin_nimi()