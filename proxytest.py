#!/usr/bin/python
# -*- coding: utf-8 -*-

#Импорт модулей
import argparse;
import sys;
import requests;

#Главная функция
def main():
	#Создаем парсер
	parse = argparse.ArgumentParser(description='Самый простой чекер HTTP прокси')
	#Добавляем опцию что граббить
	parse.add_argument('-f', action='store', dest='ProxyFileName', help='Имя файла граббинга');
	#Получаем аргументы
	args = parse.parse_args();
	#Если аргументов нет то
	if (args.ProxyFileName == None):
		#Выводим хэлп
		print (parse.print_help());
		#Выход
		exit();
	#Иначе
	else:
		#Начало обработки ошибок
		try:
			#Открываем файл и запихиваем его в список
			ProxyList = open(args.ProxyFileName).readlines();
		#Если файла нет то перехватываем ошибку
		except IOError:
			#Пишем что ошибка
			print('File not found, exiting');
			#Выходим
			sys.exit();
		#Цикл по списку прокси
		for Proxy in ProxyList:
			#Добовляем его в список
			proxies = {'http': 'http://' + Proxy[:-1] + '/'};
			#Начало обработки ошибок
			try:
				#print ('Test proxy ' + Proxy[:-1]);
				#Дедаем запрос
				page = requests.get('http://ipchicken.com/', proxies=proxies, timeout=5);
				#Если страница с кодом 200
				if page.status_code == 200:
					#Пишем прокси рабочий
					print (Proxy[:-1]);
			#Если произошла с прокси ошибка то
			except requests.exceptions.RequestException as e:
				#Ничего не делаем
				pass;

#Если имя модуля майн то 
if __name__=="__main__":
	main();
