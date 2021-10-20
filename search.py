import click
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json
import pandas as pd
import os.path
import pandas as pd

save_path='/home/diegobalam/Fake_news/searchengine/data/'
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
 
driver = webdriver.Firefox(executable_path=r'./geckodriver', options=options)

@click.group()
def cli():
    """Websearch keywords in different search engines"""
    pass

#Datos

def exportar(results,name,path=save_path):
    with open(name+'.json', 'w') as file:
        json.dump(results, file, indent=4)
    
    dataf=pd.DataFrame.from_dict(results)
    dataf.to_csv(path+name+'.csv',index=False)


@cli.command(help='The number of items to process.')
def engines():
    print("duckduck")
    print("scholar")
    print("bing")
    print("researchgate")


@cli.command(help='Collect all search enginees')
@click.option('-n', default=20, help='number of results')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')
def collect(query,name,n=20,verbose=False):
    results={}
    print("scholar")
    results["scholar"]={}
    snippets=scholar_(query,name,n,verbose)
    results["scholar"]['results']=snippets
    results["scholar"]['total']=len(snippets)
    print("duckduck")
    results["duckduck"]={}
    snippets=duckduck_(query,name,n,verbose)
    results["duckduck"]['results']=snippets
    results["duckduck"]['total']=len(snippets)
    print("bing")
    results["bing"]={}
    snippets=bing_(query,name,n,verbose)
    results["bing"]['results']=snippets
    results["bing"]['total']=len(snippets)
    print("yahoo")
    results["yahoo"]={}
    snippets=yahoo_(query,name,n,verbose)
    results["yahoo"]['results']=snippets
    results["yahoo"]['total']=len(snippets)
    print("researchgate")
    results["researchgate"]={}
    snippets=researchgate_(query,name,n,verbose)
    results["researchgate"]['results']=snippets
    results["researchgate"]['total']=len(snippets)
    print(results)
    with open(name+'.json', 'w') as file:
        json.dump(results, file, indent=4)


def scholar_(query,name,n=20,verbose=False):
    driver.get('https://scholar.google.com.mx/')
    search_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.send_keys(query)
    search_box.submit()

    elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'gs_ri')]")))
    n_=len(elements)
    snippets=[]
    position=0
    while n_<n:
        for ele in elements:
            html=ele.get_attribute("outerHTML")
            soup = BeautifulSoup(html,  "html.parser")
            #soup=BeautifulSoup(html, 'lxml')
            a=soup.find_all("a")[0]
            title=a.text
            href=a['href']
            snippet=soup.find_all("div", class_="gs_rs")[0]
            snippets.append((position,title,href,snippet.text))
            if position==n-1:
                break
            position+=1
           
        try:
            next_page = driver.find_element_by_xpath("//div[@id='gs_n']//table//tr//td[last()]//a")
            href=next_page.get_attribute('href')
            driver.get(href)
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'gs_ri')]")))
            n_+=len(elements)
        except TimeoutException as e:
            break

    for ele in elements:
        html=ele.get_attribute("outerHTML")
        soup = BeautifulSoup(html,  "html.parser")
        #soup=BeautifulSoup(html, 'lxml')
        a=soup.find_all("a")[0]
        title=a.text
        href=a['href']
        try:
            snippet=soup.find_all("div", class_="gs_rs")[0].text
        except IndexError:
            snippet=""
        snippets.append({"position":position,"title":title,"href":href,"text":snippet})
        if position==n-1:
                break
        position+=1

    #print(snippets,query,n)
    exportar(snippets,name)
    return snippets
    
def bing_(query,name,n=20,verbose=False):
    driver.get('https://www.bing.com/?setlang=es')
    search_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.send_keys(query)
    search_box.submit()

    elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//li[contains(@class,'b_algo')]")))
    n_=len(elements)
    snippets=[] 
    position=0
    while n_<n:
        for ele in elements:
            html=ele.get_attribute("outerHTML")
            soup = BeautifulSoup(html,  "html.parser")
            #soup=BeautifulSoup(html, 'lxml')
            a=soup.find_all("a")[0]
            title=a.text
            href=a['href']
            #snippet=soup.find_all("p")[0]
            #snippets.append((position,title,href,snippet.text))
            try:
                snippet=soup.find_all("p")[0].text
            except IndexError:
                snippet=""
            snippets.append({"position":position,"title":title,"href":href,"text":snippet})
            if position==n-1:
                break
            position+=1
        try:
            next_page = driver.find_element_by_class_name("sb_pagN.sb_pagN_bp.b_widePag.sb_bp")
            href=next_page.get_attribute('href')
            driver.get(href)
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//li[contains(@class,'b_algo')]")))
            n_+=len(elements)
        except TimeoutException as e:
            break

    for ele in elements:
        html=ele.get_attribute("outerHTML")
        soup = BeautifulSoup(html,  "html.parser")
        #soup=BeautifulSoup(html, 'lxml')
        a=soup.find_all("a")[0]
        title=a.text
        href=a['href']
        try:
            snippet=soup.find_all("p")[0].text
        except IndexError:
            snippet=""
        snippets.append({"position":position,"title":title,"href":href,"text":snippet})
        if position==n-1:
                break
        position+=1
    #print(snippets,query,n)
    exportar(snippets,name)
    return snippets
    
@cli.command(help='Search on the google scholar enginee')
@click.option('-n', default=20, help='number of results ')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')
def bing(query,name,n=20,verbose=False):
    bing_(query,name,n,verbose)




@cli.command(help='Search on the google scholar enginee')
@click.option('-n', default=20, help='number of results ')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')
def scholar(query,name,n=20,verbose=False):
    scholar_(query,name,n,verbose)

def yahoo_(query,name,n=20,verbose=False):
    driver.get('https://news.yahoo.com/')
    search_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "p")))
    search_box.send_keys(query)
    search_box.submit()

    elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'dd NewsArticle')]")))
    n_=len(elements)
    snippets=[]
    position=0
    while n_<n:
        for ele in elements:
            html=ele.get_attribute("outerHTML")
            soup = BeautifulSoup(html,  "html.parser")
            #soup=BeautifulSoup(html, 'lxml')
            a=soup.find_all("a")[0]
            title=a.text
            href=a['href']
            snippet=soup.find_all("p", class_="s-desc")[0]
            snippets.append((position,title,href,snippet.text))
            if position==n-1:
                break
            position+=1
            
        try:
            next_page = driver.find_element_by_class_name("next")
            href=next_page.get_attribute('href')
            driver.get(href)
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'dd NewsArticle')]")))
            n_+=len(elements)
        except TimeoutException as e:
            break

    for ele in elements:
        html=ele.get_attribute("outerHTML")
        soup = BeautifulSoup(html,  "html.parser")
        #soup=BeautifulSoup(html, 'lxml')
        a=soup.find_all("a")[0]
        title=a.text
        href=a['href']
        try:
            snippet=soup.find_all("p", class_="s-desc")[0].text
        except IndexError:
            snippet=""
        snippets.append({"position":position,"title":title,"href":href,"text":snippet})
        if position==n-1:
                break
        position+=1

    #print(snippets,query,n)
    exportar(snippets,name)
    return snippets
                                                     
@cli.command(help='Search on the google scholar enginee')
@click.option('-n', default=20, help='number of results ')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')
def yahoo(query,name,n=20,verbose=False):
    yahoo_(query,name,n,verbose)


def researchgate_(query,name,n=20,verbose=False):
    driver.get('https://www.researchgate.net/')
    search_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME,"index-search-field__input")))
    search_box.send_keys(query)
    search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,"nova-legacy-e-icon.nova-legacy-e-icon--size-s.nova-legacy-e-icon--theme-bare.nova-legacy-e-icon--color-grey.nova-legacy-e-icon--luminosity-medium")))
    search_box.click()
         
    elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'nova-legacy-o-stack__item')]")))
    n_=len(elements)
    snippets=[]
    position=0
    while n_<n:
        for ele in elements:
            html=ele.get_attribute("outerHTML")
            soup = BeautifulSoup(html,  "html.parser")
            #soup=BeautifulSoup(html, 'lxml')
            a=soup.find_all("a")[0]
            title=a.text
            href=a['href']
            snippet=soup.find_all("div", class_="nova-legacy-o-stack__item")[0]
            snippets.append((position,title,href,snippet.text))
            if position==n-1:
                break
            position+=1
            
        try:
            search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,"nova-legacy-c-button.nova-legacy-c-button--align-center.nova-legacy-c-button--radius-m.nova-legacy-c-button--size-s.nova-legacy-c-button--color-grey.nova-legacy-c-button--theme-bare.nova-legacy-c-button--width-full")))
            href=next_page.get_attribute('href')
            driver.get(href)
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'nova-legacy-o-stack__item')]")))
            n_+=len(elements)
        except TimeoutException as e:
            break

    for ele in elements:
        html=ele.get_attribute("outerHTML")
        soup = BeautifulSoup(html,  "html.parser")
        #soup=BeautifulSoup(html, 'lxml')
        a=soup.find_all("a")[0]
        title=a.text
        href=a['href']
        try:
            snippet=soup.find_all("div", class_="gs_rs")[0].text
        except IndexError:
            snippet=""
        snippets.append({"position":position,"title":title,"href":href,"text":snippet})
        if position==n-1:
                break
        position+=1

    #print(snippets,query,n)
    exportar(snippets,name)
    return snippets
    
@cli.command(help='Search on the researchgate engine')
@click.option('-n', default=20, help='number of results ')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')

def researchgate(query,name,n=20,verbose=False):
    researchgate_(query,name,n,verbose)

def duckduck_(query,name,n=20,verbose=False):
    driver.get('https://duckduckgo.com/')
    search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "q")))
    search_box.send_keys(query)
    search_box.submit()

    elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'result__body')]")))
    nxt_page=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn--full")))
    n_=len(elements)
    while nxt_page and n_<n:
        nxt_page.click()
        try:
            nxt_page=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn--full")))
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'result__body')]")))
        except TimeoutException:
            nxt_page=None
            elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class,'result__body')]")))
        n_=len(elements)

    snippets=[]
    for position,ele in enumerate(elements):
        html=ele.get_attribute("outerHTML")
        soup = BeautifulSoup(html,  "html.parser")
        #soup=BeautifulSoup(html, 'lxml')
        title=soup.find_all("h2", class_="result__title")[0]
        href=soup.find_all("a", class_="result__a")[0]
        snippet=soup.find_all("div", class_="result__snippet")[0]
        #print(html)
        if not href['href'].startswith("https://duckduckgo.com/y.js?"):
            snippets.append({"position":position,"title":href.text,"href":href["href"],"text":snippet.text})

    snippets=snippets[:n]
    #print(snippets,query,n)
    exportar(snippets,name)

    return snippets



@cli.command(help='Search on the duckduckgo engine')
@click.option('-n', default=20, help='number of results ')
@click.option('--verbose', type=bool, default=False, help='Verbise')
@click.argument('query')
@click.argument('name')
def duckduck(query,name,n=20,verbose=False):
    duckduck_(query,name,n,verbose)
  
def base_(archivo,buscador,name,n=20):
    extension = os.path.splitext(archivo)
    if extension=='.json':
      with open(archivo) as file:
    	   data = json.load(file)
    if extension=='.csv':
      data= pd.read_csv (archivo) 
    if extension=='.xlsx':
      data= pd.read_excel (archivo) 
    base={}
    cont=0
    for i in range(0,len(data)):
        base[cont]={}
        query=data['query'][i]
        base[cont]['query']=query
        snippets=buscador_(query,n,verbose)
        results[cont]['results']=snippets
        cont+=1
    with open(name+'.json', 'w') as file:
        json.dump(base, file, indent=4)
   
    return base
   
@cli.command(help='Search on the data engine')
@click.option('-n', default=20, help='number of results ')
@click.argument('query')
@click.argument('buscador')
@click.argument('name')
def base(archivo,buscador,name,n=20):
    base_(archivo,buscador,name,n=20)     
    


if __name__ == '__main__':
    cli()
    driver.close()
