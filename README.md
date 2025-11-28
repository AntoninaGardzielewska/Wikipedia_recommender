# Wikipedia_recommender

 * ściągnęłyśmy 1000 artykułów z wikipedii i 1000 artykułów z fandom.wiki używając my_spider.py


* jeżeli użytkownik poda za dużo artykułów wybieramy top 20 najbardziej różniących się od siebie
* zwracamy tylko te artykuły, który użytkownik wcześniej nie widział

"polecana?" przez nas opcja: hybrid
* łączy embedingi - mamy tutaj zrobione różne wagi w zależności od kolejności artykułów, zakładamy, zę historia jest podana od najstarszej do najnowszej
* i tfidf - tutaj wszystkie artykuły od użytkownika są połaczone w jeden długi, znormalizowany i lemmatize tekst, dzięki czemu traktujemy je trochę jak weighted average (a przynajmniej tak mi Miebs powiedział, jak się pytałam czy tak mogę zrobić)
* łączymy je za pomocą zwykłych wag: 0.4 * tfidf_sim + 0.6 * embedding_sim
* zwracamy artykuły powyżej pewnego thresholdu podobobieństwa, jeżeli żaden się nie zalicza to zwracamy top_n najbardziej podobnych

TODO:
* możliwe, że jest za dużo importów, ale niestety mi się nie podświetlają, które są niepotrzebne + wiem, że część Tobie się przyda podczas tworzenia wykresów, więc to można na sam koniec wyczyścić
* nie wiem czy chcemy zachowywać Crawling and scraping
* Present predictions (w user_urls można pokombinować z połączeniem wiki i fandom, aktualnie są tylko z wiki pliki)
