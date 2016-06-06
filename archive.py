#!/usr/bin/python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
#                  Парсер/Граббер http://pastebin.com/
#-----------------------------------------------------------------------

#Импорт модулей
from bs4 import BeautifulSoup;
import requests;
import sys;
import datetime;
import time;
import os;
import re;
import argparse;
import random;

#Урлы того что можно сграббить
urls = {'now':'http://pastebin.com/archive', 'trends':'http://pastebin.com/trends', 'week':'http://pastebin.com/trends/week','month':'http://pastebin.com/trends/month','year':'http://pastebin.com/trends/year', 'alltime':'http://pastebin.com/trends/all'};

#Урл пастебина, откуда будут скачиватся данные
RawData = 'http://pastebin.com/raw';

#HTTP заголовки, дабы сойти за браузер
headers = {'User-Agent': 'none','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.5'}

try:
	#Считываем файл с агентами
	agent = open('agents.txt').readlines();
except IOError:
	#Пишем что ошибка
	print('File not found, exiting');
	#Выходим
	sys.exit();

#Пустой глобальный список прокси
proxy = [];


def HelpComandLine(parse):
	#Выводим хэлп
	print (parse.print_help());
	#Выход
	exit();


#Функция сохранения данных
def SaveData(Path, Data):
	#Открываем файл
	FileData = open(Path + ".txt", 'w');
	#Записываем данные
	#FileData.write(Data.text.encode('utf-8'));
	FileData.write(Data.encode('utf-8'));
	#Закрываем его
	FileData.close();

#Функция захвата (ей передаем имя папки и урл что хотим сграббить)
def ChangeTrend(trend, LineUrl, prox = []):
#Если нет папки дата (это папка куда все сливаем)
	if not (os.path.exists('data')):
		#Создаем ее
		os.mkdir('data');
	#Если нет такого файла (с награбленным) в папке дата то
	if not os.path.isfile('data' + LineUrl + ".txt"):
		#Запрашиваем эту страницу
		r = GetPage(RawData + LineUrl, prox);
		#Если нет папки которая называется как тренд, те now, trends, week, month, year, alltime 
		if not (os.path.exists(trend)):
			#Создаем ее
			os.mkdir(trend);
		#Вызываем функцию сохранения данных в папку дата
		SaveData("data/"  + LineUrl, r);
		#Делаем символическую ссылку на файл что скачали +распологаем ссылку в папке тренда
		os.symlink("../data"  + LineUrl + ".txt", trend + LineUrl + ".txt");
		#Если все ок то пишем что сграбленно
		print LineUrl + " - Grabbed";
	else:
		#Иначе пишем что ничего нет
		print LineUrl + " - Found, not grabbed";

#Функция получения страницы с урлами которые будем граббить
def GetPage(url, proxi = []):
	#Берем случайный юзерагент
	headers['User-Agent'] = random.choice(agent)[:-1];
	#Если есть прокси то
	if (len(proxi) != 0):
		#Берем рандомный элемент списка
		RandomProxy = random.choice(proxi)[:-1];
		#Вывод того что мы грабим с прокси
		print ('Grabbing For Proxy ' + RandomProxy);
		#Добавляем ее в список
		proxies = {'http': 'http://' + RandomProxy + '/'};
		try:
			r  = requests.get(url, proxies=proxies, headers=headers, timeout=5);
			if r.status_code == 200:
				if re.findall(r'This page has been removed!', r.text):
					#Выводим что она удалена
					print (url + " - None");
				#Иначе
				else:
					return r.text;
		except Exception as e:
			print(RandomProxy + " Error !!!");
			#Засыпаем на определенное время
			SleepRandom = random.randint(1,5);
			print ("Sleep in %i" % SleepRandom);
			time.sleep(SleepRandom);
			#Пробум еще раз
			GetPage(url, proxi);
	else:
		try:
			r  = requests.get(url, headers=headers, timeout=5);
			if r.status_code == 200:
				if re.findall(r'This page has been removed!', r.text):
					#Выводим что она удалена
					print (url + " - None");
				#Иначе
				else:
					return r.text;
		except requests.exceptions.RequestException as e:
			print("Timeout");
		except Exception as e:
			print(e)
			print('Exiting')
			sys.exit();


#Главная функция
def main():
	#Создаем парсер
	parse = argparse.ArgumentParser(description='Парсер/Граббер pastebin.com')
	#Добавляем опцию что граббить
	parse.add_argument('-g', action='store', dest='grabbing', help='Что граббить (now, trends, week, month, year, alltime)');
	parse.add_argument('-p', action='store', dest='proxy', help='Имя файла с проксями');
	#Получаем аргументы
	args = parse.parse_args();
	#Если аргументов нет то
	if (args.grabbing == None or args.grabbing not in urls):
		HelpComandLine(parse);
	else:
		#Иначе выводим лого
		print("-----------------------------------------------------------------");
		print ("Grabbing to " + args.grabbing);
		#Выбираем тренд для граббинга
		url = urls[args.grabbing];
		#Если файл с проксями не указан то
		if (args.proxy != None):
			try:
				#Использум глобальный список
				global proxy;
				#Считываем файл с прокси
				proxy = open(args.proxy).readlines();
				#Функция получения страницы с урлами которые будем граббить
				RawPage = GetPage(url, proxy);
				print proxy;
			except IOError:
				#Пишем что ошибка
				print('Proxy file not found, exiting');
				#Выходим
				sys.exit();
		#Если проксей нет то
		else:
			#Граббим без использования прокси
			print ('Grabbing no proxy');
			#Функция получения страницы с урлами которые будем граббить
			RawPage = GetPage(url);
		#Список награбленного
		grab = [];
		#Передаем в суп, полученную страницу
		soup = BeautifulSoup(RawPage)
		#Ищем майлтайбл
		for table in soup.findAll("table", {"class": "maintable"}):	
			#Ищем все теги
			for archive in table.findAll("a"):
				#Если нету архив то, фильтруем то что не данные
				if (archive.get('href')[0:9] != '/archive/'):
					if (archive.get('href')[0:3] != '/u/'):
						if (archive.get('href')[0:4] != '/pro'):
							grab.append(archive.get('href'));
		#Выводим количество награбленных записей
		print ("Grabbed " + str(len(grab)) + " rows");
		print("-----------------------------------------------------------------");


		#Цикл по сграбленным адресам
		for LineUrl in grab:
			#Если выбрано сейчас то
			if (args.grabbing == 'now'):
				#Получаем текущюю дату
				NowData = str(datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d"));
				#Функция слива данных и в определенны папки
				ChangeTrend(NowData, LineUrl, proxy);

			#Далее в зависимости от  параметра ее вызываем
			if (args.grabbing == 'trends'):
				ChangeTrend('trends', LineUrl, proxy);

			if (args.grabbing == 'week'):
				ChangeTrend('week', LineUrl, proxy);

			if (args.grabbing == 'month'):
				ChangeTrend('month', LineUrl, proxy);

			if (args.grabbing == 'year'):
				ChangeTrend('year', LineUrl, proxy);

			if (args.grabbing == 'alltime'):
				ChangeTrend('alltime', LineUrl, proxy);

		print("-----------------------------------------------------------------");

#Если имя модуля майн то 
if __name__=="__main__":
	main();

