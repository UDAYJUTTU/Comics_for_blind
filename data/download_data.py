from selenium import webdriver
import urllib
import time
start_year=1979
end_year=2020
start_month=1
end_month=12
driver=webdriver.Chrome(r'path_to\chromedriver')
counter=1
for year in range(start_year, end_year+1):
    for month in range(start_month,end_month+1):
        url='http://pt.jikos.cz/garfield/'
        url=url+str(year)+str('/{}/'.format(month))
        driver.get(url)
        time.sleep(2)
        comics=driver.find_elements_by_tag_name("img")
        for comic in comics:
            image=comic.get_attribute("src")
            comic_image=urllib.request.urlopen(image)
            local_image=open(r'path_to\images\{}.jpg'.format(counter),'wb')
            local_image.write(comic_image.read())
            local_image.close()
            counter+=1
    time.sleep(2)