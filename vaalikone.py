#!/usr/bin/env python
# -*- coding: utf-8 -*

import json, argparse, operator, sys
from pprint import pprint

class Vaalikone(object):

	def __init__(self, tiedosto):
		json_data = open(tiedosto, 'r')
		self.data = json.load(json_data)
		json_data.close()
		self.paikkaluvut = {
		"01": 22,
		"02": 35,
		"03": 17,
		"04": 8,	
		"05": 1,
		"06": 14,
		"07": 19,
		"08": 17,
		"09": 16,
		"10": 16,
		"11": 10,
		"12": 18,
		"13": 7
		}
		
		self.kaikkiehdokkaat = 0

		# Listataan tähän kaikki ehdokkaita asettaneet puolueet datasta
		self.puolueet = []
		for ehdokas in self.data:
			if not ehdokas['party'] in self.puolueet:
				self.puolueet.append(ehdokas['party'])

	def tulosta(self):
		vertailuluvut = {}
		for key in sorted(self.paikkaluvut):
			vaalipiirin_nimi = ""
			for ehdokas in self.data:
				if key in ehdokas['district']:
					vaalipiirin_nimi = ehdokas['district']
					break
			print("\n" + vaalipiirin_nimi.upper() + "\n")
			
			for puolue in self.puolueet:
				puolue_vaalipiirissa = {}
				for ehdokas in self.data:
					if (ehdokas['party'] == puolue and key in ehdokas['district'] and int(ehdokas['views']) >= 0):
						puolue_vaalipiirissa[ ehdokas['name'] ] = int(ehdokas['views'])
				if len(puolue_vaalipiirissa) > 0:
					print("\n" + puolue + "\n")
				jarjestyspuolueessa = 0
				for puolueenehdokas in sorted(puolue_vaalipiirissa.items(), key=lambda x: x[1], reverse=True):
					jarjestyspuolueessa += 1
					vertailuluku = puolueenehdokas[1] / jarjestyspuolueessa
					vertailuluku = round(vertailuluku, 2)
					vertailuluvut[puolueenehdokas[0]] = vertailuluku
					print(puolueenehdokas[0] + " " + str(puolueenehdokas[1]) + " " + str(vertailuluku))


	def tilastoja(self):
		print("Ehdokkaita on yhteensä") + len(self.data)
		iat = []
		for ehdokas in self.data:
			#print ehdokas['name'] + " : " + ehdokas['age'] + " : " + ehdokas['party']
			ika = ehdokas['age']
			ika = [int(s) for s in ika.split() if s.isdigit()]
			# Karsitaan tyhjät arvot
			for i in ika:
				if i in range(18, 99):
					iat.append(i)
		keski_ika = float(sum(iat)) / float(len(iat))
		print("Ehdokkaiden keskimääräinen ikä on %.1f vuotta") % keski_ika

	def puolueidenkannatus(self):
		kannatusluvut = {}
		kaikki_katselut = 0
		print("\nKANNATUKSEN JAKAUTUMINEN KOKO MAASSA:\n")
		for ehdokas in self.data:
			kaikki_katselut += int(ehdokas['views'])
			if not ehdokas['party'] in kannatusluvut:
				kannatusluvut[ehdokas['party']] = int(ehdokas['views'])
			else:
				kannatusluvut[ehdokas['party']] += int(ehdokas['views'])
		numero = 0
		for puolue in sorted(kannatusluvut.items(), key=lambda x: x[1], reverse=True):
			numero += 1
			osuus = (float(puolue[1]) / float(kaikki_katselut) * 100)
			osuus = round(osuus)
			print(str(numero) + ". " + puolue[0] + " - " + str(puolue[1]) + " ääntä (" + str(osuus) + " %)")
		print("Ääniä annettu yhteensä %d" % kaikki_katselut)

	def lapimenijat(self):
		# Lasketaan vertailuluvut ehdokkaille, liitetään oliomuuttujan dataan
		self.vertailuluvut()
		# Käydään vaalipiirit yksitellen läpi
		tarkistusluku = 0
		for key in sorted(self.paikkaluvut):
			kansanedustajia_vaalipiirissa = self.paikkaluvut[key]
			# Lasketaan käsiteltävän vaalipiirin korkeimmat vertailuluvut
			vaalipiirin_vertailuluvut = []
			vaalipiirin_nimi = ""
			for ehdokas in self.data:
				if key in ehdokas['district']:
					vaalipiirin_nimi = ehdokas['district']
					break
			for ehdokas in self.data:
				if key in ehdokas['district']:
					vaalipiirin_vertailuluvut.append(float(ehdokas['vertailuluku']))
			vaalipiirin_vertailuluvut = sorted(vaalipiirin_vertailuluvut, reverse=True)
			print("\n" + vaalipiirin_nimi.upper() + "\n")
			ehdokkaan_jarjestysnumero = 0
			for i in vaalipiirin_vertailuluvut:
				for ehdokas in self.data:
					if ehdokas['vertailuluku'] == i and key in ehdokas['district']:
						tarkistusluku += 1
						ehdokkaan_jarjestysnumero += 1
						# Debug
						#sys.stdout.write(str(ehdokkaan_jarjestysnumero) + ". " + str(ehdokas['vertailuluku']) + " " + ehdokas['name'] + " (" + ehdokas['party'] + ") " + ehdokas['views'] + ehdokas['district'])
						sys.stdout.write(str(ehdokkaan_jarjestysnumero) + ". " + ehdokas['name'] + " (" + ehdokas['party'] + ") " + ehdokas['views'])

						if (ehdokkaan_jarjestysnumero < kansanedustajia_vaalipiirissa):
							sys.stdout.write(" LÄPI\n")
						elif (ehdokkaan_jarjestysnumero == kansanedustajia_vaalipiirissa):
							sys.stdout.write(" LÄPI\n --------------------------\n")
						else:
							sys.stdout.write("\n")
		print(tarkistusluku)

	def vertailuluvut(self):
		vertailuluvut = {}
		for key in sorted(self.paikkaluvut):
			for puolue in self.puolueet:
				puolue_vaalipiirissa = {}
				puolueen_aanet_vaalipiirissa = 0
				for ehdokas in self.data:
					if (ehdokas['party'] == puolue and key in ehdokas['district'] and int(ehdokas['views']) >= 0):
						puolue_vaalipiirissa[ ehdokas['name'] ] = int(ehdokas['views'])
						puolueen_aanet_vaalipiirissa += int(ehdokas['views'])
				jarjestyspuolueessa = 0
				#print(str(key) + " " + puolue + " " + str(puolueen_aanet_vaalipiirissa))
				for puolueenehdokas in sorted(puolue_vaalipiirissa.items(), key=lambda x: x[1], reverse=True):
					jarjestyspuolueessa += 1
					vertailuluku = puolueen_aanet_vaalipiirissa / jarjestyspuolueessa
					vertailuluku = round(vertailuluku, 2)
					vertailuluvut[puolueenehdokas[0]] = vertailuluku
		for ehdokas in self.data:
			ehdokas['vertailuluku'] = vertailuluvut[ehdokas['name']]
			# DEBUG:
			#print(ehdokas['name'] + " " + str(vertailuluvut[ehdokas['name']]))
		#return vertailuluvut

	def ehdokkaidenkannatus_vaalipiireittain(self, piiri):
		vaalipiiri = ""
		count = 0
		for ehdokas in self.data:
			if (piiri in ehdokas['district']):
				if (ehdokas['district'] != vaalipiiri):
					vaalipiiri = ehdokas['district']
					print("\n" + vaalipiiri.upper() + "\n")
				for puolue in self.puolueet:
					if puolue == ehdokas['party']:
						print(ehdokas['name'] + " " + ehdokas['party'] + " " + ehdokas['views'])
				count += 1
				self.kaikkiehdokkaat += 1
		print("Ehdokkaita: " + str(count))

	def kannatus_vaalipiireittain(self, piiri):
		# Funktio palauttaa tuple-listan muotoa [(puolue, äänisaalis vaalipiirissä)]
		puolueet_vaalipiireittain = {}
		vaalipiiri = ""
		for ehdokas in self.data:
			if (piiri in ehdokas['district']):
				if not ehdokas['party'] in puolueet_vaalipiireittain:
					puolueet_vaalipiireittain[ehdokas['party']] = int(ehdokas['views'])
					if (vaalipiiri == ""):
						vaalipiiri = ehdokas['district']
				else:
					puolueet_vaalipiireittain[ehdokas['party']] += int(ehdokas['views'])
		kannatus = [x for x in sorted(puolueet_vaalipiireittain.items(), key=lambda x: x[1], reverse=True)]
		return kannatus

	def laskuri(self):
		for key in sorted(self.paikkaluvut):
			vaalipiirin_nimi = ""
			for ehdokas in self.data:
				if key in ehdokas['district']:
					vaalipiirin_nimi = ehdokas['district']
					break
			print("\n" + vaalipiirin_nimi.upper() + "\n")
			vaalipiirin_kokonaisaanimaara = 0
			for ehdokas in self.data:
				if key in ehdokas['district']:
					vaalipiirin_kokonaisaanimaara += int(ehdokas['views'])
			#print(vaalipiirin_kokonaisaanimaara)
			aanet_vaalipiirissa = self.kannatus_vaalipiireittain(key)
			for aanipiiri in aanet_vaalipiirissa:
				kannatusosuus = round((float(aanipiiri[1]) / float(vaalipiirin_kokonaisaanimaara ) * 100), 1)
				print(aanipiiri[0] + " " + str(aanipiiri[1]) + " (" + str(kannatusosuus) + " %)")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Vaalikone")
	parser.add_argument("tiedosto", help="File to process.")
	args = parser.parse_args()
	vaalikone = Vaalikone(args.tiedosto)
	#vaalikone.puolueidenkannatus()
	#vaalikone.tulosta()
	#vaalikone.kannatus_vaalipiireittain()
	#vaalikone.vertailuluvut()
	vaalikone.laskuri()
	#vaalikone.lapimenijat()
	vaalikone.puolueidenkannatus()