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

#Считываем файл с агентами
agent = open('agents.txt').readlines();

def HelpComandLine(parse):
	#Выводим хэлп
	print (parse.print_help());
	#Выход
	exit();

#Функция получения страницы
def GetPage(url):
	#Берем случайный юзерагент
	headers['User-Agent'] = random.choice(agent)[:-1];
	#Делаем запрос
	try:
		r  = requests.get(url, headers=headers);
	#Если исключение то выходим
	except Exception as e:
		print(e);
		print('Exiting');
		sys.exit();
	#Ищем через регулярку что страница может быть удалена
	if re.findall(r'This page has been removed!', r.text):
		#Выводим что она удалена
		print line[:-1] + " - None";
	#Иначе
	else:
		#Результат возвращаем
		return r;

#Функция сохранения данных
def SaveData(Path, Data):
	#Открываем файл
	FileData = open(Path + ".txt", 'w');
	#Записываем данные
	FileData.write(Data.text.encode('utf-8'));
	#Закрываем его
	FileData.close();

#Функция захвата (ей передаем имя папки и урл что хотим сграббить)
def ChangeTrend(trend, LineUrl):
	#Если нет папки дата (это папка куда все сливаем)
	if not (os.path.exists('data')):
		#Создаем ее
		os.mkdir('data');
	#Если нет такого файла (с награбленным) в папке дата то
	if not os.path.isfile('data' + LineUrl + ".txt"):
		#Запрашиваем эту страницу
		r = GetPage(RawData + LineUrl);
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


#Главная функция
def main():
	#Создаем парсер
	parse = argparse.ArgumentParser(description='Парсер/Граббер pastebin.com')
	#Добавляем опцию что граббить
	parse.add_argument('-g', action='store', dest='grabbing', help='Что граббить (now, trends, week, month, year, alltime)');
	#Получаем аргументы
	args = parse.parse_args();
	#Если аргументов нет то
	if (args.grabbing == None):
		HelpComandLine(parse);
	else:
		#Иначе выводим лого
		print("-----------------------------------------------------------------");
		print ("Grabbing to " + args.grabbing);

		#Список награбленного
		grab = [];
		if (args.grabbing not in urls):
			HelpComandLine(parse);

		#Берем случайный юзерагент
		headers['User-Agent'] = random.choice(agent)[:-1];
		#Урл архива
		url = urls[args.grabbing];
		#Делаем запрос
		try:
			r  = requests.get(url, headers=headers);
		except Exception as e:
			print(e)
			print('Exiting')
			sys.exit()

		#Передаем в суп, полученную страницу
		soup = BeautifulSoup(r.text)

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
				ChangeTrend(NowData, LineUrl);

			#Далее в зависимости от  параметра ее вызываем
			if (args.grabbing == 'trends'):
				ChangeTrend('trends', LineUrl);

			if (args.grabbing == 'week'):
				ChangeTrend('week', LineUrl);

			if (args.grabbing == 'month'):
				ChangeTrend('month', LineUrl);

			if (args.grabbing == 'year'):
				ChangeTrend('year', LineUrl);

			if (args.grabbing == 'alltime'):
				ChangeTrend('alltime', LineUrl);

		print("-----------------------------------------------------------------");


#Если имя модуля майн то 
if __name__=="__main__":
	main();
