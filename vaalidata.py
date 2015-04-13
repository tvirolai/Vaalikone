#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse, csv

class Vaalidata(object):

	def __init__(self, tiedosto):

		# Listan formaatti: vaalipiiri (0), ID (1), sukunimi (2), etunimi (3), puolue (4), ikä (5), sukupuoli (6), toimiiko kansanedustajana (7)
		with open(tiedosto, 'rt') as file:
			self.data = list(csv.reader(file))

		self.puolueet = {}

		for rivi in self.data:
			if not rivi[4] in self.puolueet:
				self.puolueet[ rivi[4].strip() ] = 1
			else:
				self.puolueet[ rivi[4].strip() ] += 1

	def keski_iat(self):

		puolueiden_iat = self.puolueet.copy()
		puolueissa_naisia = self.puolueet.copy()
		puolueiden_etunimet = {}
		puolueiden_sukunimet = {}

		for puolue in puolueissa_naisia:
			puolueissa_naisia[puolue] = 0

		for rivi in self.data:
			if rivi[6] == 'F':
				puolueissa_naisia[ rivi[4] ] += 1

			if not rivi[4] in puolueiden_etunimet:
				puolueiden_etunimet[ rivi[4] ] = [ rivi[3] ]
			else:
				puolueiden_etunimet[ rivi[4] ].append(rivi[3])

			if not rivi[4] in puolueiden_sukunimet:
				puolueiden_sukunimet[ rivi[4] ] = [ rivi[2] ]
			else:
				puolueiden_sukunimet[ rivi[4] ].append(rivi[2])

		for rivi in self.data:
			puolueiden_iat[ rivi[4] ] += int(rivi[5])

		for puolue in sorted(puolueiden_iat):
			keski_ika = float((puolueiden_iat[puolue]) / float(self.puolueet[puolue]) )
			naisten_osuus = float(puolueissa_naisia[puolue]) / float(self.puolueet[puolue]) * 100
			yleisin_etunimi = self.most_common(puolueiden_etunimet[puolue])
			yleisin_etunimi_maara = puolueiden_etunimet[puolue].count(yleisin_etunimi)
			yleisin_sukunimi = self.most_common(puolueiden_sukunimet[puolue])
			yleisin_sukunimi_maara = puolueiden_sukunimet[puolue].count(yleisin_sukunimi)
			if self.puolueet[puolue] > 1:
				print( "\n" + puolue.upper() + "\n")
				print("Ehdokkaita: %s" % (self.puolueet[puolue]))
				print("Keski-ikä: %.1f" % (keski_ika))
				print("Naisia: {0:.1f} %".format(naisten_osuus) )
				if yleisin_etunimi_maara > 1:
					print("Yleisin etunimi: {0} ({1} ehdokasta)".format(yleisin_etunimi, yleisin_etunimi_maara))
				if yleisin_sukunimi_maara > 1:
					print("Yleisin sukunimi: {0} ({1} ehdokasta)".format(yleisin_sukunimi, yleisin_sukunimi_maara))

		ika_lista = []
		naisten_iat_listana = []
		miesten_iat_listana = []
		for rivi in self.data:
			ika_lista.append(int(rivi[5]))
			if rivi[6].upper().strip() == 'F':
				naisten_iat_listana.append(int(rivi[5]))
			if rivi[6].upper().strip() == 'M':
				miesten_iat_listana.append(int(rivi[5]))

		print("\n")
		print("Kaikkien ehdokkaiden keski-ikä: {0:.1f}".format( self.average( self.poistanollat(ika_lista) ) ) )
		print("Naisehdokkaiden keski-ikä: {0:.1f}".format( self.average( self.poistanollat(naisten_iat_listana) ) ) )
		print("Miesehdokkaiden keski-ikä: {0:.1f}".format( self.average( self.poistanollat(miesten_iat_listana) ) ) )

	def poistanollat(self, lista):
		return [x for x in lista if x >= 18]

	def average(self, lista):
		return sum(lista) / len(lista)

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
		edellinen_maara = 0
		rivinumero = 0
		print("EHDOKKAIDEN YLEISIMMÄT ETUNIMET (väh. 5) \n")
		for etunimi in sorted(ehdokkaiden_etunimet.items(), key=lambda x: x[1], reverse=True):
			rivinumero += 1
			if etunimi[1] < 5:
				break
			etunimien_jarjestysluku += 1
			print("%d. %s: %d"  % (etunimien_jarjestysluku, etunimi[0], etunimi[1]) )
			edellinen_maara = etunimi[1]

		edellinen_maara = 0
		print("\nEHDOKKAIDEN YLEISIMMÄT SUKUNIMET (useampi kuin yksi)\n")
		for sukunimi in sorted(ehdokkaiden_sukunimet.items(), key=lambda x: x[1], reverse=True):
			if sukunimi[1] < 2:
				break
			sukunimien_jarjestysluku += 1
			print("%d. %s: %d"  % (sukunimien_jarjestysluku, sukunimi[0], sukunimi[1]) )
			edellinen_maara = sukunimi[1]

	def most_common(self, lst):
		return max(set(lst), key=lst.count)

	def debug(self):
		print(self.puolueet)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Vaalidatan prosessointia")
	parser.add_argument("tiedosto", help="File to process.")
	parser.add_argument("-y", "--yleisinnimi", help="Tulosta äänien jakautuminen puolueittain koko maassa", action='store_true')
	parser.add_argument("-d", "--debug", help="Ööö", action='store_true')
	parser.add_argument("-k", "--iat", help="Ööö", action='store_true')

	args = parser.parse_args()
	vaalidata = Vaalidata(args.tiedosto)
	if args.yleisinnimi:
		vaalidata.yleisin_nimi()
	if args.debug:
		vaalidata.debug()
	if args.iat:
		vaalidata.keski_iat()