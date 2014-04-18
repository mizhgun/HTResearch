# HTResearch
A repository for the Anti-Trafficking Atlas.

## What does this do?
The Anti-Trafficking Atlas is a website that provides a centralized way to government and research professionals
 to do the following:

1. Find contact information for organizations and contacts involved in the anti-trafficking effort,
2. Share your own contact information so you can connect with other anti-trafficking professionals,
3. Request new organizations to be added to our index,
3. Search for research publications and news articles in the human trafficking domain, and,
4. View breakdowns of organizations by various properties and their partnerships among other organizations

## How does it do it?
The Anti-Trafficking Atlas uses Scrapy and MongoDB to scrape the websites of anti-human trafficking organizations for
information about the organization, as well as its members and partners. It then uses the various links on each page
of the organization's site to crawl to new organizations and apply the same technique to them. Once organizations are
scraped, they are ranked by the amount of available content and by the amount of connections they have to other
organizations.

## So, what's the catch?
Currently, the Anti-Trafficking Atlas only performs web crawls on anti-trafficking organizations operating in India.
In the future, we hope to expand our efforts to the globe and provide information for any country you might be
interested in.