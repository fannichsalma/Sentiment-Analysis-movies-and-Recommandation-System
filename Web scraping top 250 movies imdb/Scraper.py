import requests
from bs4 import BeautifulSoup
import csv


headers = {
    'Accept-Language': 'en-US,en;q=0.9',
}

base_url = "https://www.imdb.com/search/title/?title_type=feature&num_votes=10000,&sort=user_rating,desc&start={}&ref_=adv_nxt"
start_index = 1
movies_per_page = 50
total_movies = 10000
page = 1

try:
    with open('Top_10000_Movies_IMDb.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Movie Name", "Rating", "Runtime", "Genre", "Metascore", "Plot", "Directors", "Stars", "Votes", "Gross", "Link"])

        movie_id = 1

        while start_index <= total_movies:
            url = base_url.format(start_index)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            movie_list = soup.find_all('div', class_='lister-item-content')

            for movie in movie_list:
                movie_name = movie.h3.a.text
                rating = movie.find('div', class_='ratings-bar').strong.text
                runtime = movie.find('span', class_='runtime').text
                genre = movie.find('span', class_='genre').text.strip()
                metascore = movie.find('span', class_='metascore').text.strip() if movie.find('span', class_='metascore') else ''
                plot = movie.find_all('p', class_='text-muted')[1].text.strip()
                directors = movie.find_all('p')[2].find_all('a')
                directors = [director.text for director in directors]
                stars = movie.find_all('p')[2].find_all('a')[1:]
                stars = [star.text for star in stars]
                votes = movie.find('p', class_='sort-num_votes-visible').find_all('span')[1]['data-value']
                gross_string = movie.find('p', class_='sort-num_votes-visible').find_all('span')[-1]['data-value']
                gross = int(gross_string.replace(",", ""))
                movie_link = 'https://www.imdb.com' + movie.h3.a['href']

                writer.writerow([movie_id, movie_name, rating, runtime, genre, metascore, plot, directors, stars, votes, gross, movie_link])

                movie_id += 1
            print("Scraping complete for page", page)
            page += 1
            start_index += movies_per_page

    print("Scraping and CSV creation successful!")

except requests.exceptions.RequestException as e:
    print("Error occurred during scraping:", str(e))
except Exception as e:
    print("An error occurred:", str(e))


