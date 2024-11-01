from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Launch the Chrome browser
driver = webdriver.Chrome()

# Navigate to the website
driver.get("https://library.blinkops.com/workflows?security=Cloud%20Security")
time.sleep(10)

#To store the required data
result_descriptions=[]
apps_in_results=[]
#The while loop runs till no more new boxes are detected
#In the HTML code, only a certain number of boxes have been loaded (around 100) the rest will load
# when the user scrolls down. Hence, in 1 iteration of the below loop. We detect and obtain these boxes (around 100 at once)
# and click on each box and hover over the icons and obtain the hover text.
# Once all the boxes have been exhausted, we move to the next iteration

# At the next iteration, we again extract the boxes that have been loaded at our current position in the scroll bar. 
# Again, it maybe around 100. However, there would be overlap with the previous boxes that were loaded. To avoid getting duplicate
# data, we remove these duplcates.
# We then repeat the process in the previous steps

extracted_count=0
explored_boxes_in_scrollable_container=set()
detected_boxes=[]
while True:
    #Since we load boxes at each iteration, there maybe an overlap in the boxes loaded at t and at t-1,t-2,t-3....  
    # The earlier loaded boxes are stored in explored_boxes_in_scrollable_container so that we can check which loaded boxes are new and not already loaded and processed earlier

    #We get all loaded boxes
    time.sleep(5)
    detected_boxes = driver.find_elements(By.XPATH, "/html/body/al-root/div/al-automations-library/div/div[2]/div[2]/virtual-scroller/div[2]/*")
    time.sleep(5)
    
    #We remove the boxes loaded earlier
    detected_boxes = [box for box in detected_boxes if box not in explored_boxes_in_scrollable_container]
    
    #debugging purposes
    explored_boxes_in_scrollable_container=explored_boxes_in_scrollable_container.union(set(detected_boxes))
    
    #We now process each loaded box
    for i in range(len(detected_boxes)):
        #scroll the box into view to allow to click
        time.sleep(1)
        ActionChains(driver).scroll_to_element(detected_boxes[i]).perform()
        time.sleep(1)
        
        detected_boxes[i].click()
        time.sleep(3)

        #obtain the container_title (result description according to assignment sheet)
        container_title=detected_boxes[i].find_element(By.XPATH,"/html/body/div/div[2]/div/mat-dialog-container/al-automation-overview/div/div[1]/div/div").text

        #find the icons
        hoverables=driver.find_elements(By.XPATH, "/html/body/div/div[2]/div/mat-dialog-container/al-automation-overview/div/div[2]/div/div[1]/al-overview-details/div[3]/ui-trigger-actions-indicator/div/div/*")

        #loop through each icon to obtain the hover text
        apps_in_result=[]
        for hoverable in hoverables:
            #hover over the icon
            hover = ActionChains(driver).move_to_element(hoverable)
            hover.perform()

            #obtain the html code when hovering is happening because the html code for the text that appears while hovering
            #only appears when hovering is being done
            html=driver.page_source

            #obtain the text while hovering over the icons
            soup = BeautifulSoup(html,'html.parser')
            app=soup.find_all('div',{'class':'cdk-overlay-connected-position-bounding-box'})[0].find('div',{'class':'content ng-star-inserted'}).find('span').text
            apps_in_result.append(app)
        
        
        #click the exit button of the window we are in.
        exit_button=driver.find_element(By.XPATH, "/html/body/div/div[2]/div/mat-dialog-container/al-automation-overview/div/div[1]/ui-icon/span")

        exit_button.click()

        #Store all results
        #store the result description
        extracted_count=extracted_count+1
        print('extracted count: ',extracted_count)
        print(container_title)
        result_descriptions.append(container_title)
        #store the apps in results
        print(apps_in_result)
        apps_in_results.append(apps_in_result)

        time.sleep(1)
    
    # break loop if no more boxes present
    if len(detected_boxes)==0:
        break

dict={'Result #':range(1,1+len(result_descriptions)),'Result Descriptions':result_descriptions,'Apps in the Result':apps_in_results}
df=pd.DataFrame(dict)
df.to_csv('Apps in Results')
