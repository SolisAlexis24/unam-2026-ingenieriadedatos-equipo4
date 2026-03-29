from scraper import most_read_scraper
import json

def main():
    sc = most_read_scraper()
    sc.scrape()
    


if __name__ == "__main__":
    main()
