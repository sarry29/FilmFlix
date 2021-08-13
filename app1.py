from flask import Flask, render_template, request ,  url_for 
import pickle
import pandas as pd
from imdb import IMDb


data = pickle.load(open('moviesOriginal.pkl','rb'))
genres = pickle.load(open('movies.pkl','rb'))

filmList = list(genres.columns)
genreList = list(genres.index[1:])

# create an instance of the IMDb class
ia = IMDb()

def imageDesc(moviesData):
    imageUrl=[]
    castDetail=[]

    print("FILM POSTER URL PROCESSING")
    for i in range(len(moviesData)):
        print(moviesData[i])
        movies = ia.search_movie(moviesData[i])
        code = movies[0].movieID

        series = ia.get_movie(code)
        
        try:
            cast = series['cast']
            cast = cast[:7]
            castDetail.append(",".join(map(str,cast)))
        except:
            cast = "NOT AVAILABLE"
        # getting information
        # getting cover url of the series
        try:
            cover = series.data['cover url']
        except:
            cover = moviesData[i]
        imageUrl.append(cover)

    return imageUrl,castDetail

def genre1(GenreInput, year = 2000):
    # print("INNER : ",GenreInput," ",year)
    x = data['genres'].str.split('|')
    d = data.drop(['genres'], axis = 1)
    x = pd.concat([d, x], axis = 1)
    x = x.explode('genres')
    x= x[(x['genres'] == GenreInput) & (x['year'] >= year)][['title', 'rating', 'year']].sort_values(by = 'rating',
                            ascending = False).reset_index(drop = True).head(10)
    print(GenreInput," MOVIE RELEASE IN NEARBY YEAR : ",year)
    return x

def recommendation_movie1(movie):    
    print(movie)    
    similar_movies = genres.corrwith(genres[movie])
    # print(similar_movies,"\n\n\n")
    similar_movies = similar_movies.sort_values(ascending=False)
    similar_movies = similar_movies.iloc[1:]
    return similar_movies.head(10)


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('detail.html')

@app.route('/genreRec', methods=["GET","POST"])
def genreRec():
    if request.method == "POST":
        detailForm = request.form
        detailForm = dict(detailForm.lists())

        print(detailForm['0'][0]," ",detailForm['1'][0]," ",type(detailForm))
        recommend =  genre1(detailForm["0"][0],int(detailForm["1"][0]))
        print(recommend)
        title = recommend['title']
        rating = recommend['rating']
        year = recommend['year']

        imageUrl,castDetails = imageDesc(title)

        return render_template('genreList.html',title=title,rating=rating,year=year,genreFind=detailForm['0'][0], yearToFind=detailForm['1'][0] , imageUrl=imageUrl , castDetails=castDetails)
    return render_template('home.html',filmList = filmList, genreList=genreList, lenGenre=len(genreList))


@app.route('/movieRec', methods=["GET","POST"])
def movieRec():
    if request.method == "POST":
        detailForm = request.form 
        detailForm = dict(detailForm.lists())
        
        index = detailForm['0'][0]
        filmCol = filmList
        movieName = filmCol[int(index)]
        
        recommend =  recommendation_movie1(movieName)
        # print(recommend,"\n\n\n")
        
        title=list(recommend.index)
        rating=recommend.tolist()
        year=[]
        for i in range(len(title)):
            cur = title[i]
            cur = cur.split(' ')  
            y = cur[-1];
            y = y.strip('(')
            y = y.strip(')')
            cur.pop()
            title[i]=' '.join(cur)
            year.append(y)

        imageUrl,castDetail = imageDesc(title)

        # imageUrl = "https://m.media-amazon.com/images/M/MV5BMjJlMjJlMzYtNmU5Yy00N2MwLWJmMjEtNWUwZWIyMGViZDgyXkEyXkFqcGdeQXVyOTAzMTc2MjA@._V1_SY150_CR0, 0, 101, 150_.jpg"
        # print(imageUrl,"\n",castDetail)
        # print(title," ",year," ",rating)
        # return render_template('movieResult.html',title=title,rating=rating,year = year,movie=movieName,lenFilm=len(title),imageUrl = imageUrl,castDetail=castDetail)
        return render_template('movieResult.html',title=title,rating=rating,year = year,movie=movieName,lenFilm=len(title),imageUrl = imageUrl, castDetail=castDetail)

    return render_template('movieRecommend.html',filmList = filmList ,lenFilm=len(filmList))


if __name__== "__main__":
    # For develop use true for end user make it false
    app.run(debug=False)
    # app.run(debug=True) 
    