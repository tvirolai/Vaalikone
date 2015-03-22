#!/usr/bin/env python
# -*- coding: utf-8 -*

import json, argparse, operator, sys, csv

class Vaalikone(object):

	def __init__(self, tiedosto):
		json_data = open(tiedosto, 'r')
		self.data = json.load(json_data)
		json_data.close()

		# Haetaan Ylen vaalikoneen avoimena datana julkaistusta sisällöstä lisätietoja
		# Listan formaatti: sukunimi, etunimi, ikä, sukupuoli, toimiiko kansanedustajana (0, 1)
		with open('vastaukset.csv', 'rt') as file:
			self.lisatiedot = list(csv.reader(file))

		for rivi in self.lisatiedot:
			nimi = rivi[1] + " " + rivi[0]
			for ehdokas in self.data:
				if ehdokas['name'].upper() == nimi.upper():
					#print(ehdokas['name'].upper() + " " + nimi.upper() )	
					ehdokas['edustaja'] = rivi[4]
					next
		for ehdokas in self.data:
			if not 'edustaja' in ehdokas:
				ehdokas['edustaja'] = -1

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

		self.uusia_kansanedustajia = 0

		self.vaaliliitot = {
		"01": ["Suomen Kristillisdemokraatit (KD)", "Köyhien Asialla"],
		"02": ["Kansallinen Kokoomus", "Suomen ruotsalainen kansanpuolue"],
		"03": ["Suomen Kommunistinen Puolue", "Kommunistinen Työväenpuolue"],
		"13": ["Perussuomalaiset", "Suomen Kristillisdemokraatit (KD)"]
		}
		
		self.kaikkiehdokkaat = 0

		# Listataan tähän kaikki ehdokkaita asettaneet puolueet datasta
		self.puolueet = []
		for ehdokas in self.data:
			if not ehdokas['party'] in self.puolueet:
				self.puolueet.append(ehdokas['party'])

		# Tähän alustetaan dict-muuttuja puolueiden paikkamäärien laskemista varten
		# Määrät asetetaan läpimenijöiden tulostamisen yhteydessä.
		self.paikkamaarat = {}
		for puolue in self.puolueet:
			self.paikkamaarat[puolue] = 0

		self.paikkamaarat_nyt = {
			"Kansallinen Kokoomus": 44,
			"Suomen Sosialidemokraattinen Puolue": 42,
			"Perussuomalaiset": 39,
			"Suomen Keskusta": 35,
			"Vasemmistoliitto": 14,
			"Vihreä liitto": 10,
			"Suomen ruotsalainen kansanpuolue": 9,
			"Suomen Kristillisdemokraatit (KD)": 6
		}

		for puolue in self.puolueet:
			if not puolue in self.paikkamaarat_nyt:
				self.paikkamaarat_nyt[puolue] = 0

	def puolueiden_kannatus_koko_maassa(self):
		# Tulosta
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
				for puolueenehdokas in sorted(puolue_vaalipiirissa.items(), key=lambda x: x[1], reverse=True):
					print(puolueenehdokas[0] + " " + str(puolueenehdokas[1]))

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
		self.vaaliliittojen_vertailuluvut()
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

						sys.stdout.write(str(ehdokkaan_jarjestysnumero) + ". " + ehdokas['name'] + " (" + ehdokas['party'] + ") " + ehdokas['views'] )

						if (ehdokkaan_jarjestysnumero < kansanedustajia_vaalipiirissa):
							if ehdokas['edustaja'] == "0":
								sys.stdout.write(" UUSI")
								self.uusia_kansanedustajia += 1 
							sys.stdout.write("\n")
							ehdokas['lapi'] = 1
							self.paikkamaarat[ ehdokas['party'] ] += 1
						elif (ehdokkaan_jarjestysnumero == kansanedustajia_vaalipiirissa):
							if ehdokas['edustaja'] == "0":
								sys.stdout.write(" UUSI")
								self.uusia_kansanedustajia += 1
							sys.stdout.write("\n --------------------------\n")
							self.paikkamaarat[ ehdokas['party'] ] += 1
							ehdokas['lapi'] = 1
						else:
							if ehdokas['edustaja'] == "1":
								sys.stdout.write(" PUTOAA")

							sys.stdout.write("\n")
							ehdokas['lapi'] = 0
		print(tarkistusluku)

	def vertailuluvut(self):
		# Funktio laskee ehdokkaiden vertailuluvun ja tallentaa sen ehdokkaan tietoihin oliomuuttujassa self.data
		# Kerätään vertailuluvut aluksi dict-muotoiseen muuttujaan ja syötetään funktion lopuksi oliomuuttujaan.
		vertailuluvut = {}
		# Käydään vaalipiirit läpi järjestyksessä
		for key in sorted(self.paikkaluvut):
			vaalipiiri = key
			# Vaalipiirin sisällä puolueet
			for puolue in self.puolueet:
				# Lasketaan ensin kunkin puolueen kokonaisäänimäärä vaalipiirissä vertailuluvun laskemisen pohjaksi.
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

	def vaaliliittojen_vertailuluvut(self):
		# Lasketaan erillisessä funktiossa vielä vaaliliittojen vaikutus vertailulukuihin
		# Näiden ehdokkaiden luvut siis muiden tavoin jo aiemmin (väärin), mutta korjataan jälkikäteen oliomuuttujaan.
		# Tämä funktio on ehkä toteutettu tarpeettoman hankalasti, mutta se toimii.

		vaaliliittojen_aanet = {
		'1': 0,
		'2': 0,
		'3': 0,
		'4': 0
		}

		vertailuluvut_vaaliliitoissa = {}

		vaaliliitto_yksi = {}
		vaaliliitto_kaksi = {}
		vaaliliitto_kolme = {}
		vaaliliitto_nelja = {}

		vaaliliittojen_ehdokkaat = 0

		for ehdokas in self.data:
			if ("01" in ehdokas['district'] and ehdokas['party'] in self.vaaliliitot["01"] ):
				vaaliliittojen_aanet['1'] += int(ehdokas['views'])
				vaaliliittojen_ehdokkaat += 1
				vaaliliitto_yksi[ ehdokas['name'] ] = int(ehdokas['views'])
			elif ("03" in ehdokas['district'] and ehdokas['party'] in self.vaaliliitot["02"]):
				vaaliliittojen_aanet['2'] += int(ehdokas['views'])
				vaaliliittojen_ehdokkaat += 1
				vaaliliitto_kaksi[ ehdokas['name'] ] = int(ehdokas['views'])
			elif ("03" in ehdokas['district'] and ehdokas['party'] in self.vaaliliitot["03"]):
				vaaliliittojen_aanet['3'] += int(ehdokas['views'])
				vaaliliittojen_ehdokkaat += 1
				vaaliliitto_kolme[ ehdokas['name'] ] = int(ehdokas['views'])
			elif ("13" in ehdokas['district'] and ehdokas['party'] in self.vaaliliitot["13"]):
				vaaliliittojen_aanet['4'] += int(ehdokas['views'])
				vaaliliittojen_ehdokkaat += 1
				vaaliliitto_nelja[ ehdokas['name'] ] = int(ehdokas['views'])

		jarjestysvaaliliitossa = 0

		for vaaliliitonehdokas in sorted(vaaliliitto_yksi.items(), key=lambda x: x[1], reverse=True):
			jarjestysvaaliliitossa += 1
			vertailuluku = vaaliliittojen_aanet['1'] / jarjestysvaaliliitossa
			vertailuluku = round(vertailuluku, 2)
			vertailuluvut_vaaliliitoissa[vaaliliitonehdokas[0]] = vertailuluku

		jarjestysvaaliliitossa = 0

		for vaaliliitonehdokas in sorted(vaaliliitto_kaksi.items(), key=lambda x: x[1], reverse=True):
			jarjestysvaaliliitossa += 1
			vertailuluku = vaaliliittojen_aanet['2'] / jarjestysvaaliliitossa
			vertailuluku = round(vertailuluku, 2)
			vertailuluvut_vaaliliitoissa[vaaliliitonehdokas[0]] = vertailuluku

		jarjestysvaaliliitossa = 0

		for vaaliliitonehdokas in sorted(vaaliliitto_kolme.items(), key=lambda x: x[1], reverse=True):
			jarjestysvaaliliitossa += 1
			vertailuluku = vaaliliittojen_aanet['3'] / jarjestysvaaliliitossa
			vertailuluku = round(vertailuluku, 2)
			vertailuluvut_vaaliliitoissa[vaaliliitonehdokas[0]] = vertailuluku

		jarjestysvaaliliitossa = 0

		for vaaliliitonehdokas in sorted(vaaliliitto_nelja.items(), key=lambda x: x[1], reverse=True):
			jarjestysvaaliliitossa += 1
			vertailuluku = vaaliliittojen_aanet['4'] / jarjestysvaaliliitossa
			vertailuluku = round(vertailuluku, 2)
			vertailuluvut_vaaliliitoissa[vaaliliitonehdokas[0]] = vertailuluku

		for ehdokas in self.data:
			if ehdokas['name'] in vertailuluvut_vaaliliitoissa:
				ehdokas['vertailuluku'] = vertailuluvut_vaaliliitoissa[ehdokas['name']]

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

	def paikkamaarien_tulostus(self):
		paikkojen_muutos = 0
		print("\nPUOLUEIDEN PAIKKAMÄÄRÄT UUDESSA EDUSKUNNASSA:\n")
		for puolue in sorted(self.paikkamaarat.items(), key=lambda x: x[1], reverse=True):
			if self.paikkamaarat_nyt[puolue[0]] > puolue[1]:
				paikkojen_muutos = self.paikkamaarat_nyt[puolue[0]] - puolue[1]
				print(puolue[0] + " : " + str(puolue[1]) + " paikkaa (muutos: -" + str(paikkojen_muutos) + ")")
			elif self.paikkamaarat_nyt[puolue[0]] < puolue[1]:
				paikkojen_muutos = puolue[1] - self.paikkamaarat_nyt[puolue[0]]
				print(puolue[0] + " : " + str(puolue[1]) + " paikkaa (muutos: +" + str(paikkojen_muutos) + ")")
			elif self.paikkamaarat_nyt[puolue[0]] == puolue[1]:
				print(puolue[0] + " : " + str(puolue[1]) + " paikkaa (ei muutosta)")

	def tulosta_vain_lapimenijat(self):
		print("\nUUDET KANSANEDUSTAJAT PUOLUEITTAIN:\n")
		for puolue in sorted(self.puolueet):
			if (self.paikkamaarat[puolue] > 0):
				print("\n" + puolue.upper() + "\n")
				for ehdokas in self.data:
					if (ehdokas['party'] == puolue and ehdokas['lapi'] == 1):
						sys.stdout.write(ehdokas['name'] + " (" + str(ehdokas['views']) + ")")
						if (ehdokas['edustaja'] == "0"):
							sys.stdout.write(" UUSI\n")
						else:
							print("")
		uusien_osuus = float(self.uusia_kansanedustajia) / 200 * 100
		uusien_osuus = round(uusien_osuus, 2)
		print("\nUusia kansanedustajia: " + str(self.uusia_kansanedustajia) + " (" + str(uusien_osuus) + " %)" )

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Vaalikone")
	parser.add_argument("tiedosto", help="File to process.")
	args = parser.parse_args()
	vaalikone = Vaalikone(args.tiedosto)
	#vaalikone.puolueidenkannatus()
	#vaalikone.puolueiden_kannatus_koko_maassa()

	#vaalikone.kannatus_vaalipiireittain()
	#vaalikone.vertailuluvut()
	#vaalikone.laskuri()
	vaalikone.lapimenijat()
	vaalikone.tulosta_vain_lapimenijat()
	#vaalikone.puolueidenkannatus()
	#vaalikone.paikkamaarien_tulostus()