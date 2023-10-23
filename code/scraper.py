import asyncio
from pyppeteer import launch
import json
from datetime import datetime, timedelta
import playwright
from playwright.async_api import async_playwright

async def get_ticket_link(source, destination, date, time, railcard, retdate, rettime):
    return_needed = False
    source = source.upper()
    destination = destination.upper()

    def format_time(t):
        try:
            hour = str(t.hour)
            minute = str(t.minute)
        except:
            hour = str(t.split(':')[0])
            minute = str(t.split(':')[1])

        if len(hour) == 1:
            hour = '0' + hour

        # get minute to closest 15, round up
        if int(minute) % 15 != 0:
            minute = str(int(minute) + 15 - (int(minute) % 15))
            if minute == '60':
                minute = '00'
                hour = str(int(hour) + 1)

        if len(minute) == 1:
            minute = '0' + minute

        # right time format 
        return hour + minute

    def format_date(date):
        print(date)
        # right date format ddmmyy
        if date != 'Today':
            return date.replace("-", "")
        
    # format date and time, and return date and time if needed
    date = format_date(date)
    time = format_time(time)
    if retdate != None and rettime != None:
        return_needed = True
        retdate = format_date(retdate)
        rettime = format_time(rettime)
    print(date, time, retdate, rettime)

    if return_needed:
        returnurl = "https://ojp.nationalrail.co.uk/service/timesandfares/{source}/{destination}/{date}/{time}/dep/{retdate}/{rettime}/dep"
        url = returnurl.format(source=source, destination=destination, date=date, time=time, retdate=retdate, rettime=rettime)
        ticket_link = await get_both_tickets(url)
    else: 
        singleurl = "https://ojp.nationalrail.co.uk/service/timesandfares/{source}/{destination}/{date}/{time}/dep"
        url = singleurl.format(source=source, destination=destination, date=date, time=time)
        ticket_link = await get_single_ticket(url)


    if ticket_link == None:
        return "I couldn't find any tickets for that journey, please try again."
    else:
        print(ticket_link)
        return ticket_link
       


def get_cheapest_ticket(source, destination, date, time, railcard, retdate, rettime):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(get_ticket_link(source, destination, date, time, railcard, retdate, rettime))
    loop.close()

    formatted_ticket_string = ''

    # if only one ticket is returned, results is a list
    if len(results) == 5:
        formatted_ticket_string += "<b>Outward Journey</b> ➡️<br>"
        formatted_ticket_string += "Price: " + results[1] + "<br>"
        formatted_ticket_string += "Estimated Time: " + str(results[2]) + "<br>"
        if results[3] != '0':
            formatted_ticket_string += "Changes: " + results[3] + "<br>"
        if results[4] == 'on time':
                formatted_ticket_string += "On time✅ <br>"
        elif results[4] == 'bus service':
                formatted_ticket_string += "Bus service🚌 <br>"
        formatted_ticket_string += "Ticket <a href='" + results[0] + "'>link</a><br>"
    # if multiple tickets are returned, results is a list of lists
    else:
        total_price = 0.0
        for i, result in enumerate(results):
            if i == 0:
                formatted_ticket_string += "<b>Outward Journey</b> ➡️<br>"
            else:
                formatted_ticket_string += "<b>Return Journey ⬅️</b><br>"
            price_str = result[1].replace('£', '').replace(',', '').strip()
            price_float = float(price_str)
            total_price += price_float
            formatted_ticket_string += "Price: " + result[1] + "<br>"
            
            formatted_ticket_string += "Estimated Time: " + str(result[2]) + "<br>"
            if result[3] != '0':
                formatted_ticket_string += "Changes: " + result[3] + "<br>"
            if result[4] == 'on time':
                formatted_ticket_string += "On time✅ <br>"
            elif result[4] == 'bus service':
                formatted_ticket_string += "Bus service🚌 <br>"
            formatted_ticket_string += "<br>"
        formatted_ticket_string += "Total Price: £" + str(total_price) + "<br>"
        formatted_ticket_string += "Ticket <a href='" + results[0][0] + "'>link</a><br>"
    return formatted_ticket_string


async def get_single_ticket(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        cheapest_fare_container = await page.query_selector('xpath=//td[contains(@class, "fare has-cheapest")]/ancestor::tr[1]')
        price_container = await cheapest_fare_container.query_selector('label.opsingle')

        if price_container:
            price = await page.evaluate('element => element.textContent', price_container)

        # get journey length
        duration_container = await cheapest_fare_container.query_selector('div.dur')
        duration = await page.evaluate('element => element.textContent', duration_container)
        duration = duration.strip()

        changes_container = await cheapest_fare_container.query_selector('div.chg')
        changes = await page.evaluate('element => element.textContent', changes_container)
        changes = changes.strip()
        changes = changes[0]

        # get status
        status_container = await cheapest_fare_container.query_selector('div.status div.journey-status')
        status = await page.evaluate('element => element.textContent', status_container)
        status = status.strip()

        ticket_info = [page.url, price, duration, changes, status]
        await browser.close()
        return ticket_info

async def get_both_tickets(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        cheapest_fare_containers = await page.query_selector_all('xpath=//td[contains(@class, "fare has-cheapest")]/ancestor::tr[1]')
        ticket_info = []

        for container in cheapest_fare_containers:
            # get price
            price_container = await container.query_selector('label.opreturnselected')
            price = await page.evaluate('element => element.textContent', price_container) 

            # get journey length
            duration_container = await container.query_selector('div.dur')
            duration = await page.evaluate('element => element.textContent', duration_container)
            duration = duration.strip()

            # get changes
            changes_container = await container.query_selector('div.chg')
            changes = await page.evaluate('element => element.textContent', changes_container) 
            changes = changes.strip()
            changes = changes[0]

            # get status
            status_container = await container.query_selector('div.status div.journey-status')
            status = await page.evaluate('element => element.textContent', status_container)
            status = status.strip()

            ticket_info.append([page.url, price, duration, changes, status])
        await browser.close()

        return ticket_info
