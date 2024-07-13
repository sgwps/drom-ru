import requests
from time import sleep
from bs4 import BeautifulSoup
import consts


file_number = 79
lines_in_file = 0
counter = 0
total = 0


params = ["Бренд", "Модель", "Год", "Цена", "URL", "ПТС", "Владельцы", "Розыск", "Ограничения", "Город"]
status_line = "status"

def get_info_about_car(url):
    sleep(consts.DELAY)
    print('parsing start')
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        header = soup.find_all("h1")[0].text
        print(header)
        if header == 'Запрошенная вами страница не существует!':
        	return {"code" : 404}
    except:
        return {status_line : False, params[4] : url}
    print('parsing end')
    info = {status_line : False, params[4] : url}
    if page.ok:
        try:
            soup = BeautifulSoup(page.content, 'html.parser')
            header = soup.find_all("h1")[0].text
            brand_and_model = header.split(", ")[0].split(" ", 2)
            year = header.split(", ")[1].split(" ")[0]
            city = header.split(", ")[1].split(" ", 3)[3]
            info[params[0]] = brand_and_model[1]
            info[params[1]] = brand_and_model[2]
            info[params[2]] = year
            info[params[9]] = city
            price = soup.find_all(class_="css-0 epjhnwz1")[0]
            info[params[3]] = ''.join(price.find_all(class_='css-eazmxc e162wx9x0')[0].text.split("\xa0")[:-1])
            table = soup.find_all("table", class_="css-xalqz7 eppj3wm0")[0].find_all("tbody")[0].find_all("tr")

            data = dict()
            for row in table:
                name = row.find_all('th')
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                if len(name) != 0 and len(cols) != 0:
                    data[name[0].text.strip()] = cols[0]

            for key in data.keys():
                info[key] = data.get(key, "")
                if key not in params:
                    params.append(key)

            additional_info = soup.find_all("div", attrs={"data-ga-stats-name":"gibdd_report"})
            if len(additional_info) != 0:
                divs = additional_info[0].find_all("div")
                for div in divs:
                    text = div.text
                    if 'ПТС' in text:
                        info[params[5]] = text
                    elif 'о регистрации' in text:
                        info[params[6]] = text
                    elif 'розыск' in text:
                        info[params[7]] = text
                    elif 'граничен' in text:
                        info[params[8]] = text            
            info[status_line] = True
        except:
            pass
    return info



# Запись массива информации об автомобилях в csv-файл
def write_to_csv_file(data):
    global file_number
    global lines_in_file
    global counter
    global total
    if data.get("code") == 404:
    	return
    
    if data[status_line]:
        line = ""
        for param in params:
            line += data.get(param, "")
            line += ";"
        if counter % 10 == 0:
            print(str(counter) + " out of " + str(total))
        counter += 1
        with open(consts.DATA_DIR + f"file{file_number}.csv", "a") as f:
            if lines_in_file == 0:
                for param in params:
                    f.write(param)
                    f.write(";")
                f.write("\n")
            f.write(line.replace("\n", " "))
            f.write("\n")
            lines_in_file += 1
        if lines_in_file == 200:
            file_number += 1
            lines_in_file = 0
    else:
        print("ERROR")
        with open(consts.DATA_DIR + "errors.csv", "a") as f:
            f.write(data.get(params[4]) + '\n')




def parse(urls):
    for url in urls:
        data = get_info_about_car(url)
        write_to_csv_file(data)


def parsed_urls():
    urls = []
    for i in range(1, file_number):
        with open(f"data/file{i}.csv", "r") as f:
            for line in f:
                urls.append(line.strip().split(";")[4])
    return urls


def first_try():
    global total
    urls = []
    with open(consts.URLS_DIR + "urls.csv", 'r') as f:
        for url in f:
            urls.append(url.strip())
    parsed = parsed_urls()
    urls1 = []
    for url in urls:
        if url not in parsed:
            urls1.append(url)
    total = len(urls1)
    print(total)
    input()
    parse(urls1)


def clear_errors():
    open(consts.DATA_DIR + "errors.csv", "w").close()

def read_errors():
    errors = []
    with open(consts.DATA_DIR + "errors.csv", 'r') as f:
        for line in f:
            errors.append(line.strip())
    return errors

def repeat():
    errors = read_errors()
    print(len(errors))
    clear_errors()
    parse(errors)
    return len(errors)




def main():
    first_try()
    while repeat() > 1000:
        pass


main()
